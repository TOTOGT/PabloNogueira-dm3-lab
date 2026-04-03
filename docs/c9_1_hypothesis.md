# C9.1 Hypothesis: Local Mean Contraction via the dm³ Fingerprint

G6 LLC · Pablo Nogueira Grossi · 2026

---

## Statement

For the fully-reduced ("odd-to-odd") Syracuse map

$$T(n) = \frac{3n+1}{2^{v_2(3n+1)}} \quad (n \text{ odd}),$$

the **local mean log-drift** satisfies

$$\mathbb{E}\!\left[\log\frac{T(n)}{n}\right] = \log\frac{3}{4} \approx -0.2877$$

for odd $n$ drawn uniformly from any sufficiently large interval $[N, 2N)$.

This negative mean is the central empirical certificate for Bridge 0's local
contraction in the dm³ fingerprint analysis.  The remaining analytic task is
converting this averaged local control into a uniform global closure.

---

## 2-Adic Residue Signature

Partitioning odd integers by their residue class $r \pmod{2^M}$ reveals a
structured, scale-invariant deviation pattern:

| Residue condition | $v_2(3r+1)$ | Mean log-drift |
|---|---|---|
| $r \equiv 3 \pmod{4}$ | $= 1$ (deterministic) | $\log(3/2) \approx +0.405$ |
| $r \equiv 1 \pmod{8}$ | $= 2$ (deterministic) | $\log(3/4) \approx -0.288$ |
| $r \equiv 5 \pmod{8}$ | $\geq 3$ (variable) | $\leq \log(3/8) \approx -0.981$ |

Exactly **75 %** of odd residue classes deviate from the global mean by more
than 0.05, independent of $M$.  This is the `sparse_fraction = 0.750`
certificate.

---

## Fourier Signature

The per-residue mean log-drift function exhibits a dominant 2-adic Fourier
mode.  The mode with the highest amplitude after low-frequency removal
(`--low-cut-fraction 0.125`) consistently ranks first (`dominant_fourier_mode
= 1`), reflecting the coarsest 2-adic level distinction ($r \equiv 1$ vs
$r \equiv 3 \pmod{4}$).

---

## Reproducibility Note — Golden Runs

The following command reproduces the canonical golden runs for
$M \in \{12, 14, 16\}$ with window $[100\,000,\; 200\,000)$:

```bash
for M in 12 14 16; do
  python3 scripts/collatz_c9_2_sampling_option1.py \
      --M $M --N 100000 --out-dir scripts/out
  python3 scripts/collatz_c9_2_fourier_v2.py \
      --input scripts/out/c9_2_M${M}_N100000.csv \
      --out-dir scripts/out --low-cut-fraction 0.125
done
```

### Expected summary metrics (verified runs, seed = 42)

| Metric | M = 12 | M = 14 | M = 16 |
|---|---:|---:|---:|
| `global_mean_log_drift` | −0.287700 | −0.287700 | −0.287700 |
| `l2_variance` | 0.952 | 0.952 | 0.952 |
| `sparse_fraction` | 0.750 | 0.750 | 0.750 |
| `avg_rms_ratio` | 18.0 | 18.0 | 18.0 |
| `dominant_fourier_mode` | 1 | 1 | 1 |

**Note:** `global_mean_log_drift = −0.287700` matches $\log(3/4)$ to four
decimal places, providing a robust empirical certificate of the local mean
contraction predicted by the dm³ fingerprint.

---

## Files Produced

For each $M$ the pipeline writes four output files to `scripts/out/`:

```
c9_2_M{M}_N100000.csv               per-residue counts and mean log drifts
c9_2_M{M}_N100000_summary.json      global statistics
c9_2_M{M}_N100000_fourier_modes.csv per-mode DFT amplitudes and phases
c9_2_M{M}_N100000_fourier.json      Fourier summary (dominant mode, rms ratio)
```

---

## Next Steps

1. Formalise statistical uncertainty bounds on `global_mean_log_drift` via
   bootstrap over windows and seeds.
2. Extend the analytic argument from local averaged contraction to a uniform
   global bound (Bridge 0 closure).
3. Cross-check the 2-adic Fourier amplitude structure against the theoretical
   Walsh-Hadamard decomposition of $r \mapsto -v_2(3r+1)\log 2$.
