# D9 Obstruction Scoreboard

**Repository:** [TOTOGT/DM3-lab](https://github.com/TOTOGT/DM3-lab)  
**Coordination map:** [docs/coordination-map.md](coordination-map.md)  
**Last updated:** 2026-04-03

This scoreboard tracks every micro-lemma that must be closed to complete the D9 gap
in both the Collatz (C) and Navier–Stokes (N) tracks.

---

## Collatz Track — C9 micro-lemmas

| ID | Title | Issue | Owner | Status |
|----|-------|-------|-------|--------|
| C9.1 | Residue-class decorrelation lemma for consecutive (1,1) events (mod 2^M) | [#10](https://github.com/TOTOGT/DM3-lab/issues/10) | @GrokCollatz | 🔴 Open |
| C9.2 | Monte-Carlo and finite-range checks for consecutive (1,1) probabilities (weighted by w(n)) | [#3](https://github.com/TOTOGT/DM3-lab/issues/3) | @GrokCollatz | 🔴 Open |
| C9.3 | Formalize averaging measure μ and finite-window conventions for D9 analysis | [#13](https://github.com/TOTOGT/DM3-lab/issues/13) | @GrokCollatz | 🔴 Open |
| C9.4 | Control boundary perturbations from +1 injections and small-n edge cases | [#12](https://github.com/TOTOGT/DM3-lab/issues/12) | @GrokCollatz | 🔴 Open |

---

## Navier–Stokes Track — N9 micro-lemmas

| ID | Title | Issue | Owner | Status |
|----|-------|-------|-------|--------|
| N9.1 | Decompose Π_{j,x₀,k}−Π_j into explicit near-diagonal commutator/paraproduct pieces | [#9](https://github.com/TOTOGT/DM3-lab/issues/9) | @NS_Analyst | 🔴 Open |
| N9.2 | Define canonical localized frequency envelopes and prove envelope extraction lemmas (H_FE) | [#8](https://github.com/TOTOGT/DM3-lab/issues/8) | @NS_Analyst | 🔴 Open |
| N9.3 | Control Leray projection and pressure commutators for near-diagonal terms | [#7](https://github.com/TOTOGT/DM3-lab/issues/7) | @NS_Analyst | 🔴 Open |
| N9.4 | Quantify far-range decay and choose J so far-range ≤ ε (kernel commutator lemma) | [#6](https://github.com/TOTOGT/DM3-lab/issues/6) | @NS_Analyst | 🔴 Open |
| N9.5 | Numerical/experimental checks of near-diagonal commutator magnitudes on model flows | [#5](https://github.com/TOTOGT/DM3-lab/issues/5) | @NS_Analyst | 🔴 Open |

---

## Coordination meta-issues

| ID | Title | Issue | Owner | Status |
|----|-------|-------|-------|--------|
| DM3.1 | Register micro-lemma issues and assign owners | [#4](https://github.com/TOTOGT/DM3-lab/issues/4) | @TOTOGT | 🟡 In progress |
| DM3.2 | Community contribution guide for D9 tasks | [#11](https://github.com/TOTOGT/DM3-lab/issues/11) | @TOTOGT | 🔴 Open |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🔴 Open | Issue exists; work not yet started |
| 🟡 In progress | Actively being worked on |
| 🟢 Done | Lemma resolved and merged |
| ⚪ Blocked | Waiting on a dependency |

---

## Dependency graph

```
D9 gap (Collatz track)
  └─ C9.3  (measure conventions)
       └─ C9.1  (decorrelation lemma — analytic core)
       └─ C9.2  (numerical evidence)
            └─ C9.4  (boundary/edge-case control)

D9 gap (NS track)
  └─ N9.2  (envelope extraction)
  └─ N9.4  (far-range kernel decay)
       └─ N9.1  (near-diagonal decomposition)
            └─ N9.3  (Leray projection / pressure commutators)
            └─ N9.5  (numerical checks)
```
