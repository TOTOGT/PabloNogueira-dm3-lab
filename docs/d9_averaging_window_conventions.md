# D9 — Averaging Measure μ and Finite-Window Conventions

**G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026**  
MIT License

---

## Purpose

This document is the **canonical reference** for every D9 artifact in the
AXLE / DM3-lab project.  Any script, proof, or note that computes an
empirical frequency, density, or average over Collatz / TOGT trajectories
**must** cite this document and use one of the three window types defined
below.

---

## 1. Averaging Measure

Let $A \subseteq \mathbb{N}$ be an event (a measurable property of positive
integers, e.g. "n is odd", "T(n) < n/2").

For a finite, non-empty window $W \subset \mathbb{N}$ define the
**empirical averaging measure**

$$
\mu_W(A) \;:=\; \frac{\lvert \{n \in W : n \in A\} \rvert}{\lvert W \rvert}
$$

$\mu_W$ is a probability measure on $2^{\mathbb{N}}$ (restricted to $W$).

### 1.1 Normalization

$\mu_W(\mathbb{N}) = 1$ and $\mu_W(\emptyset) = 0$ for every non-empty $W$.
The normalization denominator is always $|W|$, **never** a logarithm or a
probability weight, unless the **logarithmic window** variant is explicitly
invoked (see §3.3).

### 1.2 Window function w(n)

The **window function**

$$
w : \mathbb{N} \;\longrightarrow\; \mathbb{N}
$$

assigns each integer $n$ to a window index $k = w(n)$.  The three canonical
choices are defined in §3.  All three satisfy:

- **Monotonicity** — $n < m \Rightarrow w(n) \le w(m)$.
- **Unboundedness** — $w(n) \to \infty$ as $n \to \infty$.
- **Finite preimage** — $w^{-1}(k)$ is a finite, non-empty set for every
  $k$ beyond the smallest window.

---

## 2. Asymptotic Notions

### 2.1 Natural (Cesàro) density

$$
d(A) \;:=\; \lim_{N \to \infty} \mu_{[1,N]}(A)
\;=\; \lim_{N \to \infty} \frac{|A \cap [1,N]|}{N}
$$

when the limit exists.  Upper and lower densities:

$$
\bar{d}(A) := \limsup_{N \to \infty} \mu_{[1,N]}(A), \qquad
\underline{d}(A) := \liminf_{N \to \infty} \mu_{[1,N]}(A).
$$

Always $0 \le \underline{d}(A) \le \bar{d}(A) \le 1$.

### 2.2 Logarithmic density

$$
\delta(A) \;:=\; \lim_{N \to \infty}
  \frac{1}{\ln N} \sum_{n=1}^{N} \frac{\mathbf{1}_{A}(n)}{n}
$$

when the limit exists.  If $d(A)$ exists then $\delta(A) = d(A)$ (Kronecker's
lemma), but $\delta(A)$ can exist even when $d(A)$ does not.

### 2.3 Dyadic density

$$
\delta_{\text{dyad}}(A)
  \;:=\; \lim_{k \to \infty} \mu_{[2^k,\, 2^{k+1})}(A)
  \;=\; \lim_{k \to \infty}
        \frac{|A \cap [2^k, 2^{k+1})|}{2^k}
$$

when the limit exists.

### 2.4 Relationship

$$
\underline{d}(A) \;\le\; \delta(A) \;\le\; \bar{d}(A)
$$

In particular, if the natural density exists it equals the logarithmic
density.  The dyadic density, when it exists, also equals the logarithmic
density (by summation by parts).

---

## 3. Canonical Window Types

### 3.1 Contiguous (arithmetic) windows

$$
W^{\text{arith}}_N \;:=\; \{1, 2, \ldots, N\}, \qquad |W^{\text{arith}}_N| = N.
$$

**Window function:** $w_{\text{arith}}(n) = n$ (trivially, each $n$ defines
the upper boundary of the window it generates).

**Use case:** direct Cesàro averages, Collatz stopping-time histograms over
$[1, N]$.

**Asymptotic rate:** $|W^{\text{arith}}_N| = N$, growing linearly.

**Limit convention:**
$$
\mu^{\text{arith}}(A) \;:=\; \lim_{N \to \infty} \mu_{W^{\text{arith}}_N}(A)
$$
Use $\limsup$ / $\liminf$ when the limit does not exist.

---

### 3.2 Dyadic (logarithmic-scale) windows

$$
W^{\text{dyad}}_k \;:=\; \{2^k, 2^k+1, \ldots, 2^{k+1}-1\},
\qquad |W^{\text{dyad}}_k| = 2^k, \quad k \ge 0.
$$

**Window function:** $w_{\text{dyad}}(n) = \lfloor \log_2 n \rfloor$.

**Use case:** scale-separated analysis; each window covers one order of
magnitude in base-2 arithmetic.  Preferred for studying events whose
frequency depends on the binary length of $n$ (e.g. parity patterns,
$v_2(3n+1)$ distributions).

**Asymptotic rate:** $|W^{\text{dyad}}_k| = 2^k$, growing exponentially.

**Limit convention:**
$$
\mu^{\text{dyad}}(A) \;:=\; \lim_{k \to \infty} \mu_{W^{\text{dyad}}_k}(A).
$$

---

### 3.3 Logarithmic (harmonic-weight) windows

This variant replaces the uniform count with harmonic weights and does **not**
partition $\mathbb{N}$; instead it accumulates a weighted sum up to $N$.

$$
\mu^{\log}_N(A)
  \;:=\; \frac{1}{H_N} \sum_{n=1}^{N} \frac{\mathbf{1}_{A}(n)}{n},
\qquad H_N := \sum_{n=1}^{N} \frac{1}{n} \approx \ln N.
$$

**Window function:** there is no hard partition; $w_{\log}(n) = n$ and the
"window" $[1, N]$ is the same as the arithmetic case, but **weights** are
$1/n$ rather than $1$.

**Use case:** logarithmic density estimates; Collatz trajectory lengths
weighted by the reciprocal of the starting value.

**Asymptotic rate:** $H_N \approx \ln N$, growing logarithmically.

**Limit convention:**
$$
\mu^{\log}(A) \;:=\; \lim_{N \to \infty} \mu^{\log}_N(A) = \delta(A).
$$

---

## 4. Summary Table

| Type | Window $W$ | Size $|W|$ | Window fn $w(n)$ | Limit |
|---|---|---|---|---|
| **Contiguous** | $[1, N]$ | $N$ | $n$ | $\lim_{N\to\infty}$ |
| **Dyadic** | $[2^k, 2^{k+1})$ | $2^k$ | $\lfloor\log_2 n\rfloor$ | $\lim_{k\to\infty}$ |
| **Logarithmic** | $[1, N]$, weight $1/n$ | $H_N\approx\ln N$ | $n$ | $\lim_{N\to\infty}$ |

---

## 5. Examples

### Example 1 — Odd integers ($A = \{n : n \text{ is odd}\}$)

**Contiguous:**
$\mu^{\text{arith}}_N(A) = \lceil N/2 \rceil / N \to 1/2$.

**Dyadic:**
$|A \cap [2^k, 2^{k+1})| = 2^{k-1}$ for $k \ge 1$, so
$\mu^{\text{dyad}}_k(A) = 2^{k-1}/2^k = 1/2$.

**Logarithmic:**
$\sum_{n=1}^{N} \mathbf{1}_{\text{odd}}(n)/n
  = 1 + 1/3 + 1/5 + \cdots \approx \tfrac{1}{2}\ln N$,
so $\mu^{\log}_N(A) \to 1/2$.

All three conventions agree: $d(A) = \delta(A) = \delta_{\text{dyad}}(A) = 1/2$.

---

### Example 2 — Powers of 2 ($A = \{1, 2, 4, 8, \ldots\}$)

**Contiguous:**
$|A \cap [1, N]| = \lfloor \log_2 N \rfloor + 1$, so
$\mu^{\text{arith}}_N(A) = O(\log N / N) \to 0$.  Natural density $d(A) = 0$.

**Dyadic:**
$|A \cap [2^k, 2^{k+1})| = 1$ for every $k \ge 0$, so
$\mu^{\text{dyad}}_k(A) = 1/2^k \to 0$.

**Logarithmic:**
$\sum_{n \in A,\ n \le N} 1/n = \sum_{j=0}^{\lfloor\log_2 N\rfloor} 2^{-j}
  < 2$, so $\mu^{\log}_N(A) \to 0$.  Logarithmic density $\delta(A) = 0$.

---

### Example 3 — Collatz event $A$: "$T(n) < n/2$" (strong decrease)

This is the event used in C9.2 conditional sampling.

- Under the **contiguous** convention with $W = [1, N]$, $\mu^{\text{arith}}_N(A)$
  counts the fraction of integers up to $N$ for which one Collatz step halves
  the value.  Empirical computation (C9.2) suggests $\mu^{\text{arith}}_N(A) \approx 1/4$.

- Under the **dyadic** convention, each scale $[2^k, 2^{k+1})$ is examined
  separately; the dyadic measure is stable across scales.

- Under the **logarithmic** convention, the contribution of large $n$ is
  down-weighted by $1/n$.

The C9.2 script (`scripts/collatz_c9_2_sampling.py`) and the C9.3 module
(`scripts/collatz_c9_3_averaging.py`) implement all three variants.

---

## 6. Canonical Convention for D9 Artifacts

Every D9 artifact (figure, table, CSV, JSON summary) **must** include:

1. **Window type** — one of `contiguous`, `dyadic`, or `logarithmic`.
2. **Window parameter** — the value of $N$ (contiguous / logarithmic) or $k$
   (dyadic) at which the computation was evaluated.
3. **Measured value** — $\mu_W(A)$ with at least four significant figures.
4. **Limit status** — whether the value is a realized limit, a limsup/liminf
   bound, or a finite approximation.
5. **Event definition** — an unambiguous specification of $A$ referencing
   either this document or a C9.x ticket.

Example D9 metadata block (JSON):

```json
{
  "d9_convention_version": "1.0",
  "event": "T(n) < n/2",
  "window_type": "dyadic",
  "window_parameter": 20,
  "window": "[1048576, 2097152)",
  "window_size": 1048576,
  "mu_W": 0.2500,
  "limit_status": "finite_approximation",
  "limsup": null,
  "liminf": null,
  "source": "docs/d9_averaging_window_conventions.md"
}
```

---

## 7. References

- C9.2 ticket and script: `scripts/collatz_c9_2_sampling.py`
- C9.3 implementation: `scripts/collatz_c9_3_averaging.py`
- NS lane notes: `docs/analysis_ns/README.md`
- Erdős–Turán conjecture on logarithmic densities (background)
- Tao, T. (2022). *Almost all Collatz orbits attain almost bounded values.*
  Forum of Mathematics Pi, 10, e12.

$$C \to K \to F \to U \to \infty$$
