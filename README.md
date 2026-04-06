# AXLE/Kakeya

**Finite-directions Kakeya formalization in Lean 4 / Mathlib**

## What this is

A honest, self-contained Lean 4 module formalizing a finite-directions
variant of the Kakeya problem in ℝ³. It does not claim to formalize the
full Wang–Zahl (2025) result. It proves what it can prove, labels what
remains open, and contains no unjustified `sorry`.

## File

`AXLE/Kakeya/Finite.lean`

## What is proved (no sorry)

| Theorem | Statement |
|---|---|
| `span_singleton_lt_top` | `span ℝ {u} ≠ ⊤` in E3 when `u ≠ 0` |
| `affine_line_ne_top` | The affine line through `x` in direction `u` is a proper subspace |
| `segment_measure_zero` | A unit segment in ℝ³ has 3D Lebesgue measure zero |
| `finite_segments_measure_zero` | A finite union of unit segments has measure zero |
| `thickened_segment_pos_measure` | An ε-thickened segment has positive measure for ε > 0 |
| `finite_kakeya_thickened_positive_measure` | If K contains an ε-tube in some direction, volume K > 0 |

## What is not proved (honest sorry)

| Theorem | Status |
|---|---|
| `thickened_segment_volume_lower_bound` | `volume(tube) ≥ π ε²`; true, proof requires Fubini over cross-sections; tracked |

## Key definitions

```lean
-- A unit segment from x in direction u
def unitSegment (u x : E3) : Set E3 :=
  { p | ∃ t ∈ Icc 0 1, p = x + t • u }

-- An ε-thickened tube around the unit segment
def thickenedSegment (u x : E3) (ε : ℝ) : Set E3 :=
  { p | ∃ t ∈ Icc 0 1, dist p (x + t • u) < ε }
```

## Why the naive theorem is false

The original formulation `containsSegments K dirs → volume K > 0` is **false**:
unit segments in ℝ³ have 3D Lebesgue measure zero, so a finite union of
them has measure zero regardless of K. The correct statement requires
ε-thickened tubes.

## Build verification

Before building, run these `#check` calls in a scratch file with the same
imports to verify Mathlib spelling:

```lean
#check @addHaar_affineSubspace
#check @AffineSubspace.direction_mk'
#check @AffineSubspace.direction_top
#check @finrank_span_singleton
#check @EuclideanSpace.finrank_eq
#check @Submodule.finrank_top
```

Then:

```bash
lake build AXLE.Kakeya.Finite
```

## What this is not

- This is not a formalization of Wang–Zahl (2025). That proof is 127 pages
  and has not been formalized in Mathlib.
- This is not part of a proof of the Collatz conjecture.
- The `sorry` in `thickened_segment_volume_lower_bound` is real and tracked.

## What comes next

1. Close `thickened_segment_volume_lower_bound` via Fubini / change of variables
2. Add a disjointness lemma for tubes in sufficiently separated directions
3. State a quantitative multi-tube lower bound: if dirs has n elements with
   pairwise angle ≥ δ, then `volume K ≥ n · c(δ) · ε²`

## Author

Pablo Nogueira Grossi, G6 LLC, 2026
