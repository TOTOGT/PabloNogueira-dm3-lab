# NS lane analysis notes

This directory holds **NS lane** analysis drafts, sketches, and LaTeX notes.

Guidelines:
- Keep NS notes lane‑pure: do not reference Collatz deliverables or Collatz-specific filenames.
- Do not commit empirical CSV/JSON outputs. Attach them to issues (N9.2 #8 / N9.1 #9) instead.
- Do not assume baseline 1/2 unless explicitly defined; record baseline p0 in summaries.
- Use clear filenames: `n9_v0.1_topic.tex`, `n9_v0.1_operator_estimate.tex`, etc.

Current status: waiting for observable definition (A/B events, class space, scale parameter, admissibility,
windowing/weighting, baseline p0) from N9.2 #8 / N9.1 #9.

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

