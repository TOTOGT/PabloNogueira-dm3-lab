# NS Lane Analysis Notes

This directory holds **NS lane** analysis drafts, sketches, and LaTeX notes.

**NS (Non-Standard / Numerical-Spectral) lane** is a parallel research track to the D9 Collatz lane. It applies the dm³ operator framework to spectral and numerical analysis questions that are structurally analogous to the Collatz mixing hypothesis but arise in different mathematical settings.

---

## Filing Guidelines

- Keep NS notes **lane-pure**: do not reference Collatz deliverables or Collatz-specific filenames.
- Do not commit empirical CSV/JSON outputs — attach them to issues (N9.2 #8 / N9.1 #9) instead.
- Do not assume baseline `1/2` unless explicitly defined; record baseline `p0` in all summaries.
- Use clear filenames: `n9_v0.1_topic.tex`, `n9_v0.1_operator_estimate.tex`, etc.

---

## Current Status

Waiting for observable definition from issues N9.2 #8 / N9.1 #9:
- A/B event definitions
- Class space and scale parameter
- Admissibility conditions
- Windowing / weighting conventions
- Baseline `p0`

---

## Related Files

- `docs/c9_1_hypothesis.md` — Collatz lane analogue (H_mix statement and testing protocol)
- `docs/CONTRIBUTING_D9.md` — D9 contributor guide (useful as a structural template for NS contributions)
- `scripts/collatz_c9_2_sampling.py` — Sampling script (Collatz lane; adapt for NS observables)

---

## N9.4 — Kernel Commutator Lemma: Far-Range Decay

**Formal Lean 4 proof:** `lean/KernelCommutatorDecay.lean`

### Kernel decay assumption

The curvature operator **K** in the AXLE chain C → K → F → U acts at discrete scales
j ∈ ℤ through a kernel K(j, k).  The decay hypothesis (`KernelDecayHyp`) states:

```
|K(j, k)| ≤ E0 · exp(−ν · (j − k))   for all j ≥ k
```

Constants:

| Symbol | Role | Sign |
|--------|------|------|
| E0     | Amplitude bound (may encode a time horizon T via E0 = C₀ · T) | > 0 |
| ν      | Spectral-gap decay rate | > 0 |
| T      | Scale / time horizon (enters via E0) | > 0 |
| ε      | Far-range tolerance | > 0 |
| J      | Far-range cut-off index | ∈ ℕ |

### Far-range bound

For any base scale k and cut-off J:

```
∑_{n ≥ 0} |K(k + J + n, k)| ≤ E0 · exp(−ν · J) · (1 − exp(−ν))⁻¹
```

Proof: comparison with the geometric series ∑ exp(−ν)ⁿ = (1 − exp(−ν))⁻¹.
The bound is **uniform in k**.

### Choice of J(ε)

```
J(ε) := ⌈ log(E0 / (ε · (1 − exp(−ν)))) / ν ⌉₊
```

With J = J(ε), the far-range sum is ≤ ε (theorem `farRange_le_eps`).

**Dependence on E0, ν, T:**
- J(ε) ~ (1/ν) · log(E0 / ε) as ε → 0.
- Larger E0 (or T) → larger J(ε).
- Larger ν (faster decay) → smaller J(ε).

