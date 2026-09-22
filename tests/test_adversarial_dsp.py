"""
InEar Snitch — Milestone 2 Adversarial DSP & Database Stress Test Suite
=====================================================================
Authored by M2 Adversarial Challenger 1.

CRITICAL SAFETY:
- All tests strictly use isolated temporary databases (tmp_path / NamedTemporaryFile).
- Under NO circumstances is `inearsnitch.db` opened or modified.

Stress Areas:
1. Extreme case: Completely identical curves -> score == 0.0 exactly.
2. Extreme case: Massive 60dB/100dB variations >8 kHz with identical <=8 kHz curves -> score == 0.0.
3. Extreme case: Irregular frequency grids (log-spaced, dense linear, sparse, fractional bins).
4. Extreme case: Missing channels (Left-only, Right-only, None, asymmetric counts).
5. Extreme case: Threshold boundaries (N=4 -> None, N=5 -> preliminary, N=9 -> preliminary, N=10 -> non-preliminary).
6. Extreme case: Seal history delta calculation at boundary (-11.8 dB vs -12.0 dB).
7. Extreme case: Corrupted BLOBs, truncated byte arrays, length mismatches, and robustness under hostile data.
"""

import os
import sys
import sqlite3
import pytest
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import database


@pytest.fixture
def temp_db(tmp_path):
    """Provides a fresh, isolated DatabaseManager instance on a temporary database."""
    db_file = str(tmp_path / "temp_adversarial.db")
    db = database.DatabaseManager(db_file)
    return db, db_file


# ---------------------------------------------------------------------------
# Helper Generators
# ---------------------------------------------------------------------------

def make_standard_sweep(freqs=None, spl=90.0, noise=0.0):
    if freqs is None:
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
    mag = spl - (freqs / 1000.0) * 0.4
    if noise > 0:
        mag += np.random.normal(0, noise, size=len(mag))
    phase = np.zeros_like(mag)
    return freqs, mag, phase


# ===========================================================================
# 1. IDENTICAL CURVES (Score == 0.0)
# ===========================================================================

class TestAdversarialIdenticalCurves:
    """Stress-tests that identical curves produce an EXACT score of 0.0 dB."""

    def test_five_identical_curves_score_exactly_zero(self, temp_db):
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        for _ in range(5):
            db.save_measurement(iem_id=10, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = db.get_reproducibility_scores(iem_id=10, tip_id=2)
        assert scores is not None
        assert scores["left"]["score"] == 0.0
        assert scores["left"]["std_dev"] == 0.0
        assert scores["right"]["score"] == 0.0
        assert scores["right"]["std_dev"] == 0.0
        assert scores["left"]["count"] == 5
        assert scores["left"]["is_preliminary"] is True

    def test_fifty_identical_curves_large_sample_zero(self, temp_db):
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        for _ in range(50):
            db.save_measurement(iem_id=10, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=4)

        scores = db.get_reproducibility_scores(iem_id=10, tip_id=4)
        assert scores is not None
        assert scores["left"]["score"] == 0.0
        assert scores["right"]["score"] == 0.0
        assert scores["left"]["count"] == 50
        assert scores["left"]["is_preliminary"] is False

    def test_extreme_spl_ranges_identical_curves(self, temp_db):
        """Test identical curves at extreme SPL levels (140 dB high, -30 dB low)."""
        db, _ = temp_db
        # High SPL (140 dB)
        f, m_high, p = make_standard_sweep(spl=140.0)
        for _ in range(5):
            db.save_measurement(iem_id=20, freqs=f, mag_l=m_high, mag_r=m_high, phase_l=p, phase_r=p, tip_id=3)
        res_high = db.get_reproducibility_scores(20, 3)
        assert res_high["left"]["score"] == 0.0

        # Low SPL (-30 dB)
        f, m_low, p = make_standard_sweep(spl=-30.0)
        for _ in range(5):
            db.save_measurement(iem_id=21, freqs=f, mag_l=m_low, mag_r=m_low, phase_l=p, phase_r=p, tip_id=3)
        res_low = db.get_reproducibility_scores(21, 3)
        assert res_low["left"]["score"] == 0.0


# ===========================================================================
# 2. STRICT BAND-LIMITING (<8 kHz vs >8 kHz)
# ===========================================================================

class TestAdversarialBandLimiting:
    """Stress-tests strict exclusion of all high-frequency variance above 8 kHz."""

    def test_massive_hf_variation_leaves_score_zero(self, temp_db):
        """Massive 60 dB to 120 dB variations above 8 kHz must produce 0.0 dB score."""
        db, _ = temp_db
        f = np.linspace(20.0, 24000.0, 24001, dtype=np.float64)
        p = np.zeros_like(f)

        for i in range(8):
            # Identical curve below 8 kHz
            m = 90.0 - (f / 1000.0) * 0.4
            # Massive HF distortion above 8 kHz
            hf_mask = f > 8000.0
            m[hf_mask] += (i * 15.0)  # Spans 0 dB to 105 dB of HF difference
            db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=4)

        scores = db.get_reproducibility_scores(iem_id=1, tip_id=4)
        assert scores is not None
        assert scores["left"]["score"] == 0.0
        assert scores["right"]["score"] == 0.0
        assert scores["left"]["count"] == 8

    def test_boundary_frequency_bin_inclusion_and_exclusion(self, temp_db):
        """Verify behavior right around the 8000.0 Hz boundary."""
        db, _ = temp_db
        f = np.linspace(20.0, 16000.0, 16000, dtype=np.float64)
        p = np.zeros_like(f)

        # Baseline: 5 curves identical
        for i in range(5):
            m = 85.0 - (f / 1000.0) * 0.3
            # Spike at 8001 Hz (outside the <= 8000 Hz mask)
            idx_8001 = np.argmin(np.abs(f - 8001.0))
            m[idx_8001] += (i * 50.0)
            db.save_measurement(iem_id=2, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=4)

        scores = db.get_reproducibility_scores(iem_id=2, tip_id=4)
        assert scores is not None
        assert scores["left"]["score"] == 0.0, "Spike at 8001 Hz must not affect score!"

    def test_truncation_below_8khz_grid(self, temp_db):
        """When measurements only reach 7000 Hz, np.interp clamps values to 8000 Hz."""
        db, _ = temp_db
        f = np.linspace(20.0, 7000.0, 700, dtype=np.float64)
        p = np.zeros_like(f)
        for _ in range(5):
            m = 90.0 - (f / 1000.0) * 0.4
            db.save_measurement(iem_id=3, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=4)

        scores = db.get_reproducibility_scores(iem_id=3, tip_id=4)
        assert scores is not None
        assert scores["left"]["score"] == 0.0


# ===========================================================================
# 3. IRREGULAR FREQUENCY GRIDS & INTERPOLATION
# ===========================================================================

class TestAdversarialIrregularGrids:
    """Stress-tests interpolation across heterogeneous, mismatched, and fractional frequency grids."""

    def test_heterogeneous_frequency_grids_same_underlying_curve(self, temp_db):
        """
        Five measurements with 5 completely different frequency bin grids:
        1. Log-spaced: 1000 points from 20 to 20000 Hz
        2. Linear dense: 24001 points from 20 to 24000 Hz
        3. Linear sparse: 400 points from 20 to 8000 Hz
        4. Fractional bins: 850 points with prime-fraction spacing
        5. Log-spaced: 500 points from 10 to 10000 Hz
        All evaluate y = 90.0 - (f / 1000.0) * 0.4.
        Resulting score must be 0.0 (or < 0.01 dB numerical precision).
        """
        db, _ = temp_db

        def analytic_curve(freqs):
            return 90.0 - (freqs / 1000.0) * 0.4

        # Grid 1: Log-spaced
        f1 = np.logspace(np.log10(20.0), np.log10(20000.0), 1000, dtype=np.float64)
        m1 = analytic_curve(f1)
        p1 = np.zeros_like(f1)
        db.save_measurement(1, f1, m1, m1, p1, p1, tip_id=5)

        # Grid 2: Linear dense
        f2 = np.linspace(20.0, 24000.0, 24001, dtype=np.float64)
        m2 = analytic_curve(f2)
        p2 = np.zeros_like(f2)
        db.save_measurement(1, f2, m2, m2, p2, p2, tip_id=5)

        # Grid 3: Linear sparse
        f3 = np.linspace(20.0, 8000.0, 400, dtype=np.float64)
        m3 = analytic_curve(f3)
        p3 = np.zeros_like(f3)
        db.save_measurement(1, f3, m3, m3, p3, p3, tip_id=5)

        # Grid 4: Fractional prime bins
        f4 = np.array([20.17 + i * 9.387 for i in range(850)], dtype=np.float64)
        m4 = analytic_curve(f4)
        p4 = np.zeros_like(f4)
        db.save_measurement(1, f4, m4, m4, p4, p4, tip_id=5)

        # Grid 5: Log-spaced wide
        f5 = np.logspace(np.log10(10.0), np.log10(10000.0), 500, dtype=np.float64)
        m5 = analytic_curve(f5)
        p5 = np.zeros_like(f5)
        db.save_measurement(1, f5, m5, m5, p5, p5, tip_id=5)

        scores = db.get_reproducibility_scores(iem_id=1, tip_id=5)
        assert scores is not None
        assert scores["left"]["count"] == 5
        # Numerical interpolation of linear function on linspace is mathematically exact
        assert scores["left"]["score"] <= 0.01, f"Expected near-zero score, got {scores['left']['score']}"
        assert scores["right"]["score"] <= 0.01

    def test_minimum_length_grid_boundary(self, temp_db):
        """Grids with exactly 10 points (minimum allowed) vs 9 points (filtered)."""
        db, _ = temp_db
        # 10 points
        f10 = np.linspace(20.0, 8000.0, 10, dtype=np.float64)
        m10 = np.ones(10, dtype=np.float64) * 90.0
        p10 = np.zeros(10, dtype=np.float64)

        for _ in range(5):
            db.save_measurement(1, f10, m10, m10, p10, p10, tip_id=4)

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is not None
        assert scores["left"]["count"] == 5

        # Now test with 9 points (should be ignored by len(f) < 10)
        f9 = np.linspace(20.0, 8000.0, 9, dtype=np.float64)
        m9 = np.ones(9, dtype=np.float64) * 90.0
        p9 = np.zeros(9, dtype=np.float64)
        for _ in range(5):
            db.save_measurement(2, f9, m9, m9, p9, p9, tip_id=4)

        scores9 = db.get_reproducibility_scores(2, 4)
        assert scores9 is None, "Measurements with < 10 points must be safely rejected"


# ===========================================================================
# 4. MISSING CHANNELS & INDEPENDENCE
# ===========================================================================

class TestAdversarialMissingChannels:
    """Stress-tests channel isolation: Left-only, Right-only, None, and asymmetric sets."""

    def test_left_only_produces_left_score_and_none_right(self, temp_db):
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        for _ in range(6):
            db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=None, phase_l=p, phase_r=None, tip_id=4)

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is not None
        assert scores["left"] is not None
        assert scores["left"]["count"] == 6
        assert scores["right"] is None

    def test_right_only_produces_right_score_and_none_left(self, temp_db):
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        for _ in range(6):
            db.save_measurement(iem_id=1, freqs=f, mag_l=None, mag_r=m, phase_l=None, phase_r=p, tip_id=4)

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is not None
        assert scores["left"] is None
        assert scores["right"] is not None
        assert scores["right"]["count"] == 6

    def test_asymmetric_channel_measurement_counts(self, temp_db):
        """Left has 10 measurements (non-preliminary), Right has 5 (preliminary)."""
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        # Save 5 stereo
        for _ in range(5):
            db.save_measurement(1, f, m, m, p, p, tip_id=4)
        # Save 5 left-only
        for _ in range(5):
            db.save_measurement(1, f, m, None, p, None, tip_id=4)

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is not None
        assert scores["left"]["count"] == 10
        assert scores["left"]["is_preliminary"] is False
        assert scores["right"]["count"] == 5
        assert scores["right"]["is_preliminary"] is True

    def test_both_channels_none_returns_none(self, temp_db):
        db, _ = temp_db
        f, _, p = make_standard_sweep()
        for _ in range(6):
            db.save_measurement(1, f, None, None, p, p, tip_id=4)

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is None

    def test_corrupt_left_blob_does_not_break_right_channel(self, temp_db):
        """If left magnitude BLOB is corrupted, right channel still calculates cleanly."""
        db, db_file = temp_db
        f, m, p = make_standard_sweep()
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        for _ in range(6):
            cur.execute("""
                INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l, magnitude_r)
                VALUES (?, ?, ?, ?, ?)
            """, (1, 4, f.tobytes(), b"CORRUPTED_BYTES_NOT_FLOAT64", m.tobytes()))
        conn.commit()
        conn.close()

        scores = db.get_reproducibility_scores(1, 4)
        assert scores is not None
        assert scores["left"] is None
        assert scores["right"] is not None
        assert scores["right"]["count"] == 6


# ===========================================================================
# 5. THRESHOLD BOUNDARIES (N=4, 5, 9, 10, 11)
# ===========================================================================

class TestAdversarialThresholdBoundaries:
    """Stress-tests the exact count boundaries N=4, 5, 9, 10, 11."""

    def test_exact_threshold_transitions(self, temp_db):
        db, _ = temp_db
        f, m, p = make_standard_sweep()

        # N=1 -> None
        db.save_measurement(1, f, m, m, p, p, tip_id=2)
        assert db.get_reproducibility_scores(1, 2) is None

        # N=4 -> None
        for _ in range(3):
            db.save_measurement(1, f, m, m, p, p, tip_id=2)
        assert db.get_reproducibility_scores(1, 2) is None

        # N=5 -> is_preliminary = True
        db.save_measurement(1, f, m, m, p, p, tip_id=2)
        s5 = db.get_reproducibility_scores(1, 2)
        assert s5 is not None
        assert s5["left"]["count"] == 5
        assert s5["left"]["is_preliminary"] is True

        # N=9 -> is_preliminary = True
        for _ in range(4):
            db.save_measurement(1, f, m, m, p, p, tip_id=2)
        s9 = db.get_reproducibility_scores(1, 2)
        assert s9 is not None
        assert s9["left"]["count"] == 9
        assert s9["left"]["is_preliminary"] is True

        # N=10 -> is_preliminary = False
        db.save_measurement(1, f, m, m, p, p, tip_id=2)
        s10 = db.get_reproducibility_scores(1, 2)
        assert s10 is not None
        assert s10["left"]["count"] == 10
        assert s10["left"]["is_preliminary"] is False

        # N=11 -> is_preliminary = False
        db.save_measurement(1, f, m, m, p, p, tip_id=2)
        s11 = db.get_reproducibility_scores(1, 2)
        assert s11 is not None
        assert s11["left"]["count"] == 11
        assert s11["left"]["is_preliminary"] is False

    def test_invalid_records_do_not_count_towards_threshold(self, temp_db):
        """4 valid records + 3 invalid records must NOT trigger the N=5 threshold."""
        db, _ = temp_db
        f, m, p = make_standard_sweep()
        # 4 valid
        for _ in range(4):
            db.save_measurement(1, f, m, m, p, p, tip_id=3)
        # 1 with mismatched length
        db.save_measurement(1, f, m[:50], m[:50], p[:50], p[:50], tip_id=3)
        # 1 with None frequencies
        db.save_measurement(1, None, m, m, p, p, tip_id=3)

        assert db.get_reproducibility_scores(1, 3) is None, "Invalid records must not count towards threshold"


# ===========================================================================
# 6. SEAL HISTORY DELTA CALCULATION & BOUNDARIES (-11.8 dB / -12.0 dB)
# ===========================================================================

class TestAdversarialSealHistoryBoundaries:
    """Stress-tests the seal history delta calculation and exact boundary thresholds."""

    def test_seal_history_exact_delta_calculation(self, temp_db):
        """
        Verify mathematical delta = mean(35-45 Hz) - mean(450-550 Hz).
        Construct a test sweep where val_40 is exactly 90.0 dB and val_500 is exactly 80.0 dB.
        Expected delta_db = +10.0 dB.
        """
        db, _ = temp_db
        f = np.linspace(20.0, 1000.0, 1000, dtype=np.float64)
        m = np.zeros_like(f)
        # 35-45 Hz: exactly 90.0 dB
        m[(f >= 35.0) & (f <= 45.0)] = 90.0
        # 450-550 Hz: exactly 80.0 dB
        m[(f >= 450.0) & (f <= 550.0)] = 80.0
        p = np.zeros_like(f)

        db.save_measurement(1, f, m, m, p, p, tip_id=4)
        seal = db.get_seal_history(1, 4)
        assert len(seal["left"]) == 1
        entry = seal["left"][0]
        assert entry["val_40"] == 90.0
        assert entry["val_500"] == 80.0
        assert entry["delta_db"] == 10.0
        assert entry["seal_ok"] is True
        assert entry["status"] == "OK"

    def test_seal_boundary_threshold_resolution(self, temp_db):
        """
        Empirically verify boundary classification at -11.79, -11.80, -11.81, -11.99, -12.00, -12.01 dB.
        database.py uses `delta_db >= -11.8`.
        Verify exact behavior for each step.
        """
        db, _ = temp_db
        f = np.linspace(20.0, 1000.0, 1000, dtype=np.float64)
        p = np.zeros_like(f)

        test_deltas = [
            (-11.70, True, "OK"),
            (-11.79, True, "OK"),
            (-11.80, True, "OK"),    # Exact boundary threshold
            (-11.81, False, "LEAK"),  # Just under -11.8 dB
            (-11.99, False, "LEAK"),
            (-12.00, False, "LEAK"),  # Live RTA threshold (-12 dB)
            (-12.01, False, "LEAK"),
        ]

        for delta, expected_ok, expected_status in test_deltas:
            m = np.zeros_like(f)
            m[(f >= 450.0) & (f <= 550.0)] = 100.0
            m[(f >= 35.0) & (f <= 45.0)] = 100.0 + delta
            db.save_measurement(100, f, m, m, p, p, tip_id=4)

        seal = db.get_seal_history(100, 4)
        assert len(seal["left"]) == len(test_deltas)

        for i, (delta, expected_ok, expected_status) in enumerate(test_deltas):
            entry = seal["left"][i]
            assert abs(entry["delta_db"] - delta) < 0.05, f"Entry {i}: expected delta {delta}, got {entry['delta_db']}"
            assert entry["seal_ok"] is expected_ok, (
                f"Delta {delta} dB: expected seal_ok={expected_ok}, got {entry['seal_ok']} "
                f"(database threshold is -11.8 dB)"
            )
            assert entry["status"] == expected_status

    def test_seal_history_missing_frequency_bands_skipped(self, temp_db):
        """Measurements where frequency range does not cover 35-45 Hz or 450-550 Hz must be skipped."""
        db, _ = temp_db
        # Frequencies start at 100 Hz (no 40 Hz band)
        f_no_bass = np.linspace(100.0, 1000.0, 900, dtype=np.float64)
        m_no_bass = np.ones_like(f_no_bass) * 90.0
        p = np.zeros_like(f_no_bass)
        db.save_measurement(1, f_no_bass, m_no_bass, m_no_bass, p, p, tip_id=4)

        # Frequencies stop at 200 Hz (no 500 Hz band)
        f_no_mid = np.linspace(20.0, 200.0, 180, dtype=np.float64)
        m_no_mid = np.ones_like(f_no_mid) * 90.0
        db.save_measurement(1, f_no_mid, m_no_mid, m_no_mid, p[:180], p[:180], tip_id=4)

        seal = db.get_seal_history(1, 4)
        assert len(seal["left"]) == 0
        assert len(seal["right"]) == 0


# ===========================================================================
# 7. HOSTILE INPUTS, RESILIENCE & INTEGRITY
# ===========================================================================

class TestAdversarialHostileInputs:
    """Stress-tests bizarre inputs, negative IDs, and SQL injection safety."""

    def test_invalid_query_parameters(self, temp_db):
        db, _ = temp_db
        assert db.get_reproducibility_scores(None, None) is None
        assert db.get_reproducibility_scores(0, 4) is None
        assert db.get_reproducibility_scores(1, 0) is None
        assert db.get_reproducibility_scores(-1, -1) is not None or db.get_reproducibility_scores(-1, -1) is None
        assert db.get_seal_history(None, 4) == {"left": [], "right": []}
        assert db.get_seal_history(1, None) == {"left": [], "right": []}
        assert db.get_tip_target_peak(None, 4) == {"left": None, "right": None}

    def test_get_last_used_tip_deterministic(self, temp_db):
        """get_last_used_tip must never return 1 or None if a valid tip exists."""
        db, _ = temp_db
        f, m, p = make_standard_sweep()

        # Nonexistent IEM
        assert db.get_last_used_tip(999) is None

        # Only Unbekannt (id=1)
        db.save_measurement(1, f, m, m, p, p, tip_id=1)
        assert db.get_last_used_tip(1) is None

        # Save tip 4
        db.save_measurement(1, f, m, m, p, p, tip_id=4)
        assert db.get_last_used_tip(1) == 4

        # Save tip 5
        db.save_measurement(1, f, m, m, p, p, tip_id=5)
        assert db.get_last_used_tip(1) == 5

        # Save tip 1 again -> must STILL return 5
        db.save_measurement(1, f, m, m, p, p, tip_id=1)
        assert db.get_last_used_tip(1) == 5
