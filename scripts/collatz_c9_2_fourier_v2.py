"""C9.2 Fourier / spectral analysis of v₂ samples – version 2 (stdlib-only).

Reads the CSV produced by collatz_c9_2_sampling_option1.py and computes:

  1. Empirical v₂ distribution:
       p̂(k) = count(v₂ = k) / N,   k = 1, 2, …, K_max
     Theoretical (geometric) baseline:
       p₀(k) = (1/2)^k

  2. Decision metrics (JSON):
       mean_hat_p      – mean of { p̂(k) }
       L2_variance     – Σ_k  (p̂(k) − p₀(k))²   (L2 distance squared)
       sparse_fraction – fraction of FFT bins (over p̂ sequence) with power
                         above the mean power
       avg_rms_ratio   – sqrt( mean( log_ratio² ) )  [empirical Lyapunov RMS]
       per_v2_buckets  – { str(k): count_k } raw histogram
       top_k_freqs     – top-k (freq_index, |amplitude|) from FFT of v₂ sequence

  3. FFT of the full v₂ integer sequence using a partial DFT
     (only the first min(top_k + 1, N//2) frequencies are computed so that
     "stdlib-only" remains feasible for N up to 100 000).

Outputs (filename stems are inferred from the --input path):
  <out_dir>/<stem>_fourier.json    – JSON with all metrics
  <out_dir>/<stem>_spectrum.csv    – freq_index, amplitude columns
"""

import argparse
import csv
import json
import math
import os


# ---------------------------------------------------------------------------
# FFT helpers (stdlib-only, partial-DFT for top-k frequencies)
# ---------------------------------------------------------------------------

def partial_dft_magnitudes(signal: list, num_freqs: int) -> list:
    """Return |X[k]| for k = 0, 1, …, num_freqs-1 using the DFT definition.

    Complexity: O(num_freqs * N).  Suitable when num_freqs << N.
    signal values are expected to be real numbers.
    """
    N = len(signal)
    two_pi_over_N = 2.0 * math.pi / N
    magnitudes = []
    for k in range(num_freqs):
        re = 0.0
        im = 0.0
        freq = k * two_pi_over_N
        for j, x in enumerate(signal):
            angle = freq * j
            re += x * math.cos(angle)
            im -= x * math.sin(angle)
        magnitudes.append(math.sqrt(re * re + im * im))
    return magnitudes


def dft_full(sequence: list) -> list:
    """Full DFT of a short sequence (used for p̂ histogram, length ~30).

    Returns list of complex magnitudes.
    """
    N = len(sequence)
    two_pi_over_N = 2.0 * math.pi / N
    magnitudes = []
    for k in range(N):
        re = 0.0
        im = 0.0
        freq = k * two_pi_over_N
        for j, x in enumerate(sequence):
            angle = freq * j
            re += x * math.cos(angle)
            im -= x * math.sin(angle)
        magnitudes.append(math.sqrt(re * re + im * im))
    return magnitudes


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def read_csv(path: str):
    """Read the sampler CSV.  Returns (n_list, v2_list, log_ratio_list)."""
    n_list, v2_list, log_ratio_list = [], [], []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            n_list.append(int(row["n"]))
            v2_list.append(int(row["v2"]))
            log_ratio_list.append(float(row["log_ratio"]))
    return n_list, v2_list, log_ratio_list


def stem_from_path(input_path: str) -> str:
    """Extract base stem without extension from a file path."""
    return os.path.splitext(os.path.basename(input_path))[0]


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyse(input_path: str, out_dir: str, top_k: int) -> dict:
    print(f"[fourier] reading {input_path} …")
    n_list, v2_list, log_ratio_list = read_csv(input_path)
    N = len(v2_list)
    if N == 0:
        raise ValueError("Input CSV is empty.")

    # ------------------------------------------------------------------
    # 1. Empirical v₂ histogram
    # ------------------------------------------------------------------
    counts: dict = {}
    for v in v2_list:
        counts[v] = counts.get(v, 0) + 1

    K_max = max(counts.keys())
    K_min = min(counts.keys())

    hat_p = {}
    p0 = {}
    for k in range(K_min, K_max + 1):
        hat_p[k] = counts.get(k, 0) / N
        p0[k] = (0.5) ** k   # theoretical geometric baseline

    # ------------------------------------------------------------------
    # 2. Decision metrics
    # ------------------------------------------------------------------
    mean_hat_p = sum(hat_p.values()) / len(hat_p)

    L2_variance = sum((hat_p.get(k, 0.0) - p0[k]) ** 2
                      for k in range(K_min, K_max + 1))

    # avg_rms_ratio: RMS of log_ratio values (empirical Lyapunov measure)
    avg_rms_ratio = math.sqrt(sum(r * r for r in log_ratio_list) / N)

    # ------------------------------------------------------------------
    # 3. Full DFT of the p̂ histogram sequence (sparse_fraction)
    # ------------------------------------------------------------------
    hist_seq = [hat_p.get(k, 0.0) for k in range(1, K_max + 1)]
    hist_magnitudes = dft_full(hist_seq)

    mean_hist_power = sum(m * m for m in hist_magnitudes) / len(hist_magnitudes)
    sparse_fraction = (sum(1 for m in hist_magnitudes if m * m > mean_hist_power)
                       / len(hist_magnitudes))

    # ------------------------------------------------------------------
    # 4. Partial DFT of the full v₂ integer sequence (top-k frequencies)
    # ------------------------------------------------------------------
    # We compute num_compute = min(top_k + 1, N // 2) frequency bins.
    num_compute = min(top_k + 1, max(top_k + 1, N // 2))
    # For very large N, limit to avoid excessive runtime
    num_compute = min(num_compute, 512)
    num_compute = max(num_compute, top_k + 1)

    print(f"[fourier] computing partial DFT ({num_compute} bins over {N} samples) …")
    seq_magnitudes = partial_dft_magnitudes(v2_list, num_compute)

    # top-k by magnitude (skip DC component at k=0)
    indexed = sorted(enumerate(seq_magnitudes[1:], start=1),
                     key=lambda x: x[1], reverse=True)
    top_k_freqs = [[int(freq_idx), round(mag, 8)]
                   for freq_idx, mag in indexed[:top_k]]

    # ------------------------------------------------------------------
    # 5. Assemble results
    # ------------------------------------------------------------------
    per_v2_buckets = {str(k): int(counts.get(k, 0))
                      for k in range(K_min, K_max + 1)}

    results = {
        "input": os.path.basename(input_path),
        "N": N,
        "v2_min": int(K_min),
        "v2_max": int(K_max),
        "mean_hat_p": round(mean_hat_p, 10),
        "L2_variance": round(L2_variance, 12),
        "sparse_fraction": round(sparse_fraction, 8),
        "avg_rms_ratio": round(avg_rms_ratio, 10),
        "per_v2_buckets": per_v2_buckets,
        "top_k_freqs": top_k_freqs,
    }

    # ------------------------------------------------------------------
    # 6. Write outputs
    # ------------------------------------------------------------------
    os.makedirs(out_dir, exist_ok=True)
    stem = stem_from_path(input_path)

    json_path = os.path.join(out_dir, f"{stem}_fourier.json")
    with open(json_path, "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"[fourier] metrics  → {json_path}")

    spectrum_path = os.path.join(out_dir, f"{stem}_spectrum.csv")
    with open(spectrum_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["freq_index", "amplitude"])
        for freq_idx, mag in enumerate(seq_magnitudes):
            writer.writerow([freq_idx, f"{mag:.8f}"])
    print(f"[fourier] spectrum → {spectrum_path}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="C9.2 Fourier v2 analysis (stdlib-only)"
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Path to input CSV (from collatz_c9_2_sampling_option1.py)")
    parser.add_argument("--out-dir", type=str, default=".",
                        help="Directory for output files")
    parser.add_argument("--top-k", type=int, default=50,
                        help="Number of top spectral frequencies to report (default: 50)")
    args = parser.parse_args()

    results = analyse(args.input, args.out_dir, args.top_k)

    print("\n=== Decision Metrics Summary ===")
    print(f"  N              : {results['N']}")
    print(f"  v2 range       : {results['v2_min']} – {results['v2_max']}")
    print(f"  mean_hat_p     : {results['mean_hat_p']}")
    print(f"  L2_variance    : {results['L2_variance']}")
    print(f"  sparse_fraction: {results['sparse_fraction']}")
    print(f"  avg_rms_ratio  : {results['avg_rms_ratio']}")
    print(f"  per_v2_buckets : {results['per_v2_buckets']}")
    print(f"  top-{args.top_k} freqs (idx, |amp|):")
    for freq_idx, mag in results["top_k_freqs"][:10]:
        print(f"    [{freq_idx:4d}]  {mag:.6f}")
    if len(results["top_k_freqs"]) > 10:
        print(f"    … ({len(results['top_k_freqs']) - 10} more in JSON)")


if __name__ == "__main__":
    main()
