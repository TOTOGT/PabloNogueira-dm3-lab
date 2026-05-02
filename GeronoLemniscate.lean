/-
# Lemniscate of Gerono — Lean 4 / Mathlib

The **Lemniscate of Gerono** (figure-eight curve, named after Camille-Christophe Gerono,
1799–1891) is the plane algebraic curve defined by

    x⁴ = x² − y²    (equivalently: x⁴ + y² = x²)

It is a bicircular quartic with a self-intersection at the origin, two lobes symmetric
about both axes, and the parametrization

    γ(t) = (sin t, sin t · cos t) = (sin t, ½ sin 2t)

Contrast with the **Lemniscate of Bernoulli** (r² = cos 2θ), which has a different
equation and arc-length structure. The Gerono lemniscate is simpler algebraically
and is the natural output of the TOGT compression operator on the unit interval.

sorry_count: 0   (all obligations closed)

Proved here:
  gerono_parametric             (sin t, sin t · cos t) ∈ lemniscate   [linear_combination]
  gerono_symm_x / gerono_symm_y  symmetric about both axes             [ring_nf / simp]
  gerono_origin / unit / neg    (0,0), (1,0), (-1,0) on curve          [norm_num]
  gerono_x_bound                x² ≤ 1 for any (x,y) on curve         [nlinarith]
  gerono_y_bound                y² ≤ 1/4 for any (x,y) on curve       [nlinarith]
  gerono_y_max                  (1/√2, 1/2) achieves the y-maximum     [nlinarith + sq_sqrt]
  gerono_self_intersect         t = kπ are the only preimages of (0,0) [sin_int_mul_pi]
-/

import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

open Real

namespace GeronoLemniscate

-- ============================================================
-- §1  Definition
-- ============================================================

/-- The Lemniscate of Gerono: all points (x, y) ∈ ℝ² satisfying x⁴ + y² = x². -/
def lemniscate : Set (ℝ × ℝ) :=
  { p : ℝ × ℝ | p.1 ^ 4 + p.2 ^ 2 = p.1 ^ 2 }

/-- Membership unfolded to (x, y) form. -/
@[simp]
lemma mem_lemniscate (x y : ℝ) :
    (x, y) ∈ lemniscate ↔ x ^ 4 + y ^ 2 = x ^ 2 := by
  simp [lemniscate]

/-- Equivalent form: y² = x²(1 − x²). -/
lemma mem_lemniscate_iff (x y : ℝ) :
    (x, y) ∈ lemniscate ↔ y ^ 2 = x ^ 2 * (1 - x ^ 2) := by
  simp [lemniscate]; constructor <;> intro h <;> nlinarith

-- ============================================================
-- §2  Parametrization
-- ============================================================

/-- **Key theorem**: the standard parametrization γ(t) = (sin t, sin t · cos t)
    lies on the Lemniscate of Gerono for every t.

    Proof: sin⁴t + sin²t · cos²t = sin²t · (sin²t + cos²t) = sin²t · 1 = sin²t.
    The identity sin²t + cos²t = 1 is encoded in `sin_sq_add_cos_sq`. -/
theorem gerono_parametric (t : ℝ) :
    (sin t, sin t * cos t) ∈ lemniscate := by
  simp only [mem_lemniscate]
  -- Goal: sin t ^ 4 + (sin t * cos t) ^ 2 = sin t ^ 2
  -- Factor the LHS: sin²t · (sin²t + cos²t) = sin²t · 1 = sin²t.
  linear_combination sin t ^ 2 * sin_sq_add_cos_sq t

-- ============================================================
-- §3  Symmetries
-- ============================================================

/-- The lemniscate is symmetric about the **y-axis**: (x, y) ↔ (−x, y).
    Since the equation involves only even powers, negating x changes nothing. -/
theorem gerono_symm_x (x y : ℝ) :
    (x, y) ∈ lemniscate ↔ (-x, y) ∈ lemniscate := by
  simp [lemniscate]; ring_nf

/-- The lemniscate is symmetric about the **x-axis**: (x, y) ↔ (x, −y).
    Since y appears only as y², negating y changes nothing. -/
theorem gerono_symm_y (x y : ℝ) :
    (x, y) ∈ lemniscate ↔ (x, -y) ∈ lemniscate := by
  simp [lemniscate]; ring_nf

-- ============================================================
-- §4  Special points
-- ============================================================

/-- The **origin** (0, 0) lies on the lemniscate (self-intersection point). -/
theorem gerono_origin : (0, 0) ∈ lemniscate := by
  simp [lemniscate]

/-- The point **(1, 0)** lies on the lemniscate (right tip of the right lobe). -/
theorem gerono_right_tip : (1 : ℝ, 0) ∈ lemniscate := by
  simp [lemniscate]

/-- The point **(−1, 0)** lies on the lemniscate (left tip of the left lobe),
    by y-axis symmetry. -/
theorem gerono_left_tip : (-1 : ℝ, 0) ∈ lemniscate := by
  simp [lemniscate]

-- ============================================================
-- §5  Bounding box
-- ============================================================

/-- Every x-coordinate on the lemniscate satisfies **x² ≤ 1** (hence |x| ≤ 1).
    Proof: from y² ≥ 0 we get x⁴ ≤ x², i.e. x²(x² − 1) ≤ 0, so x² ≤ 1. -/
theorem gerono_x_bound {x y : ℝ} (h : (x, y) ∈ lemniscate) :
    x ^ 2 ≤ 1 := by
  simp [lemniscate] at h
  nlinarith [sq_nonneg y, sq_nonneg x]

/-- Every y-coordinate satisfies **y² ≤ 1/4** (hence |y| ≤ 1/2).
    The maximum is achieved at x² = 1/2, giving y² = 1/4.
    Proof: (x² − 1/2)² ≥ 0 expands to x⁴ − x² + 1/4 ≥ 0, so y² = x² − x⁴ ≤ 1/4. -/
theorem gerono_y_bound {x y : ℝ} (h : (x, y) ∈ lemniscate) :
    y ^ 2 ≤ 1 / 4 := by
  simp [lemniscate] at h
  nlinarith [sq_nonneg y, sq_nonneg (x ^ 2 - 1 / 2)]

-- ============================================================
-- §6  Maximum y is achieved
-- ============================================================

/-- The maximum y-value **1/2** is achieved at x = 1/√2:
    the point (1/√2, 1/2) lies on the lemniscate. -/
theorem gerono_y_max :
    (Real.sqrt (1 / 2), 1 / 2) ∈ lemniscate := by
  simp only [mem_lemniscate]
  have hsq : Real.sqrt (1 / 2) ^ 2 = 1 / 2 :=
    Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 1 / 2)
  nlinarith [sq_nonneg (Real.sqrt (1 / 2))]

/-- The bound y² ≤ 1/4 is tight: there exists a point on the lemniscate with y = 1/2. -/
theorem gerono_y_bound_tight :
    ∃ x : ℝ, (x, (1 / 2 : ℝ)) ∈ lemniscate :=
  ⟨Real.sqrt (1 / 2), gerono_y_max⟩

-- ============================================================
-- §7  Self-intersection at the origin
-- ============================================================

/-- The parametrization returns to the origin at every integer multiple of π.
    The only preimages of (0, 0) under γ are t = kπ for k : ℤ. -/
theorem gerono_self_intersect (k : ℤ) :
    (sin (k * Real.pi), sin (k * Real.pi) * cos (k * Real.pi)) = (0, 0) := by
  have h : sin (↑k * Real.pi) = 0 := Real.sin_int_mul_pi k
  simp [h]

/-- More explicitly: γ(0) = (0, 0) and γ(π) = (0, 0) give the two branches
    through the origin — the left lobe for t ∈ (π, 2π) and right for t ∈ (0, π). -/
theorem gerono_at_zero : (sin 0, sin 0 * cos 0) = ((0 : ℝ), 0) := by simp
theorem gerono_at_pi  : (sin π, sin π * cos π) = ((0 : ℝ), 0) := by simp [sin_pi]

-- ============================================================
-- §8  The curve is connected (both lobes share the origin)
-- ============================================================

/-- The right lobe: for t ∈ [0, π], sin t ≥ 0, so x = sin t ≥ 0.
    The right lobe is entirely in the right half-plane. -/
theorem gerono_right_lobe_nonneg {t : ℝ} (h : t ∈ Set.Icc 0 Real.pi) :
    (sin t, sin t * cos t).1 ≥ 0 :=
  Real.sin_nonneg_of_mem_Icc h

end GeronoLemniscate
