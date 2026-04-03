#!/usr/bin/env python3
"""
scripts/collatz_c9_2_fourier.py

Stdlib-only Fourier diagnostics for Collatz per-class hat_p.

Outputs:
  - {output}/c9_2_M{M}_N{N}_fourier.json
  - {output}/c9_2_M{M}_N{N}_fourier_modes.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from collections import defaultdict
from statistics import mean

TAU = 2.0 * math.pi

def v2_int(x: int) -> int:
    if x == 0:
        return 10**9
    v = 0
    while (x & 1) == 0:
        x >>= 1
        v += 1
    return v

def parse_M_N_from_filename(path: str) -> tuple[int | None, int | None]:
    base = os.path.basename(path)
    m = re.search(r"_M(\d+)_N(\d+)\.csv$", base)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))

def load_hat_p(csv_path: str) -> dict[int, float]:
    out: dict[int, float] = {}
    with open(csv_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                a = int(row["class"])
            except Exception:
                continue
            hp = row.get("hat_p", "")
            if hp is None or hp == "" or hp.lower() == "none":
                continue
            try:
                out[a] = float(hp)
            except Exception:
                continue
    return out

def compute_fourier(res_to_hp: dict[int, float], q: int) -> tuple[dict[int, complex], float, float]:
    residues = sorted(res_to_hp.keys())
    vals = [res_to_hp[a] for a in residues]
    if not vals:
        return {}, float("nan"), float("nan")
    m_hp = mean(vals)
    g = {a: (res_to_hp[a] - m_hp) for a in residues}
    l2_var = sum((g[a] ** 2) for a in residues) / len(residues)
    F: dict[int, complex] = {}
    n = float(len(residues))
    for xi in range(q):
        s_re = 0.0
        s_im = 0.0
        for a in residues:
            theta = TAU * ((xi * a) % q) / q
            c = math.cos(theta)
            sn = math.sin(theta)
            ga = g[a]
            s_re += ga * c
            s_im -= ga * sn
        F[xi] = complex(s_re / n, s_im / n)
    return F, m_hp, l2_var

def bucket_stats(F: dict[int, complex], M: int) -> tuple[dict[int, dict[str, float]], list[dict[str, float]]]:
    buckets: dict[int, list[float]] = defaultdict(list)
    modes = []
    for xi, z in F.items():
        if xi == 0:
            continue
        r = v2_int(xi)
        if r > M - 1:
            r = M - 1
        a = abs(z)
        buckets[r].append(a)
        modes.append((a, xi, z))
    bucket_out: dict[int, dict[str, float]] = {}
    for r in range(M):
        arr = buckets.get(r, [])
        if not arr:
            bucket_out[r] = {"count": 0, "max_absF": 0.0, "rms_absF": 0.0}
            continue
        max_a = max(arr)
        rms = math.sqrt(sum(x * x for x in arr) / len(arr))
        bucket_out[r] = {"count": len(arr), "max_absF": max_a, "rms_absF": rms}
    modes.sort(reverse=True, key=lambda t: t[0])
    top = []
    for a, xi, z in modes[:50]:
        top.append({"xi": int(xi), "v2_xi": int(min(v2_int(xi), M - 1)), "absF": float(a), "reF": float(z.real), "imF": float(z.imag)})
    return bucket_out, top

def write_modes_csv(out_csv: str, F: dict[int, complex], M: int) -> None:
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["xi", "v2_xi", "absF", "reF", "imF"])
        for xi in sorted(F.keys()):
            if xi == 0:
                continue
            z = F[xi]
            w.writerow([xi, min(v2_int(xi), M - 1), abs(z), z.real, z.imag])

def main() -> int:
    ap = argparse.ArgumentParser(description="Compute empirical Fourier coefficients from Collatz sampling CSV")
    ap.add_argument("--csv", required=True, help="Path to c9_2_M{M}_N{N}.csv")
    ap.add_argument("--M", type=int, default=None, help="Override M (otherwise parse from filename)")
    ap.add_argument("--output", type=str, default="scripts/out", help="Output directory for JSON/CSV")
    ap.add_argument("--top-k", type=int, default=50, help="Number of top modes to include in JSON summary")
    args = ap.parse_args()

    M_file, N_file = parse_M_N_from_filename(args.csv)
    M = args.M if args.M is not None else M_file
    if M is None:
        raise SystemExit("Could not infer M from filename; pass --M explicitly.")
    q = 1 << M

    res_to_hp = load_hat_p(args.csv)
    F, mean_hp, l2_var = compute_fourier(res_to_hp, q)
    buckets, top_modes = bucket_stats(F, M)
    if args.top_k < len(top_modes):
        top_modes = top_modes[: args.top_k]

    os.makedirs(args.output, exist_ok=True)
    base = os.path.basename(args.csv).replace(".csv", "")
    out_json = os.path.join(args.output, f"{base}_fourier.json")
    out_modes = os.path.join(args.output, f"{base}_fourier_modes.csv")

    write_modes_csv(out_modes, F, M)

    summary = {
        "input_csv": args.csv,
        "M": M,
        "q": q,
        "N": N_file,
        "n_classes_used": len(res_to_hp),
        "mean_hat_p": mean_hp,
        "l2_variance_empirical": l2_var,
        "per_v2_bucket": buckets,
        "top_modes": top_modes,
        "notes": "F(xi) computed from g(a)=hat_p(a)-mean_hat_p over classes present in CSV.",
    }

    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)

    print("Wrote:", out_json)
    print("Wrote:", out_modes)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
