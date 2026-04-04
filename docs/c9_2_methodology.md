# C9.2 Methodology — Weighted (1,1) Consecutive-Valuation Probabilities

**Issue:** [TOTOGT/DM3-lab#3](https://github.com/TOTOGT/DM3-lab/issues/3)
**Status:** Empirical investigation — no proof is claimed.

---

## 1. Definitions

### 1.1 Odd-normalised Collatz step

For **odd** `n ≥ 3`, define the return map

```
T(n) = (3n + 1) / 2^{v₂(3n+1)}
```

where `v₂(x)` denotes the **2-adic valuation** of `x` (the largest power of 2
dividing `x`).  By construction `T(n)` is always odd, and `v₂(3n+1) ≥ 1`
because `3n+1` is even when `n` is odd.

### 1.2 Events A and B

| Symbol | Definition | Equivalent modular condition |
|--------|-----------|------------------------------|
| `A(n)` | `v₂(3n+1) = 1` | `n ≡ 3 (mod 4)` |
| `B(n)` | `v₂(3·T(n)+1) = 1` | depends on `n mod 8` given `A(n)` |

Both events are fully determined by `n` (no randomness).

### 1.3 (1,1) indicator

```
I₁₁(n) = 1[A(n) ∧ B(n)]
```

This is 1 when two **consecutive** Collatz macro-steps each have 2-adic
valuation exactly 1 (i.e., the "short" step type in the dm³ / H_mix
framework).

### 1.4 Contact-form weight

```
w(n) = 1 / log(n)
```

This weight gives larger `n` less influence and is chosen to match the
contact-form measure used in the analytic part of the DM3 framework.

### 1.5 Weighted probabilities

For a finite sample set (window) `W`:

```
P_w(E) = Σ_{n ∈ W} w(n) · 1_E(n)  /  Σ_{n ∈ W} w(n)
```

The metrics reported are:

| Metric | Formula |
|--------|---------|
| `p_A` | `P_w(A)` |
| `p_B` | `P_w(B)` |
| `p_A_and_B` | `P_w(A ∧ B)` |
| `p11_conditional` | `P_w(A ∧ B) / P_w(A)` (if `P_w(A) > 0`) |
| `rho` | `Cov_w(1_A, 1_B) / sqrt(Var_w(1_A) · Var_w(1_B))` |

where:
```
Cov_w(1_A, 1_B) = P_w(A ∧ B) - P_w(A) · P_w(B)
Var_w(1_A)      = P_w(A) · (1 - P_w(A))
Var_w(1_B)      = P_w(B) · (1 - P_w(B))
```

If either variance is zero, `rho` is set to `null`.

---

## 2. Windowing and Sampling Modes

### 2.1 Window semantics

The window is the half-open interval `[N, N + window_size)` (exclusive upper
bound).  All values of `n` within the window that are **odd** and satisfy
`n ≥ min_n` (default 33) are eligible.

When `--window-size` is omitted, the script uses the **dyadic** window
`[N, 2N)`, so `window_size = N`.

### 2.2 Sampling modes

| Mode | Description | Determinism |
|------|-------------|-------------|
| `exhaustive` | Enumerates every eligible odd `n` | Deterministic |
| `stride` | Enumerates every `k`-th eligible odd `n`; `k` auto-computed from `--max-samples` or set with `--stride-k` | Deterministic |
| `random` | Draws `min(max_samples, total_eligible)` distinct odd `n` uniformly without replacement using Floyd's algorithm | Seeded |

### 2.3 Minimum n

Only `n ≥ min_n` (default 33) are sampled.  This avoids very small `n` where
the logarithmic weight `1/log(n)` would be disproportionately large and where
Collatz dynamics are atypical.

---

## 3. Bootstrap Uncertainty Estimation

### 3.1 Weighted bootstrap

Rows are resampled with replacement, where each row's sampling probability
is proportional to `w(n)`.  This preserves the weighted measure structure.

### 3.2 Block bootstrap

Contiguous blocks of rows are resampled with replacement.  This is more
appropriate when rows may be correlated (e.g., nearby `n` may share residue
class patterns).  Default block size: 100 rows.

### 3.3 Output

Both modes report:
- `p11_se`, `rho_se`: empirical standard errors
- `p11_ci_95`, `rho_ci_95`: 2.5th–97.5th percentile confidence intervals

---

## 4. Per-Residue Breakdown (optional, `--M`)

When `--M` is supplied, the sample is grouped by `a = n mod 2^M` (only odd
residues appear since we restrict to odd `n`).  For each residue class, the
script reports:

- `count`: number of sampled `n` in this class
- `weighted_count`: sum of `w(n)` over the class
- `p_A`, `p_B`, `p_A_and_B`, `p11`: class-level weighted probabilities

This enables 2-adic Fourier analysis of the `p11` function (using a separate
Fourier script).

---

## 5. How to Interpret `p11` and `rho`

### 5.1 Expected value under independence

If `A` and `B` were independent under the weighted measure:
```
P_w(A ∧ B) = P_w(A) · P_w(B)
```
so `p11_conditional = P_w(B)` and `rho = 0`.

### 5.2 Observed behaviour

Empirically, for large `N` (e.g., `N = 100000` to `N = 1000000`):
- `p_A ≈ 0.5` (about half of odd `n` satisfy `A(n)`)
- `p_B ≈ 0.5`
- `p11_conditional ≈ 0.5` (near independence)
- `rho` is small (near 0)

This near-independence is consistent with the H_mix hypothesis that the
two consecutive valuations are approximately independent under the weighted
measure for large `n`.

### 5.3 Finite-range checks

The runner provides a matrix of window sizes and modes so that convergence
as `N → ∞` can be monitored.  A decreasing `|rho|` and stable `p11_conditional`
across runs is the expected empirical certificate.

---

## 6. Output Files

For each run, the sampler produces:

| File | Contents |
|------|----------|
| `<stem>.csv` | Per-sample data: `n, A, B, w, v2_1, T_n, v2_2` |
| `<stem>_summary.json` | All metrics, window info, bootstrap results |

The CSV schema is:
```
n       : the odd integer sampled
A       : 1 if v2(3n+1)=1, else 0
B       : 1 if v2(3*T(n)+1)=1, else 0
w       : 1/log(n)
v2_1    : v2(3n+1)
T_n     : T(n) = (3n+1)/2^{v2_1}
v2_2    : v2(3*T_n+1)
```

---

## 7. Reproducibility

### 7.1 Self-test

```bash
python3 scripts/collatz_c9_2_p11_sampler.py --self-test
```

Validates: `T(n)` odd, `v₂ ≥ 1`, weights finite, probabilities in `[0,1]`,
bootstrap output shapes.

### 7.2 Canonical golden runs

```bash
# Run from repo root
bash scripts/collatz_c9_2_p11_runner.sh
```

Or manually:
```bash
# Exhaustive, N=100000
python3 scripts/collatz_c9_2_p11_sampler.py \
  --N 100000 --mode exhaustive --seed 42 \
  --out-dir results/c9_2/run1_N1e5_exhaustive

# Random, N=1000000
python3 scripts/collatz_c9_2_p11_sampler.py \
  --N 1000000 --mode random --max-samples 1000000 --seed 42 \
  --out-dir results/c9_2/run2_N1e6_random
```

### 7.3 No external dependencies

Both scripts use **Python stdlib only** (no numpy, pandas, or matplotlib).
The CSV output is suitable for plotting with any tool (gnuplot, Excel, etc.).

---

## 8. Limitations

1. **Finite window**: All statistics are averages over a finite window.  The
   asymptotic behaviour as `N → ∞` is not proven here.

2. **Contact-form weight**: The choice `w(n) = 1/log(n)` is motivated by the
   DM3 analytic framework.  Different weights may give different values of
   `rho`.

3. **No plots in this PR**: CSV output is provided for external plotting.
   A plotting guide can be added in a follow-up.

4. **Bootstrap validity**: The weighted bootstrap assumes rows are
   approximately independent.  For large windows this is reasonable, but
   near-consecutive `n` may share 2-adic residue class properties.  The
   block bootstrap mitigates this.

5. **Scope**: This is empirical evidence only.  No proof of H_mix or any
   asymptotic claim is made.

---

## 9. Related Files

| Path | Description |
|------|-------------|
| `scripts/collatz_c9_2_p11_sampler.py` | Main sampler (this PR) |
| `scripts/collatz_c9_2_p11_runner.sh` | Recommended run matrix (this PR) |
| `scripts/collatz_c9_2_sampling.py` | Earlier C9.2 sampling script (graded drift observable) |
| `docs/c9_1_hypothesis.md` | C9.1 hypothesis statement |
| `results/c9_2/` | Output directory for run results |
