#!/usr/bin/env python3
"""
collatz_c9_2_sampling.py
========================
Empirical sampling for the D9 modular mixing hypothesis (H_mix).

For a given M and window I=[N, N+window_size), enumerate all admissible
residue classes a mod 2^M (odd a with v2(3a+1)=1, i.e. a ≡ 3 mod 4),
then sample odd n in the window with n ≡ a (mod 2^M) and A(n) true.

For each such (residue, n) pair compute:
  - A(n) : v2(3n+1) = 1
  - B(n) : v2(3*T(n)+1) = 1
  - w(n) = 1/log(n)

Outputs:
  out/residue_stats_M{M}_N{N}.csv
  out/summary_M{M}_N{N}.csv

See docs/c9_1_hypothesis.md and scripts/README.md for context.
"""

import argparse
import csv
import math
import os
import random
import sys


# ── 2-adic helpers ──────────────────────────────────────────────────────────

def v2(n: int) -> int:
    """Return the 2-adic valuation of n (largest k with 2^k | n)."""
    if n == 0:
        return float('inf')
    k = 0
    while n % 2 == 0:
        n >>= 1
        k += 1
    return k


def collatz_next_odd(n: int) -> int:
    """Apply one Collatz macro-step: T(n) = (3n+1) / 2^{v2(3n+1)}."""
    m = 3 * n + 1
    return m >> v2(m)


def event_A(n: int) -> bool:
    """A(n): v2(3n+1) = 1."""
    return v2(3 * n + 1) == 1


def event_B(n: int) -> bool:
    """B(n): v2(3*T(n)+1) = 1."""
    return v2(3 * collatz_next_odd(n) + 1) == 1


# ── Admissible residues ──────────────────────────────────────────────────────

def admissible_residues(M: int):
    """
    Return all admissible residues a mod 2^M:
      - a is odd
      - v2(3a+1) = 1  (equivalently a ≡ 3 mod 4, since 3·3≡1 mod 4)
    """
    mod = 1 << M  # 2^M
    result = []
    for a in range(1, mod, 2):      # odd residues
        if v2(3 * a + 1) == 1:      # A-event true
            result.append(a)
    return result


# ── Sampling ─────────────────────────────────────────────────────────────────

def sample_residue(
    a: int,
    M: int,
    N: int,
    window_end: int,
    mode: str,
    max_samples: int,
    stride: int,
    rng: random.Random,
) -> dict:
    """
    Sample odd n in [N, window_end) with n ≡ a (mod 2^M) and A(n) true.
    Returns a dict with weighted counts.
    """
    mod = 1 << M

    # First odd n >= N that is ≡ a (mod mod)
    # We need n ≡ a (mod mod) and n odd.
    # Since a is odd and mod is a power of 2, n ≡ a (mod mod) => n is odd.
    start = N + ((a - N) % mod)
    if start < N:
        start += mod

    # Build candidate list depending on mode
    if mode in ('exhaustive', 'stride'):
        step = mod if mode == 'exhaustive' else mod * stride
        candidates = range(start, window_end, step)
    elif mode == 'random':
        # Collect all candidates then sample randomly
        all_cands = list(range(start, window_end, mod))
        if len(all_cands) > max_samples:
            candidates = rng.sample(all_cands, max_samples)
        else:
            candidates = all_cands
    else:
        raise ValueError(f"Unknown mode: {mode!r}")

    count_A = 0
    count_AB = 0
    weighted_A = 0.0
    weighted_AB = 0.0
    processed = 0

    for n in candidates:
        if processed >= max_samples and mode != 'random':
            break
        if n < 3:
            continue
        if not event_A(n):
            # Should always be true for admissible a, but guard anyway
            continue
        w = 1.0 / math.log(n)
        count_A += 1
        weighted_A += w
        if event_B(n):
            count_AB += 1
            weighted_AB += w
        processed += 1

    p_hat = (weighted_AB / weighted_A) if weighted_A > 0 else float('nan')

    return {
        'count_A': count_A,
        'count_AB': count_AB,
        'weighted_A': weighted_A,
        'weighted_AB': weighted_AB,
        'p_hat': p_hat,
    }


# ── Output helpers ────────────────────────────────────────────────────────────

def ensure_out_dir(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)


def write_residue_csv(path: str, M: int, N: int, window_end: int, rows: list):
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'M', 'N', 'window_end', 'residue_a',
            'count_A', 'count_AB', 'weighted_A', 'weighted_AB', 'p_hat',
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_csv(path: str, M: int, N: int, window_end: int,
                      mean_p: float, mean_over_residues: float,
                      max_deviation: float, aggregate_deviation: float,
                      quantiles: dict):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        writer.writerow(['M', M])
        writer.writerow(['N', N])
        writer.writerow(['window_end', window_end])
        writer.writerow(['mean_p_overall', mean_p])
        writer.writerow(['mean_p_over_residues', mean_over_residues])
        writer.writerow(['max_deviation_per_residue', max_deviation])
        writer.writerow(['aggregate_signed_deviation_D_N', aggregate_deviation])
        for q_label, q_val in sorted(quantiles.items()):
            writer.writerow([f'p_hat_q{q_label}', q_val])


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description='Empirical sampling for Collatz D9 mixing hypothesis (H_mix).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--M', type=int, default=4,
                        help='Modulus exponent (residues mod 2^M).')
    parser.add_argument('--N', type=int, default=100000,
                        help='Window start (inclusive).')
    parser.add_argument('--window-size', type=int, default=None,
                        help='Window size (default: N, giving I=[N,2N)).')
    parser.add_argument('--mode', choices=['exhaustive', 'stride', 'random'],
                        default='exhaustive',
                        help='Sampling mode within each residue class.')
    parser.add_argument('--stride', type=int, default=1,
                        help='Stride multiplier (used with --mode stride).')
    parser.add_argument('--max-samples', type=int, default=100000,
                        help='Max samples per residue class.')
    parser.add_argument('--seed', type=int, default=42,
                        help='RNG seed (used with --mode random).')
    parser.add_argument('--out-dir', type=str, default='out',
                        help='Output directory for CSV files.')
    return parser.parse_args()


def quantile(values: list, q: float) -> float:
    """Simple quantile computation (linear interpolation)."""
    if not values:
        return float('nan')
    sv = sorted(values)
    n = len(sv)
    idx = q * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return sv[lo] * (1 - frac) + sv[hi] * frac


def main():
    args = parse_args()

    M = args.M
    N = args.N
    window_size = args.window_size if args.window_size is not None else N
    window_end = N + window_size
    mode = args.mode
    max_samples = args.max_samples
    stride = args.stride
    out_dir = args.out_dir
    rng = random.Random(args.seed)

    admissible = admissible_residues(M)
    n_admissible = len(admissible)

    print(f"D9 H_mix empirical sampler")
    print(f"  M={M}, 2^M={1<<M}, admissible residues: {n_admissible}")
    print(f"  Window I=[{N}, {window_end})  (size={window_size})")
    print(f"  Mode: {mode}, max_samples/residue: {max_samples}, seed: {args.seed}")
    print()

    rows = []
    total_wA = 0.0
    total_wAB = 0.0

    for a in admissible:
        stats = sample_residue(
            a=a, M=M, N=N, window_end=window_end,
            mode=mode, max_samples=max_samples,
            stride=stride, rng=rng,
        )
        row = {
            'M': M,
            'N': N,
            'window_end': window_end,
            'residue_a': a,
            'count_A': stats['count_A'],
            'count_AB': stats['count_AB'],
            'weighted_A': stats['weighted_A'],
            'weighted_AB': stats['weighted_AB'],
            'p_hat': stats['p_hat'],
        }
        rows.append(row)
        total_wA += stats['weighted_A']
        total_wAB += stats['weighted_AB']

    # Overall weighted p
    mean_p_overall = (total_wAB / total_wA) if total_wA > 0 else float('nan')

    # Stats over residues
    valid_phats = [r['p_hat'] for r in rows if not math.isnan(r['p_hat'])]
    mean_over_residues = (sum(valid_phats) / len(valid_phats)
                          if valid_phats else float('nan'))
    # Aggregate signed deviation D_N = sum_a (W_N(a)/W_N) * (p_hat(a) - 0.5)
    aggregate_deviation = sum(
        r['weighted_A'] / total_wA * (r['p_hat'] - 0.5)
        for r in rows
        if total_wA > 0 and not math.isnan(r['p_hat'])
    ) if total_wA > 0 else float('nan')
    max_dev = max(abs(p - 0.5) for p in valid_phats) if valid_phats else float('nan')
    qs = {
        '25': quantile(valid_phats, 0.25),
        '50': quantile(valid_phats, 0.50),
        '75': quantile(valid_phats, 0.75),
        '90': quantile(valid_phats, 0.90),
        '95': quantile(valid_phats, 0.95),
    }

    # Print human-readable summary
    print(f"Results")
    print(f"  Overall weighted p_hat (pooled):       {mean_p_overall:.6f}  (target ≈ 0.5)")
    print(f"  Mean p_hat over residues:               {mean_over_residues:.6f}")
    print(f"  Max |p_hat - 0.5| per residue:          {max_dev:.6f}  (≈0.5 expected: B is mod-8 deterministic)")
    print(f"  Aggregate signed deviation |D_N(M)|:    {abs(aggregate_deviation):.6f}  (H_mix quantity; target ≈ 0)")
    print(f"  p_hat quantiles: Q25={qs['25']:.4f}  Q50={qs['50']:.4f}"
          f"  Q75={qs['75']:.4f}  Q90={qs['90']:.4f}  Q95={qs['95']:.4f}")
    print()
    # H_mix check uses the aggregate deviation, not the per-residue max
    mixing_ok = not math.isnan(aggregate_deviation) and abs(aggregate_deviation) < 0.05
    print(f"  H_mix informal check (|D_N(M)| < 0.05): {'PASS' if mixing_ok else 'FAIL/unclear'}")
    print(f"  (Note: per-residue max ≈ 0.5 is expected; the H_mix quantity is the aggregate |D_N(M)|)")
    print()

    # Write CSVs
    ensure_out_dir(out_dir)
    residue_path = os.path.join(out_dir, f'residue_stats_M{M}_N{N}.csv')
    summary_path = os.path.join(out_dir, f'summary_M{M}_N{N}.csv')

    write_residue_csv(residue_path, M, N, window_end, rows)
    write_summary_csv(summary_path, M, N, window_end,
                      mean_p_overall, mean_over_residues, max_dev,
                      aggregate_deviation, qs)

    print(f"Output written:")
    print(f"  {residue_path}")
    print(f"  {summary_path}")


if __name__ == '__main__':
    main()
