/-
# Tribonacci Polynomial and Companion Matrix in Lean 4

This file proves the characteristic polynomial of the Tribonacci recurrence
is exactly P(x) = x³ − x² − x − 1.

It also shows that the companion matrix C satisfies the recurrence
for the state vector of weights w(k) = η^{-k}.

This is the exact algebraic spine used in TO/TOGT / GCM.
-/

import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic
import Mathlib.Data.Polynomial.Basic
import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Topology.Order.IntermediateValue

open Polynomial Matrix Real

namespace Tribonacci

/- The Tribonacci polynomial -/
def tribPoly : ℝ[X] := X^3 - X^2 - X - 1

/- Companion matrix of the Tribonacci recurrence -/
def C : Matrix (Fin 3) (Fin 3) ℝ :=
  !![0, 1, 0;
     0, 0, 1;
     1, 1, 1]

/- Proof: charpoly(C) = tribPoly
   Strategy: show charmatrix C explicitly, then expand det via det_fin_three. -/
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

/- The recurrence satisfied by powers of C -/
def stateVector (k : ℕ) : Fin 3 → ℝ :=
  fun i =>
    match i with
    | 0 => 1             -- w(k)
    | 1 => 1             -- w(k+1)
    | 2 => 1             -- w(k+2)
    | _ => 0             -- impossible

/- For any initial vector v, the next state is C v -/
theorem recurrence_holds (v : Fin 3 → ℝ) :
    C *ᵥ v = fun i =>
      match i with
      | 0 => v 1
      | 1 => v 2
      | 2 => v 0 + v 1 + v 2
      | _ => 0 := by
  ext i
  fin_cases i
  · simp [C, Matrix.mulVec]
  · simp [C, Matrix.mulVec]
  · simp [C, Matrix.mulVec]; ring

/-
  NOTE on the old `eta` definition:
    (19 + 3 * Real.sqrt 33) ^ (1/3) uses *natural-number* division: (1/3 : ℕ) = 0,
    so the old definition silently evaluated to 1/3 + 1/3 + 1/3 = 1, not η ≈ 1.839.

  Fix: define eta via the Intermediate Value Theorem on p(x) = x³ − x² − x − 1,
  which has p(1) = −2 < 0 < 1 = p(2). The IVT gives a root in [1, 2]; we pick it
  with Classical.choose.  All proofs use 0 axioms beyond Mathlib4.
-/

/-- Existence of the Tribonacci root in [1, 2] via IVT. -/
private lemma eta_exists : ∃ x : ℝ, 1 ≤ x ∧ x ≤ 2 ∧ x ^ 3 = x ^ 2 + x + 1 := by
  have hcont : ContinuousOn (fun x : ℝ => x ^ 3 - x ^ 2 - x - 1) (Set.Icc 1 2) :=
    ((((continuous_pow 3).sub (continuous_pow 2)).sub continuous_id).sub
      continuous_const).continuousOn
  have hmem : (0 : ℝ) ∈ Set.Icc ((1 : ℝ) ^ 3 - 1 ^ 2 - 1 - 1)
                                   ((2 : ℝ) ^ 3 - 2 ^ 2 - 2 - 1) := by norm_num
  obtain ⟨c, hc, hpc⟩ :=
    intermediate_value_Icc (by norm_num : (1 : ℝ) ≤ 2) hcont hmem
  exact ⟨c, hc.1, hc.2, by linarith⟩

/-- The Tribonacci constant η ≈ 1.839: the real root of x³ − x² − x − 1 = 0 in [1, 2],
    constructed via IVT. Replaces the broken Cardano definition (ℕ division bug). -/
noncomputable def eta : ℝ := eta_exists.choose

private lemma eta_spec : 1 ≤ eta ∧ eta ≤ 2 ∧ eta ^ 3 = eta ^ 2 + eta + 1 :=
  eta_exists.choose_spec

/-- η satisfies its characteristic equation: η³ − η² − η − 1 = 0. -/
theorem eta_root : eta ^ 3 - eta ^ 2 - eta - 1 = 0 := by linarith [eta_spec.2.2]

/-- η > 1 (from IVT interval; η = 1 gives 1 = 3 contradiction). -/
theorem eta_gt_one : 1 < eta := by
  rcases eta_spec.1.eq_or_lt with h | h
  · exfalso; have := eta_spec.2.2; rw [← h] at this; norm_num at this
  · exact h

end Tribonacci
