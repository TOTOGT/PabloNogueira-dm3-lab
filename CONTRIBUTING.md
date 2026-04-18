# Contributing to DM3-lab / AXLE

Thank you for your interest in contributing to the AXLE community! This guide covers both the GitHub file-upload workflow (including from mobile) and the specific conventions for **D9 micro-tasks** — numerical scripts, analytic notes, and reproducible pull requests.

---

## Adding Files Using the GitHub Mobile App (Phone)

You can upload files directly to this repository from your phone without needing a computer. Follow these steps:

### Step 1 — Install the GitHub App
1. Download the **GitHub** app from the [App Store (iOS)](https://apps.apple.com/app/github/id1477376905) or [Google Play (Android)](https://play.google.com/store/apps/details?id=com.github.android).
2. Sign in with your GitHub account (or create one for free at [github.com](https://github.com)).

### Step 2 — Open the DM3-lab Repository
1. Open the GitHub app on your phone.
2. Tap the **Search** (🔍) icon and search for `TOTOGT/DM3-lab`.
3. Tap the repository to open it.

### Step 3 — Fork the Repository (First-Time Contributors)
> If you are a collaborator with write access, skip to Step 4.

1. Tap the **Fork** button (top-right area of the repository page).
2. This creates your own personal copy of AXLE where you can freely make changes.

### Step 4 — Navigate to the Target Folder
1. In the repository (or your fork), tap **Code** to browse the file tree.
2. Navigate into the folder where you want to upload your file (e.g., `/docs`, `/simulations`, `/mappings`).

### Step 5 — Upload Your File
1. Tap the **+** (plus) or **Add file** button in the folder view.
2. Select **Upload file**.
3. Tap **Choose files** and pick the file(s) from your phone's storage, camera roll, or cloud drive.
4. Wait for the upload to complete.

### Step 6 — Commit the Change
1. Scroll down to the **Commit changes** section.
2. Add a short description of what you are uploading (e.g., `Add Lean proof for Target 6`).
3. Tap **Commit changes** (or **Propose changes** if working from a fork).

### Step 7 — Open a Pull Request (Fork Workflow)
> Skip this step if you committed directly to your own branch.

1. After committing, tap **Create Pull Request**.
2. Add a title and description explaining your contribution.
3. Tap **Submit** to send the PR for review.

---

## File Guidelines

| Folder | Accepted Content |
|--------|-----------------|
| `/lean/` | Lean 4 proof files (`.lean`) |
| `/simulations/` | Python scripts (`.py`) and output data |
| `/mappings/` | Domain mapping documents (`.md`, `.pdf`) |
| `/docs/` | References, excerpts, and technical notes |
| Root | Diagrams (`.svg`, `.png`) and top-level docs |

**Please avoid** uploading large binary files (videos, uncompressed audio) or files unrelated to TOGT / AXLE research.

---

## D9 Micro-Task Contributions

D9 tasks are small, self-contained work items (numerical experiments, analytic notes, Lean proofs) tied to the DM3 scoreboard. Anyone can self-assign a task by commenting on the relevant issue.

### Running Numerical Scripts

All scripts live in `/scripts/` and `/simulations/`. Use Python 3.10+.

**1. Install dependencies**

```bash
pip install numpy networkx matplotlib
```

**2. Run a script**

```bash
# Example — C9.2 conditional sampling
python scripts/collatz_c9_2_sampling.py \
  --N 1000 --M 50 \
  --window-type dyadic --start 1 --end 1024 \
  --sample-rate 0.1 --seed 42 \
  --output scripts/out/my_run
```

Output files (`.csv` and `_summary.json`) are written to `scripts/out/`. Create that directory first if it does not exist:

```bash
mkdir -p scripts/out
```

**3. Reproduce a prior result**

Always pass `--seed <integer>` to lock the random state. The seed used in any published result must be recorded in the PR description and the corresponding JSON summary file.

**4. Connectome simulations**

```bash
python simulations/connectome_loader.py   # synthetic fallback, no extra data needed
python simulations/simple_to_operator.py
```

Plots are saved to `outputs/` (created automatically).

---

### LaTeX / Formatting Guidelines for Analytic Notes

Place analytic write-ups in `/docs/` as `.md` files (preferred for version control) or `.pdf` (compiled separately).

**Markdown with inline math (`.md`)**

- Use standard GitHub-flavored Markdown.
- Inline math: `` $f(n) = \lfloor n/2 \rfloor$ ``
- Display math: fenced with `$$` on its own line.
- Label every key equation with a bold tag, e.g. `**(Eq. C9.2)**`.

**LaTeX source (`.tex`)**

- Keep one `.tex` file per note; compile with `pdflatex` or `lualatex`.
- Use `\label{eq:name}` and `\ref{eq:name}` — never bare equation numbers.
- Preferred packages: `amsmath`, `amssymb`, `hyperref`.
- Avoid custom macros that are not defined in the same file.
- Include a `\bibliographystyle{plain}` entry and a `.bib` file when citing external work.

**Naming convention**

```
docs/<topic>_<author-initials>_<YYYY-MM>.md
# e.g. docs/collatz_c9_sampling_PG_2026-04.md
```

---

## Questions?

Open an [Issue](https://github.com/TOTOGT/DM3-lab/issues) or reach out:

**Contact:** Pablo Grossi | PabloGrossi@hotmail.com | G6 LLC · Newark, NJ · 2026
