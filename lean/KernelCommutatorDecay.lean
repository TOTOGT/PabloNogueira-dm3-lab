/-
  N9.4 — Kernel Commutator Lemma: Far-Range Decay
  G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026
  MIT License

  Quantifies how the far-range (j ≥ k + J) contribution of a
  convolution-type kernel is controlled by exponential decay, and
  provides the explicit formula for J(ε) ensuring far-range ≤ ε
  uniformly.

  Parameters
  ----------
  E0 : ℝ  — kernel amplitude bound    (E0 > 0)
  ν  : ℝ  — decay exponent             (ν  > 0)
  T  : ℝ  — summation / scale horizon  (T  > 0)  [enters via E0 · T product]
  ε  : ℝ  — tolerance                  (ε  > 0)
  J  : ℕ  — far-range cut-off index

  Operator context
  ----------------
  In the AXLE chain C → K → F → U, the curvature operator K acts at
  discrete scales j ∈ ℤ.  Two scales j and k interact through the
  kernel K(j, k).  When |j − k| ≥ J (far range), the kernel decay
  assumption guarantees the interaction is uniformly small.

  Main results
  ------------
  · farRange_bound   :  ∑ₙ |K(k + J + n, k)| ≤ E0 · exp(−ν·J) · (1 − exp(−ν))⁻¹
  · chooseJ          :  J(ε) := ⌈log(E0 / (ε · (1 − exp(−ν)))) / ν⌉₊
  · farRange_le_eps  :  with J = J(ε), far-range sum ≤ ε
-/

import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Topology.Algebra.InfiniteSum.Basic
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Topology.Algebra.InfiniteSum.Order

namespace TOGT

-- ============================================================
-- SECTION N9.4.1: KERNEL DECAY ASSUMPTIONS AND CONSTANTS
-- ============================================================

/-- Kernel decay hypothesis for the AXLE curvature operator K.

    The kernel K : ℤ → ℤ → ℝ satisfies an exponential decay bound
    in the scale separation j − k:

      |K(j, k)| ≤ E0 · exp(−ν · (j − k))   for all j ≥ k

    Constants:
    · E0 > 0 : amplitude bound (may depend on the time horizon T via E0 = C · T)
    · ν  > 0 : decay rate (determined by the spectral gap of the curvature)

    This is the standing assumption for all far-range estimates.
    It captures the off-diagonal decay standard in Calderón–Zygmund
    and pseudodifferential operator theory. -/
structure KernelDecayHyp (K : ℤ → ℤ → ℝ) (E0 ν : ℝ) : Prop where
  /-- Amplitude bound is positive. -/
  E0_pos : 0 < E0
  /-- Decay rate is positive. -/
  ν_pos  : 0 < ν
  /-- Pointwise exponential decay for j ≥ k. -/
  decay  : ∀ (j k : ℤ), k ≤ j →
             |K j k| ≤ E0 * Real.exp (-ν * (↑(j - k) : ℝ))

-- ============================================================
-- SECTION N9.4.2: GEOMETRIC SERIES AUXILIARY LEMMAS
-- ============================================================

private lemma exp_neg_nonneg (ν : ℝ) : 0 ≤ Real.exp (-ν) :=
  le_of_lt (Real.exp_pos _)

private lemma exp_neg_lt_one {ν : ℝ} (hν : 0 < ν) : Real.exp (-ν) < 1 := by
  rw [Real.exp_lt_one_iff]; linarith

/-- The series ∑ₙ exp(−ν)ⁿ is summable for ν > 0. -/
private lemma summable_exp_geo (ν : ℝ) (hν : 0 < ν) :
    Summable (fun n : ℕ => Real.exp (-ν) ^ n) :=
  summable_geometric_of_lt_one (exp_neg_nonneg ν) (exp_neg_lt_one hν)

/-- The series ∑ₙ exp(−ν)ⁿ = (1 − exp(−ν))⁻¹ for ν > 0.
    This is the key geometric-series identity. -/
private lemma tsum_exp_geo (ν : ℝ) (hν : 0 < ν) :
    ∑' n : ℕ, Real.exp (-ν) ^ n = (1 - Real.exp (-ν))⁻¹ :=
  tsum_geometric_of_lt_one (exp_neg_nonneg ν) (exp_neg_lt_one hν)

/-- exp(−ν)ⁿ = exp(−ν · n).  Proved by induction on n using exp_add. -/
private lemma exp_pow_eq_exp_mul (ν : ℝ) (n : ℕ) :
    Real.exp (-ν) ^ n = Real.exp (-ν * ↑n) := by
  induction n with
  | zero => simp
  | succ k ih =>
    rw [pow_succ, ih, ← Real.exp_add]
    congr 1
    push_cast
    ring

-- ============================================================
-- SECTION N9.4.3: FAR-RANGE BOUND
-- ============================================================

/-- **Far-range bound.**

    Under KernelDecayHyp K E0 ν, for any base scale k : ℤ and
    cut-off J : ℕ, the series of absolute kernel values over all
    far-range displacements n ≥ 0 satisfies:

      ∑ₙ |K(k + J + n, k)| ≤ E0 · exp(−ν · J) · (1 − exp(−ν))⁻¹

    Proof strategy
    ──────────────
    1. Bound each term by the geometric majorant
         |K(k+J+n, k)| ≤ E0 · exp(−ν·J) · exp(−ν)ⁿ.
    2. The majorant series is summable (geometric series, ratio exp(−ν) < 1).
    3. Apply the comparison test and evaluate the geometric sum.

    Dependence: the bound scales as E0 (amplitude), decays in ν (rate),
    and in J (cut-off); if E0 incorporates a time horizon T, the
    dependence on T appears linearly through E0 · T. -/
theorem farRange_bound
    (K : ℤ → ℤ → ℝ) (E0 ν : ℝ)
    (hK : KernelDecayHyp K E0 ν)
    (k : ℤ) (J : ℕ) :
    ∑' n : ℕ, |K (k + ↑J + ↑n) k| ≤
      E0 * Real.exp (-ν * ↑J) * (1 - Real.exp (-ν))⁻¹ := by
  -- Step 1: pointwise bound on each term
  have hmaj : ∀ n : ℕ, |K (k + ↑J + ↑n) k| ≤
      E0 * Real.exp (-ν * ↑J) * Real.exp (-ν) ^ n := by
    intro n
    -- The index k + J + n is ≥ k
    have hle : k ≤ k + ↑J + ↑n := by
      have h1 : (0 : ℤ) ≤ ↑J := Int.coe_nat_nonneg J
      have h2 : (0 : ℤ) ≤ ↑n := Int.coe_nat_nonneg n
      linarith
    -- Apply the decay hypothesis
    have hdecay := hK.decay (k + ↑J + ↑n) k hle
    -- Simplify the cast of the scale difference
    have hcast : (↑(k + ↑J + ↑n - k) : ℝ) = (↑J : ℝ) + ↑n := by
      push_cast; ring
    rw [hcast] at hdecay
    -- Factor the exponential and convert to geometric form
    calc |K (k + ↑J + ↑n) k|
        ≤ E0 * Real.exp (-ν * (↑J + ↑n)) := hdecay
      _ = E0 * (Real.exp (-ν * ↑J) * Real.exp (-ν) ^ n) := by
            rw [show -ν * ((↑J : ℝ) + ↑n) = (-ν * ↑J) + (-ν * ↑n) by ring,
                Real.exp_add, exp_pow_eq_exp_mul]
      _ = E0 * Real.exp (-ν * ↑J) * Real.exp (-ν) ^ n := by ring
  -- Step 2: the majorant series is summable
  have hg_sum : Summable (fun n : ℕ => E0 * Real.exp (-ν * ↑J) * Real.exp (-ν) ^ n) :=
    (summable_exp_geo ν hK.ν_pos).mul_left _
  -- Step 3: the kernel series is summable by comparison
  have hf_sum : Summable (fun n : ℕ => |K (k + ↑J + ↑n) k|) :=
    Summable.of_norm_bounded _ hg_sum (fun n => by
      simp only [Real.norm_eq_abs, abs_abs]; exact hmaj n)
  -- Step 4: compare the sums and evaluate the geometric series
  calc ∑' n : ℕ, |K (k + ↑J + ↑n) k|
      ≤ ∑' n : ℕ, E0 * Real.exp (-ν * ↑J) * Real.exp (-ν) ^ n :=
          tsum_le_tsum hmaj hf_sum hg_sum
    _ = E0 * Real.exp (-ν * ↑J) * ∑' n : ℕ, Real.exp (-ν) ^ n := by
          rw [tsum_mul_left]
    _ = E0 * Real.exp (-ν * ↑J) * (1 - Real.exp (-ν))⁻¹ := by
          rw [tsum_exp_geo ν hK.ν_pos]

-- ============================================================
-- SECTION N9.4.4: CHOICE OF J(ε) AND MAIN COROLLARY
-- ============================================================

/-- **Optimal cut-off index J(ε).**

    Given amplitude E0, decay rate ν, and tolerance ε, define:

      J(ε) := ⌈ log(E0 / (ε · (1 − exp(−ν)))) / ν ⌉₊

    This is the smallest natural number J such that the far-range
    bound E0 · exp(−ν · J) · (1 − exp(−ν))⁻¹ is ≤ ε.

    Dependence:
    · Larger E0 (or larger T when E0 = C · T) → larger J(ε).
    · Larger ν (faster decay) → smaller J(ε).
    · Smaller ε (tighter tolerance) → larger J(ε).
    · Growth: J(ε) ~ (1/ν) · log(E0 / ε) as ε → 0. -/
noncomputable def chooseJ (E0 ν ε : ℝ) : ℕ :=
  ⌈Real.log (E0 / (ε * (1 - Real.exp (-ν)))) / ν⌉₊

/-- **Main corollary: far-range ≤ ε with J = J(ε).**

    Under KernelDecayHyp K E0 ν, for any base scale k and ε > 0,
    setting J = chooseJ E0 ν ε yields:

      ∑ₙ |K(k + J(ε) + n, k)| ≤ ε

    This is the kernel commutator lemma for the AXLE operator chain:
    truncating the scale interaction at J(ε) incurs error ≤ ε
    uniformly in k. -/
theorem farRange_le_eps
    (K : ℤ → ℤ → ℝ) (E0 ν ε : ℝ)
    (hK : KernelDecayHyp K E0 ν)
    (hε : 0 < ε)
    (k : ℤ) :
    ∑' n : ℕ, |K (k + ↑(chooseJ E0 ν ε) + ↑n) k| ≤ ε := by
  set J := chooseJ E0 ν ε with hJ_def
  -- 1 − exp(−ν) > 0 because exp(−ν) < 1
  have h1mexp_pos : 0 < 1 - Real.exp (-ν) := by
    linarith [exp_neg_lt_one hK.ν_pos]
  -- The argument of the logarithm is positive
  have harg_pos : 0 < E0 / (ε * (1 - Real.exp (-ν))) :=
    div_pos hK.E0_pos (mul_pos hε h1mexp_pos)
  -- J ≥ log(...) / ν by the ceiling definition
  have hJ_ge : Real.log (E0 / (ε * (1 - Real.exp (-ν)))) / ν ≤ (↑J : ℝ) :=
    Nat.le_ceil _
  -- Therefore exp(−ν · J) ≤ ε · (1 − exp(−ν)) / E0
  have hexp_bound : Real.exp (-ν * ↑J) ≤ ε * (1 - Real.exp (-ν)) / E0 := by
    have hlog_le : Real.log (E0 / (ε * (1 - Real.exp (-ν)))) ≤ ν * ↑J := by
      have := (div_le_iff hK.ν_pos).mp hJ_ge; linarith
    calc Real.exp (-ν * ↑J)
        ≤ Real.exp (-Real.log (E0 / (ε * (1 - Real.exp (-ν))))) := by
              apply Real.exp_le_exp.mpr; linarith
      _ = (E0 / (ε * (1 - Real.exp (-ν))))⁻¹ := by
              rw [Real.exp_neg, Real.exp_log harg_pos]
      _ = ε * (1 - Real.exp (-ν)) / E0 := by
              rw [inv_div]
  -- Apply farRange_bound and simplify with the above estimate
  have hbound := farRange_bound K E0 ν hK k J
  have h1mexp_nn : 0 ≤ (1 - Real.exp (-ν))⁻¹ :=
    inv_nonneg.mpr (le_of_lt h1mexp_pos)
  calc ∑' n : ℕ, |K (k + ↑J + ↑n) k|
      ≤ E0 * Real.exp (-ν * ↑J) * (1 - Real.exp (-ν))⁻¹ := hbound
    _ ≤ E0 * (ε * (1 - Real.exp (-ν)) / E0) * (1 - Real.exp (-ν))⁻¹ := by
          apply mul_le_mul_of_nonneg_right _ h1mexp_nn
          exact mul_le_mul_of_nonneg_left hexp_bound (le_of_lt hK.E0_pos)
    _ = ε := by
          have hE0ne : E0 ≠ 0 := hK.E0_pos.ne'
          have h1mne : 1 - Real.exp (-ν) ≠ 0 := h1mexp_pos.ne'
          field_simp [hE0ne, h1mne]

/-
  FINAL STATUS — N9.4:

  DEFINITIONS:
  · KernelDecayHyp    — exponential decay |K(j,k)| ≤ E0·exp(−ν·(j−k))
  · chooseJ           — explicit J(ε) = ⌈log(E0/(ε·(1−e^{−ν})))/ν⌉₊

  PROVED — zero sorry, zero axioms:
  · exp_pow_eq_exp_mul  — exp(−ν)ⁿ = exp(−ν·n)  [by induction]
  · summable_exp_geo    — ∑ exp(−ν)ⁿ is summable for ν > 0
  · tsum_exp_geo        — ∑ exp(−ν)ⁿ = (1 − exp(−ν))⁻¹
  · farRange_bound      — far-range tsum ≤ E0·exp(−ν·J)·(1−exp(−ν))⁻¹
  · farRange_le_eps     — with J = J(ε), far-range sum ≤ ε  [MAIN RESULT]

  DEPENDENCE ON PARAMETERS:
  · E0 : amplitude constant (may encode time horizon T as E0 = C₀·T).
          Larger E0 → larger J(ε) ~ (1/ν)·log(E0/ε).
  · ν  : decay rate.  Larger ν → smaller J(ε); faster geometric decay.
  · T  : enters through E0 = C₀·T.  J(ε) ~ (1/ν)·log(T/ε) as T grows.
  · ε  : tolerance.  J(ε) ~ (1/ν)·log(1/ε) as ε → 0.

  The bound E0·exp(−ν·J)·(1−exp(−ν))⁻¹ is uniform in k, confirming
  that J(ε) controls the far-range error across all base scales.
-/

end TOGT
