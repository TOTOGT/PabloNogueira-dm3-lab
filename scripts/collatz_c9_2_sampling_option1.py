"""
C9.2 Sampling Option 1: Graded drift sampling over a dyadic window,
stratified per odd residue class mod 2^M.

For each odd residue class a mod 2^M this script:
  1. Draws n_per_class random odd integers n ≡ a (mod 2^M) from the
     dyadic window [2^dyadic_exp, 2^(dyadic_exp+1) - 1].
  2. Computes the log-drift  log(T(n) / n)  where T is the Syracuse
     fully-reduced odd-to-odd map: T(n) = (3n+1) / 2^v2(3n+1).
  3. Accumulates per-residue mean log-drift  hat_p[a].

Outputs (in --out-dir):
  c9_2_M{M}_N{N}.csv           -- one row per sample: residue, n, log_drift
  c9_2_M{M}_N{N}_summary.json  -- summary statistics
"""

import argparse
import csv
import json
import math
import os
import random


# ---------------------------------------------------------------------------
# Syracuse map (fully-reduced odd-to-odd form)
# ---------------------------------------------------------------------------

def T(n: int) -> int:
    """Return (3n+1) / 2^v2(3n+1), always odd."""
    m = 3 * n + 1
    while m % 2 == 0:
        m //= 2
    return m


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="C9.2 Option-1 sampler: graded drift over dyadic window."
    )
    parser.add_argument("--M", type=int, required=True,
                        help="Modulus exponent: modulus = 2^M")
    parser.add_argument("--N", type=int, required=True,
                        help="Total target sample count (distributed evenly across residues)")
    parser.add_argument("--dyadic-exp", type=int, default=20,
                        help="Dyadic window base exponent k: n ∈ [2^k, 2^(k+1)-1] (default: 20)")
    parser.add_argument("--out-dir", type=str, default="scripts/out",
                        help="Directory to write output files (default: scripts/out)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    modulus = 2 ** args.M
    odd_residues = list(range(1, modulus, 2))   # 2^(M-1) odd residue classes
    n_per_class = max(1, args.N // len(odd_residues))

    # Dyadic window [lo, hi]
    k = args.dyadic_exp
    lo = 2 ** k
    hi = 2 ** (k + 1) - 1

    rows: list[tuple[int, int, float]] = []
    per_residue_stats: dict[int, dict] = {}

    for a in odd_residues:
        # Smallest n ≡ a (mod modulus) with n >= lo
        offset = (a - lo % modulus) % modulus
        base = lo + offset
        if base > hi:
            continue
        k_max = (hi - base) // modulus
        if k_max < 0:
            continue

        logs: list[float] = []
        for _ in range(n_per_class):
            idx = random.randint(0, k_max)
            n = base + idx * modulus
            log_drift = math.log(T(n) / n)
            logs.append(log_drift)
            rows.append((a, n, log_drift))

        if logs:
            per_residue_stats[a] = {
                "mean_log_drift": sum(logs) / len(logs),
                "count": len(logs),
            }

    # Global statistics
    all_logs = [r[2] for r in rows]
    total = len(all_logs)
    global_mean = sum(all_logs) / total if total > 0 else float("nan")

    n_res = len(per_residue_stats)
    mean_hat_p = (
        sum(v["mean_log_drift"] for v in per_residue_stats.values()) / n_res
        if n_res > 0 else float("nan")
    )
    l2_variance = (
        sum((v["mean_log_drift"] - mean_hat_p) ** 2 for v in per_residue_stats.values()) / n_res
        if n_res > 0 else float("nan")
    )

    # Write CSV
    csv_path = os.path.join(args.out_dir, f"c9_2_M{args.M}_N{args.N}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["residue", "n", "log_drift"])
        for a, n, ld in rows:
            writer.writerow([a, n, f"{ld:.10f}"])

    # Write summary JSON
    summary = {
        "M": args.M,
        "N": args.N,
        "modulus": modulus,
        "num_odd_residues": len(odd_residues),
        "n_per_class": n_per_class,
        "total_samples": total,
        "dyadic_exp": args.dyadic_exp,
        "seed": args.seed,
        "global_mean_log_drift": global_mean,
        "mean_hat_p": mean_hat_p,
        "l2_variance_empirical": l2_variance,
        "per_residue": {
            str(a): v for a, v in sorted(per_residue_stats.items())
        },
    }
    json_path = os.path.join(args.out_dir, f"c9_2_M{args.M}_N{args.N}_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Written: {csv_path}  ({total} rows)")
    print(f"Written: {json_path}")


if __name__ == "__main__":
    main()
