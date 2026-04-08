import Mathlib.Data.Nat.Basic
import Mathlib.Init.Function

namespace Dm3CollatzToy

structure CollatzState where
  value : ℕ
  deriving DecidableEq

def attractor : CollatzState := ⟨0⟩
def isSimplyConnected (_X : CollatzState) : Prop := True

inductive Dm3Op
  | C | K | F | U
  deriving DecidableEq, Repr

open Dm3Op

def G {α} (C K F U : α → α) : α → α :=
  U ∘ F ∘ K ∘ C

def C_collatz (X : CollatzState) : CollatzState := ⟨X.value.pred⟩
def K_collatz (X : CollatzState) : CollatzState := X
def F_collatz (X : CollatzState) : CollatzState := X
def U_collatz (X : CollatzState) : CollatzState := X

def collatzStep_dm3 (X : CollatzState) : CollatzState := C_collatz X

theorem collatz_operatorDecomposition :
  ∀ X, collatzStep_dm3 X = (G C_collatz K_collatz F_collatz U_collatz) X := fun _ => rfl

lemma iterate_collatzStep_value (X : CollatzState) (n : ℕ) :
    (collatzStep_dm3^[n] X).value = X.value - n := by
  induction n generalizing X with
  | zero =>
    simp [Function.iterate_zero, Nat.sub_zero]
  | succ n ih =>
    rw [Function.iterate_succ', Function.comp]
    simp [collatzStep_dm3, C_collatz]
    rw [ih ⟨X.value.pred⟩]
    simp [Nat.pred_eq_sub_one, Nat.sub_succ]

lemma iterate_to_attractor (X : CollatzState) :
    collatzStep_dm3^[X.value] X = attractor := by
  apply CollatzState.ext
  simp [attractor, iterate_collatzStep_value]

theorem collatz_converges
    (X : CollatzState) (_hX : isSimplyConnected X) :
    ∃ n : ℕ, (collatzStep_dm3^[n] X).value = 0 :=
  ⟨X.value, by simpa [attractor] using congrArg CollatzState.value (iterate_to_attractor X)⟩

def M_collatz (X : CollatzState) : Prop := X.value = 0
def E_collatz (X : CollatzState) : Prop := X = attractor

theorem E_collatz_iff_attractor (X : CollatzState) :
    E_collatz X ↔ X = attractor := by rfl

theorem M_collatz_iff_E_collatz (X : CollatzState) :
    M_collatz X ↔ E_collatz X := by
  simp [M_collatz, E_collatz, attractor]

theorem entropy_monotone (X : CollatzState) (h : ¬ M_collatz X) :
    (collatzStep_dm3 X).value < X.value := by
  simp [collatzStep_dm3, C_collatz, M_collatz] at h ⊢
  rw [Nat.pred_eq_sub_one]
  exact Nat.sub_one_lt (Nat.pos_of_ne_zero h)

end Dm3CollatzToy
