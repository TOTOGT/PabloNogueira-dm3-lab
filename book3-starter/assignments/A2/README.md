# Assignment 2 — Operator Chains: C → K → F → U

**Type:** Individual or Pair *(your teacher will tell you which applies to your section)*  
**Due:** [Teacher will announce]  
**Points:** [Teacher will announce]

---

## Learning Goals

- Trace a full C → K → F → U operator chain through a concrete example
- Implement the chain in Python using the starter functions
- Compare two different inputs and observe how the chain behaves differently

---

## Background Reading

1. Re-read `assignments/dm3-glossary.md`.
2. Review the operator chain diagram from A1.
3. Look at `scripts/starter.py` — the `OperatorChain` class is the focus here.

---

## Part 1 — Trace by Hand

Below is a small dataset: `[8, 3, 8, 1, 5, 3, 2, 5, 5]`

Trace through the operator chain **step by step** in writing:

**Step 1 – Compress (C):** Remove duplicates and sort.  
> **Result after C:**

**Step 2 – Kernel (K):** Find the minimum value (the "seed").  
> **Result after K:**

**Step 3 – Flow (F):** Generate a sequence starting from the kernel by doubling each step, stopping before you exceed the maximum value in the compressed list.  
> **Result after F:**

**Step 4 – Unify (U):** Combine the Flow sequence and the Compressed list into one sorted list of unique values.  
> **Result after U (final output):**

---

## Part 2 — Code

Open `scripts/starter.py`.  
Complete the `OperatorChain` class methods:

- `compress(data)` — same as A1: unique + sorted
- `kernel(data)` — return the minimum value
- `flow(kernel_val, max_val)` — return `[kernel_val, kernel_val*2, kernel_val*4, ...]` while ≤ max_val
- `unify(compressed, flowed)` — merge and return sorted unique values

Then run:
```bash
python scripts/starter.py
```

---

## Part 3 — Comparison

Run the chain on a **second dataset of your choice** (at least 8 numbers, some duplicates).  
Write it here and show the output at each step:

> **My dataset:**  
> **After C:**  
> **After K:**  
> **After F:**  
> **After U:**

**Q:** How did the Flow step behave differently between the two datasets? Why?

> **Your answer:**

---

## Pair Work Note

If working in pairs: divide the work so each person writes at least one method and Part 3.  
Add a short note at the bottom of this file saying who did what.

> **Pair contribution note:**

---

## Submission

```bash
git add .
git commit -m "A2 – operator chain complete"
git push
```

---

*Assignment 2 · Book 3 · TOTOGT · 2026*
