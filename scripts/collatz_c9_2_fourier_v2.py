"""
collatz_c9_2_fourier_v2.py  –  Gold Fourier v2
Reads   : c9_2_M{M}_N{N}.csv  (columns n, xi, v2_xi, p_hat)
Produces:
  c9_2_M{M}_N{N}_fourier.json        – summary metrics
  c9_2_M{M}_N{N}_fourier_modes.csv   – top-K Fourier modes

Metrics in JSON
---------------
mean_hat_p            – mean of p_hat column
l2_variance_empirical – Var[xi] (sample variance of xi values)
sparse_fraction_hatp  – fraction of DFT bins with |F[k]| > threshold
per_v2_bucket         – dict: v2_value -> {count, mean_xi, mean_p_hat}
avg_rms_ratio         – mean over per-v2 buckets of (rms_xi / global_rms_xi)

Fourier
-------
Policy A: zero-mean the signal before DFT (subtract mean(xi)).
Radix-2 FFT (stdlib cmath only; zero-pad to next power of 2 if needed).
"""

import argparse
import cmath
import csv
import json
import math
import os
import sys


# ---------------------------------------------------------------------------
# Radix-2 Cooley-Tukey FFT  (in-place, iterative)
# ---------------------------------------------------------------------------

def _next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p <<= 1
    return p


def fft(x: list) -> list:
    """Radix-2 iterative Cooley-Tukey FFT.
    Input length must be a power of 2.
    Returns a new list of complex values."""
    N = len(x)
    assert N & (N - 1) == 0, "Length must be a power of 2"
    a = [complex(v) for v in x]

    # bit-reversal permutation
    j = 0
    for i in range(1, N):
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    # butterfly passes
    length = 2
    while length <= N:
        half = length >> 1
        w = cmath.exp(-2j * cmath.pi / length)
        for i in range(0, N, length):
            wn = 1 + 0j
            for k in range(half):
                u = a[i + k]
                v = wn * a[i + k + half]
                a[i + k] = u + v
                a[i + k + half] = u - v
                wn *= w
        length <<= 1

    return a


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def load_csv(path: str):
    """Returns list of dicts with keys: n(int), xi(int), v2_xi(int), p_hat(float)."""
    rows = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append({
                "n":      int(r["n"]),
                "xi":     int(r["xi"]),
                "v2_xi":  int(r["v2_xi"]),
                "p_hat":  float(r["p_hat"]),
            })
    return rows


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def sample_variance(vals: list) -> float:
    n = len(vals)
    if n < 2:
        return 0.0
    mu = sum(vals) / n
    return sum((v - mu) ** 2 for v in vals) / (n - 1)


def rms(vals: list) -> float:
    if not vals:
        return 0.0
    return math.sqrt(sum(v * v for v in vals) / len(vals))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="C9.2 Fourier analysis v2")
    p.add_argument("--input",   required=True, help="Path to input CSV")
    p.add_argument("--out-dir", required=True, help="Output directory")
    p.add_argument("--top-k",   type=int, default=20,
                   help="Number of top modes to write to CSV")
    p.add_argument("--sparse-threshold", type=float, default=None,
                   help="Threshold for sparse_fraction_hatp; default = 1/sqrt(N)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    rows = load_csv(args.input)
    if not rows:
        print("ERROR: empty input CSV", file=sys.stderr)
        sys.exit(1)

    # ---- derive stem name for outputs ----
    base = os.path.splitext(os.path.basename(args.input))[0]  # e.g. c9_2_M8_N10000
    os.makedirs(args.out_dir, exist_ok=True)

    out_json = os.path.join(args.out_dir, f"{base}_fourier.json")
    out_csv  = os.path.join(args.out_dir, f"{base}_fourier_modes.csv")

    n_rows = len(rows)
    xi_vals   = [r["xi"]    for r in rows]
    p_vals    = [r["p_hat"] for r in rows]
    v2_vals   = [r["v2_xi"] for r in rows]

    # ---- basic metrics ----
    mean_hat_p            = sum(p_vals) / n_rows
    l2_variance_empirical = sample_variance(xi_vals)

    # ---- FFT (Policy A: zero-mean xi) ----
    mean_xi = sum(xi_vals) / n_rows
    signal  = [x - mean_xi for x in xi_vals]

    N_fft = _next_pow2(n_rows)
    # zero-pad
    padded = signal + [0.0] * (N_fft - n_rows)
    F = fft(padded)

    abs_F = [abs(c) for c in F]
    threshold = args.sparse_threshold if args.sparse_threshold is not None \
                else 1.0 / math.sqrt(n_rows)
    sparse_fraction_hatp = sum(1 for a in abs_F if a > threshold) / N_fft

    # ---- per-v2 bucket stats ----
    buckets: dict = {}
    for r in rows:
        key = r["v2_xi"]
        if key not in buckets:
            buckets[key] = {"count": 0, "sum_xi": 0.0, "sum_p": 0.0, "sq_xi": 0.0}
        buckets[key]["count"]  += 1
        buckets[key]["sum_xi"] += r["xi"]
        buckets[key]["sum_p"]  += r["p_hat"]
        buckets[key]["sq_xi"]  += r["xi"] ** 2

    global_rms_xi = rms(xi_vals)

    per_v2_bucket = {}
    rms_ratios    = []
    for k, b in sorted(buckets.items()):
        cnt      = b["count"]
        mean_xi_b = b["sum_xi"] / cnt
        mean_p_b  = b["sum_p"]  / cnt
        rms_xi_b  = math.sqrt(b["sq_xi"] / cnt)
        ratio     = rms_xi_b / global_rms_xi if global_rms_xi > 0 else 0.0
        rms_ratios.append(ratio)
        per_v2_bucket[str(k)] = {
            "count":     cnt,
            "mean_xi":   mean_xi_b,
            "mean_p_hat": mean_p_b,
            "rms_xi":    rms_xi_b,
            "rms_ratio": ratio,
        }

    avg_rms_ratio = sum(rms_ratios) / len(rms_ratios) if rms_ratios else 0.0

    # ---- write JSON ----
    summary = {
        "input_file":             os.path.basename(args.input),
        "n_samples":              n_rows,
        "mean_hat_p":             mean_hat_p,
        "l2_variance_empirical":  l2_variance_empirical,
        "sparse_fraction_hatp":   sparse_fraction_hatp,
        "per_v2_bucket":          per_v2_bucket,
        "avg_rms_ratio":          avg_rms_ratio,
        "fft_n":                  N_fft,
        "mean_xi":                mean_xi,
    }
    with open(out_json, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"JSON → {out_json}")

    # ---- write top-K modes CSV ----
    # Only first half of spectrum (real signal symmetry)
    half = N_fft // 2 + 1
    modes = []
    for k in range(half):
        xi_k = k  # frequency index
        modes.append((xi_k, v2(k) if k > 0 else 0, abs_F[k], F[k].real, F[k].imag))

    modes.sort(key=lambda m: -m[2])  # sort by |F| descending
    top = modes[:args.top_k]

    with open(out_csv, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["xi", "v2_xi", "absF", "reF", "imF"])
        for row in top:
            writer.writerow(row)
    print(f"CSV  → {out_csv}")

    # ---- brief summary to stdout ----
    print(f"n_samples             = {n_rows}")
    print(f"mean_hat_p            = {mean_hat_p:.6f}")
    print(f"l2_variance_empirical = {l2_variance_empirical:.4f}")
    print(f"sparse_fraction_hatp  = {sparse_fraction_hatp:.6f}")
    print(f"avg_rms_ratio         = {avg_rms_ratio:.6f}")
    print(f"per_v2 buckets        = {list(per_v2_bucket.keys())}")


def v2(n: int) -> int:
    """2-adic valuation."""
    if n == 0:
        return 0
    k = 0
    while n % 2 == 0:
        n >>= 1
        k += 1
    return k


if __name__ == "__main__":
    main()
