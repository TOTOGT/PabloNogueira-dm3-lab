"""
N9.5 — Numerical/experimental checks of near-diagonal commutator magnitudes
        on model flows.

Goal
----
Run small-scale simulations with localized initial data (and a caloric-extension
proxy) to estimate near-diagonal commutator sizes and test the envelope
hypothesis:

    ||[P_j, a · ∂_x] f||_2  ≲  C · 2^{-σ|j-k|}  · ||f||_2

where P_j is the j-th Littlewood–Paley projection onto dyadic frequency band
[2^j, 2^{j+1}), a is the model flow amplitude, and k is the reference scale.

Setup
-----
- 1-D periodic domain  [0, 2π),  N = 2^10 grid points.
- Model flows:
    (A) Localized bump  a(x) = exp(-α(x-π)²)   (localized initial data).
    (B) Caloric proxy   a(x,t) = exp(-α(x-π)² - β·t)  evaluated at t = 0.5
        (mimics caloric extension smoothing at an interior time slice).
- Littlewood–Paley projections  P_j  implemented as sharp spectral cutoffs
  in Fourier space:  P̂_j(ξ) = 1  if  2^j ≤ |ξ| < 2^{j+1}.
- Commutator: [P_j, a · ∂_x] f = P_j(a · ∂_x f) - a · ∂_x(P_j f).
- Reference function f chosen as a fixed localized smooth bump at scale k.
- Envelope prediction: C_env(j) = C₀ · 2^{-σ·max(0, j-k)}.

Outputs
-------
scripts/out/n9_5_commutator_magnitudes.json   — raw magnitude table
scripts/out/n9_5_commutator_plot.png          — envelope comparison plot

G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026
MIT License
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")          # headless backend for CI / non-GUI runs
import matplotlib.pyplot as plt
import numpy as np

# ── CONSTANTS ─────────────────────────────────────────────────────────────────

N          = 1024            # grid points  (must be a power of 2)
J_MIN      = 1               # smallest dyadic scale
J_MAX      = 9               # largest dyadic scale  (2^9 = 512 < N/2 = 512)
K_REF      = 4               # reference scale for the test function f
J_RANGE    = 6               # measure j ∈ [k, k+J]  →  J = 6
SIGMA_TRUE = 1.0             # theoretical decay rate (σ) for envelope fit
ALPHA      = 8.0             # bump width for localized initial data
BETA       = 0.5             # caloric decay rate
T_CALORIC  = 0.5             # time slice for caloric proxy

# ── GRID & MODEL FLOWS ────────────────────────────────────────────────────────

def make_grid(N: int = N) -> np.ndarray:
    """Uniform grid on [0, 2π)."""
    return np.linspace(0, 2 * np.pi, N, endpoint=False)


def model_flow_localized(x: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """
    Localized bump flow: a(x) = exp(-α(x-π)²).
    Models a localized initial datum.
    """
    return np.exp(-alpha * (x - np.pi) ** 2)


def model_flow_caloric(x: np.ndarray,
                       t: float = T_CALORIC,
                       alpha: float = ALPHA,
                       beta: float = BETA) -> np.ndarray:
    """
    Caloric extension proxy: a(x,t) = exp(-α(x-π)² - β·t).
    Evaluated at interior time t to mimic heat-kernel smoothing.
    """
    return np.exp(-alpha * (x - np.pi) ** 2 - beta * t)


def reference_function(x: np.ndarray, k: int = K_REF) -> np.ndarray:
    """
    Test function f localised at scale k:
      f(x) = sin(2^k · x) · envelope(x).
    """
    freq = 2 ** k
    envelope = np.exp(-2.0 * (x - np.pi) ** 2)
    return np.sin(freq * x) * envelope


# ── LITTLEWOOD–PALEY PROJECTIONS ──────────────────────────────────────────────

def lp_project(f: np.ndarray, j: int) -> np.ndarray:
    """
    Littlewood–Paley projection P_j onto dyadic band [2^j, 2^{j+1}).

    Uses the FFT; the sharp spectral cutoff is fine for comparison purposes
    (smooth cutoffs would give the same asymptotic decay rate).
    """
    F = np.fft.rfft(f)
    freqs = np.fft.rfftfreq(len(f), d=1.0 / len(f)).astype(int)  # integer freqs
    lo, hi = 2 ** j, 2 ** (j + 1)
    mask = (np.abs(freqs) >= lo) & (np.abs(freqs) < hi)
    F_proj = F * mask
    return np.fft.irfft(F_proj, n=len(f))


def deriv_spectral(f: np.ndarray) -> np.ndarray:
    """Spectral derivative ∂_x f on periodic grid via FFT."""
    N_loc = len(f)
    F = np.fft.rfft(f)
    freqs = np.fft.rfftfreq(N_loc, d=1.0 / N_loc)
    # ∂_x ↔ multiplication by iξ  (ξ in angular frequency = 2π · freq / L)
    # Here the grid is [0, 2π), so L = 2π and freq is the integer wavenumber.
    F_d = F * (1j * freqs)
    return np.fft.irfft(F_d, n=N_loc)


# ── COMMUTATOR ────────────────────────────────────────────────────────────────

def commutator_norm(a: np.ndarray, f: np.ndarray, j: int) -> float:
    """
    Compute  ||[P_j, a · ∂_x] f||_2  (L² norm per unit length).

      [P_j, a · ∂_x] f = P_j(a · ∂_x f) - a · ∂_x(P_j f)
    """
    dx_f   = deriv_spectral(f)
    Pj_f   = lp_project(f, j)
    dx_Pjf = deriv_spectral(Pj_f)

    term1  = lp_project(a * dx_f, j)
    term2  = a * dx_Pjf
    diff   = term1 - term2

    N_loc  = len(diff)
    L2     = math.sqrt(np.sum(diff ** 2) / N_loc)  # normalized L²
    return L2


# ── ENVELOPE PREDICTION ───────────────────────────────────────────────────────

def envelope_prediction(j: int,
                        k: int,
                        C0: float,
                        sigma: float = SIGMA_TRUE) -> float:
    """
    Exponential envelope:  C₀ · 2^{-σ · max(0, j-k)}.
    """
    return C0 * (2.0 ** (-sigma * max(0, j - k)))


# ── MAIN SIMULATION ───────────────────────────────────────────────────────────

def run_simulation(label: str,
                   a: np.ndarray,
                   f: np.ndarray,
                   k: int = K_REF,
                   J: int = J_RANGE) -> Dict:
    """
    Sweep j ∈ [k, k+J] and record ||[P_j, a·∂_x] f||_2.
    Returns a result dictionary.
    """
    j_values: List[int]   = list(range(k, min(k + J + 1, J_MAX + 1)))
    magnitudes: List[float] = []

    print(f"\n[N9.5] Flow: {label}")
    print(f"  j range: [{j_values[0]}, {j_values[-1]}]  (k={k}, J={J})")
    print(f"  {'j':>4}  {'||[Pj,a∂x]f||_2':>20}")

    for j in j_values:
        mag = commutator_norm(a, f, j)
        magnitudes.append(mag)
        print(f"  {j:>4}  {mag:>20.8e}")

    # Fit envelope constant C₀ to j=k value
    C0_fit = magnitudes[0] if magnitudes[0] > 0 else 1e-12
    envelope = [envelope_prediction(j, k, C0_fit) for j in j_values]

    # Check if magnitudes are within 2× the envelope (lenient test)
    within_envelope = [
        mag <= 2.0 * env + 1e-14
        for mag, env in zip(magnitudes, envelope)
    ]
    hypothesis_confirmed = all(within_envelope)

    print(f"  Envelope hypothesis (within 2×): "
          f"{'CONFIRMED ✓' if hypothesis_confirmed else 'VIOLATED ✗'}")

    return {
        "label":                label,
        "k_ref":                k,
        "J_range":              J,
        "j_values":             j_values,
        "commutator_magnitudes": [float(m) for m in magnitudes],
        "envelope_C0":          float(C0_fit),
        "envelope_sigma":       SIGMA_TRUE,
        "envelope_prediction":  [float(e) for e in envelope],
        "within_envelope":      within_envelope,
        "hypothesis_confirmed": hypothesis_confirmed,
    }


# ── PLOT ──────────────────────────────────────────────────────────────────────

def make_plot(results: List[Dict], output_path: Path) -> None:
    """Plot commutator magnitudes vs. envelope prediction for both flows."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)
    fig.patch.set_facecolor("#00040F")

    colors = {
        "Localized bump": "#0ABAB5",
        "Caloric proxy":  "#C9A84C",
    }
    marker = "o"

    for ax, result in zip(axes, results):
        ax.set_facecolor("#060A12")
        label   = result["label"]
        j_vals  = result["j_values"]
        mags    = result["commutator_magnitudes"]
        envs    = result["envelope_prediction"]
        color   = colors.get(label, "#FFFFFF")

        ax.semilogy(j_vals, mags, marker=marker, color=color,
                    linewidth=1.8, markersize=7, label="measured")
        ax.semilogy(j_vals, envs, "--", color="#F5F0E8",
                    linewidth=1.4, alpha=0.7,
                    label=f"envelope  C₀·2^{{-σ(j-k)}}, σ={SIGMA_TRUE}")
        ax.fill_between(j_vals,
                        [e * 0.1 for e in envs],
                        [e * 2.0 for e in envs],
                        color="#0ABAB5", alpha=0.08, label="±factor-of-2 band")

        k_ref = result["k_ref"]
        ax.axvline(k_ref, color="#888", linestyle=":", linewidth=1, alpha=0.6)
        ax.text(k_ref + 0.1, min(mags) * 1.5, f"k={k_ref}",
                color="#888", fontsize=8)

        confirmed = result["hypothesis_confirmed"]
        ax.set_title(
            f"{label}\nEnvelope hyp.: {'✓ confirmed' if confirmed else '✗ violated'}",
            color="#F5F0E8", fontsize=11
        )
        ax.set_xlabel("scale j", color="#F5F0E8")
        ax.set_ylabel("||[Pⱼ, a·∂ₓ]f||₂", color="#F5F0E8")
        ax.tick_params(colors="#F5F0E8")
        for sp in ax.spines.values():
            sp.set_edgecolor("#333")
        leg = ax.legend(fontsize=8, facecolor="#060A12",
                        labelcolor="#F5F0E8", edgecolor="#333")
        ax.set_xticks(j_vals)
        ax.xaxis.label.set_color("#F5F0E8")
        ax.yaxis.label.set_color("#F5F0E8")

    fig.suptitle(
        "N9.5 — Near-diagonal commutator magnitudes on model flows\n"
        "j ∈ [k, k+J],  P_j = Littlewood–Paley projection,  "
        "a = model flow amplitude\n"
        "G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026",
        color="#F5F0E8", fontsize=10, y=1.03
    )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, facecolor="#00040F", bbox_inches="tight")
    print(f"\n[N9.5] Plot saved: {output_path}")
    plt.close()


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("N9.5 — Near-diagonal commutator magnitude checks")
    print("G6 LLC · Pablo Nogueira Grossi · Newark NJ · 2026")
    print("=" * 60)

    x = make_grid(N)
    f = reference_function(x, k=K_REF)

    # Model flows
    a_loc     = model_flow_localized(x)
    a_caloric = model_flow_caloric(x)

    # Run simulations
    result_loc     = run_simulation("Localized bump",  a_loc,     f)
    result_caloric = run_simulation("Caloric proxy",   a_caloric, f)

    results = [result_loc, result_caloric]

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for r in results:
        status = "CONFIRMED ✓" if r["hypothesis_confirmed"] else "VIOLATED ✗"
        print(f"  {r['label']:20s}  envelope hypothesis: {status}")
        max_mag  = max(r["commutator_magnitudes"])
        min_mag  = min(r["commutator_magnitudes"])
        decay    = min_mag / max_mag if max_mag > 0 else float("nan")
        print(f"    max magnitude = {max_mag:.4e},  "
              f"min = {min_mag:.4e},  "
              f"decay ratio = {decay:.4f}")

    # Persist outputs
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "n9_5_commutator_magnitudes.json"
    payload = {
        "experiment":   "N9.5 near-diagonal commutator checks",
        "grid_N":       N,
        "k_ref":        K_REF,
        "J_range":      J_RANGE,
        "sigma_theory": SIGMA_TRUE,
        "results":      results,
    }
    with open(json_path, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\n[N9.5] Data saved : {json_path}")

    plot_path = out_dir / "n9_5_commutator_plot.png"
    make_plot(results, plot_path)

    print("\n[N9.5] Done. C → K → F → U → ∞")


if __name__ == "__main__":
    main()
