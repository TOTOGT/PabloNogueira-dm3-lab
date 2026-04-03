"""
Fibonacci Recurrence in Admissible Collatz/Syracuse Traces
===========================================================
G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026

Demonstrates that the number of admissible U/D step-sequences of length n
satisfies the Fibonacci recurrence  a_n = a_{n-1} + a_{n-2}.

Three complementary views are provided:
  1. Direct enumeration of admissible sequences (no UU rule).
  2. Concrete Collatz orbit traces mapped to U/D sequences.
  3. Fibonacci-weighted transfer matrix mod 2^M (M configurable).

Usage:
    python collatz_fibonacci_traces.py [--max-n N] [--mod-M M] [--orbit START]

Defaults: --max-n 14  --mod-M 6  --orbit 27
"""

import argparse
import itertools
from collections import defaultdict


# ---------------------------------------------------------------------------
# Part 1 – Direct enumeration of admissible sequences
# ---------------------------------------------------------------------------

def is_admissible(seq: tuple[str, ...]) -> bool:
    """Return True iff seq contains no two consecutive U's."""
    for i in range(len(seq) - 1):
        if seq[i] == "U" and seq[i + 1] == "U":
            return False
    return True


def enumerate_admissible(n: int) -> list[tuple[str, ...]]:
    """Return all admissible sequences of length n that start with U.

    These correspond to Collatz traces starting from an odd integer:
    the first step is always U (apply 3n+1), followed by at least one D
    (halving), with no two consecutive U's allowed anywhere.

    With a_1=1, a_2=1 these counts satisfy a_n = F_n exactly.
    """
    return [
        s for s in itertools.product("UD", repeat=n)
        if s[0] == "U" and is_admissible(s)
    ]


def fibonacci(n: int) -> int:
    """Return F_n with F_1=1, F_2=1, F_3=2, …"""
    if n <= 0:
        return 0
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def print_admissible_table(max_n: int) -> None:
    print("\n=== Part 1: Admissible sequence counts vs Fibonacci numbers ===")
    print(f"{'n':>4}  {'|admissible(n)|':>16}  {'F_n':>6}  {'match?':>7}")
    print("-" * 40)
    prev_count = 0
    for n in range(1, max_n + 1):
        seqs = enumerate_admissible(n)
        count = len(seqs)
        fib_n = fibonacci(n)
        match = "✓" if count == fib_n else "✗"
        print(f"{n:>4}  {count:>16}  {fib_n:>6}  {match:>7}")
        prev_count = count
    print()
    print("Recurrence check  a_n = a_{n-1} + a_{n-2}:")
    counts = [len(enumerate_admissible(k)) for k in range(1, max_n + 1)]
    for i in range(2, len(counts)):
        ok = counts[i] == counts[i - 1] + counts[i - 2]
        print(f"  n={i + 1}: {counts[i]} = {counts[i - 1]} + {counts[i - 2]}  {'✓' if ok else '✗'}")


# ---------------------------------------------------------------------------
# Part 2 – Concrete Collatz orbits → U/D traces
# ---------------------------------------------------------------------------

def collatz_orbit(start: int, limit: int = 500) -> list[int]:
    """Return the orbit of `start` under the full Collatz map until 1."""
    seq = [start]
    n = start
    for _ in range(limit):
        if n == 1:
            break
        n = (3 * n + 1) if n % 2 == 1 else n // 2
        seq.append(n)
    return seq


def orbit_to_ud(orbit: list[int]) -> tuple[str, ...]:
    """Convert an orbit to a U/D step sequence."""
    steps = []
    for val in orbit[:-1]:
        steps.append("U" if val % 2 == 1 else "D")
    return tuple(steps)


def print_orbit_trace(start: int, max_steps: int = 30) -> None:
    print(f"\n=== Part 2: Collatz orbit trace for n={start} ===")
    orbit = collatz_orbit(start)
    trace = orbit_to_ud(orbit)
    # Show first max_steps steps
    display_orbit = orbit[:max_steps + 1]
    display_trace = trace[:max_steps]
    print(f"Orbit (first {max_steps} steps): {display_orbit}")
    print(f"U/D trace:                       {''.join(display_trace)}")
    print(f"Admissible (no UU)?              {'Yes' if is_admissible(display_trace) else 'No'}")

    # Show sub-traces of each length 1..min(14, len(trace))
    check_len = min(10, len(display_trace))
    print(f"\nSub-trace lengths 1..{check_len} — admissibility breakdown:")
    for n in range(1, check_len + 1):
        sub = display_trace[:n]
        adm = is_admissible(sub)
        print(f"  length {n}: {''.join(sub)}  {'admissible' if adm else 'NOT admissible'}")


# ---------------------------------------------------------------------------
# Part 3 – Fibonacci-weighted transfer matrix mod 2^M
# ---------------------------------------------------------------------------

def syracuse_step(n: int) -> int:
    """Apply one step of the Syracuse (accelerated) map: n must be odd."""
    assert n % 2 == 1, "Syracuse step requires odd input"
    val = 3 * n + 1
    while val % 2 == 0:
        val //= 2
    return val


def build_transfer_matrix(M: int) -> dict[int, int]:
    """
    Build the forward transfer map T: odd integers mod 2^M → odd integers mod 2^M.
    Returns a dict {source_odd: target_odd} for each odd value in [1, 2^M).
    """
    modulus = 2 ** M
    mapping = {}
    for n in range(1, modulus, 2):
        mapping[n] = syracuse_step(n) % modulus
    return mapping


def fibonacci_path_weights(mapping: dict[int, int], num_steps: int) -> dict[tuple[int, int], int]:
    """
    Compute, for each (start, end) pair of odd residues mod 2^M,
    the Fibonacci-weighted count of paths of length `num_steps`.

    Weight of a path of k Syracuse steps is F_k (Fibonacci number).
    Here every path has the same length so the weight is simply F_{num_steps}
    per path, but when we enumerate paths of *all* lengths up to num_steps
    and weight by F_k, we get a richer structure.

    This function returns the total F-weighted multiplicity for paths of
    exactly `num_steps` steps from each start to each end.
    """
    # paths of length 1: direct edges, weight F_1 = 1
    # paths of length k: compose k-1 paths + 1 step, cumulative weight F_k
    # We build a matrix (as dict) and compose it.
    nodes = sorted(mapping.keys())

    # adjacency: adj[a][b] = 1 if T(a) = b (mod 2^M)
    # Fibonacci-weighted matrix after k steps: W_k[a][b] = F_k * (number of length-k paths a→b)
    # Since T is deterministic, there is exactly 0 or 1 path of each length.
    # W_k = F_k * (A^k) where A is the 0/1 adjacency matrix.
    def mat_mult(A: dict, B: dict, nodes: list[int]) -> dict:
        C: dict = defaultdict(lambda: defaultdict(int))
        for i in nodes:
            for j in nodes:
                if A[i][j] != 0:
                    for k in nodes:
                        if B[j][k] != 0:
                            C[i][k] += A[i][j] * B[j][k]
        return C

    # Initial adjacency matrix A (step 1)
    A: dict = defaultdict(lambda: defaultdict(int))
    for src, tgt in mapping.items():
        A[src][tgt] = 1

    # Compute A^num_steps
    current = A
    for _ in range(num_steps - 1):
        current = mat_mult(current, A, nodes)

    fib_weight = fibonacci(num_steps)
    result = {}
    for i in nodes:
        for j in nodes:
            w = current[i][j]
            if w > 0:
                result[(i, j)] = fib_weight * w
    return result


def print_transfer_matrix(M: int, num_steps: int) -> None:
    modulus = 2 ** M
    mapping = build_transfer_matrix(M)
    nodes = sorted(mapping.keys())

    print(f"\n=== Part 3: Fibonacci-weighted transfer matrix (mod 2^{M} = {modulus}) ===")
    print(f"Number of odd residues: {len(nodes)}")
    print(f"\nSyracuse map T on odd integers mod {modulus}:")
    for src in nodes:
        print(f"  T({src:>3}) → {mapping[src]:>3}")

    print(f"\nFibonacci-weighted path count for {num_steps} steps (weight = F_{num_steps} = {fibonacci(num_steps)}):")
    weights = fibonacci_path_weights(mapping, num_steps)
    for (src, tgt), w in sorted(weights.items()):
        print(f"  {src:>3} →[{num_steps} steps]→ {tgt:>3}  weight = {w}")

    # Cumulative Fibonacci-weighted transfer across all lengths 1..max_steps
    print(f"\nCumulative Fibonacci-weighted transfer (lengths 1..{num_steps}):")
    cumulative: dict[tuple[int, int], int] = defaultdict(int)
    for k in range(1, num_steps + 1):
        for (src, tgt), w in fibonacci_path_weights(mapping, k).items():
            cumulative[(src, tgt)] += w
    for (src, tgt), w in sorted(cumulative.items()):
        print(f"  {src:>3} →[1..{num_steps} steps]→ {tgt:>3}  cumulative F-weight = {w}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fibonacci recurrence in admissible Collatz/Syracuse traces"
    )
    parser.add_argument(
        "--max-n", type=int, default=14,
        help="Maximum sequence length for enumeration (default: 14)"
    )
    parser.add_argument(
        "--mod-M", type=int, default=6,
        help="Exponent M for mod-2^M transfer matrix (default: 6)"
    )
    parser.add_argument(
        "--orbit", type=int, default=27,
        help="Starting integer for Collatz orbit trace (default: 27)"
    )
    parser.add_argument(
        "--matrix-steps", type=int, default=5,
        help="Number of Syracuse steps for transfer matrix weights (default: 5)"
    )
    args = parser.parse_args()

    print_admissible_table(args.max_n)
    print_orbit_trace(args.orbit)
    print_transfer_matrix(args.mod_M, args.matrix_steps)


if __name__ == "__main__":
    main()
