# TOGT Operator Flow — C → K → F → U

This page provides two ready-to-embed figures of the TOGT operator chain for the
Collatz / dm³ setting.  Both show the **macro-step** $T = U \circ F \circ K \circ C$
and the data tokens passed between operators.

---

## Mermaid flowchart

> Renders in Markdown viewers that support Mermaid (GitHub Pages, many docs sites).

```mermaid
flowchart LR
  style C fill:#f8f3d4,stroke:#b8860b,stroke-width:1.5px
  style K fill:#e8f4f8,stroke:#0b6b8a,stroke-width:1.5px
  style F fill:#f4e8f8,stroke:#6b0b8a,stroke-width:1.5px
  style U fill:#e8f8ea,stroke:#0b8a3f,stroke-width:1.5px
  style Tbox fill:#ffffff,stroke:#333,stroke-width:1px,stroke-dasharray: 4 2

  C[<b>C Contact Injection</b><br/>Input: odd n<br/>Action: C(n)=3n+1]
  K[<b>K Kernel Valuation</b><br/>Input: even m<br/>Action: K(m)=(m/2^{v2(m)}, v2(m))]
  F[<b>F Flux Dissipation</b><br/>Input: (k,v)<br/>Action: h(k) - v·log 2]
  U[<b>U Update Unfold</b><br/>Input: (k, h')<br/>Action: return next odd kernel]
  Tbox[[<b>Macro-step</b><br/>T(n)=U∘F∘K∘C = (3n+1)/2^{v2(3n+1)}]]

  C -->|3n+1| K
  K -->|kernel k, valuation v| F
  F -->|updated height h'| U
  U -->|next odd kernel| Tbox
  Tbox -.->|iterate| C
```

**Data tokens**

| Edge | Token | Meaning |
|------|-------|---------|
| C → K | `3n+1` | Contact image (always even) |
| K → F | `(k, v)` | Odd kernel `k` and 2-adic valuation `v = v₂(3n+1)` |
| F → U | `h'` | Updated height: `h(k) − v·log 2` |
| U → T | next odd kernel | Input to the next iteration |

---

## Compact SVG

The same diagram is available as a standalone SVG asset at
[`../06_operator_flow.svg`](../06_operator_flow.svg).

Embed in HTML:

```html
<img src="06_operator_flow.svg" alt="TOGT operator flow C→K→F→U" width="900"/>
```

Include in LaTeX (after saving as PDF or converting with Inkscape):

```latex
\includegraphics[width=\linewidth]{06_operator_flow.pdf}
```

---

## Bridge 0 note

The figure makes explicit that **local dissipation control** (the `h'` token from F)
does **not** yet imply global orbit closure — that implication is Bridge 0, the key
open problem targeted by AXLE Target 5 (Lean 4 formal verification).
