# scripts/README.md — Collatz D9 Sampling Script

This directory contains empirical tooling for the D9 deliverable of the
Collatz dm³ project.  The main script tests the modular mixing hypothesis
**(H_mix)** described in `docs/c9_1_hypothesis.md` and the LaTeX document
`docs/d9_v0.2.tex`.

---

## `collatz_c9_2_sampling.py`

### Purpose

For a given modulus exponent `M` and integer window `I = [N, N + window_size)`,
the script:

1. Enumerates all **admissible** residue classes `a mod 2^M`
   (odd `a` with `v₂(3a+1) = 1`, i.e. `a ≡ 3 mod 4`, since `3·3 ≡ 1 mod 4`).
2. For each residue `a`, samples odd `n ∈ I` with `n ≡ a (mod 2^M)` and
   event `A(n)` true (`v₂(3n+1) = 1`).
3. Computes contact-form weights `w(n) = 1/log(n)`.
4. Records weighted counts for events `A(n)` and `A(n) ∧ B(n)`
   (where `B(n) : v₂(3T(n)+1) = 1`).
5. Outputs per-residue statistics and a summary to CSV files.

### Requirements

**No third-party dependencies.**  Pure Python ≥ 3.8 (stdlib only):
`argparse`, `csv`, `math`, `os`, `random`, `sys`.

---

## Usage

```bash
cd scripts/

# Basic run: M=4, window I=[100000, 200000)
python collatz_c9_2_sampling.py

# Custom M and window
python collatz_c9_2_sampling.py --M 5 --N 1000000 --window-size 1000000

# Random sampling mode (useful for very large windows)
python collatz_c9_2_sampling.py --M 4 --N 10000000 --mode random --max-samples 5000 --seed 123

# Stride mode (every 3rd candidate)
python collatz_c9_2_sampling.py --M 4 --N 100000 --mode stride --stride 3

# Custom output directory
python collatz_c9_2_sampling.py --out-dir /tmp/d9_results
```

---

## Command-line options

| Flag | Default | Description |
|------|---------|-------------|
| `--M` | `4` | Modulus exponent: residues are mod `2^M` |
| `--N` | `100000` | Window start (inclusive) |
| `--window-size` | `N` | Window size (default gives `I=[N, 2N)`) |
| `--mode` | `exhaustive` | Sampling mode: `exhaustive`, `stride`, or `random` |
| `--stride` | `1` | Stride multiplier for `stride` mode |
| `--max-samples` | `100000` | Maximum samples per residue class |
| `--seed` | `42` | RNG seed for `random` mode |
| `--out-dir` | `out` | Output directory for CSV files |

---

## Output files

Both files are written to `<out-dir>/` (default: `out/`).

### `residue_stats_M{M}_N{N}.csv`

One row per admissible residue class.

| Column | Description |
|--------|-------------|
| `M` | Modulus exponent |
| `N` | Window start |
| `window_end` | Window end (exclusive) |
| `residue_a` | Residue `a mod 2^M` |
| `count_A` | Number of sampled `n` with `A(n)` true |
| `count_AB` | Number of sampled `n` with `A(n) ∧ B(n)` true |
| `weighted_A` | `Σ w(n)` over `n` with `A(n)` true |
| `weighted_AB` | `Σ w(n)` over `n` with `A(n) ∧ B(n)` true |
| `p_hat` | `weighted_AB / weighted_A` (estimate of `Pr(B|R_a)`) |

### `summary_M{M}_N{N}.csv`

| Metric | Description |
|--------|-------------|
| `mean_p_overall` | Pooled weighted `p = Σ_a weighted_AB(a) / Σ_a weighted_A(a)` |
| `mean_p_over_residues` | Simple mean of per-residue `p_hat` values |
| `max_deviation_per_residue` | `max_a |p_hat(a) − 0.5|` (≈ 0.5 expected; not the H_mix quantity) |
| `aggregate_signed_deviation_D_N` | `|D_N(M)|` = weighted sum of signed deviations (the H_mix quantity) |
| `p_hat_q{25,50,75,90,95}` | Quantiles of the per-residue `p_hat` distribution |

---

## Interpreting results for (H_mix)

**(H_mix)(M, η) holds empirically** if `aggregate_signed_deviation_D_N` ≤ `η` in
the output summary.  To assert mean contraction (see `docs/d9_v0.2.tex`), we need
`η < log₂(4/3) / c_step ≈ 1.0`.

**Important:** `max_deviation_per_residue ≈ 0.5` is **expected and normal** — it
reflects that `B(n)` is fully determined by `n mod 8`, so each admissible class
has `p_hat = 0` or `1`.  The H_mix quantity is the *aggregate signed deviation*
`|D_N(M)|`, where the ±1/2 terms cancel.

The script prints an informal pass/fail check using threshold `η = 0.05` on
`|D_N(M)|`.  A more rigorous analytic verification is required; see
`docs/c9_1_hypothesis.md` for the testing protocol.

---

## Example output (illustrative)

```
D9 H_mix empirical sampler
  M=4, 2^M=16, admissible residues: 4
  Window I=[100000, 200000)  (size=100000)
  Mode: exhaustive, max_samples/residue: 100000, seed: 42

Results
  Overall weighted p_hat (pooled):       0.499999  (target ≈ 0.5)
  Mean p_hat over residues:               0.500000
  Max |p_hat - 0.5| per residue:          0.500000  (≈0.5 expected: B is mod-8 deterministic)
  Aggregate signed deviation |D_N(M)|:    0.000001  (H_mix quantity; target ≈ 0)
  p_hat quantiles: Q25=0.0000  Q50=0.5000  Q75=1.0000  Q90=1.0000  Q95=1.0000

  H_mix informal check (|D_N(M)| < 0.05): PASS
  (Note: per-residue max ≈ 0.5 is expected; the H_mix quantity is the aggregate |D_N(M)|)
```

---

## Directory structure

```
scripts/
├── collatz_c9_2_sampling.py   ← main script
├── README.md                  ← this file
├── out/                       ← CSV output (not committed; see .gitkeep)
│   └── .gitkeep
└── examples/                  ← optional small sample CSVs
```

---

## Related files

- `docs/d9_v0.2.tex` — LaTeX document with full analytic context
- `docs/c9_1_hypothesis.md` — Standalone H_mix statement and testing protocol
- `docs/CONTRIBUTING_D9.md` — Contributor guide
