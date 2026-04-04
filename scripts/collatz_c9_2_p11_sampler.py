#!/usr/bin/env python3
"""
scripts/collatz_c9_2_p11_sampler.py

Stdlib-only Monte-Carlo / exhaustive sampler for C9.2 (issue #3).

Definitions:
  T(n)   = (3n+1) / 2^{v2(3n+1)}   for odd n  (odd-normalised Collatz step)
  A(n)   : v2(3n+1) == 1
  B(n)   : v2(3*T(n)+1) == 1
  I11(n) : A(n) and B(n)
  w(n)   : 1 / log(n)               (contact-form weight)

Weighted probabilities over sample set W:
  P_w(E) = sum_{n in W} w(n)*1_E(n) / sum_{n in W} w(n)

Metrics computed: p_A, p_B, p_A_and_B, p11_conditional (= p_A_and_B/p_A),
  rho (weighted Pearson between 1_A and 1_B).

Outputs:
  <out-dir>/p11_N<N>_<mode>_seed<seed>.csv
  <out-dir>/p11_N<N>_<mode>_seed<seed>_summary.json

Usage example (self-test):
  python3 scripts/collatz_c9_2_p11_sampler.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Core arithmetic
# ---------------------------------------------------------------------------

def v2(x: int) -> int:
    """Return the 2-adic valuation of positive integer x."""
    if x <= 0:
        return 0
    v = 0
    while x & 1 == 0:
        x >>= 1
        v += 1
    return v


def T(n: int) -> int:
    """Odd-normalised Collatz step: T(n) = (3n+1) / 2^{v2(3n+1)} for odd n."""
    x = 3 * n + 1
    while x & 1 == 0:
        x >>= 1
    return x


def compute_row(n: int):
    """
    Return (v2_1, t, v2_2, A, B, w) for odd n.
    v2_1 = v2(3n+1)
    t    = T(n)
    v2_2 = v2(3t+1)
    A    = (v2_1 == 1)
    B    = (v2_2 == 1)
    w    = 1/log(n)
    """
    val1 = v2(3 * n + 1)
    t = T(n)
    val2 = v2(3 * t + 1)
    a = int(val1 == 1)
    b = int(val2 == 1)
    w = 1.0 / math.log(n)
    return val1, t, val2, a, b, w


# ---------------------------------------------------------------------------
# Sampling generators
# ---------------------------------------------------------------------------

def _first_odd_ge(n: int) -> int:
    return n if n & 1 else n + 1


def iter_exhaustive(n_start: int, n_end: int, min_n: int):
    """Yield all odd n in [n_start, n_end) with n >= min_n."""
    lo = max(n_start, min_n)
    lo = _first_odd_ge(lo)
    n = lo
    while n < n_end:
        yield n
        n += 2


def iter_stride(n_start: int, n_end: int, min_n: int, stride_k: int):
    """Yield every stride_k-th odd n in [n_start, n_end) with n >= min_n."""
    lo = max(n_start, min_n)
    lo = _first_odd_ge(lo)
    n = lo
    count = 0
    while n < n_end:
        if count % stride_k == 0:
            yield n
        count += 1
        n += 2


def iter_random(n_start: int, n_end: int, min_n: int, max_samples: int, seed: int):
    """
    Draw up to max_samples odd n uniformly from [n_start, n_end) with n >= min_n.
    Uses reservoir / rejection sampling without materialising the full list.
    """
    rng = random.Random(seed)
    lo = max(n_start, min_n)
    lo = _first_odd_ge(lo)
    # Pool of odd integers in [lo, n_end): indices 0,1,...
    # count = ceil((n_end - lo) / 2)
    if lo >= n_end:
        return
    total_odds = (n_end - lo + 1) // 2  # number of odd n in [lo, n_end)
    k = min(max_samples, total_odds)
    if k <= 0:
        return
    # Sample k distinct indices in [0, total_odds) via Floyd's algorithm
    selected = set()
    for i in range(total_odds - k, total_odds):
        j = rng.randint(0, i)
        if j in selected:
            selected.add(i)
        else:
            selected.add(j)
    for idx in sorted(selected):
        yield lo + 2 * idx


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(rows):
    """
    rows: list of (n, A, B, w, v2_1, T_n, v2_2)
    Returns dict with p_A, p_B, p_A_and_B, p11_conditional, rho, sum_weights.
    """
    sw = sum(r[3] for r in rows)
    if sw == 0:
        return dict(p_A=None, p_B=None, p_A_and_B=None,
                    p11_conditional=None, rho=None, sum_weights=0.0)

    p_a = sum(r[3] * r[1] for r in rows) / sw
    p_b = sum(r[3] * r[2] for r in rows) / sw
    p_ab = sum(r[3] * r[1] * r[2] for r in rows) / sw

    p11_cond = (p_ab / p_a) if p_a > 0 else None

    var_a = p_a * (1.0 - p_a)
    var_b = p_b * (1.0 - p_b)
    cov = p_ab - p_a * p_b
    if var_a > 0 and var_b > 0:
        rho = cov / math.sqrt(var_a * var_b)
    else:
        rho = None

    return dict(
        p_A=p_a, p_B=p_b, p_A_and_B=p_ab,
        p11_conditional=p11_cond, rho=rho,
        sum_weights=sw,
    )


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap_weighted(rows, n_resamples: int, seed: int):
    """
    Weighted bootstrap: resample rows with replacement, weight-proportional.
    Returns (se_p11, se_rho, ci95_p11, ci95_rho).
    """
    if not rows:
        return None
    rng = random.Random(seed + 9999)
    weights = [r[3] for r in rows]
    total_w = sum(weights)
    if total_w == 0:
        return None
    cum = []
    acc = 0.0
    for ww in weights:
        acc += ww
        cum.append(acc)

    def draw_index():
        u = rng.random() * total_w
        lo2, hi2 = 0, len(cum) - 1
        while lo2 < hi2:
            mid = (lo2 + hi2) // 2
            if cum[mid] < u:
                lo2 = mid + 1
            else:
                hi2 = mid
        return lo2

    p11_samples = []
    rho_samples = []
    n = len(rows)
    for _ in range(n_resamples):
        sample = [rows[draw_index()] for _ in range(n)]
        m = compute_metrics(sample)
        p11_samples.append(m["p11_conditional"])
        rho_samples.append(m["rho"])

    def se_ci(vals):
        vals2 = [v for v in vals if v is not None]
        if not vals2:
            return None, (None, None)
        mn = sum(vals2) / len(vals2)
        se = math.sqrt(sum((x - mn) ** 2 for x in vals2) / len(vals2))
        vals2_s = sorted(vals2)
        lo2 = vals2_s[int(0.025 * len(vals2_s))]
        hi2 = vals2_s[min(int(0.975 * len(vals2_s)), len(vals2_s) - 1)]
        return se, (lo2, hi2)

    se_p11, ci_p11 = se_ci(p11_samples)
    se_rho, ci_rho = se_ci(rho_samples)
    return dict(
        n_resamples=n_resamples,
        mode="weighted",
        p11_se=se_p11,
        rho_se=se_rho,
        p11_ci_95=list(ci_p11) if ci_p11 else None,
        rho_ci_95=list(ci_rho) if ci_rho else None,
    )


def bootstrap_block(rows, n_resamples: int, seed: int, block_size: int = 100):
    """
    Block bootstrap: resample contiguous blocks of rows with replacement.
    """
    if not rows:
        return None
    rng = random.Random(seed + 7777)
    n = len(rows)
    n_blocks = max(1, n // block_size)
    actual_block = n // n_blocks

    p11_samples = []
    rho_samples = []
    for _ in range(n_resamples):
        sample = []
        for _ in range(n_blocks):
            start = rng.randint(0, n - actual_block)
            sample.extend(rows[start: start + actual_block])
        m = compute_metrics(sample)
        p11_samples.append(m["p11_conditional"])
        rho_samples.append(m["rho"])

    def se_ci(vals):
        vals2 = [v for v in vals if v is not None]
        if not vals2:
            return None, (None, None)
        mn = sum(vals2) / len(vals2)
        se = math.sqrt(sum((x - mn) ** 2 for x in vals2) / len(vals2))
        vals2_s = sorted(vals2)
        lo2 = vals2_s[int(0.025 * len(vals2_s))]
        hi2 = vals2_s[min(int(0.975 * len(vals2_s)), len(vals2_s) - 1)]
        return se, (lo2, hi2)

    se_p11, ci_p11 = se_ci(p11_samples)
    se_rho, ci_rho = se_ci(rho_samples)
    return dict(
        n_resamples=n_resamples,
        mode="block",
        p11_se=se_p11,
        rho_se=se_rho,
        p11_ci_95=list(ci_p11) if ci_p11 else None,
        rho_ci_95=list(ci_rho) if ci_rho else None,
    )


# ---------------------------------------------------------------------------
# Per-residue breakdown
# ---------------------------------------------------------------------------

def per_residue_breakdown(rows, M: int):
    """
    Group rows by a = n mod 2^M (odd residues only).
    Returns dict: residue -> {count, weighted_count, p_A, p_B, p_A_and_B, p11}.
    """
    mod = 1 << M
    groups: dict[int, list] = {}
    for r in rows:
        n = r[0]
        a = n % mod
        if a not in groups:
            groups[a] = []
        groups[a].append(r)

    result = {}
    for a in sorted(groups.keys()):
        g = groups[a]
        m = compute_metrics(g)
        result[str(a)] = dict(
            count=len(g),
            weighted_count=m["sum_weights"],
            p_A=m["p_A"],
            p_B=m["p_B"],
            p_A_and_B=m["p_A_and_B"],
            p11=m["p11_conditional"],
        )
    return result


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_self_test():
    """Validate basic invariants on small known inputs."""
    errors = []

    # T(n) must be odd
    for n in [3, 5, 7, 9, 11, 13, 15, 21, 33, 35, 99, 101]:
        t = T(n)
        if t % 2 == 0:
            errors.append(f"T({n}) = {t} is even (must be odd)")

    # v2(3n+1) >= 1 for all odd n (since 3n+1 is even when n is odd)
    for n in [1, 3, 5, 7, 33, 101, 999]:
        val = v2(3 * n + 1)
        if val < 1:
            errors.append(f"v2(3*{n}+1) = {val}, expected >= 1")

    # weights must be finite and positive for n >= 3
    for n in [33, 100, 10001]:
        n_odd = n if n % 2 == 1 else n + 1
        w = 1.0 / math.log(n_odd)
        if not (math.isfinite(w) and w > 0):
            errors.append(f"w({n_odd}) = {w}, expected finite positive")

    # check A(n): n = 3 mod 4  => v2(3n+1) = 1
    # n=3: 3*3+1=10, v2=1 ✓; n=7: 3*7+1=22, v2=1 ✓
    for n, expected_A in [(3, True), (7, True), (5, False), (1, False)]:
        val1 = v2(3 * n + 1)
        got_A = (val1 == 1)
        if got_A != expected_A:
            errors.append(f"A({n}): expected {expected_A}, got {got_A} (v2={val1})")

    # probabilities in [0, 1]
    rows = []
    for n in range(33, 500, 2):
        val1, t, val2, a, b, w = compute_row(n)
        rows.append((n, a, b, w, val1, t, val2))
    m = compute_metrics(rows)
    for key in ["p_A", "p_B", "p_A_and_B"]:
        val = m[key]
        if val is None or not (0.0 <= val <= 1.0):
            errors.append(f"Metric {key} = {val} not in [0,1]")

    # bootstrap output shapes
    bs = bootstrap_weighted(rows[:50], n_resamples=50, seed=42)
    if bs is None:
        errors.append("bootstrap_weighted returned None unexpectedly")
    else:
        for key in ["n_resamples", "mode", "p11_se", "rho_se", "p11_ci_95", "rho_ci_95"]:
            if key not in bs:
                errors.append(f"bootstrap result missing key: {key}")
        if bs.get("p11_ci_95") is not None:
            ci = bs["p11_ci_95"]
            if len(ci) != 2:
                errors.append(f"p11_ci_95 should have 2 elements, got {len(ci)}")

    # CSV column count
    sample_rows = list(iter_exhaustive(33, 101, 33))
    if len(sample_rows) == 0:
        errors.append("iter_exhaustive produced no rows for [33,101)")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\nSelf-test FAILED ({len(errors)} error(s))", file=sys.stderr)
        return False
    else:
        print("Self-test PASSED (all invariants hold)")
        return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_output_stem(args) -> str:
    seed_tag = f"_seed{args.seed}" if args.mode in ("random",) else ""
    return f"p11_N{args.N}_{args.mode}{seed_tag}"


def main():
    ap = argparse.ArgumentParser(
        description="C9.2 weighted (1,1) probability sampler (stdlib-only)"
    )
    ap.add_argument("--M", type=int, default=None,
                    help="If given, produce per-residue breakdown by a = n mod 2^M")
    ap.add_argument("--N", type=int, default=100000,
                    help="Window start (lower bound)")
    ap.add_argument("--window-size", type=int, default=None,
                    help="Window size; if omitted use dyadic [N, 2N)")
    ap.add_argument("--mode", choices=["exhaustive", "random", "stride"],
                    default="exhaustive")
    ap.add_argument("--max-samples", type=int, default=1_000_000,
                    help="Cap for random/stride modes")
    ap.add_argument("--stride-k", type=int, default=None,
                    help="Stride for stride mode; auto-computed if omitted")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", type=str, default="results/c9_2")
    ap.add_argument("--bootstrap", type=int, default=1000,
                    help="Number of bootstrap resamples (0 to disable)")
    ap.add_argument("--bootstrap-mode", choices=["weighted", "block"],
                    default="weighted")
    ap.add_argument("--min-n", type=int, default=33,
                    help="Minimum n to include (must be odd; default 33)")
    ap.add_argument("--self-test", action="store_true",
                    help="Run built-in invariant checks and exit")
    args = ap.parse_args()

    if args.self_test:
        ok = run_self_test()
        sys.exit(0 if ok else 1)

    # Validate min_n
    if args.min_n < 3:
        ap.error("--min-n must be >= 3")
    if args.min_n % 2 == 0:
        args.min_n += 1  # ensure odd

    # Determine window
    N = args.N
    if args.window_size is not None:
        window_size = args.window_size
        n_end = N + window_size
        dyadic = False
    else:
        window_size = N  # dyadic: [N, 2N)
        n_end = 2 * N
        dyadic = True

    n_start = N

    # Build generator
    if args.mode == "exhaustive":
        gen = iter_exhaustive(n_start, n_end, args.min_n)
    elif args.mode == "random":
        gen = iter_random(n_start, n_end, args.min_n, args.max_samples, args.seed)
    elif args.mode == "stride":
        if args.stride_k is not None:
            stride_k = args.stride_k
        else:
            # Estimate total odds in window then compute stride
            lo = max(n_start, args.min_n)
            lo = _first_odd_ge(lo)
            total_odds = max(1, (n_end - lo + 1) // 2)
            stride_k = max(1, total_odds // args.max_samples)
            # Ensure stride_k is odd to avoid mod-4 residue-class aliasing.
            # An even stride steps by stride_k*2 in value, which is 0 mod 4,
            # so the sampled n would all share the same residue mod 4.
            if stride_k % 2 == 0:
                stride_k += 1  # round up to nearest odd (stays <= max_samples)
        gen = iter_stride(n_start, n_end, args.min_n, stride_k)
    else:
        ap.error(f"Unknown mode: {args.mode}")

    # Collect rows
    rows = []
    for n in gen:
        val1, t, val2, a, b, w = compute_row(n)
        rows.append((n, a, b, w, val1, t, val2))

    # Compute metrics
    metrics = compute_metrics(rows)

    # Bootstrap
    bs_result = None
    if args.bootstrap > 0 and rows:
        if args.bootstrap_mode == "weighted":
            bs_result = bootstrap_weighted(rows, args.bootstrap, args.seed)
        else:
            bs_result = bootstrap_block(rows, args.bootstrap, args.seed)

    # Per-residue breakdown
    residue_breakdown = None
    if args.M is not None:
        residue_breakdown = per_residue_breakdown(rows, args.M)

    # Output paths
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    stem = build_output_stem(args)
    csv_path = Path(args.out_dir) / f"{stem}.csv"
    json_path = Path(args.out_dir) / f"{stem}_summary.json"

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        w_csv = csv.writer(f)
        w_csv.writerow(["n", "A", "B", "w", "v2_1", "T_n", "v2_2"])
        for r in rows:
            n_val, a, b, ww, val1, t, val2 = r
            w_csv.writerow([n_val, a, b, f"{ww:.10f}", val1, t, val2])

    # Build summary JSON
    summary = {
        "M": args.M,
        "N": N,
        "window_size": window_size,
        "window": {
            "start": n_start,
            "end": n_end,
            "exclusive_end": True,
            "dyadic": dyadic,
        },
        "mode": args.mode,
        "seed": args.seed,
        "min_n": args.min_n,
        "n_sampled": len(rows),
        "sum_weights": metrics["sum_weights"],
        "p_A": metrics["p_A"],
        "p_B": metrics["p_B"],
        "p_A_and_B": metrics["p_A_and_B"],
        "p11_conditional": metrics["p11_conditional"],
        "rho": metrics["rho"],
        "note": (
            "T(n)=(3n+1)/2^{v2(3n+1)} for odd n. "
            "A(n): v2(3n+1)=1. B(n): v2(3*T(n)+1)=1. "
            "w(n)=1/log(n). "
            "P_w(E)=sum_W w(n)*1_E(n)/sum_W w(n). "
            "p11_conditional = P_w(A and B)/P_w(A). "
            "rho = Cov_w(1_A,1_B)/sqrt(Var_w(1_A)*Var_w(1_B))."
        ),
    }
    if bs_result is not None:
        summary["bootstrap"] = bs_result
    if residue_breakdown is not None:
        summary["per_residue"] = residue_breakdown

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Console summary
    print(f"Mode          : {args.mode}")
    print(f"Window        : [{n_start}, {n_end})  (dyadic={dyadic})")
    print(f"n_sampled     : {len(rows)}")
    print(f"sum_weights   : {metrics['sum_weights']:.6f}")
    print(f"p_A           : {metrics['p_A']}")
    print(f"p_B           : {metrics['p_B']}")
    print(f"p_A_and_B     : {metrics['p_A_and_B']}")
    print(f"p11_cond      : {metrics['p11_conditional']}")
    print(f"rho           : {metrics['rho']}")
    print(f"CSV  -> {csv_path}")
    print(f"JSON -> {json_path}")


if __name__ == "__main__":
    main()
