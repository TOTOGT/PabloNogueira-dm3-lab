# DM³ Research Programme: Document Structure
## Pablo Nogueira Grossi · G6 LLC · 2026

---

# OVERVIEW DOCUMENT

## Title
**A Generative Operator Framework for Open Problems in Mathematics:
The dm³ Research Programme**

## Abstract
We describe a research programme based on the dm³ operator cycle
(Compression–Curvature–Fold–Unfolding–Entropic boundary), which provides
a common structural language for analysing three open problems: the Collatz
conjecture, the Birch and Swinnerton-Dyer conjecture, and the Navier–Stokes
regularity problem.

For each problem, the programme (i) identifies a structural correspondence
between the known mathematics and the dm³ operator assignments, (ii) locates
the precise formal gap between the structural argument and a complete proof,
and (iii) proposes a specific formalisation target in Lean 4 (AXLE repository,
github.com/TOTOGT/AXLE).

No problem is claimed to be solved. The contribution of this programme is the
identification of a common proof architecture and the precise statement of what
remains to be done in each case.

**Three companion papers** develop each case in detail:
- Paper I: Collatz (discrete arithmetic instance)
- Paper II: BSD (algebraic–analytic instance)
- Paper III: Navier–Stokes (continuous fluid instance)

**What is established across all three:**
The dm³ operator assignments are not analogies. In each case, known mathematical
objects (Euler factors, functional equations, viscous dissipation) correspond to
specific operators. The structural correspondence is precise and independently
checkable.

**What is not established:**
The formal gap in each case — the step from structural correspondence to a
complete proof — remains open. The programme identifies this gap exactly.

MSC 2020: 37C70, 11B37, 35Q30, 11G40
Keywords: dm³ framework, Collatz conjecture, Birch–Swinnerton-Dyer,
Navier–Stokes, generative operators, formal verification, Lean 4

---

# PAPER I: COLLATZ

## Title
**The Collatz Conjecture as a Visibility Problem:
A dm³ Framework Perspective**

## Abstract
The Collatz conjecture — that every positive integer eventually reaches 1
under the iteration T(n) = n/2 (even) or 3n+1 (odd) — remains unproved.
This paper presents a structural analysis of the conjecture within the dm³
operator framework.

**What is established:**

(1) *Operator correspondence.* The Collatz map admits a precise dm³
decomposition: parity halving is the compression operator (C); the 3n+1
step is curvature (K); trajectory turning points are fold events (F);
descent into the basin of attraction is unfolding (U); the 1–2–4 cycle
is the entropic boundary (E). These assignments are not analogical — each
is a specific arithmetic operation.

(2) *Mean contraction.* The geometric mean multiplicative factor per
compression–curvature pair is 3/4 < 1. This is a proved fact, not a
conjecture. Tao (2019) establishes that almost all orbits attain almost
bounded values, formalising the dissipation argument for logarithmic density.

(3) *Uniqueness of the attractor.* The 1–2–4 cycle is the unique cycle
compatible with the dm³ closure condition under the 2–3 interaction.
This is argued structurally; it is not an independent proof of uniqueness.

(4) *Precise gap identification.* Three structural proof strategies are
presented (dissipation, curvature bounding, fold–stabilisation). Each
reduces the conjecture to a specific open sub-problem: the gap between
"almost all" and "all" in the dissipation argument; the absence of a
worst-case descent bound; and the absence of a formal categorical definition
of discrete dm³ membership.

**What is not established:**
The Collatz conjecture is not proved. Discrete dm³ membership of the
Collatz map is argued but not formally verified. Convergence does not
follow from the structural argument alone.

**Proposed formalisation target (AXLE Target 5):**
Lean 4 verification of discrete dm³ membership for the Collatz map,
followed by derivation of convergence from the closure theorems of the
extended category.

MSC 2020: 37C70, 11B37
Keywords: Collatz conjecture, dm³ framework, generative operators,
mean contraction, formal verification, Lean 4

---

# PAPER II: BSD

## Title
**The Birch and Swinnerton-Dyer Conjecture as Entropic Closure:
A dm³ Structural Reinterpretation**

## Abstract
The Birch and Swinnerton-Dyer conjecture — that the rank of an elliptic
curve E/ℚ equals the order of vanishing of L(E,s) at s=1 — is reinterpreted
within the dm³ operator framework.

**What is established:**

(1) *Operator correspondence.* The known mathematical objects of BSD admit
precise dm³ assignments: the local Euler product factors are compression (C);
the conductor is curvature (K); the functional equation is the fold operator
(F); the Modularity Theorem is unfolding (U); the BSD condition itself (analytic
rank equals algebraic rank) is the entropic boundary (E). Each assignment
corresponds to a specific mathematical object, not a metaphor.

(2) *Known results in operator language.* Kolyvagin's theorem (rank ≤ 1 cases),
the analytic continuation via Modularity, and the functional equation are
described within this language. No new mathematical content is added to these
results; the contribution is the structural organisation.

(3) *Resonant ladder structure.* The BSD heuristic — that partial products
∏_{p≤X} #E(𝔽_p)/p grow like C_E·(log X)^r — is identified as structurally
parallel to the Collatz resonant ladder 3^k·n/2^m. In both cases, local
compression and global curvature interact to produce a ladder whose exponent
records attractor depth.

(4) *Precise gap identification.* BSD is equivalent to the claim that every
elliptic curve is a complete dm³ system. The gap: no proof that E is always
reached for arbitrary rank; the categorical extension to higher-rank curves
is not formalised.

**What is not established:**
BSD is not proved. The dm³ reinterpretation does not add analytic content
beyond known results. The theorem on p.XX is stated in structural form only
and is not an independent mathematical result.

**Proposed formalisation target (AXLE Target 6):**
Lean 4 formalisation of the operator assignments for rank-0 and rank-1
curves (where BSD is known), as a test case for the general programme.

MSC 2020: 11G40, 14H52, 11G05
Keywords: Birch–Swinnerton-Dyer conjecture, elliptic curves, L-functions,
dm³ framework, generative operators, formal verification

---

# PAPER III: NAVIER–STOKES

## Title
**Navier–Stokes Regularity as Entropic Closure:
A dm³ Structural Reinterpretation**

## Abstract
The Navier–Stokes regularity problem — whether smooth initial data on ℝ³
always produces a globally smooth solution — is reinterpreted within the
dm³ operator framework as the continuous counterpart of the Collatz case.

**What is established:**

(1) *Operator correspondence.* The terms of the Navier–Stokes equations
admit dm³ assignments: viscous dissipation is compression (C); the
nonlinear advection term (u·∇)u is curvature (K); vortex stretching is
the fold operator (F); pressure projection is unfolding (U); the energy
equality / enstrophy bound is the entropic boundary (E).

(2) *Energy equality as closure condition.* The energy equality
‖u(t)‖² + 2ν∫₀ᵗ‖∇u‖² ds = ‖u₀‖²
is identified with the dm³ closure condition: dissipation (C) exactly
accounts for the energy introduced by curvature (K). This is a known
result (Leray 1934 for weak solutions); the dm³ language organises it.

(3) *Structural incompatibility of blow-up.* The argument that blow-up
is structurally incompatible with dm³ closure is presented: if the
entropic boundary E is reached, the energy cascade is bounded and no
singularity forms. This is argued structurally; it is not a proof.

(4) *Precise gap identification.* Three gaps parallel the Collatz gaps:
(a) no proof that E is always reached for arbitrary initial data;
(b) no proof that the 3-6-9 vortex structure is the unique attractor
in the continuous setting; (c) the quantitative enstrophy bound that
would turn the structural argument into a regularity theorem is missing.

**What is not established:**
NS regularity is not proved. The structural argument does not constitute
a blow-up prevention proof. No new analytic estimates are derived.

**Proposed formalisation target (AXLE Target 7):**
Lean 4 formalisation of the energy equality in dm³ language, as a
foundation for the regularity argument.

MSC 2020: 35Q30, 76D05, 35B65
Keywords: Navier–Stokes equations, regularity, energy equality,
dm³ framework, generative operators, formal verification

---

# WHAT TO DO WITH THE MONSTER PAPER CONTENT

The current Monster Paper contains significant non-mathematical content
(historical lineages, capoeira, tooth regeneration, mitochondrial DNA,
institutional theory) that does not belong in the three mathematics papers.
Two options:

**Option A:** Retain the Monster Paper as a separate philosophical/
programmatic document, clearly labelled as such, not as a mathematics paper.
Retitle it: "A Generative Architecture for Planetary Systems: Philosophical
and Programmatic Foundations of the dm³ Framework."

**Option B:** Archive the Monster Paper as a working document and let the
three split papers plus the overview document serve as the public-facing work.

The historical and cultural material is not a weakness if it is in the right
container. It becomes a weakness when it shares a document with theorems
about BSD and Navier–Stokes, because it signals to mathematical readers
that the claims are not being made in good faith.
