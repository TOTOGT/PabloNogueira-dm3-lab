"""
Tests for scripts/collatz_c9_4_boundary.py

Run with:  python -m pytest scripts/tests/test_c9_4_boundary.py -v
"""

import sys
import os

# Allow importing from the scripts directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from collatz_c9_4_boundary import (
    N_SMALL,
    v2,
    collatz_step,
    injection_bias,
    catalog_small_n_exceptions,
    count_exceptions,
    verify_o1n_bound,
    average_bias_in_window,
    identify_boundary_windows,
    decorrelation_bias_estimate,
    generate_report,
)


# ---------------------------------------------------------------------------
# v2 — 2-adic valuation
# ---------------------------------------------------------------------------


class TestV2:
    def test_power_of_two(self):
        assert v2(1) == 0
        assert v2(2) == 1
        assert v2(4) == 2
        assert v2(8) == 3
        assert v2(16) == 4

    def test_odd(self):
        assert v2(1) == 0
        assert v2(3) == 0
        assert v2(7) == 0
        assert v2(15) == 0

    def test_mixed(self):
        # 12 = 4 * 3, v2 = 2
        assert v2(12) == 2
        # 10 = 2 * 5, v2 = 1
        assert v2(10) == 1
        # 40 = 8 * 5, v2 = 3
        assert v2(40) == 3

    def test_invalid(self):
        with pytest.raises(ValueError):
            v2(0)
        with pytest.raises(ValueError):
            v2(-1)


# ---------------------------------------------------------------------------
# collatz_step
# ---------------------------------------------------------------------------


class TestCollatzStep:
    def test_even(self):
        assert collatz_step(2) == 1
        assert collatz_step(4) == 2
        assert collatz_step(8) == 4
        assert collatz_step(100) == 50

    def test_odd_known_values(self):
        # T(1): 3*1+1 = 4, v2(4)=2, T = 4/4 = 1
        assert collatz_step(1) == 1
        # T(3): 3*3+1 = 10, v2(10)=1, T = 10/2 = 5
        assert collatz_step(3) == 5
        # T(5): 3*5+1 = 16, v2(16)=4, T = 16/16 = 1
        assert collatz_step(5) == 1
        # T(7): 3*7+1 = 22, v2(22)=1, T = 22/2 = 11
        assert collatz_step(7) == 11
        # T(9): 3*9+1 = 28, v2(28)=2, T = 28/4 = 7
        assert collatz_step(9) == 7
        # T(11): 3*11+1 = 34, v2(34)=1, T = 34/2 = 17
        assert collatz_step(11) == 17
        # T(13): 3*13+1 = 40, v2(40)=3, T = 40/8 = 5
        assert collatz_step(13) == 5
        # T(27): 3*27+1 = 82, v2(82)=1, T = 41
        assert collatz_step(27) == 41

    def test_invalid(self):
        with pytest.raises(ValueError):
            collatz_step(0)
        with pytest.raises(ValueError):
            collatz_step(-5)


# ---------------------------------------------------------------------------
# injection_bias
# ---------------------------------------------------------------------------


class TestInjectionBias:
    def test_even_returns_zero(self):
        for n in [2, 4, 6, 100, 1000]:
            assert injection_bias(n) == 0.0

    def test_odd_formula(self):
        # Δ(n) = 1/(3n+1)
        for n in [1, 3, 5, 7, 11, 27, 99]:
            expected = 1.0 / (3 * n + 1)
            assert abs(injection_bias(n) - expected) < 1e-15

    def test_decreasing(self):
        biases = [injection_bias(n) for n in [1, 3, 5, 7, 9, 11]]
        # Bias must be strictly decreasing for consecutive odd n
        for a, b in zip(biases, biases[1:]):
            assert a > b

    def test_invalid(self):
        with pytest.raises(ValueError):
            injection_bias(0)
        with pytest.raises(ValueError):
            injection_bias(-3)


# ---------------------------------------------------------------------------
# catalog_small_n_exceptions
# ---------------------------------------------------------------------------


class TestCatalogSmallNExceptions:
    def test_returns_only_odd(self):
        rows = catalog_small_n_exceptions(20)
        for r in rows:
            assert r["n"] % 2 == 1

    def test_exit_dir_field(self):
        rows = catalog_small_n_exceptions(20, window_start=1, window_end=20)
        for r in rows:
            assert r["exit_dir"] in ("below", "above", "none")

    def test_n1_stays_in_default_window(self):
        # T(1) = 1, should be 'none' for window [1, 64]
        rows = catalog_small_n_exceptions(64, window_start=1, window_end=64)
        row_n1 = next(r for r in rows if r["n"] == 1)
        assert row_n1["T_n"] == 1
        assert row_n1["exit_dir"] == "none"

    def test_n5_exits_narrow_window(self):
        # T(5) = 1, exits [3, 5]
        rows = catalog_small_n_exceptions(5, window_start=3, window_end=5)
        row_n5 = next(r for r in rows if r["n"] == 5)
        assert row_n5["T_n"] == 1
        assert row_n5["exit_dir"] == "below"

    def test_v2_field(self):
        rows = catalog_small_n_exceptions(20)
        for r in rows:
            n = r["n"]
            raw = 3 * n + 1
            assert r["v2_val"] == v2(raw)

    def test_bias_field(self):
        rows = catalog_small_n_exceptions(20)
        for r in rows:
            assert abs(r["bias"] - 1.0 / (3 * r["n"] + 1)) < 1e-7

    def test_window_end_defaults_to_n_max(self):
        rows_default = catalog_small_n_exceptions(32)
        rows_explicit = catalog_small_n_exceptions(32, window_end=32)
        assert rows_default == rows_explicit


# ---------------------------------------------------------------------------
# count_exceptions
# ---------------------------------------------------------------------------


class TestCountExceptions:
    def test_counts_add_up(self):
        counts = count_exceptions(64)
        total = counts["exits_below"] + counts["exits_above"] + counts["interior"]
        assert total == counts["total_odd"]

    def test_frequency_range(self):
        counts = count_exceptions(64)
        assert 0.0 <= counts["exit_frequency"] <= 1.0

    def test_empty_range(self):
        # n_max = 0 gives no odd values
        counts = count_exceptions(0)
        assert counts["total_odd"] == 0
        assert counts["exits_below"] == 0
        assert counts["exits_above"] == 0
        assert counts["interior"] == 0
        assert counts["exit_frequency"] == 0.0


# ---------------------------------------------------------------------------
# verify_o1n_bound
# ---------------------------------------------------------------------------


class TestVerifyO1nBound:
    def test_bound_holds_for_all(self):
        rows = verify_o1n_bound(1, 512)
        for r in rows:
            assert r["bound_satisfied"], (
                f"O(1/n) bound violated at n={r['n']}: ratio={r['ratio_bias_times_n']}"
            )

    def test_ratio_approaches_one_third(self):
        rows = verify_o1n_bound(1, 10000)
        # For large n, ratio = n/(3n+1) → 1/3
        large_n_rows = [r for r in rows if r["n"] >= 1000]
        for r in large_n_rows:
            assert abs(r["ratio_bias_times_n"] - 1.0 / 3) < 0.001

    def test_ratio_strictly_less_than_one_third(self):
        # n/(3n+1) < 1/3 always, with equality only at n→∞
        rows = verify_o1n_bound(1, 200)
        for r in rows:
            assert r["ratio_bias_times_n"] < 1.0 / 3

    def test_returns_only_odd(self):
        rows = verify_o1n_bound(1, 20)
        for r in rows:
            assert r["n"] % 2 == 1


# ---------------------------------------------------------------------------
# average_bias_in_window
# ---------------------------------------------------------------------------


class TestAverageBiasInWindow:
    def test_avg_bias_below_predicted_bound(self):
        result = average_bias_in_window(100, 199)
        assert result["ratio"] is not None
        # avg_bias ≤ Δ(n_min) = 1/(3*n_min+1) → ratio ≤ 1
        assert result["ratio"] <= 1.0

    def test_ratio_close_to_one(self):
        # The ratio avg_bias / Δ(n_min) converges to ~0.70 for large dyadic windows
        result = average_bias_in_window(1000, 1999)
        assert result["ratio"] is not None
        # ratio should be positive and ≤ 1
        assert 0.0 < result["ratio"] <= 1.0

    def test_empty_window(self):
        # Start > end → no odd values
        result = average_bias_in_window(10, 9)
        assert result["avg_bias"] is None

    def test_n_bar_in_window(self):
        result = average_bias_in_window(10, 20)
        assert result["n_bar"] is not None
        assert 10 <= result["n_bar"] <= 20


# ---------------------------------------------------------------------------
# identify_boundary_windows
# ---------------------------------------------------------------------------


class TestIdentifyBoundaryWindows:
    def test_first_window_is_boundary(self):
        windows = identify_boundary_windows(1, 128, 16)
        assert windows[0]["is_boundary"] is True

    def test_last_window_is_boundary(self):
        windows = identify_boundary_windows(1, 128, 16)
        assert windows[-1]["is_boundary"] is True

    def test_interior_windows_exist(self):
        windows = identify_boundary_windows(1, 256, 16)
        interior = [w for w in windows if not w["is_boundary"]]
        assert len(interior) > 0

    def test_exit_frequency_non_negative(self):
        windows = identify_boundary_windows(1, 128, 16)
        for w in windows:
            assert 0.0 <= w["exit_frequency"] <= 1.0

    def test_exit_count_consistent(self):
        windows = identify_boundary_windows(1, 64, 8)
        for w in windows:
            assert w["exit_count"] <= w["total_odd"]


# ---------------------------------------------------------------------------
# decorrelation_bias_estimate
# ---------------------------------------------------------------------------


class TestDecorrelationBiasEstimate:
    def test_full_range_avg_bias_o1n(self):
        result = decorrelation_bias_estimate(1, 512, exclude_boundary_windows=False)
        # avg_bias ≤ predicted_avg = 1/(3*n_min+1) → ratio ≤ 1
        assert result["ratio"] is not None
        assert result["ratio"] <= 1.0

    def test_excluded_boundary_reduces_or_equals_avg_bias(self):
        full = decorrelation_bias_estimate(
            1, 1024, exclude_boundary_windows=False, window_size=32
        )
        excl = decorrelation_bias_estimate(
            1, 1024, exclude_boundary_windows=True, window_size=32
        )
        # Excluding the low-n boundary window raises n_min, so predicted_avg
        # (= 1/(3*n_min+1)) becomes smaller and avg_bias decreases.
        assert excl["n_min"] > full["n_min"]
        assert excl["avg_bias"] < full["avg_bias"]

    def test_sample_count_decreases_with_exclusion(self):
        full = decorrelation_bias_estimate(
            1, 512, exclude_boundary_windows=False, window_size=16
        )
        excl = decorrelation_bias_estimate(
            1, 512, exclude_boundary_windows=True, window_size=16
        )
        assert excl["sample_count"] < full["sample_count"]

    def test_ratio_field(self):
        result = decorrelation_bias_estimate(100, 500)
        assert result["ratio"] is not None
        assert result["ratio"] > 0


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------


class TestGenerateReport:
    def test_report_sections_present(self):
        report = generate_report(n_max_small=16, n_end_bounds=64, window_size=8)
        assert "small_n_catalog" in report
        assert "small_n_counts" in report
        assert "o1n_verification" in report
        assert "window_analysis" in report
        assert "decorrelation_full" in report
        assert "decorrelation_excl" in report
        assert "avg_bias_windows" in report

    def test_o1n_bound_holds_in_report(self):
        report = generate_report(n_max_small=16, n_end_bounds=128, window_size=8)
        assert report["o1n_verification"]["bound_holds"] is True
        assert len(report["o1n_verification"]["violations"]) == 0

    def test_catalog_has_expected_size(self):
        # Odd values in [1, 16]: 1,3,5,7,9,11,13,15 → 8 rows
        report = generate_report(n_max_small=16, n_end_bounds=64, window_size=8)
        assert len(report["small_n_catalog"]) == 8

    def test_dyadic_windows_count(self):
        report = generate_report(n_max_small=16, n_end_bounds=64, window_size=8)
        # expects exponents 3..10 → 8 windows
        assert len(report["avg_bias_windows"]) == 8

    def test_decorrelation_full_ratio_leq_one(self):
        report = generate_report(n_max_small=16, n_end_bounds=128, window_size=8)
        # avg_bias ≤ 1/(3*n_min+1) → ratio ≤ 1
        assert report["decorrelation_full"]["ratio"] <= 1.0
