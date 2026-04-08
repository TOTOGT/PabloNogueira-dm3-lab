import Mathlib.Data.Nat.Basic
import Mathlib.Init.Function

namespace Dm3PoincareToy

structure Toy3Complex where
  complexity : ℕ
  deriving DecidableEq

def sphereComplex : Toy3Complex := ⟨0⟩
def isSimplyConnected (_X : Toy3Complex) : Prop := True

def C_toy (X : Toy3Complex) : Toy3Complex := ⟨X.complexity.pred⟩
def K_toy (X : Toy3Complex) : Toy3Complex := X
def F_toy (X : Toy3Complex) : Toy3Complex := X
def U_toy (X : Toy3Complex) : Toy3Complex := X
def G {α} (C K F U : α → α) : α → α := U ∘ F ∘ K ∘ C
def toyRicciStep (X : Toy3Complex) : Toy3Complex := C_toy X

theorem toyPoincare_operatorDecomposition :
    ∀ X, toyRicciStep X = (G C_toy K_toy F_toy U_toy) X := fun _ => rfl

lemma iterate_toyRicciStep_complexity (X : Toy3Complex) (n : ℕ) :
    (toyRicciStep^[n] X).complexity = X.complexity - n := by
  induction n generalizing X with
  | zero => simp [Function.iterate_zero, Nat.sub_zero]
  | succ n ih =>
    rw [Function.iterate_succ', Function.comp]
    simp only [toyRicciStep, C_toy]
    rw [ih ⟨X.complexity.pred⟩]
    simp [Nat.pred_eq_sub_one, Nat.sub_succ]

lemma iterate_to_sphere (X : Toy3Complex) :
    toyRicciStep^[X.complexity] X = sphereComplex := by
  apply Toy3Complex.ext
  simp only [sphereComplex]
  rw [iterate_toyRicciStep_complexity]
  exact Nat.sub_self X.complexity

theorem toyPoincare_converges
    (X : Toy3Complex) (_hX : isSimplyConnected X) :
    ∃ n : ℕ, toyRicciStep^[n] X = sphereComplex :=
  ⟨X.complexity, iterate_to_sphere X⟩

-- M_toy : entropic boundary — true when the flow has nowhere left to go
def M_toy (X : Toy3Complex) : Prop := X.complexity = 0

-- E_toy : stability detector — true when X has reached the canonical attractor
def E_toy (X : Toy3Complex) : Prop := X = sphereComplex

-- E_toy detects exactly sphereComplex
theorem E_toy_iff_sphere (X : Toy3Complex) :
    E_toy X ↔ X = sphereComplex := by rfl

-- M_toy and E_toy coincide on this model
theorem M_toy_iff_E_toy (X : Toy3Complex) :
    M_toy X ↔ E_toy X := by
  simp [M_toy, E_toy, sphereComplex]
  exact Nat.eq_zero_iff

-- Perelman-style monotonicity: complexity strictly decreases until M_toy
theorem entropy_monotone (X : Toy3Complex) (h : ¬ M_toy X) :
    (toyRicciStep X).complexity < X.complexity := by
  simp [toyRicciStep, C_toy, M_toy] at *
  rw [Nat.pred_eq_sub_one]
  exact Nat.sub_one_lt_of_lt (Nat.pos_of_ne_zero h)

end Dm3PoincareToy
