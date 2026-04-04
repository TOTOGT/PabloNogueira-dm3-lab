# Assignment 3 — Scaling Hierarchies Simulation

**Type:** Pair or Group *(your teacher will tell you which applies to your section)*  
**Due:** [Teacher will announce]  
**Points:** [Teacher will announce]

---

## Learning Goals

- Understand what a "scaling hierarchy" means in dm³ terms
- Run a simulation that shows a pattern repeating at larger and larger scales
- Visualize the output and explain what you see

---

## Background Reading

1. Read the [Collatz Paper (Grossi 2026)](https://github.com/TOTOGT/DM3-lab/blob/main/Collatz_Paper_Grossi2026.pdf) — Introduction section only.
2. Look at the simulation files in [DM3-lab/simulations/](https://github.com/TOTOGT/DM3-lab/tree/main/simulations).
3. Review `scripts/starter.py` — the `ScalingHierarchy` class.

---

## Part 1 — Concept Questions

Answer as a group. One answer per group is fine.

**Q1.** What does it mean for a pattern to "repeat at a larger scale"?  
Give one example from nature and one from mathematics.

> **Nature example:**  
> **Math example:**

**Q2.** In the dm³ framework, what role does the **Kernel (K)** play in building a scaling hierarchy?

> **Your answer:**

**Q3.** What is the Collatz sequence? Write the first 10 steps starting from the number 6.

> **Collatz from 6:**

---

## Part 2 — Simulation Code

Open `scripts/starter.py`.  
Complete the `ScalingHierarchy` class:

- `collatz_sequence(n)` — return the full Collatz sequence starting from `n` until it reaches 1
- `hierarchy_depth(n)` — return how many steps the Collatz sequence takes (its length)
- `find_deepest(limit)` — among all integers from 1 to `limit`, return the one with the longest Collatz sequence

Run and confirm:
```bash
python scripts/starter.py
```

---

## Part 3 — Visualization

In a Jupyter notebook or Python script, plot:
1. The Collatz sequence for `n = 27` (a famously long one).
2. A bar chart: for each n from 1 to 50, show the depth of its Collatz sequence.

Save your plot(s) as `.png` files inside `assignments/A3/`.  
Name them: `A3_collatz_sequence.png` and `A3_collatz_depths.png`.

---

## Part 4 — Group Reflection

Write 3–5 sentences as a group answering:  
*How does the Collatz sequence illustrate the idea of a "regeneration loop" in dm³?*

> **Group reflection:**

---

## Group Contribution Note

List each member and what they contributed.

| Member | Contribution |
|---|---|
| | |
| | |
| | |

---

## Submission

```bash
git add .
git commit -m "A3 – scaling hierarchy simulation"
git push
```

---

*Assignment 3 · Book 3 · TOTOGT · 2026*
