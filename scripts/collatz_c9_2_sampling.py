#!/usr/bin/env python3
"""C9.2 gold sampler — stdlib-only per-class Collatz sampling.

Outputs
-------
  <output>/c9_2_M{M}_N{N}.csv          — per-sample rows
  <output>/c9_2_M{M}_N{N}_summary.json — per-residue summary statistics

Observable definitions
----------------------
  event_A(n): 1 if n is odd, else 0
  event_B(n): 1 if T(n) < n  (odd-normalized Collatz image strictly less than n)

Collatz map T(n)
    n even  -> n / 2
    n odd   -> (3n + 1) / 2   (odd-normalised, skips the trivial even step)
"""

import argparse
import csv
import json
import math
import os
import random


def collatz_step(n: int) -> int:
    """One odd-normalised Collatz step."""
    if n % 2 == 0:
        return n // 2
    return (3 * n + 1) // 2


def collatz_trajectory(n: int, max_steps: int = 10_000):
    """Yield successive Collatz iterates starting at n (not including n)."""
    x = n
    for _ in range(max_steps):
        x = collatz_step(x)
        yield x
        if x == 1:
            break


def event_a(n: int) -> int:
    """event_A: 1 if n is odd."""
    return int(n % 2 == 1)


def event_b(n: int) -> int:
    """event_B: 1 if T(n) < n (odd-normalised image strictly less than n)."""
    return int(collatz_step(n) < n)


def dyadic_residue(n: int, M: int) -> int:
    """Return n mod 2^M (dyadic residue class)."""
    return n % (2 ** M)


def sample_class(residue: int, M: int, n_samples: int, rng: random.Random) -> list:
    """Draw n_samples integers from the residue class `residue mod 2^M`."""
    modulus = 2 ** M
    # Sample integers in [modulus, modulus * 2^16) that fall in the residue class.
    # We use offset multiples: n = residue + k * modulus, k >= 1.
    upper_k = 2 ** 16
    samples = []
    for _ in range(n_samples):
        k = rng.randint(1, upper_k)
        samples.append(residue + k * modulus)
    return samples


def compute_row(n: int, residue: int, M: int) -> dict:
    """Compute observable row for a single starting integer n."""
    a = event_a(n)
    b = event_b(n)
    traj = list(collatz_trajectory(n))
    stopping_time = len(traj)
    # Empirical mean of event_A along trajectory (excluding starting point)
    traj_a = [event_a(x) for x in traj]
    mean_traj_a = sum(traj_a) / len(traj_a) if traj_a else float("nan")
    return {
        "n": n,
        "residue": residue,
        "M": M,
        "event_A": a,
        "event_B": b,
        "stopping_time": stopping_time,
        "mean_traj_event_A": round(mean_traj_a, 6),
    }


def run(N: int, M: int, window_type: str, output_dir: str, seed: int):
    modulus = 2 ** M
    n_classes = modulus
    # samples per class — distribute N evenly, at least 1
    samples_per_class = max(1, N // n_classes)

    rng = random.Random(seed)

    os.makedirs(output_dir, exist_ok=True)
    base_name = f"c9_2_M{M}_N{N}"
    csv_path = os.path.join(output_dir, base_name + ".csv")
    summary_path = os.path.join(output_dir, base_name + "_summary.json")

    fieldnames = ["n", "residue", "M", "event_A", "event_B", "stopping_time", "mean_traj_event_A"]

    # Per-residue accumulators for summary
    class_stats: dict[int, dict] = {}

    with open(csv_path, "w", newline="") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()

        for r in range(n_classes):
            ns = sample_class(r, M, samples_per_class, rng)
            rows = [compute_row(n, r, M) for n in ns]
            for row in rows:
                writer.writerow(row)

            # Accumulate stats
            ea_vals = [row["event_A"] for row in rows]
            eb_vals = [row["event_B"] for row in rows]
            st_vals = [row["stopping_time"] for row in rows]
            mta_vals = [row["mean_traj_event_A"] for row in rows]

            def _mean(v):
                return sum(v) / len(v) if v else float("nan")

            def _std(v):
                if len(v) < 2:
                    return float("nan")
                m = _mean(v)
                return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))

            class_stats[r] = {
                "residue": r,
                "M": M,
                "n_samples": len(rows),
                "mean_event_A": round(_mean(ea_vals), 6),
                "std_event_A": round(_std(ea_vals), 6),
                "mean_event_B": round(_mean(eb_vals), 6),
                "std_event_B": round(_std(eb_vals), 6),
                "mean_stopping_time": round(_mean(st_vals), 3),
                "std_stopping_time": round(_std(st_vals), 3),
                "mean_traj_event_A": round(_mean(mta_vals), 6),
            }

    # Write summary JSON
    summary = {
        "M": M,
        "modulus": modulus,
        "N": N,
        "samples_per_class": samples_per_class,
        "window_type": window_type,
        "seed": seed,
        "csv_path": csv_path,
        "n_classes": n_classes,
        "per_class": class_stats,
    }
    with open(summary_path, "w") as fj:
        json.dump(summary, fj, indent=2)

    print(f"[sampler] wrote {csv_path}")
    print(f"[sampler] wrote {summary_path}")
    print(f"[sampler] M={M}, modulus={modulus}, classes={n_classes}, samples/class={samples_per_class}, total={n_classes * samples_per_class}")


def main():
    parser = argparse.ArgumentParser(description="C9.2 per-class Collatz sampler")
    parser.add_argument("--N", type=int, default=100_000, help="Total sample budget")
    parser.add_argument("--M", type=int, required=True, help="Dyadic window size (2^M classes)")
    parser.add_argument("--window-type", default="dyadic", help="Window type label (default: dyadic)")
    parser.add_argument("--output", default="scripts/out", help="Output directory")
    parser.add_argument("--seed", type=int, default=1, help="Random seed")
    args = parser.parse_args()
    run(args.N, args.M, args.window_type, args.output, args.seed)


if __name__ == "__main__":
    main()
