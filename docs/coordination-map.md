# D9 Coordination Map

**Repository:** [TOTOGT/DM3-lab](https://github.com/TOTOGT/DM3-lab)  
**Obstruction scoreboard:** [docs/obstruction-scoreboard.md](obstruction-scoreboard.md)  
**Last updated:** 2026-04-03

This document maps each D9 micro-lemma issue to its assigned owner and describes
the coordination protocol for the two research tracks.

---

## Owner assignments

### Collatz track (C9.x)

| Issue | ID | Owner | Notes |
|-------|----|-------|-------|
| [#10](https://github.com/TOTOGT/DM3-lab/issues/10) | C9.1 | @GrokCollatz | Analytic core — decorrelation lemma |
| [#3](https://github.com/TOTOGT/DM3-lab/issues/3)   | C9.2 | @GrokCollatz | Numerical / Monte-Carlo evidence |
| [#13](https://github.com/TOTOGT/DM3-lab/issues/13) | C9.3 | @GrokCollatz | Measure conventions (prerequisite for C9.1) |
| [#12](https://github.com/TOTOGT/DM3-lab/issues/12) | C9.4 | @GrokCollatz | Boundary perturbation control |

### Navier–Stokes track (N9.x)

| Issue | ID | Owner | Notes |
|-------|----|-------|-------|
| [#9](https://github.com/TOTOGT/DM3-lab/issues/9) | N9.1 | @NS_Analyst | Near-diagonal decomposition |
| [#8](https://github.com/TOTOGT/DM3-lab/issues/8) | N9.2 | @NS_Analyst | Envelope extraction lemmas (H_FE) |
| [#7](https://github.com/TOTOGT/DM3-lab/issues/7) | N9.3 | @NS_Analyst | Leray projection / pressure commutators |
| [#6](https://github.com/TOTOGT/DM3-lab/issues/6) | N9.4 | @NS_Analyst | Far-range kernel decay; choose J |
| [#5](https://github.com/TOTOGT/DM3-lab/issues/5) | N9.5 | @NS_Analyst | Numerical checks of commutator magnitudes |

### Meta / coordination

| Issue | ID | Owner | Notes |
|-------|----|-------|-------|
| [#4](https://github.com/TOTOGT/DM3-lab/issues/4)   | DM3.1 | @TOTOGT | Register issues and assign owners |
| [#11](https://github.com/TOTOGT/DM3-lab/issues/11) | DM3.2 | @TOTOGT | Contribution guide for D9 tasks |

---

## Workflow

1. **Pick up an issue** — comment "Taking this" on the issue and self-assign.
2. **Open a branch** — name it `<id>/<short-slug>` (e.g., `c9.1/decorrelation-lemma`).
3. **Commit work** — LaTeX notes go in `docs/analysis_<track>/`, scripts in `scripts/`.
4. **Open a PR** — title: `[C9.1] <short description>`.  Link the issue with `Closes #N`.
5. **Checklist** — all items in the issue checklist must be ticked before merge.
6. **Update scoreboard** — change the status cell in
   [obstruction-scoreboard.md](obstruction-scoreboard.md) from 🔴 to 🟢.

---

## Communication channels

- GitHub Issues — primary forum for per-lemma discussion
- PR review threads — technical commentary on proofs / scripts
- [obstruction-scoreboard.md](obstruction-scoreboard.md) — single source of truth for status

---

## Quick links

| Resource | Link |
|----------|------|
| Obstruction scoreboard | [docs/obstruction-scoreboard.md](obstruction-scoreboard.md) |
| Contribution guide | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Collatz paper (Grossi 2026) | [Collatz_Paper_Grossi2026.pdf](../Collatz_Paper_Grossi2026.pdf) |
| All open issues | [github.com/TOTOGT/DM3-lab/issues](https://github.com/TOTOGT/DM3-lab/issues) |
