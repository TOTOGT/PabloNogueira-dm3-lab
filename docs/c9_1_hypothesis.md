# D9 Micro-Obligation C9.1 — The Mixing Hypothesis (H_mix)

**Status:** OPEN — this is the single remaining micro-obligation for D9.

**No claim of proof is made here.**  This document records the precise statement
of (H_mix), its relationship to the mean-contraction argument, and the protocol
for empirical and analytic investigation.

---

## 1. Precise Statement

**Definition (Admissible residue class).** Fix `M ≥ 2`.  A residue `a mod 2^M`
is *admissible* if:
- `a` is odd, and
- `v₂(3a+1) = 1` (equivalently, `3a+1 ≡ 2 mod 4`, equivalently `a ≡ 3 mod 4`,
  since `3·3 = 9 ≡ 1 mod 4`).

The set of admissible residues modulo `2^M` is denoted `A_M`.
Its cardinality is `|A_M| = 2^(M-2)`.

**Definition (Notation).** For odd `n`, write:
- `T(n) = (3n+1) / 2^{v₂(3n+1)}` — the Collatz macro-step (next odd),
- `A(n)`: `v₂(3n+1) = 1` (equivalently `n ≡ 3 mod 4`),
- `B(n)`: `v₂(3T(n)+1) = 1` (equivalently `n ≡ 7 mod 8`, among `n` with `A(n)`),
- `w(n) = 1/log(n)` — contact-form weight,
- `Pr_{I,w}(E | R)` — weighted conditional probability on window `I=[N,2N)`,
- `W_N(a) = Σ_{n ∈ R_a} w(n)`, `W_N = Σ_{n ∈ I_N} w(n)`.

**Remark on determinism.** Since `B(n)` is fully determined by `n mod 8` (given
`A(n)`), for any `M ≥ 3`, every admissible class `a mod 2^M` has `p_hat(a)` equal
to exactly `0` or `1`.  The signed deviations `δ_a = p_hat(a) − 1/2 = ±1/2`
alternate, and the non-trivial quantity is their WEIGHTED SUM (the aggregate
defect `D_N`), not each individual deviation.

**Hypothesis (H_mix)(M, η).**  We say **(H_mix)(M, η)** holds if for all
sufficiently large `N` (depending only on `M` and `η`),

```
|D_N(M)| ≤ η,
```

where the **aggregate signed deviation** is:

```
D_N(M) = Σ_{a ∈ A_M}  (W_N(a) / W_N) · (Pr_{I,w}(B(n) | R_a) − 1/2).
```

Here `R_a = { n ∈ I_N : n ≡ a (mod 2^M), A(n) }`.

In words: the weighted average (over admissible classes, weighted by their
occupancy in window `I_N`) of the signed deviations from `1/2` has absolute
value at most `η`.  For `M=3`, this aggregate is exactly `0` by symmetry.  For
larger `M`, the residual depends on higher-order equidistribution of `n mod 2^M`
in the window and is the genuinely hard part.

---

## 2. Why (H_mix) Suffices for Mean Contraction

The **Reduction Lemma** (Theorem in `docs/d9_v0.2.tex`) states:

> If **(H_mix)(M, η)** holds for some `η < log₂(4/3) / c_step ≈ 1.0`,
> then mean contraction holds:
> ```
> limsup_{N→∞} Λ̄_N ≤ −log₂(4/3) + c_step · η < 0.
> ```

The constant `c_step` captures the excess per-step log-ratio from a `(1,1)`-event;
it is approximately `log₂(3/4) ≈ 0.415`.  The threshold on `η` is explicit.

---

## 3. Testing Protocol

### Empirical testing

Use the script `scripts/collatz_c9_2_sampling.py`:

```bash
cd scripts/

# Quick test: M=4, window I=[100000,200000)
python collatz_c9_2_sampling.py --M 4 --N 100000

# Larger window, M=5
python collatz_c9_2_sampling.py --M 5 --N 1000000 --window-size 1000000

# Random sampling on large window
python collatz_c9_2_sampling.py --M 6 --N 10000000 --mode random --max-samples 10000
```

**What to look for in the output:**

| Metric | Target for (H_mix) evidence |
|--------|-----------------------------|
| `aggregate_signed_deviation_D_N` | As small as possible; close to 0 supports (H_mix) |
| `mean_p_overall` | Close to 0.5 |
| `max_deviation_per_residue` | ≈ 0.5 is EXPECTED (B is mod-8 deterministic); ignore for H_mix |

The key metric is `aggregate_signed_deviation_D_N` (= `|D_N(M)|`), NOT
`max_deviation_per_residue`.  Per-residue `p_hat = 0` or `1` is normal behavior.

Report outputs using the format in Section 4 below.

### Analytic testing

To prove (H_mix)(M, η) analytically:

1. **Fix M.** Work modulo `2^M`.
2. **Enumerate admissible classes** `a ∈ A_M`.
3. **Propagate through T(n):** for `n ≡ a (mod 2^M)` with `A(n)` true,
   determine the residue of `T(n)` mod a suitable modulus, and compute
   `Pr(B(n) | n ≡ a (mod 2^M), A(n))` by residue arithmetic.
4. **Bound the deviation** from `1/2` uniformly over admissible classes.
5. **State an explicit `η`** and verify the threshold condition.

See Issue C9.1 in the repository for the full proof checklist.

---

## 4. Reporting Format

When reporting empirical or analytic results for (H_mix), please include:

```
## H_mix Report

- M:            <value>
- Window:       I = [N, window_end), N = <value>
- Sampling mode: <exhaustive/stride/random>, max_samples = <value>
- Seed:         <value>

Results:
- Overall weighted p_hat:              <value>
- Mean p_hat over residues:            <value>
- Aggregate signed deviation |D_N(M)|: <value>  [H_mix threshold: η < log₂(4/3)/c_step ≈ 1.0]
- Max per-residue |p_hat − 0.5|:       <value>  [expected ≈ 0.5; not the H_mix quantity]

Residue breakdown: [attach residue_stats CSV or paste key rows]

Conclusion: H_mix(M=<>, η=<>) supported / not supported by this data.
```

---

## 5. Open Questions

- For which minimal `(M, η)` does the analytic proof go through?
- Is `η` monotone decreasing in `M` (better control for larger `M`)?
- Can the contact-form weight `w(n) = 1/log(n)` be replaced by natural density
  without changing the conclusion?

---

## 6. Cross-References

- Full analytic context: `docs/d9_v0.2.tex`
- Empirical script: `scripts/collatz_c9_2_sampling.py`
- Script guide: `scripts/README.md`
- Contributor guide: `docs/CONTRIBUTING_D9.md`
- GitHub Issue C9.1: *Prove residue-class decorrelation lemma*
