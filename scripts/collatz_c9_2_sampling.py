#!/usr/bin/env python3
"""
C9.2 Collatz per-class probability sampler (stdlib only).

Estimates, for each residue class r mod 2^M:
    hat_p(r) = P(event_B | event_A, n ≡ r mod 2^M)

where:
    event_A(n) : n is odd
    event_B(n) : T(n) < n,  T(n) = odd_part(3n+1)  [odd-normalised Collatz step]

Output files (in --outdir, default: <script_dir>/out/):
    c9_2_M{M}_N{N}.csv          per-class table
    c9_2_M{M}_N{N}_summary.json run metadata + global stats

CSV columns:
    class, weighted_count_A, weighted_count_A_and_B,
    hat_p, raw_count_A, raw_count_A_and_B

Usage:
    python3 collatz_c9_2_sampling.py --M 12 --N 100000
    python3 collatz_c9_2_sampling.py --M 14 --N 500000 --seed 7
"""

import argparse
import csv
import json
import math
import os
import random
import sys

# ---------------------------------------------------------------------------
# Maths helpers
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_OUTDIR = os.path.join(_SCRIPT_DIR, "out")


def odd_normalized_collatz(n: int) -> int:
    """Return T(n) = odd part of (3n+1)."""
    m = 3 * n + 1
    while m & 1 == 0:
        m >>= 1
    return m


def event_A(n: int) -> bool:
    """Event A: n is odd."""
    return bool(n & 1)


def event_B(n: int) -> bool:
    """Event B: T(n) < n."""
    return odd_normalized_collatz(n) < n


# ---------------------------------------------------------------------------
# Sampler
# ---------------------------------------------------------------------------

def sample(M: int, N: int, seed: int) -> dict:
    """
    Draw N odd integers uniformly at random and accumulate per-class stats.

    Because event_A ≡ (n odd), we restrict to odd n; consequently every
    sampled n maps to an odd residue class mod 2^M.

    Weight: uniform (1.0 per sample).

    Returns a dict  r -> {weighted_count_A, weighted_count_A_and_B,
                          raw_count_A, raw_count_A_and_B}
    for r in 0 .. 2^M-1.
    """
    rng = random.Random(seed)
    modulus = 1 << M

    counts = {
        r: {"weighted_count_A": 0.0,
            "weighted_count_A_and_B": 0.0,
            "raw_count_A": 0,
            "raw_count_A_and_B": 0}
        for r in range(modulus)
    }

    # Sample from [1, 2^(M+20)] so residue classes are well covered.
    upper = 1 << (M + 20)

    for _ in range(N):
        # Generate a random odd integer in [1, upper]
        n = rng.randint(0, (upper - 1) >> 1) * 2 + 1

        r = n % modulus  # always odd

        counts[r]["weighted_count_A"] += 1.0
        counts[r]["raw_count_A"] += 1

        if event_B(n):
            counts[r]["weighted_count_A_and_B"] += 1.0
            counts[r]["raw_count_A_and_B"] += 1

    return counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2: per residue-class mod 2^M Collatz probability sampler"
    )
    parser.add_argument("--M", type=int, required=True,
                        help="Bit depth: residue classes are mod 2^M")
    parser.add_argument("--N", type=int, required=True,
                        help="Total number of odd integers to sample")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--outdir", type=str, default=_DEFAULT_OUTDIR,
                        help="Output directory")
    args = parser.parse_args()

    M, N, seed = args.M, args.N, args.seed
    os.makedirs(args.outdir, exist_ok=True)

    base = f"c9_2_M{M}_N{N}"
    csv_path  = os.path.join(args.outdir, f"{base}.csv")
    json_path = os.path.join(args.outdir, f"{base}_summary.json")

    print(f"[C9.2 sampler] M={M}  N={N}  seed={seed}", flush=True)
    print(f"[C9.2 sampler] event_A: n odd  |  event_B: T(n)<n", flush=True)
    print(f"[C9.2 sampler] Sampling...", flush=True)

    counts = sample(M, N, seed)
    modulus = 1 << M

    # ---- build rows --------------------------------------------------------
    rows = []
    for r in range(modulus):
        c = counts[r]
        wa  = c["weighted_count_A"]
        wab = c["weighted_count_A_and_B"]
        hat_p = wab / wa if wa > 0 else float("nan")
        rows.append({
            "class":                  r,
            "weighted_count_A":       wa,
            "weighted_count_A_and_B": wab,
            "hat_p":                  hat_p,
            "raw_count_A":            c["raw_count_A"],
            "raw_count_A_and_B":      c["raw_count_A_and_B"],
        })

    # ---- write CSV ---------------------------------------------------------
    fieldnames = [
        "class", "weighted_count_A", "weighted_count_A_and_B",
        "hat_p", "raw_count_A", "raw_count_A_and_B",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # ---- summary stats (non-empty / non-NaN classes) -----------------------
    valid_rows = [r for r in rows if not math.isnan(r["hat_p"])]
    hp = [r["hat_p"] for r in valid_rows]
    n_valid = len(hp)

    if hp:
        p_mean = sum(hp) / n_valid
        p_var  = sum((v - p_mean) ** 2 for v in hp) / n_valid
        p_min  = min(hp)
        p_max  = max(hp)
    else:
        p_mean = p_var = p_min = p_max = float("nan")

    summary = {
        "M":                    M,
        "N":                    N,
        "seed":                 seed,
        "modulus":              modulus,
        "n_classes":            modulus,
        "n_nonempty_classes":   n_valid,
        "event_A":              "n is odd",
        "event_B":              "T(n) < n,  T(n) = odd_part(3n+1)",
        "weight":               "uniform (1.0 per sample)",
        "hat_p_mean":           p_mean,
        "hat_p_var":            p_var,
        "hat_p_min":            p_min,
        "hat_p_max":            p_max,
        "csv_path":             csv_path,
    }

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"[C9.2 sampler] Written: {csv_path}")
    print(f"[C9.2 sampler] Written: {json_path}")
    print(
        f"[C9.2 sampler] hat_p  "
        f"mean={p_mean:.6f}  var={p_var:.6f}  "
        f"min={p_min:.6f}  max={p_max:.6f}  "
        f"classes_used={n_valid}/{modulus}"
    )


if __name__ == "__main__":
    main()
