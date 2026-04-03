"""
collatz_c9_2_sampling.py — C9.2 Conditional Sampling

G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026
MIT License

Conditional sampling of Collatz trajectories with window-type support.
Window conventions follow docs/d9_averaging_window_conventions.md (C9.3).

Window types
------------
dyadic   W_k = {2^k, …, 2^(k+1)−1}; --start / --end must satisfy start=2^k, end=2^(k+1)−1
range    W   = {start, …, end}       (arbitrary contiguous interval)
"""

import argparse
import json
import math
import os
import random


# ── event and Collatz map ─────────────────────────────────────────────────────

def event_A(n):
    """Event A: n is odd (one step of Collatz may apply the 3n+1 branch)."""
    return n % 2 == 1


def _v2(n):
    """2-adic valuation: largest k with 2^k | n."""
    if n == 0:
        return 0
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def T(n):
    """
    One step of the Collatz map.

    T(n) = n/2            if n is even
    T(n) = (3n+1)/2^v2    if n is odd  (fully reduced odd step)
    """
    if n % 2 == 0:
        return n // 2
    raw = 3 * n + 1
    return raw // (2 ** _v2(raw))


# ── window helpers (D9 conventions) ──────────────────────────────────────────

def build_window(window_type, start, end):
    """
    Return the list of integers in the requested window.

    window_type='dyadic' : validates that [start, end] = [2^k, 2^(k+1)-1]
    window_type='range'  : arbitrary contiguous interval [start, end]

    See docs/d9_averaging_window_conventions.md §3 for full specification.
    """
    if window_type == 'dyadic':
        k = int(math.floor(math.log2(start))) if start >= 1 else 0
        expected_start = 2 ** k
        expected_end = 2 ** (k + 1) - 1
        if start != expected_start or end != expected_end:
            raise ValueError(
                f"dyadic window requires start=2^k and end=2^(k+1)-1; "
                f"got start={start}, end={end} (expected {expected_start}–{expected_end} "
                f"for k={k})"
            )
    return list(range(start, end + 1))


# ── sampling ──────────────────────────────────────────────────────────────────

def sample(N, M, threshold, sample_rate, window_type, start, end):
    """
    Draw up to M conditional samples from the Collatz map restricted to a window.

    Parameters
    ----------
    N           : upper bound on n (legacy; use start/end for window control)
    M           : maximum number of samples to collect
    threshold   : if set, discard samples where T(n) < threshold
    sample_rate : probability of including each eligible n in the sample
    window_type : 'dyadic' or 'range' (D9 convention)
    start, end  : window boundaries (inclusive)

    Returns
    -------
    list of sampled T(n) values
    """
    window = build_window(window_type, start, end)
    samples = []
    for n in window:
        if len(samples) >= M:
            break
        if not event_A(n):
            continue
        if random.random() > sample_rate:
            continue
        value = T(n)
        if threshold is not None and value < threshold:
            continue
        samples.append(value)
    return samples


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='C9.2 Conditional Sampling',
        epilog='Window conventions: docs/d9_averaging_window_conventions.md',
    )
    parser.add_argument('--N', type=int, required=True,
                        help='Upper bound on n (informational; actual window set by --start/--end)')
    parser.add_argument('--M', type=int, required=True,
                        help='Maximum number of samples')
    parser.add_argument('--window-type', type=str, choices=['dyadic', 'range'], required=True,
                        help='Window type: dyadic=[2^k,2^(k+1)) or range=[start,end]')
    parser.add_argument('--start', type=int, required=True,
                        help='Window lower bound (inclusive)')
    parser.add_argument('--end', type=int, required=True,
                        help='Window upper bound (inclusive)')
    parser.add_argument('--output', type=str, required=True,
                        help='Output file base path (without extension)')
    parser.add_argument('--sample-rate', type=float, required=True,
                        help='Probability [0,1] of including each eligible n')
    parser.add_argument('--threshold', type=float, required=False,
                        help='Discard samples where T(n) < threshold')
    parser.add_argument('--seed', type=int, required=False,
                        help='Random seed for reproducibility')

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    results = sample(
        args.N, args.M, args.threshold, args.sample_rate,
        args.window_type, args.start, args.end,
    )

    # D9 metadata (convention v1.0)
    # μ_W(A) = |{n ∈ W : event_A(n)}| / |W| — exhaustive count, independent of sampling
    window_size = args.end - args.start + 1
    event_count = sum(1 for n in range(args.start, args.end + 1) if event_A(n))
    mu_W = event_count / window_size if window_size > 0 else 0.0
    d9_meta = {
        "d9_convention_version": "1.0",
        "event": "odd",
        "window_type": args.window_type,
        "window_parameter": args.start,
        "window": f"[{args.start}, {args.end}]",
        "window_size": window_size,
        "mu_W": round(mu_W, 6),
        "limit_status": "finite_approximation",
        "limsup": None,
        "liminf": None,
        "source": "docs/d9_averaging_window_conventions.md",
    }

    os.makedirs(os.path.join('scripts', 'out'), exist_ok=True)
    output_csv = os.path.join('scripts', 'out', f'c9_2_M{args.M}_N{args.N}.csv')
    output_json = os.path.join('scripts', 'out', f'c9_2_M{args.M}_N{args.N}_summary.json')

    with open(output_csv, 'w') as f:
        for result in results:
            f.write(f'{result}\n')

    with open(output_json, 'w') as f:
        json.dump({'results': results, 'd9': d9_meta}, f, indent=2)

    print(f"[C9.2] window_type={args.window_type}  "
          f"window=[{args.start},{args.end}]  "
          f"samples={len(results)}  mu_W={d9_meta['mu_W']}")
    print(f"[C9.2] output → {output_csv}  {output_json}")
