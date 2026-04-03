#!/usr/bin/env python3
"""
Collatz C9.2 Canonical Sampler - Option 1
==========================================

Semantics:
  A      = n is odd
  B      = T(n) < n  (Collatz full step decreases the value)
  Weight = uniform

For each odd residue class a mod 2^M, estimates

  hat_p(a) = #{n in sample : A(n) and B(n)} / #{n in sample : A(n)}

which equals P(T(n) < n | n is odd, n ≡ a mod 2^M) under the uniform measure.

Only odd residues are visited (even residues always yield A_count = 0 and
are therefore uninformative), halving both runtime and I/O.

Outputs
-------
  <out-dir>/c9_2_M<M>_N<N>.csv          per-residue table
  <out-dir>/c9_2_M<M>_N<N>_summary.json aggregate statistics

Usage example
-------------
  python3 scripts/collatz_c9_2_sampling_option1.py \\
      --M 8 --N 100000 --window-size 10000 \\
      --mode random --max-samples 200 --seed 123 --out-dir scripts/out
"""

import argparse
import csv
import json
import math
import os
import random

# Number of decimal places used when formatting hat_p values.
_HAT_P_FMT = '.6f'


# ---------------------------------------------------------------------------
# Core Collatz machinery
# ---------------------------------------------------------------------------

def _v2(k: int) -> int:
    """2-adic valuation of k (number of trailing zero bits)."""
    if k == 0:
        return 0
    count = 0
    while k & 1 == 0:
        k >>= 1
        count += 1
    return count


def collatz_T(n: int) -> int:
    """
    Full Collatz step:
      - n even : T(n) = n // 2
      - n odd  : T(n) = (3n + 1) / 2^v2(3n+1)  (reduce to odd in one go)
    """
    if n & 1 == 0:
        return n >> 1
    m = 3 * n + 1
    return m >> _v2(m)


def event_A(n: int) -> bool:
    """A: n is odd."""
    return n & 1 == 1


def event_B(n: int) -> bool:
    """B: the Collatz step is a decrease, T(n) < n."""
    return collatz_T(n) < n


# ---------------------------------------------------------------------------
# Samplers per residue class
# ---------------------------------------------------------------------------

def _candidates(a: int, mod: int, n_start: int, window_size: int):
    """
    Yield the first element and count of integers n in [n_start, n_start+window_size)
    with n ≡ a (mod mod).
    """
    rem = n_start % mod
    offset = (a - rem) % mod
    first = n_start + offset
    if first >= n_start + window_size:
        return first, 0
    count = (n_start + window_size - first + mod - 1) // mod
    return first, count


def sample_random(a: int, mod: int, n_start: int, window_size: int,
                  max_samples: int, rng: random.Random):
    """
    Draw up to *max_samples* values n ≡ a (mod mod) from
    [n_start, n_start + window_size) using uniform random sampling
    without replacement.
    """
    first, count = _candidates(a, mod, n_start, window_size)
    if count == 0:
        return []
    if count <= max_samples:
        return [first + i * mod for i in range(count)]
    indices = sorted(rng.sample(range(count), max_samples))
    return [first + i * mod for i in indices]


def sample_exhaustive(a: int, mod: int, n_start: int, window_size: int,
                      max_samples: int):
    """
    Enumerate all n ≡ a (mod mod) in [n_start, n_start + window_size),
    capped at *max_samples*.
    """
    first, count = _candidates(a, mod, n_start, window_size)
    count = min(count, max_samples)
    return [first + i * mod for i in range(count)]


# stride mode: thin enumeration (every k-th candidate)
def sample_stride(a: int, mod: int, n_start: int, window_size: int,
                  max_samples: int):
    """
    Stride through candidates n ≡ a (mod mod) in
    [n_start, n_start + window_size), selecting at most *max_samples*
    evenly-spaced candidates.
    """
    first, count = _candidates(a, mod, n_start, window_size)
    if count == 0:
        return []
    step = max(1, count // max_samples)
    indices = range(0, count, step)
    return [first + i * mod for i in indices][:max_samples]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            'Collatz C9.2 Sampler (Option 1): '
            'A = odd, B = T(n) < n, uniform weight.'
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--M', type=int, required=True,
                        help='Modulus exponent: residue classes are 0 .. 2^M - 1')
    parser.add_argument('--N', type=int, required=True,
                        help='Window start (first integer in the sampling window)')
    parser.add_argument('--window-size', type=int, required=True,
                        help='Number of consecutive integers in the window')
    parser.add_argument('--mode', choices=['random', 'exhaustive', 'stride'],
                        default='random',
                        help='Sampling mode')
    parser.add_argument('--max-samples', type=int, default=10000,
                        help='Max samples per residue class (safety cap for '
                             'exhaustive/stride; also caps random draws)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility (random mode)')
    parser.add_argument('--out-dir', type=str, default='scripts/out',
                        help='Directory for output files')
    args = parser.parse_args()

    mod = 1 << args.M  # 2^M
    rng = random.Random(args.seed)

    os.makedirs(args.out_dir, exist_ok=True)
    stem = f'c9_2_M{args.M}_N{args.N}'
    csv_path = os.path.join(args.out_dir, f'{stem}.csv')
    json_path = os.path.join(args.out_dir, f'{stem}_summary.json')

    rows = []
    total_A = 0
    total_AB = 0

    # Iterate only over odd residues: even residues always give A_count = 0
    for a in range(1, mod, 2):
        if args.mode == 'random':
            ns = sample_random(a, mod, args.N, args.window_size,
                               args.max_samples, rng)
        elif args.mode == 'stride':
            ns = sample_stride(a, mod, args.N, args.window_size,
                               args.max_samples)
        else:  # exhaustive
            ns = sample_exhaustive(a, mod, args.N, args.window_size,
                                   args.max_samples)

        # All n sampled here have residue a which is odd, so event_A(n) is
        # always True by construction.  A single pass is sufficient.
        A_count = len(ns)
        AB_count = sum(1 for n in ns if event_B(n))

        if A_count > 0:
            hat_p_str = format(AB_count / A_count, _HAT_P_FMT)
        else:
            hat_p_str = 'NaN'

        total_A += A_count
        total_AB += AB_count

        rows.append({
            'residue': a,
            'mod': mod,
            'sample_size': len(ns),
            'A_count': A_count,
            'AB_count': AB_count,
            'hat_p': hat_p_str,
        })

    # Write CSV
    fieldnames = ['residue', 'mod', 'sample_size', 'A_count', 'AB_count', 'hat_p']
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Write JSON summary
    global_hat_p = total_AB / total_A if total_A > 0 else math.nan
    summary = {
        'M': args.M,
        'mod': mod,
        'N': args.N,
        'window_size': args.window_size,
        'mode': args.mode,
        'max_samples': args.max_samples,
        'seed': args.seed,
        'residues_processed': len(rows),
        'total_A': total_A,
        'total_AB': total_AB,
        'global_hat_p': 'NaN' if math.isnan(global_hat_p) else global_hat_p,
        'csv': csv_path,
    }
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)

    # Console summary
    hat_p_display = (
        format(global_hat_p, _HAT_P_FMT) if not math.isnan(global_hat_p) else 'NaN'
    )
    print(f'[OK] CSV  -> {csv_path}')
    print(f'[OK] JSON -> {json_path}')
    print(f'     residues={len(rows)}  total_A={total_A}  '
          f'total_AB={total_AB}  global_hat_p={hat_p_display}')


if __name__ == '__main__':
    main()
