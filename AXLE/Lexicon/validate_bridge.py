#!/usr/bin/env python3
"""
AXLE/Lexicon/validate_bridge.py
Version: 1.0
Author: G6 LLC / Pablo Nogueira Grossi — Newark NJ

Runs the coherence_bridge.yaml translation_engine against every domain row.
Reports per-row integrity and, for new entries, assigns a provisional claim level.

Usage:
    python validate_bridge.py coherence_bridge.yaml
    python validate_bridge.py coherence_bridge.yaml --new entry.yaml
    python validate_bridge.py coherence_bridge.yaml --quiet
"""

import sys
import argparse
import textwrap
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not found. Run: pip install pyyaml")

# ── Constants ────────────────────────────────────────────────────────────────

TOGT_SLOTS = ["togt_C", "togt_K", "togt_F", "togt_U", "togt_E"]
PARAM_KEYS  = ["mu_max", "omega", "beta"]
VALID_CLAIM_LEVELS = {"empirical", "analogical", "formally_stated", "formally_verified"}

ANSI = {
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "bold":   "\033[1m",
    "reset":  "\033[0m",
}

def color(text: str, *codes: str) -> str:
    """Apply ANSI color codes (skipped if not a TTY)."""
    if not sys.stdout.isatty():
        return text
    prefix = "".join(ANSI[c] for c in codes)
    return f"{prefix}{text}{ANSI['reset']}"

# ── Claim level rules ────────────────────────────────────────────────────────

def expected_claim_level(answered_slots: int, has_calibrated_params: bool) -> str:
    """
    Derive claim level from five-question count and parameter calibration.
    This mirrors claim_level_rules in the YAML.
    """
    if answered_slots == 5 and has_calibrated_params:
        return "empirical"
    if 3 <= answered_slots <= 4:
        return "analogical"
    if answered_slots < 3:
        return "metaphorical (not listed)"
    # 5 answered but no calibrated params → empirical candidate, flag it
    return "empirical (params needed)"

# ── Row validation ───────────────────────────────────────────────────────────

class RowReport:
    def __init__(self, row_id: str):
        self.row_id   = row_id
        self.errors   : list[str] = []
        self.warnings : list[str] = []
        self.info     : list[str] = []
        self.passed   = True

    def error(self, msg: str):
        self.errors.append(msg)
        self.passed = False

    def warn(self, msg: str):
        self.warnings.append(msg)

    def note(self, msg: str):
        self.info.append(msg)


def count_answered_slots(row: dict) -> tuple[int, list[str]]:
    """
    Count how many TOGT slots (C,K,F,U,E) are filled with substantive text.
    Note: a filled slot does not distinguish "answered from domain math" vs
    "answered by TOGT analogy" — that distinction requires human judgment and
    is encoded in the claim_level declaration.  The validator uses slot counts
    only as a lower-bound sanity check (all slots must be filled for empirical).
    Returns (count, list_of_answered_slot_names).
    """
    PLACEHOLDER_FRAGMENTS = [
        "tbd", "not yet", "not applicable", "n/a", "placeholder"
    ]
    answered = []
    for slot in TOGT_SLOTS:
        val = row.get(slot)
        if val is None:
            continue
        val_lower = str(val).strip().lower()
        if not val_lower:
            continue
        if any(p in val_lower for p in PLACEHOLDER_FRAGMENTS):
            continue
        answered.append(slot)
    return len(answered), answered


def calibration_status(row: dict) -> tuple[bool, bool, str]:
    """
    Returns (fully_calibrated, geometrically_calibrated, description).
    fully_calibrated     : mu_max, omega, beta all non-null AND parameter_status='calibrated'
    geometrically_calibrated : g_threshold non-null from domain observation (not TOGT ID)
    """
    params       = row.get("parameters", {}) or {}
    param_status = str(row.get("parameter_status", "")).strip().lower()
    g            = row.get("g_threshold")
    g_src        = str(row.get("g_threshold_source", "")).lower()

    full_dyn     = (param_status == "calibrated" and
                    all(params.get(k) is not None for k in PARAM_KEYS))
    g_is_domain  = (g is not None and
                    "togt identification" not in g_src and
                    "togt" not in g_src.replace("-", "").lower())

    if full_dyn:
        desc = "fully calibrated (mu_max, omega, beta + g_threshold)"
    elif g_is_domain:
        desc = "geometrically calibrated (g_threshold from domain; dynamical params null)"
    else:
        desc = "uncalibrated"

    return full_dyn, g_is_domain, desc


def validate_row(row: dict) -> RowReport:
    row_id = row.get("id", "<unnamed>")
    rep    = RowReport(row_id)
    claim  = row.get("claim_level", "")

    # ── 1. Claim level must be valid ────────────────────────────────────────
    if claim not in VALID_CLAIM_LEVELS:
        rep.error(f"claim_level '{claim}' is not one of {sorted(VALID_CLAIM_LEVELS)}")

    # ── 2. All five TOGT slots must be filled for empirical rows ─────────────
    n_answered, answered_slots = count_answered_slots(row)
    missing_slots = [s for s in TOGT_SLOTS if s not in answered_slots]
    if missing_slots:
        if claim == "empirical":
            rep.error(f"empirical row missing TOGT slots: {missing_slots}")
        else:
            rep.warn(f"TOGT slots not filled: {missing_slots}")
    rep.note(f"TOGT slots filled: {n_answered}/5")

    # ── 3. Calibration status ────────────────────────────────────────────────
    full_cal, geo_cal, cal_desc = calibration_status(row)
    rep.note(f"Parameters: {cal_desc}")
    rep.note(f"Declared claim level: {claim}")

    # Empirical: requires all 5 slots + at least geometric calibration.
    # Full dynamical calibration (mu_max, omega, beta) is preferred; geometric
    # calibration (g_threshold from domain) is accepted with a warning.
    if claim == "empirical":
        if not (full_cal or geo_cal):
            rep.error(
                "empirical row has no calibrated parameters. "
                "Either calibrate (mu_max, omega, beta) via domain fits, "
                "or derive g_threshold from domain observation and document it."
            )
        elif geo_cal and not full_cal:
            params = row.get("parameters", {}) or {}
            null_params = [k for k in PARAM_KEYS if params.get(k) is None]
            rep.warn(
                f"empirical row uses geometric calibration only (g_threshold from domain). "
                f"Dynamical parameters {null_params} are null. "
                "Consider fitting (mu_max, omega, beta) when domain data permit."
            )

    # Analogical: should NOT have fully calibrated dynamical params
    # (that would indicate empirical status).
    if claim == "analogical" and full_cal:
        rep.warn(
            "analogical row has fully calibrated (mu_max, omega, beta). "
            "If those values come from domain measurement, consider upgrading to 'empirical'."
        )
    if claim == "analogical" and n_answered < 3:
        rep.error(
            f"analogical requires ≥3 filled TOGT slots; only {n_answered} found."
        )

    # ── 4. Parameter internal consistency ────────────────────────────────────
    params       = row.get("parameters", {}) or {}
    param_status = str(row.get("parameter_status", "")).strip().lower()
    if param_status == "calibrated":
        null_params = [k for k in PARAM_KEYS if params.get(k) is None]
        if null_params:
            rep.error(
                f"parameter_status is 'calibrated' but {null_params} are null. "
                "Either fill the values or set a descriptive parameter_status."
            )
    if claim in ("analogical", "formally_stated", "formally_verified"):
        non_null_params = [k for k in PARAM_KEYS if params.get(k) is not None]
        if non_null_params and param_status != "calibrated":
            rep.warn(
                f"Non-null parameter values {non_null_params} present for a "
                f"'{claim}' row but parameter_status is not 'calibrated'. "
                "Add parameter_source or set parameter_status: calibrated."
            )

    # ── 5. g_threshold rules ─────────────────────────────────────────────────
    g = row.get("g_threshold")
    g_src = str(row.get("g_threshold_source", "")).lower()

    if claim in ("formally_stated", "formally_verified") and g is not None:
        rep.error(
            f"g_threshold={g} is present on a '{claim}' row. "
            "Pure mathematical claims have no stability threshold."
        )

    # Asymptotic / one-shot rows should have null g_threshold
    asymptotic_markers = ["asymptotic", "limit", "g → ∞", "g→∞", "one-shot", "binary"]
    is_asymptotic = any(m in g_src for m in asymptotic_markers)
    if is_asymptotic and g is not None:
        rep.error(
            f"g_threshold={g} present but g_threshold_source describes an "
            "asymptotic/one-shot result. Set g_threshold: null."
        )

    # g_threshold present on analogical should be flagged as TOGT identification
    if claim == "analogical" and g is not None:
        if "togt identification" not in g_src and "togt" not in g_src.replace("-","").lower():
            rep.warn(
                f"g_threshold={g} on analogical row — "
                "g_threshold_source should note this is a TOGT identification, "
                "not a domain-derived result."
            )

    # ── 6. Required fields ───────────────────────────────────────────────────
    for req in ("id", "name", "claim_level", "source"):
        if not row.get(req):
            rep.error(f"Required field '{req}' is missing or empty.")

    # ── 7. Lean4 fields for formally_stated / formally_verified ─────────────
    if claim in ("formally_stated", "formally_verified"):
        for lf in ("lean4_theorem", "lean4_sorry_label"):
            if not row.get(lf):
                rep.warn(f"'{claim}' row should have field '{lf}'.")
        sorry_count = row.get("lean4_sorry_count")
        if claim == "formally_verified" and sorry_count != 0:
            rep.error(
                "formally_verified requires lean4_sorry_count: 0. "
                f"Found: {sorry_count}"
            )
        if claim == "formally_stated" and sorry_count == 0:
            rep.error(
                "lean4_sorry_count is 0 but claim_level is 'formally_stated'. "
                "If all sorrys are closed, upgrade to 'formally_verified'."
            )

    return rep


# ── New-entry provisional scoring ────────────────────────────────────────────

def score_new_entry(entry: dict) -> None:
    """
    Interactive (or file-based) provisional claim level assignment for a new
    domain entry.  Prints the five-question answers and the derived level.
    """
    print(color("\n── New Entry Provisional Assessment ──", "cyan", "bold"))
    name = entry.get("name", entry.get("id", "<unnamed>"))
    print(f"  Domain: {name}\n")

    n_answered, answered = count_answered_slots(entry)
    full_cal, geo_cal, cal_desc = calibration_status(entry)
    derived = expected_claim_level(n_answered, full_cal or geo_cal)
    declared = entry.get("claim_level", "(not set)")

    questions = {
        "togt_C": "C — Compression",
        "togt_K": "K — Curvature",
        "togt_F": "F — Fold / transition",
        "togt_U": "U — Attractor / fixed point",
        "togt_E": "E — Stability criterion",
    }
    for slot, label in questions.items():
        val = entry.get(slot)
        mark = color("✓", "green") if slot in answered else color("✗", "red")
        answer = str(val).strip() if val else color("(not provided)", "yellow")
        print(f"  {mark} {label}:")
        if val:
            wrapped = textwrap.fill(answer, width=70, initial_indent="      ",
                                    subsequent_indent="      ")
            print(wrapped)
        else:
            print(f"      {answer}")

    print(f"\n  Slots filled   : {n_answered}/5")
    print(f"  Parameters     : {cal_desc}")
    print(f"  Declared claim level : {color(declared, 'bold')}")
    print(f"  Derived claim level  : {color(derived, 'bold')}")

    if declared != derived and declared != "(not set)":
        print(color(f"\n  ⚠ Mismatch — review claim_level declaration.", "yellow"))
    elif derived == "metaphorical (not listed)":
        print(color("\n  ✗ Too few TOGT slots answered for inclusion in the bridge.", "red"))
    else:
        print(color(f"\n  ✓ Provisional level: {derived}", "green"))


# ── Full lexicon validation ───────────────────────────────────────────────────

def validate_lexicon(data: dict, quiet: bool = False) -> bool:
    """
    Validate all rows in the lexicon.
    Returns True if all rows pass (no errors).
    """
    domains = data.get("domains", [])
    if not domains:
        print(color("No domains found in lexicon.", "red"))
        return False

    # Check formally_verified_rows
    fv_rows = data.get("formally_verified_rows", [])
    for fv in fv_rows:
        fv_id = fv.get("id", "<unnamed>")
        if fv.get("lean4_sorry_count", -1) != 0:
            print(color(
                f"ERROR: formally_verified_rows entry '{fv_id}' has non-zero sorry count.",
                "red"
            ))

    all_passed = True
    reports    = []

    for row in domains:
        rep = validate_row(row)
        reports.append(rep)
        if not rep.passed:
            all_passed = False

    # ── Print report ─────────────────────────────────────────────────────────
    width = 60
    print(color("\n" + "═" * width, "bold"))
    print(color("  AXLE coherence_bridge integrity report", "bold"))
    print(color("═" * width, "bold"))

    for rep in reports:
        status = color("PASS", "green") if rep.passed else color("FAIL", "red")
        print(f"\n  [{status}] {color(rep.row_id, 'bold')}")

        if not quiet:
            for note in rep.info:
                print(color(f"         ℹ  {note}", "cyan"))
        for warn in rep.warnings:
            print(color(f"         ⚠  {warn}", "yellow"))
        for err in rep.errors:
            print(color(f"         ✗  {err}", "red"))

    # ── Summary ───────────────────────────────────────────────────────────────
    n_total  = len(reports)
    n_passed = sum(1 for r in reports if r.passed)
    n_failed = n_total - n_passed
    n_warns  = sum(len(r.warnings) for r in reports)

    print(color("\n" + "─" * width, "bold"))
    print(f"  Rows: {n_total}  |  "
          f"{color(f'Passed: {n_passed}', 'green')}  |  "
          f"{color(f'Failed: {n_failed}', 'red') if n_failed else 'Failed: 0'}  |  "
          f"{color(f'Warnings: {n_warns}', 'yellow') if n_warns else 'Warnings: 0'}")

    fv_count = len(fv_rows)
    print(f"  formally_verified rows: {fv_count}  "
          f"{'(correct — no zero-sorry proofs yet)' if fv_count == 0 else ''}")
    print(color("─" * width + "\n", "bold"))

    return all_passed


# ── Claim level upgrade path ──────────────────────────────────────────────────

def print_upgrade_paths(data: dict) -> None:
    """
    For each row, print what is needed to reach the next claim level.
    """
    upgrade_map = {
        "analogical":      "empirical",
        "formally_stated": "formally_verified",
    }
    domains = data.get("domains", [])
    print(color("\n── Upgrade paths ──", "cyan", "bold"))
    for row in domains:
        claim  = row.get("claim_level", "")
        target = upgrade_map.get(claim)
        if not target:
            continue
        row_id = row.get("id", "<unnamed>")
        n, answered = count_answered_slots(row)
        params = row.get("parameters", {}) or {}
        calibrated = all(params.get(k) is not None for k in PARAM_KEYS)

        print(f"\n  {color(row_id, 'bold')}  ({claim} → {target})")
        if target == "empirical":
            missing_slots = [s for s in TOGT_SLOTS if s not in answered]
            if missing_slots:
                print(f"    • Answer TOGT slots: {missing_slots}")
            if not calibrated:
                missing_params = [k for k in PARAM_KEYS
                                  if params.get(k) is None]
                print(f"    • Calibrate parameters: {missing_params} "
                      f"(requires domain-specific measurement or QMC fit)")
        if target == "formally_verified":
            sc = row.get("lean4_sorry_count", "?")
            label = row.get("lean4_sorry_label", "?")
            print(f"    • Close {sc} sorry(s): {label}")
            print(f"    • Update lean4_sorry_count to 0 and change claim_level")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate AXLE coherence_bridge.yaml integrity."
    )
    parser.add_argument("lexicon", help="Path to coherence_bridge.yaml")
    parser.add_argument(
        "--new", metavar="ENTRY_YAML",
        help="Score a new domain entry YAML for provisional claim level."
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress informational notes; show only warnings and errors."
    )
    parser.add_argument(
        "--upgrades", action="store_true",
        help="Print upgrade paths for each row."
    )
    args = parser.parse_args()

    # Load lexicon
    lex_path = Path(args.lexicon)
    if not lex_path.exists():
        sys.exit(f"File not found: {lex_path}")
    with open(lex_path) as f:
        data = yaml.safe_load(f)

    # Validate
    passed = validate_lexicon(data, quiet=args.quiet)

    # Upgrade paths
    if args.upgrades:
        print_upgrade_paths(data)

    # New entry
    if args.new:
        new_path = Path(args.new)
        if not new_path.exists():
            sys.exit(f"New entry file not found: {new_path}")
        with open(new_path) as f:
            entry = yaml.safe_load(f)
        # entry may be a single dict or wrapped in a list
        if isinstance(entry, list):
            for e in entry:
                score_new_entry(e)
        else:
            score_new_entry(entry)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
