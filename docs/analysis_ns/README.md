# NS lane analysis notes

This directory holds **NS lane** analysis drafts, sketches, and LaTeX notes.

Guidelines:
- Keep NS notes lane‑pure: do not reference Collatz deliverables or Collatz-specific filenames.
- Do not commit empirical CSV/JSON outputs. Attach them to issues (N9.2 #8 / N9.1 #9) instead.
- Do not assume baseline 1/2 unless explicitly defined; record baseline p0 in summaries.
- Use clear filenames: `n9_v0.1_topic.tex`, `n9_v0.1_operator_estimate.tex`, etc.

## Windowing and averaging conventions

All windowing/weighting choices for observables must follow the canonical
specification in **[docs/d9_averaging_window_conventions.md](../d9_averaging_window_conventions.md)**
(C9.3).  That document defines:

- The empirical averaging measure μ_W(A) and its normalization.
- Three canonical window types: *contiguous*, *dyadic*, *logarithmic*.
- The window function w(n) and its asymptotic properties.
- limsup / liminf conventions and the relationship between natural,
  logarithmic, and dyadic densities.
- A mandatory D9 metadata block for every artifact.

Current status: observable definition (A/B events, class space, scale
parameter, admissibility, windowing/weighting, baseline p0) is now
specified in `docs/d9_averaging_window_conventions.md` (closes C9.3).

