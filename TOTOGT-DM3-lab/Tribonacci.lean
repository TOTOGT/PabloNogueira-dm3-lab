/-
# Tribonacci Polynomial and Companion Matrix in Lean 4

This file proves the characteristic polynomial of the Tribonacci recurrence
is exactly P(x) = x³ − x² − x − 1, and establishes the companion matrix C.

This is the correct algebraic spine for the dm³ Criticality Principle.
The dominant root η* ≈ 1.839 (the Tribonacci constant) is defined via the
Intermediate Value Theorem (not the Cardano formula, which is harder to
formalize in Lean 4 due to rpow/cube-root reasoning).

sorry_count: 0
  All obligations closed.

  Note on tribonacci_growth_rate: the existential statement (∃ K > 0, ∀ n, n ≤ K·η^n)
  does NOT require Jordan decomposition. It follows directly from η > 1 via the
  Bernoulli inequality: η^n ≥ 1 + n·(η−1), so K = 1/(η−1) works.
  Jordan/spectral theory would be needed for the stronger convergence statement
  T(n)/η^n → C (specific limit), which is a separate theorem.
-/

import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.Data.Polynomial.Basic
import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Topology.Order.IntermediateValue

open Polynomial Matrix Real

namespace Tribonacci

/-- The Tribonacci characteristic polynomial P(x) = x³ − x² − x − 1.
    This is the minimal polynomial of the Tribonacci constant η* ≈ 1.839.
    Note: this is distinct from V_c(q) = q³ − cq which has roots at
    0, ±√c and no connection to the Tribonacci constant. -/
def tribPoly : ℝ[X] := X ^ 3 - X ^ 2 - X - 1

/-- Companion matrix of the Tribonacci recurrence T(n) = T(n-1) + T(n-2) + T(n-3). -/
def C : Matrix (Fin 3) (Fin 3) ℝ :=
  !![0, 1, 0;
     0, 0, 1;
     1, 1, 1]

/-- charpoly(C) = tribPoly.
    Strategy: explicitly compute charmatrix C as a 3×3 polynomial matrix,
    then expand det via Matrix.det_fin_three and close with ring. -/
theorem charpoly_C_eq_tribPoly :
    charpoly C = tribPoly := by
  unfold charpoly tribPoly
  have hmat : charmatrix C = !![
      Polynomial.X, -(1 : ℝ[X]), 0;
      0, Polynomial.X, -(1 : ℝ[X]);
      -(1 : ℝ[X]), -(1 : ℝ[X]), Polynomial.X - 1] := by
    ext i j
    fin_cases i <;> fin_cases j <;>
    simp [charmatrix, C, Matrix.smul_fin_three, Matrix.one_fin_three,
          algebraMap_eq, map_one, map_zero, map_neg, Polynomial.algebraMap_eq]
  rw [hmat, Matrix.det_fin_three]
  ring

/-- The recurrence: C acts on state vectors by shifting and summing. -/
theorem recurrence_holds (v : Fin 3 → ℝ) :
    C *ᵥ v = fun i =>
      match i with
      | 0 => v 1
      | 1 => v 2
      | 2 => v 0 + v 1 + v 2 := by
  ext i
  fin_cases i
  · simp [C, Matrix.mulVec, Matrix.dotProduct]
  · simp [C, Matrix.mulVec, Matrix.dotProduct]
  · simp [C, Matrix.mulVec, Matrix.dotProduct]; ring

/-- The standard initial state vector (1, 1, 1) for the Tribonacci recurrence. -/
def initialState : Fin 3 → ℝ := fun _ => 1

-- ============================================================
-- Tribonacci constant η via IVT
-- ============================================================

/-- Existence of the Tribonacci root in [1, 2] via the Intermediate Value Theorem.
    The characteristic polynomial p(x) = x³ − x² − x − 1 satisfies
    p(1) = −2 < 0 and p(2) = 1 > 0. -/
private lemma eta_exists : ∃ x : ℝ, 1 ≤ x ∧ x ≤ 2 ∧ x ^ 3 = x ^ 2 + x + 1 := by
  have hcont : ContinuousOn (fun x : ℝ => x ^ 3 - x ^ 2 - x - 1) (Set.Icc 1 2) :=
    ((((continuous_pow 3).sub (continuous_pow 2)).sub continuous_id).sub
      continuous_const).continuousOn
  have hmem : (0 : ℝ) ∈ Set.Icc ((1 : ℝ) ^ 3 - 1 ^ 2 - 1 - 1)
                                   ((2 : ℝ) ^ 3 - 2 ^ 2 - 2 - 1) := by norm_num
  obtain ⟨c, hc, hpc⟩ :=
    intermediate_value_Icc (by norm_num : (1 : ℝ) ≤ 2) hcont hmem
  exact ⟨c, hc.1, hc.2, by linarith⟩

/-- The Tribonacci constant η ≈ 1.839286755214161: the real root of
    x³ − x² − x − 1 = 0 in [1, 2], constructed via the IVT.

    NOTE: The previous Cardano-formula definition using `rpow` was correct in
    spirit but difficult to formalize (cube-root algebra for rpow is involved).
    The IVT approach gives the same value with a clean Lean 4 proof. -/
noncomputable def eta : ℝ := eta_exists.choose

private lemma eta_spec : 1 ≤ eta ∧ eta ≤ 2 ∧ eta ^ 3 = eta ^ 2 + eta + 1 :=
  eta_exists.choose_spec

/-- η satisfies P(η) = 0, i.e. η³ − η² − η − 1 = 0. -/
theorem eta_root : eta ^ 3 - eta ^ 2 - eta - 1 = 0 := by linarith [eta_spec.2.2]

/-- η > 1 (from IVT interval; η = 1 gives 1 = 3 contradiction). -/
theorem eta_gt_one : 1 < eta := by
  rcases eta_spec.1.eq_or_lt with h | h
  · exfalso; have := eta_spec.2.2; rw [← h] at this; norm_num at this
  · exact h

/-- η > 0. -/
theorem eta_pos : 0 < eta := lt_trans one_pos eta_gt_one

/-- Exponential dominance: η^n grows at least linearly (in fact exponentially faster).
    Proof: take K = 1/(η−1). By the Bernoulli inequality,
      η^n = (1+(η−1))^n ≥ 1 + n·(η−1)
    so K·η^n ≥ (1 + n·(η−1))/(η−1) = 1/(η−1) + n ≥ n.

    Note: the stronger spectral statement T(n)/η^n → C would require Jordan
    decomposition; this existential bound follows from η > 1 alone. -/
theorem tribonacci_growth_rate :
    ∃ (K : ℝ), K > 0 ∧ ∀ n : ℕ, (n : ℝ) ≤ K * eta ^ n := by
  have hδ : 0 < eta - 1 := by linarith [eta_gt_one]
  refine ⟨1 / (eta - 1), by positivity, fun n => ?_⟩
  -- Bernoulli inequality: (1 + δ)^n ≥ 1 + n·δ, so η^n ≥ 1 + n·(η−1)
  have hbern : 1 + (n : ℝ) * (eta - 1) ≤ eta ^ n := by
    have h := one_add_mul_le_pow (x := eta - 1) (by linarith : (-1 : ℝ) ≤ eta - 1) n
    have : 1 + (eta - 1) = eta := by ring
    rw [this] at h; exact h
  -- n ≤ 1/(η−1) + n = 1/(η−1)·(1 + n·(η−1)) ≤ 1/(η−1)·η^n
  calc (n : ℝ)
      ≤ 1 / (eta - 1) + (n : ℝ) := by linarith [div_pos one_pos hδ]
    _ = 1 / (eta - 1) * (1 + (n : ℝ) * (eta - 1)) := by
        field_simp [hδ.ne']; ring
    _ ≤ 1 / (eta - 1) * eta ^ n :=
        mul_le_mul_of_nonneg_left hbern (by positivity)

end Tribonacci
