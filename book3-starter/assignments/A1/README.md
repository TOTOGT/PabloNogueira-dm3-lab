# Assignment 1 — Introduction to dm³ Operators

**Type:** Individual  
**Due:** [Teacher will announce]  
**Points:** [Teacher will announce]

---

## Learning Goals

By the end of this assignment you will be able to:
- Describe the four core dm³ operators in your own words (C, K, F, U)
- Recognize the operator chain pattern in a simple example
- Write a short Python function that models one operator

---

## Background Reading

Before you start:
1. Read `assignments/dm3-glossary.md` (in this repo).
2. Skim the [DM3-lab README](https://github.com/TOTOGT/DM3-lab) — focus on the "Core Focus" section.
3. Look at `scripts/starter.py` — you will extend it in Part 3.

---

## Part 1 — Written Response (no code needed)

Answer the following questions **in this file**, below each question.  
Write in complete sentences. 2–4 sentences per answer is enough.

**Q1.** In your own words, what does the **Compression (C)** operator do?  
*(Hint: think about what "compression" means in everyday life — like a zip file or a summary.)*

> **Your answer here:**

---

**Q2.** What does it mean for a system to have a **Kernel (K)**?  
*(Hint: think of a kernel as the "seed rule" — the simplest instruction that generates complexity.)*

> **Your answer here:**

---

**Q3.** Give one real-world example (from any field) of a **Flow (F)** pattern.  
*(Examples: water flowing downhill, information spreading through a social network, a disease spreading through a population.)*

> **Your answer here:**

---

**Q4.** Why is **Unification (U)** important at the end of the operator chain?

> **Your answer here:**

---

## Part 2 — Diagram (draw or describe)

Draw (by hand, then upload a photo) **or** write a text description of the operator chain:

```
Input → C → K → F → U → Output
```

Show what each arrow means with a short label.  
Place your diagram or description here:

> **Your diagram / description here:**

---

## Part 3 — Code (Python)

Open `scripts/starter.py`.  
Complete the function `apply_compression(data)` so that it:
1. Takes a list of numbers as input.
2. Returns only the **unique** values (removes duplicates).
3. Returns them **sorted** from smallest to largest.

Example:
```python
apply_compression([3, 1, 2, 1, 3, 5])
# Expected output: [1, 2, 3, 5]
```

Run the starter script to check your work:
```bash
python scripts/starter.py
```

---

## Submission

1. Fill in your answers above (Parts 1 and 2).
2. Edit `scripts/starter.py` (Part 3).
3. Commit and push:
   ```bash
   git add .
   git commit -m "A1 – completed"
   git push
   ```

---

*Assignment 1 · Book 3 · TOTOGT · 2026*
