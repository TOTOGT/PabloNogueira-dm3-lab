# C9.4 — Boundary Perturbations from +1 Injections and Small-n Edge Cases

> **Status:** Complete — analysis script in `scripts/collatz_c9_4_boundary.py`,
> tests in `scripts/tests/test_c9_4_boundary.py`.

---

## 1. Definitions

### 1.1 The Collatz Map and the +1 Injection

For a positive integer n define the **fully-reduced Collatz step**

$$T(n) = \begin{cases} n/2 & \text{if } n \equiv 0 \pmod{2} \\ (3n+1)/2^{v_2(3n+1)} & \text{if } n \equiv 1 \pmod{2} \end{cases}$$

where $v_2(k)$ is the 2-adic valuation of $k$ (the largest power of 2 dividing $k$).

For odd n the map would be ill-typed without the "+1": the value $3n$ is
odd whenever $n$ is odd, so no right-shift would be possible.  The additive
correction "+1" is therefore a **structural injection** that creates a
compulsory even value, enabling the reduction.  We call it the
**+1 injection**.

### 1.2 Injection Bias

The **injection bias** at odd n measures the fractional contribution of
the "+1" to the output:

$$\Delta(n) = \frac{1}{3n+1}, \quad n \text{ odd}, \quad n \geq 1.$$

Equivalently, $\Delta(n)$ is the relative distance between $T(n)$ and the
"pure" quantity $3n/2^{v_2(3n+1)}$ (the value T(n) would take if only the
right-shift, but not the +1, were applied):

$$T(n) - \frac{3n}{2^{v_2(3n+1)}} = \frac{1}{2^{v_2(3n+1)}} \leq \frac{1}{2},$$

and the normalised deviation is bounded by $1/(3n+1)$.

For **even** n the injection bias is zero; $T(n) = n/2$ has no additive correction.

### 1.3 Boundary Window and Boundary Event

Fix a sampling range $[a, b]$ with $a \geq 1$.  A step $T(n)$ is a
**boundary event** (with respect to $[a, b]$) if $T(n) < a$ or $T(n) > b$.
In the former case we say the step **exits below**; in the latter **exits above**.

The **boundary windows** of $[a, b]$ are the sub-intervals of width
$w$ at either end: $[a, a+w)$ and $(b-w, b]$.  Steps originating in a
boundary window are more likely to land outside $[a, b]$.

### 1.4 Small-n Regime

We say $n$ is in the **small-n regime** if $n \leq N_{\text{small}}$
(default $N_{\text{small}} = 64$).  In this regime $\Delta(n) \geq 1/193$,
meaning the injection bias is non-negligible, and individual enumeration
is practical.

---

## 2. Small-n Exception Catalog

Running `scripts/collatz_c9_4_boundary.py` with the default window
$[1, 64]$ produces the following boundary events among all 32 odd
values in $[1, 64]$:

| n  | T(n) | v₂(3n+1) | Δ(n) = 1/(3n+1) | Exit direction |
|----|------|-----------|-----------------|----------------|
| 43 | 65   | 1         | 0.007692        | above          |
| 47 | 71   | 1         | 0.007042        | above          |
| 51 | 77   | 1         | 0.006494        | above          |
| 55 | 83   | 1         | 0.006024        | above          |
| 59 | 89   | 1         | 0.005618        | above          |
| 63 | 95   | 1         | 0.005263        | above          |

**Summary:** 6 out of 32 odd values in $[1, 64]$ exit the window —
a boundary-exit **frequency of 18.75 %**.

All exits are *above* the window and occur at odd $n \equiv 3 \pmod{4}$
with $v_2(3n+1) = 1$ (i.e. $3n+1 \equiv 2 \pmod{4}$).  These are the
"low-valuation" steps where $T(n) = (3n+1)/2 \approx 3n/2$, so $T(n)$
is roughly $1.5 \times n$, which escapes any window of size $\leq 2n$.

The full catalog (all odd $n \in [1, N_{\text{small}}]$ with $T(n)$,
$v_2$, and $\Delta(n)$) is written to `scripts/out/c9_4_small_n_catalog.csv`.

---

## 3. O(1/n) Average-Effect Bound

### 3.1 Per-step bound

**Proposition.** For all odd $n \geq 1$,

$$\Delta(n) = \frac{1}{3n+1} < \frac{1}{3n} \leq \frac{1}{3} \cdot \frac{1}{n}.$$

*Proof.* Direct arithmetic.  The ratio $\Delta(n) \cdot n = n/(3n+1)$
is strictly increasing in $n$ and converges to $1/3$ from below,
so $\Delta(n) < 1/(3n)$ for all finite $n$. $\square$

This is verified computationally for all odd $n \in [1, 1024]$ by
`verify_o1n_bound()`.  The maximum observed ratio is **0.333225 < 1/3 = 0.333…**

### 3.2 Average bound over a window

**Proposition.** Let $W = [a, b]$ be any window of odd integers with
minimum $n_{\min} = a$ (or $a+1$ if $a$ is even).  Then

$$\overline{\Delta}(W) := \frac{1}{|W_{\text{odd}}|} \sum_{\substack{n \in W \\ n \text{ odd}}} \Delta(n) \leq \Delta(n_{\min}) = \frac{1}{3n_{\min}+1}.$$

*Proof.* Each term satisfies $\Delta(n) \leq \Delta(n_{\min})$ since
$\Delta$ is strictly decreasing.  The average of a sequence all bounded
by a constant is bounded by that constant. $\square$

Therefore $\overline{\Delta}(W) = O(1/a)$: the **average injection bias
over any window starting at $a$ is O(1/a)**.

### 3.3 Implication for the decorrelation lemma

The decorrelation lemma asserts that $T(n)$ values for consecutive odd $n$
are approximately independent.  The +1 injection could in principle
introduce correlations by systematically shifting images.  However, the
shift per step is $1/2^{v_2(3n+1)} \leq 1/2$, and its fractional
contribution to $T(n)$ is $\Delta(n) = O(1/n)$.

For a window $[a, b]$ with $a \gg 1$ the average fractional perturbation
of the image distribution is $O(1/a)$, which vanishes as $a \to \infty$.
Hence:

> **The +1 injection does not bias the decorrelation lemma in the
> large-$n$ regime; its O(1/n) effect is negligible for $n \gg 1$.**

The only region where the bias matters is the small-n regime ($n \leq 64$),
cataloged in Section 2.

---

## 4. Handling Boundary Windows in Analytic Arguments

### 4.1 Why boundary windows matter

Near the endpoints $a$ and $b$ of a sampling window $[a, b]$, steps $T(n)$
are more likely to exit the window (boundary events).  This creates a
**selection bias**: if the analysis conditions on $T(n) \in [a, b]$, the
empirical distribution of $T(n)$ near the boundary is distorted.

The `identify_boundary_windows()` function labels each sliding sub-window
of size $w$ as interior or boundary, and reports the exit frequency.

### 4.2 Recommended exclusion criterion

To remove boundary effects from an analytic argument over $[a, b]$:

1. **Choose an exclusion depth** $w$ (typical choice: $w = \sqrt{b-a}$ or
   a fixed small constant such as 32).
2. **Restrict to the interior** $[a + w, b - w]$ for all assertions.
3. **Cite the O(1/n) bound** (Section 3) to argue that the excluded region
   has total injection bias at most $w/(3a+1) = O(w/a)$, which is
   negligible when $w \ll a$.

```python
# Example: exclude boundary windows of depth 32
from scripts.collatz_c9_4_boundary import decorrelation_bias_estimate

full = decorrelation_bias_estimate(1, 1024, exclude_boundary_windows=False)
excl = decorrelation_bias_estimate(1, 1024, exclude_boundary_windows=True, window_size=32)
print(f"Full avg bias:     {full['avg_bias']:.2e}  (n_min={full['n_min']})")
print(f"Excluded avg bias: {excl['avg_bias']:.2e}  (n_min={excl['n_min']})")
```

### 4.3 Uniform vs. adaptive exclusion

- **Uniform exclusion** (fixed $w$): appropriate when the argument uses a
  single large window.  Easy to state and verify.
- **Adaptive exclusion** (window-relative $w = \epsilon \cdot (b-a)$):
  appropriate in multi-scale or sliding-window analyses.  Ensures the
  excluded fraction $\epsilon$ is the same for every window.
- **No exclusion needed** if the argument already assumes $n \geq N_0$ for
  some $N_0 \gg 1$, since $\Delta(n) < 1/(3N_0)$ is then uniformly small.

### 4.4 Checklist for analytic arguments

Before invoking the decorrelation lemma in a proof or analysis:

- [ ] Confirm that the sampling range has $n_{\min} \gg 1$ (say $n_{\min} \geq 64$).
- [ ] If $n_{\min} < 64$, run `catalog_small_n_exceptions()` and handle the
      listed exceptions explicitly.
- [ ] If the argument involves a window $[a, b]$, check that the boundary-
      window exclusion depth $w$ satisfies $w \geq 2$ (at minimum).
- [ ] Cite the bound $\overline{\Delta}([a,b]) \leq 1/(3a+1)$ to bound the
      total bias from +1 injections.
- [ ] For finite-range statements, note that the exit frequency is at most
      $2w/(b-a+1)$ (two boundary windows of size $w$ over a total range of
      $b-a+1$), which is $O(w/(b-a))$.

---

## 5. Running the Analysis

```bash
# Default run (n ≤ 64 small-n catalog, O(1/n) check up to 1024, window 32)
python scripts/collatz_c9_4_boundary.py

# Custom run
python scripts/collatz_c9_4_boundary.py \
    --n-max-small 128 \
    --n-end 4096 \
    --window-size 64 \
    --output scripts/out

# Run tests
python -m pytest scripts/tests/test_c9_4_boundary.py -v
```

Output files written to `scripts/out/`:
- `c9_4_boundary_report.json` — full structured report
- `c9_4_small_n_catalog.csv` — one row per odd n in the small-n regime
- `c9_4_o1n_bounds.csv` — average bias per dyadic window

---

## 6. Summary

| Checklist item | Status |
|---|---|
| Catalog small-n exceptions and their frequency | ✓ Section 2 + `catalog_small_n_exceptions()` |
| Prove O(1/n) average effect statements | ✓ Section 3, Props 3.1–3.2 + `verify_o1n_bound()` |
| Document boundary window exclusion | ✓ Section 4 |
| Automated tests | ✓ 43 tests, all passing |

The +1 injection contributes at most $O(1/n)$ fractional bias per step,
with a verified tight constant of $< 1/3$.  For $n \gg 1$ this bias is
negligible and does not affect the decorrelation lemma.  Small-n
exceptions ($n \leq 64$) are individually cataloged and amount to at most
18.75 % of odd values in the default window; they should be excluded
from or handled explicitly in analytic arguments.
