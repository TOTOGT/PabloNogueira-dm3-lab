*** Begin Patch
*** Add File: scripts/collatz_c9_2_sampling.py
+#!/usr/bin/env python3
+"""
+scripts/collatz_c9_2_sampling.py
+
+Stdlib-only Collatz sampling script for C9.2 empirical pipeline.
+
+Outputs:
+  - {output}/c9_2_M{M}_N{N}.csv
+  - {output}/c9_2_M{M}_N{N}_summary.json
+
+Default observable:
+  - event_A(n): n odd
+  - event_B(n): T(n) < n where T(n) is odd-normalized Collatz image
+"""
+from __future__ import annotations
+
+import argparse
+import csv
+import json
+import os
+import random
+import math
+from collections import defaultdict
+from statistics import mean
+
+# ---------- Observable (defaults) ----------
+def event_A(n: int) -> bool:
+    return (n & 1) == 1
+
+def collatz_one_step_image(n: int) -> int:
+    if (n & 1) == 0:
+        return n // 2
+    x = 3 * n + 1
+    while (x & 1) == 0:
+        x >>= 1
+    return x
+
+def event_B(n: int) -> bool:
+    return collatz_one_step_image(n) < n
+# ------------------------------------------
+
+def weight(n: int) -> float:
+    return 1.0
+
+def enumerate_window(window_type: str, N: int, start: int | None = None, end: int | None = None):
+    if window_type == "dyadic":
+        start = N
+        end = 2 * N
+    elif window_type == "range":
+        if start is None or end is None:
+            raise ValueError("range requires --start and --end")
+    else:
+        raise ValueError("unknown window_type")
+    assert start is not None and end is not None
+    n = start
+    while n <= end:
+        yield n
+        n += 1
+
+def compute_per_class(N: int, M: int, window_type: str, start: int | None, end: int | None, sample_rate: float, seed: int):
+    random.seed(seed)
+    mod = 1 << M
+    counts_A = defaultdict(float)
+    counts_A_and_B = defaultdict(float)
+    counts_raw_A = defaultdict(int)
+    counts_raw_A_and_B = defaultdict(int)
+    total_weight = 0.0
+    total_seen = 0
+
+    for n in enumerate_window(window_type, N, start, end):
+        if sample_rate < 1.0 and random.random() > sample_rate:
+            continue
+        total_seen += 1
+        total_weight += weight(n)
+        a = n % mod
+        if event_A(n):
+            w = weight(n)
+            counts_A[a] += w
+            counts_raw_A[a] += 1
+            if event_B(n):
+                counts_A_and_B[a] += w
+                counts_raw_A_and_B[a] += 1
+
+    results = []
+    for a in sorted(counts_A.keys()):
+        ca = counts_A[a]
+        cab = counts_A_and_B.get(a, 0.0)
+        hat_p = (cab / ca) if ca > 0 else None
+        results.append((a, ca, cab, hat_p, counts_raw_A.get(a, 0), counts_raw_A_and_B.get(a, 0)))
+    return results, total_weight, total_seen
+
+def compute_L2_variance(results):
+    vals = [r[3] for r in results if r[3] is not None]
+    if not vals:
+        return None
+    m = mean(vals)
+    var = sum((x - m) ** 2 for x in vals) / len(vals)
+    return var, m, len(vals)
+
+def compute_sparse_fraction(results, threshold: float = 0.05):
+    total = 0
+    bad = 0
+    for (_, _, _, hat_p, _, _) in results:
+        if hat_p is None:
+            continue
+        total += 1
+        if abs(hat_p - 0.5) > threshold:
+            bad += 1
+    return (bad / total) if total > 0 else None, bad, total
+
+def main() -> int:
+    parser = argparse.ArgumentParser(description="Collatz C9.2 sampling: per-class conditional probabilities")
+    parser.add_argument("--N", type=int, default=100000)
+    parser.add_argument("--M", type=int, default=16)
+    parser.add_argument("--window-type", choices=["dyadic", "range"], default="dyadic")
+    parser.add_argument("--start", type=int, default=None)
+    parser.add_argument("--end", type=int, default=None)
+    parser.add_argument("--output", type=str, default="scripts/out")
+    parser.add_argument("--sample-rate", type=float, default=1.0)
+    parser.add_argument("--threshold", type=float, default=0.05)
+    parser.add_argument("--seed", type=int, default=0)
+    args = parser.parse_args()
+
+    os.makedirs(args.output, exist_ok=True)
+    results, total_weight, total_seen = compute_per_class(args.N, args.M, args.window_type, args.start, args.end, args.sample_rate, args.seed)
+
+    base = f"c9_2_M{args.M}_N{args.N}"
+    csv_path = os.path.join(args.output, f"{base}.csv")
+    with open(csv_path, "w", newline="") as f:
+        w = csv.writer(f)
+        w.writerow(["class", "weighted_count_A", "weighted_count_A_and_B", "hat_p", "raw_count_A", "raw_count_A_and_B"])
+        for row in results:
+            w.writerow(row)
+
+    l2 = compute_L2_variance(results)
+    sparse_frac, bad, total = compute_sparse_fraction(results, threshold=args.threshold)
+
+    summary = {
+        "N": args.N,
+        "M": args.M,
+        "window_type": args.window_type,
+        "total_weight": total_weight,
+        "total_seen": total_seen,
+        "l2_variance": l2[0] if l2 else None,
+        "l2_mean_hat_p": l2[1] if l2 else None,
+        "num_classes": l2[2] if l2 else 0,
+        "sparse_fraction": sparse_frac,
+        "sparse_bad": bad,
+        "sparse_total": total,
+        "sample_rate": args.sample_rate,
+        "seed": args.seed,
+        "notes": "event_A = odd n; event_B = one-step contraction T(n) < n"
+    }
+
+    json_path = os.path.join(args.output, f"{base}_summary.json")
+    with open(json_path, "w") as f:
+        json.dump(summary, f, indent=2)
+
+    print("Wrote CSV:", csv_path)
+    print("Wrote summary JSON:", json_path)
+    return 0
+
+if __name__ == "__main__":
+    raise SystemExit(main())
+
*** End Patch
