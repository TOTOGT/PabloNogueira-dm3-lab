#!/usr/bin/env python3
"""
scripts/collatz_c9_2_sampling_option1.py  (graded drift observable)
Window: n in [N, 2N] inclusive, odd n only.
Grouping: a = n mod 2^M.
Observable: hat_p(a) = mean log(T_syr(n)/n) over odd n ≡ a (mod 2^M) in [N,2N].
T_syr(n) = (3n+1)/2^v2(3n+1).
"""

from __future__ import annotations
import argparse, csv, json, math, os

def v2_int(x: int) -> int:
    v = 0
    while (x & 1) == 0:
        x >>= 1; v += 1
    return v

def T_syr(n: int) -> int:
    x = 3 * n + 1
    x >>= v2_int(x)
    return x

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--out-dir", type=str, default="scripts/out")
    # kept for CLI compat with runner
    ap.add_argument("--window-size", type=int, default=None)
    ap.add_argument("--mode", default="exhaustive")
    ap.add_argument("--max-samples", type=int, default=None)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    M, N, q = args.M, args.N, 1 << args.M
    os.makedirs(args.out_dir, exist_ok=True)
    csv_path     = os.path.join(args.out_dir, f"c9_2_M{M}_N{N}.csv")
    summary_path = os.path.join(args.out_dir, f"c9_2_M{M}_N{N}_summary.json")

    count     = [0]   * q
    sum_drift = [0.0] * q
    total_n   = 0
    total_d   = 0.0

    start = N if (N & 1) == 1 else N + 1
    for n in range(start, 2 * N + 1, 2):
        a = n % q
        t = T_syr(n)
        d = math.log(t) - math.log(n)
        count[a]     += 1
        sum_drift[a] += d
        total_n      += 1
        total_d      += d

    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["residue_a","raw_count_A","raw_count_AB",
                    "weighted_A","weighted_AB","hat_p"])
        for a in range(q):
            if (a & 1) == 0 or count[a] == 0:
                w.writerow([a, 0, 0, 0.0, 0.0, ""])
                continue
            c  = count[a]
            sd = sum_drift[a]
            w.writerow([a, c, c, float(c), float(sd), sd / c])

    mean_global = total_d / total_n if total_n else float("nan")
    summary = {
        "observable": "mean log(T_syr(n)/n) per residue class",
        "window": [N, 2*N],
        "M": M, "N": N, "q": q,
        "total_odd_samples": total_n,
        "global_mean_log_drift": mean_global,
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Sampler done → {csv_path}")
    print(f"Global mean log-drift: {mean_global:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
