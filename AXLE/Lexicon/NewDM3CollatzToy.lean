import Mathlib.Data.Nat.Basic
import Mathlib.Init.Function

/-!
# Toy Collatz / descent pillar (Kakeya-style, fully proved)

Note: `collatzStep_dm3` is `pred` (subtract 1), not the true Collatz map
(n/2 if even, 3n+1 if odd). This is a structural analogue only — a formally
verified dm³ pillar that matches the C/K/F/U grammar and closes the entropy
arc. A separate pillar for the true Collatz map requires a different
termination argument and is not yet formalized in dm³.

sorry_count: 0
-/

namespace Dm3CollatzToy

/-- A toy Collatz state: encoded by a single natural `value`. -/
structure CollatzState where
  value : ℕ
  deriving DecidableEq

/-- Canonical attractor: value 0. -/
def attractor : CollatzState := ⟨0⟩

/-- Simply-connected predicate (toy version: always true in this model). -/
def isSimplyConnected (_X : CollatzState) : Prop := True

/-- dm³ operator grammar. -/
inductive Dm3Op
  | C | K | F | U
  deriving DecidableEq, Repr

open Dm3Op

/-- TOGT composite operator: U ∘ F ∘ K ∘ C. -/
def G {α} (C K F U : α → α) : α → α := U ∘ F ∘ K ∘ C

/-- C_collatz: compression — decrease value by 1 (Nat.pred). -/
def C_collatz (X : CollatzState) : CollatzState := ⟨X.value.pred⟩

/-- K_collatz: curvature operator — identity in this toy model. -/
def K_collatz (X : CollatzState) : CollatzState := X

/-- F_collatz: folding operator — identity in this toy model. -/
def F_collatz (X : CollatzState) : CollatzState := X

/-- U_collatz: attractor operator — identity in this toy model. -/
def U_collatz (X : CollatzState) : CollatzState := X

/-- One step of toy "Collatz flow": just C_collatz (pred on value). -/
def collatzStep_dm3 (X : CollatzState) : CollatzState := C_collatz X

/-! ## Operator decomposition -/

/-- collatzStep_dm3 factors as G C K F U.
    K, F, U are identities so G reduces to C_collatz. -/
theorem collatz_operatorDecomposition :
    ∀ X, collatzStep_dm3 X = (G C_collatz K_collatz F_collatz U_collatz) X :=
  fun _ => rfl

/-! ## Core iteration lemma -/

/-- Iterating collatzStep_dm3 n times subtracts n from value (floored at 0). -/
lemma iterate_collatzStep_value (X : CollatzState) (n : ℕ) :
    (collatzStep_dm3^[n] X).value = X.value - n := by
  induction n generalizing X with
  | zero => simp [Function.iterate_zero, Nat.sub_zero]
  | succ n ih =>
    rw [Function.iterate_succ', Function.comp]
    simp only [collatzStep_dm3, C_collatz]
    rw [ih ⟨X.value.pred⟩]
    simp [Nat.pred_eq_sub_one, Nat.sub_succ]

/-! ## Convergence to attractor -/

/-- After exactly v steps, ⟨v⟩ reaches value 0, i.e. attractor. -/
lemma iterate_to_attractor (X : CollatzState) :
    collatzStep_dm3^[X.value] X = attractor := by
  apply CollatzState.ext
  simp only [attractor]
  rw [iterate_collatzStep_value]
  exact Nat.sub_self X.value

/-! ## Main convergence theorem -/

/-- **Toy Collatz convergence.**
    Every simply-connected CollatzState flows to `attractor`
    under iteration of `collatzStep_dm3`. -/
theorem collatz_converges
    (X : CollatzState) (_hX : isSimplyConnected X) :
    ∃ n : ℕ, collatzStep_dm3^[n] X = attractor :=
  ⟨X.value, iterate_to_attractor X⟩

/-! ## Entropy operators: M and E -/

/-- M_collatz: entropic boundary — true when the flow has reached closure.
    Equivalent to: value = 0. -/
def M_collatz (X : CollatzState) : Prop := X.value = 0

/-- E_collatz: stability detector — true when X has reached the attractor.
    Equivalent to: X = attractor. -/
def E_collatz (X : CollatzState) : Prop := X = attractor

/-- E_collatz is equivalent to value = 0 (the nontrivial content). -/
theorem E_collatz_iff_value_zero (X : CollatzState) :
    E_collatz X ↔ X.value = 0 := by
  simp [E_collatz, attractor, CollatzState.ext_iff]

/-- M_collatz and E_collatz coincide on this model. -/
theorem M_collatz_iff_E_collatz (X : CollatzState) :
    M_collatz X ↔ E_collatz X := by
  simp [M_collatz, E_collatz_iff_value_zero]

/-- Perelman-style monotonicity: value strictly decreases until M_collatz.
    Intuitively: ¬ M_collatz X ↔ X.value > 0. -/
theorem entropy_monotone (X : CollatzState) (h : ¬ M_collatz X) :
    (collatzStep_dm3 X).value < X.value := by
  simp only [collatzStep_dm3, C_collatz, M_collatz] at *
  rw [Nat.pred_eq_sub_one]
  omega

/-! ## Sanity checks -/

example : collatzStep_dm3^[5] ⟨5⟩ = attractor :=
  iterate_to_attractor ⟨5⟩

example : collatzStep_dm3^[0] ⟨0⟩ = attractor :=
  iterate_to_attractor ⟨0⟩

#check @collatz_converges
#check @entropy_monotone

end Dm3CollatzToy
