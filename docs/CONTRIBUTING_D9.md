# Contributing to D9 (Collatz dm³ Lane)

Welcome to the D9 contribution guide.  D9 is the deliverable targeting
conditional closure of the mean-contraction argument for the Collatz
conjecture framework within the dm³ project.

**The single remaining open item** is micro-obligation **(H_mix)** — see
`docs/c9_1_hypothesis.md` for the precise statement.

---

## 1. Quick-start: Running the Empirical Scripts

### Requirements

- Python ≥ 3.8 (no third-party packages needed)
- Any OS with a terminal

### Steps

```bash
# 1. Clone the repo and navigate to scripts/
git clone https://github.com/TOTOGT/PabloNogueira-dm3-lab.git
cd PabloNogueira-dm3-lab/scripts/

# 2. Run the sampling script with defaults
python collatz_c9_2_sampling.py

# 3. Check the output
cat out/summary_M4_N100000.csv
```

See `scripts/README.md` for full documentation of all options.

---

## 2. Analytic Contributions: Note Style

Analytic contributions (proofs, lemma drafts) should be submitted as:

- **LaTeX files** placed in `docs/` (e.g., `docs/c9_1_proof_draft.tex`)
- Use the minimal standalone preamble style of `docs/d9_v0.2.tex`:
  ```latex
  \documentclass[11pt,a4paper]{article}
  \usepackage{amsmath,amssymb,amsthm}
  \usepackage{hyperref}
  \usepackage{geometry}
  \geometry{margin=2.5cm}
  ```
- Define macros consistently with those in `docs/d9_v0.2.tex`.
- State clearly whether results are conditional on **(H_mix)** or other
  open hypotheses.
- **Do not claim C9.1 proved** unless you provide a complete, verifiable proof.

---

## 3. PR Checklist

Before opening a pull request for a D9 contribution, verify:

### For analytic/LaTeX contributions
- [ ] LaTeX compiles standalone (`pdflatex docs/your_note.tex`)
- [ ] All new theorems/lemmas clearly state whether they are conditional
- [ ] No overclaiming: if a result requires (H_mix), say so explicitly
- [ ] Notation consistent with `docs/d9_v0.2.tex`
- [ ] Cross-references to relevant issues (C9.1–C9.4) included

### For empirical/script contributions
- [ ] Script runs with no third-party dependencies (stdlib only)
- [ ] Script has an `--help` flag and argparse documentation
- [ ] Output CSVs conform to the schema in `scripts/README.md`
- [ ] No output CSVs committed to the repo (only `.gitkeep` in `scripts/out/`)
- [ ] `scripts/README.md` updated if new flags or outputs are added

### For all contributions
- [ ] PR description clearly states what is added/changed
- [ ] PR description explicitly notes: "conditional on (H_mix)" if applicable
- [ ] Linked to the relevant issue (C9.1, C9.2, C9.3, or C9.4)
- [ ] No large binary files added

---

## 4. Issue Map for D9

| Issue | Title | Status |
|-------|-------|--------|
| C9.1 | Prove residue-class decorrelation lemma (mod 2^M) | **OPEN** — core analytic task |
| C9.2 | Run refined Monte-Carlo checks (weighted by w(n)) | Open — empirical |
| C9.3 | Formalize averaging measure and window conventions | Open — analytic |
| C9.4 | Control boundary perturbations and small-n edge cases | Open — analytic |

The Reduction Lemma (`docs/d9_v0.2.tex`, Theorem 5.1) shows that **closing C9.1
suffices to close D9**.  All other components (C9.2–C9.4) provide supporting
evidence and formal hygiene.

---

## 5. Key Files

| File | Purpose |
|------|---------|
| `docs/d9_v0.2.tex` | LaTeX: full analytic framework, Reduction Lemma |
| `docs/c9_1_hypothesis.md` | Standalone (H_mix) statement and testing protocol |
| `scripts/collatz_c9_2_sampling.py` | Empirical sampling script (stdlib only) |
| `scripts/README.md` | Script usage guide |
| `docs/CONTRIBUTING_D9.md` | This file |

---

## 6. Contact and Discussion

- Open an issue in [TOTOGT/PabloNogueira-dm3-lab](https://github.com/TOTOGT/PabloNogueira-dm3-lab)
  and tag it with `D9`, `collatz`, and `community`.
- For analytic discussions, reference the issue number in your PR description.
- For large datasets or plots that shouldn't be committed, share a link
  (e.g., Zenodo, Dropbox) in the issue thread.

---

## 7. Related Contribution Guides

- General repo contributing guide: `CONTRIBUTING.md`
- Lean proof conventions: `lean/` directory
- Simulation conventions: `simulations/` directory
