#!/usr/bin/env python3
"""
collatz_c9_2_fourier_v2.py
Policy A: undefined hat_p → g[a]=0 after centering on defined residues only.
Observable: graded drift hat_p(a) = mean log(T_syr(n)/n) per residue class.
Stdlib-only radix-2 FFT. Per-v2 buckets, rms_ratio, all C9.2 decision metrics.
Sparsity: mean-centered (|hat_p(a) - mean_hat_p| >= threshold).
"""

import argparse, csv, json, math, re
from pathlib import Path


def parse_M_N(filename):
    m = re.search(r'_M(\d+)_N(\d+)\.csv$', filename)
    if not m:
        raise ValueError(f"Cannot parse M,N from: {filename}")
    return int(m.group(1)), int(m.group(2))


def v2(x):
    if x <= 0:
        return 0
    v = 0
    while x % 2 == 0:
        x //= 2; v += 1
    return v


def fft_inplace(a):
    """In-place radix-2 Cooley-Tukey FFT. len(a) must be power of 2."""
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit; bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = -2 * math.pi / length
        wlen = complex(math.cos(ang), math.sin(ang))
        for i in range(0, n, length):
            w = 1 + 0j
            half = length >> 1
            for jj in range(half):
                u = a[i + jj]
                v_val = a[i + jj + half] * w
                a[i + jj]        = u + v_val
                a[i + jj + half] = u - v_val
                w *= wlen
        length <<= 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input",     required=True)
    ap.add_argument("--out-dir",   required=True)
    ap.add_argument("--top-k",     type=int,   default=50)
    ap.add_argument("--threshold", type=float, default=0.05)
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    M, N = parse_M_N(inp.name)
    q = 1 << M

    # --- load hat_p (fix: sum only first occurrence per residue) ---
    hat_p  = [None] * q
    n_def  = 0
    sum_hp = 0.0
    with open(inp, newline="") as f:
        for row in csv.DictReader(f):
            a   = int(row["residue_a"])
            raw = row.get("hat_p", "").strip()
            if not raw or raw.lower() == "none":
                continue
            hp = float(raw)
            if hat_p[a] is None:      # first time: count + sum
                n_def  += 1
                sum_hp += hp
            hat_p[a] = hp             # last write wins (safe: one row per residue)

    if n_def == 0:
        raise ValueError("No defined hat_p values in CSV")

    mean_hp = sum_hp / n_def

    # --- build g, compute metrics ---
    g          = [0.0] * q
    l2_sum     = 0.0
    sparse_bad = 0
    for a in range(q):
        if hat_p[a] is not None:
            d = hat_p[a] - mean_hp
            g[a]    = d
            l2_sum += d * d
            # sparsity: mean-centered (fix: was 0.5, now mean_hp)
            if abs(hat_p[a] - mean_hp) >= args.threshold:
                sparse_bad += 1

    l2_var      = l2_sum / n_def
    sparse_frac = sparse_bad / n_def

    # --- FFT ---
    fft_vals = [complex(x) for x in g]
    fft_inplace(fft_vals)
    F = [z / q for z in fft_vals]

    # --- modes (xi != 0) ---
    modes = []
    for xi in range(1, q):
        absF = abs(F[xi])
        modes.append({
            "xi":    xi,
            "v2_xi": v2(xi),
            "absF":  absF,
            "reF":   F[xi].real,
            "imF":   F[xi].imag,
        })
    modes.sort(key=lambda m: m["absF"], reverse=True)

    # --- per-v2 buckets ---
    bkt_sq  = {}
    bkt_cnt = {}
    bkt_max = {}
    for m in modes:
        r = min(m["v2_xi"], M - 1)
        bkt_sq[r]  = bkt_sq.get(r,  0.0) + m["absF"] ** 2
        bkt_cnt[r] = bkt_cnt.get(r, 0)   + 1
        bkt_max[r] = max(bkt_max.get(r, 0.0), m["absF"])

    per_v2 = {}
    rms0   = 0.0
    for r in range(M):
        cnt = bkt_cnt.get(r, 0)
        rms = math.sqrt(bkt_sq[r] / cnt) if cnt else 0.0
        per_v2[str(r)] = {
            "count":    cnt,
            "max_absF": bkt_max.get(r, 0.0),
            "rms_absF": rms,
        }
        if r == 0:
            rms0 = rms

    ratios = []
    for r in range(1, M):
        rms_r = per_v2[str(r)]["rms_absF"]
        ratio = (rms_r / rms0) if rms0 > 0 else None
        per_v2[str(r)]["rms_ratio"] = ratio
        if ratio is not None:
            ratios.append(ratio)
    per_v2["0"]["rms_ratio"] = None

    avg_rms_ratio = (sum(ratios) / len(ratios)) if ratios else None

    # --- write CSV (all modes) ---
    stem     = inp.stem
    csv_path = out / f"{stem}_fourier_modes.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["xi", "v2_xi", "absF", "reF", "imF"])
        for m in modes:
            w.writerow([m["xi"], m["v2_xi"], m["absF"], m["reF"], m["imF"]])

    # --- write JSON (fix: observable string updated) ---
    json_path = out / f"{stem}_fourier.json"
    summary = {
        "M": M, "N": N, "q": q,
        "n_defined_hat_p":       n_def,
        "mean_hat_p":            mean_hp,
        "l2_variance_empirical": l2_var,
        "sparse_threshold":      args.threshold,
        "sparse_fraction_hatp":  sparse_frac,
        "sparse_bad":            sparse_bad,
        "avg_rms_ratio":         avg_rms_ratio,
        "per_v2_bucket":         per_v2,
        "top_modes":             modes[:args.top_k],
        "policy":                "A",
        "observable":            "graded drift: hat_p(a)=mean log(T_syr(n)/n) over odd n in [N,2N], grouped by a mod 2^M",
        "sparsity_baseline":     "mean-centered: |hat_p(a) - mean_hat_p| >= threshold",
    }
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Fourier v2 complete  M={M} N={N}")
    print(f"  JSON  → {json_path}")
    print(f"  CSV   → {csv_path}")
    print(f"  mean_hat_p (mean drift) : {mean_hp:.6f}")
    print(f"  l2_variance             : {l2_var:.6f}")
    print(f"  sparse_fraction         : {sparse_frac:.4f}")
    print(f"  avg_rms_ratio           : {avg_rms_ratio}")


if __name__ == "__main__":
    main()
