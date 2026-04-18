## D9 Task — PR Checklist

**Related issue / scoreboard task:** closes #<!-- issue number -->

**Scoreboard entry:** <!-- link to the DM3 scoreboard row, if applicable -->

---

### What this PR does

<!-- One-sentence summary of the contribution (proof, script, note, mapping …) -->

---

### Checklist

#### Reproducibility
- [ ] All random seeds are fixed and recorded (pass `--seed <n>` or equivalent).
- [ ] The exact command used to generate output is pasted below (or in the script header).
- [ ] Output files (`.csv`, `.json`, `.png`) committed to the correct folder (`scripts/out/`, `outputs/`), **or** too large and linked externally with a checksum.

#### Tests / verification
- [ ] Script runs end-to-end without error on a clean install (`pip install numpy networkx matplotlib`).
- [ ] Numerical results match the expected values stated in the issue (or deviations are explained).
- [ ] Lean proof compiles without `sorry` (if applicable).

#### Data
- [ ] No raw binary blobs > 10 MB committed; large files use a link + SHA-256 hash.
- [ ] Data sources are cited (FlyWire API URL, paper DOI, etc.).

#### Formatting (analytic notes)
- [ ] Equations use the agreed LaTeX/Markdown conventions from [CONTRIBUTING.md](https://github.com/TOTOGT/DM3-lab/blob/main/CONTRIBUTING.md).
- [ ] File is named `docs/<topic>_<initials>_<YYYY-MM>.md` (or `.pdf` with matching `.tex` source).

#### Scoreboard
- [ ] PR title starts with the task ID, e.g. `[D9-42] …`.
- [ ] Scoreboard link or issue reference included above.

---

### Reproduction command

```bash
# paste the exact command here, e.g.:
# python scripts/collatz_c9_2_sampling.py --N 1000 --M 50 \
#   --window-type dyadic --start 1 --end 1024 \
#   --sample-rate 0.1 --seed 42 --output scripts/out/my_run
```

### Notes for reviewers

<!-- Any context that helps the reviewer validate the result -->
