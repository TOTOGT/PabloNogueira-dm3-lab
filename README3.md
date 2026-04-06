# TOGT / DM³-Lab

Research repository for the DM³ framework and associated Lean 4 formalizations.

**Author:** Pablo Nogueira Grossi, G6 LLC, 2026

---

## Repository structure

```
.
├── book3-starter/          # Course assignments (A1–A4) and dm3 glossary
├── docs/                   # Papers, hypotheses, contributing guides
│   ├── d9_v0.2.tex         # Main paper (LaTeX)
│   ├── c9_1_hypothesis.md
│   └── index.md
├── issues/                 # Tracked open problems (12 issues)
├── lean/                   # Lean 4 source files
│   ├── AXLE.lean
│   ├── finite.lean         # Finite-directions Kakeya module
│   ├── gronwall_proof.lean
│   └── Main.lean
├── scripts/                # Python simulations and sampling
│   ├── collatz_c9_2_sampling.py
│   └── collatz_lyapunov_double.py
├── outputs/                # Generated data and figures
├── simulations/            # SVG diagrams
├── Finite.lean             # Root-level Kakeya file (see lean/ for canonical)
├── Collatz_Paper_Grossi2026.pdf
└── lakefile.toml
```

---

## Lean 4 modules

### `lean/finite.lean` / `Finite.lean`

Finite-directions Kakeya formalization in ℝ³.

**Proved (no sorry):**
- `segment_measure_zero` — unit segments have 3D Lebesgue measure zero
- `finite_segments_measure_zero` — finite unions of segments have measure zero
- `thickened_segment_pos_measure` — ε-tubes have positive measure for ε > 0
- `finite_kakeya_thickened_positive_measure` — K containing an ε-tube has positive volume

**Open (honest sorry):**
- `thickened_segment_volume_lower_bound` — `volume(tube) ≥ π ε²`; requires Fubini

### `lean/gronwall_proof.lean`

Gronwall inequality formalization. Status: see file.

### `lean/AXLE.lean`

Main AXLE module. Imports and coordinates submodules.

---

## Open issues (13)

| # | Title | Domain |
|---|---|---|
| 01 | Collatz Lean 4 | Mathematics |
| 02 | Coherence bridge Lean 4 | Mathematics |
| 03 | Structural hypothesis Lean 4 | Mathematics |
| 04 | Flywire real data | Simulation |
| 05 | Saturn parameter derivation | Simulation |
| 06 | String theory DM³ | Simulation |
| 07 | Martian colony simulation | Simulation |
| 08 | Hyper-Mahlo Lean 4 | Mathematics |
| 09 | ZFC axiomatization | Mathematics |
| 10 | CI/CD pipeline | Infrastructure |
| 11 | Plasma Lean 4 | Mathematics |
| 12 | CEFR worksheets | Education |

---

## Scripts

| File | Purpose |
|---|---|
| `collatz_c9_2_sampling.py` | Collatz trajectory sampling, outputs CSV/JSON |
| `collatz_lyapunov_double.py` | Lyapunov exponent estimation for Collatz |

Output data in `scripts/out/`.

---

## Build (Lean)

```bash
lake build
```

Key `#check` calls before building `finite.lean`:

```lean
#check @addHaar_affineSubspace
#check @AffineSubspace.direction_mk'
#check @AffineSubspace.direction_top
#check @finrank_span_singleton
#check @EuclideanSpace.finrank_eq
#check @Submodule.finrank_top
```

---

## Scope and honest status

- **Collatz** (issue-01): open; no proof of convergence exists in this repo
- **Finite.lean**: proves a finite-directions analogue using elementary
  measure theory; does not formalize Wang–Zahl (2025)
- **Hyper-Mahlo / ZFC** (issues-08, 09): open research directions
- **Simulations** (issues-04–07, 11): exploratory; not peer-reviewed results

---

## Contributing

See `CONTRIBUTING.md` and `docs/CONTRIBUTING_D9.md`.

## License

See `LICENSE`.
