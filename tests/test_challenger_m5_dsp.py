"""
InEar Snitch — Milestone 5 Challenger DSP & UI Stress Test Suite
================================================================
Empirical challenge harness for TipAnalysisCardWidget and DSP algorithms.
Stress areas:
1. Helmholtz resonance peak detection (@staticmethod detect_helmholtz_peak):
   - Multiple local peaks (5 kHz, 8.2 kHz, 12 kHz) -> strictly returns [6000, 10000] Hz peak
   - Multiple competing peaks inside [6000, 10000] Hz window
   - Boundary exact peaks at 6000 Hz and 10000 Hz
   - Noisy curves, completely flat frequency response
   - All NaN/Inf values, sparse NaNs, empty numpy arrays, mismatched lengths
   - Signals where peak or frequencies are strictly outside [6000, 10000] Hz
2. Historical fallback & delta badge representation:
   - Fallback to DB historical median peak when live data is absent or out of band
   - Partial fallback (Left live, Right DB fallback)
   - Delta categorization (<=200 Hz green, <=500 Hz amber, >500 Hz red)
3. Reproducibility score logic & UI sample size thresholds:
   - N = 0, 1, 4 measurements: empty state warning visible ("min. 5 measurements required, currently N={count}")
   - N = 5, 9 measurements: preliminary badge visible (is_preliminary=True, amber styling #451a03 / #fbbf24)
   - N = 10, 50 measurements: stable badge visible (is_preliminary=False, green styling #065f46 / #34d399)
4. L / R channel separation & band-limiting:
   - Asymmetric channel scores (Left variable vs Right identical, and vice-versa)
   - Zero score bleeding between Left and Right labels
   - Band-limiting strictly to 20–8000 Hz (massive >8 kHz variations ignored)
5. Widget reactivity & ProKit gate:
   - Combo box tip switching and signal emission
   - IEM profile switching
   - Seal history trend rendering

SAFETY INVARIANT:
- All database operations are strictly isolated to tmp_path.
- inearsnitch.db is NEVER modified.
"""

import os
import sys
import tempfile
import pytest
import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
from analysis_ui import TipAnalysisCardWidget


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    """Provides a singleton headless QApplication for Qt widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["ChallengerM5Test", "-platform", "offscreen"])
    return app


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    """Redirects config data dir to prevent altering production files."""
    temp_dir = str(tmp_path / "app_data")
    os.makedirs(temp_dir, exist_ok=True)
    monkeypatch.setattr(config, "get_data_dir", lambda: temp_dir)
    if hasattr(config, "revoke_prokit"):
        config.revoke_prokit()
    token_file = os.path.join(temp_dir, ".prokit_unlocked")
    if os.path.exists(token_file):
        os.remove(token_file)
    yield temp_dir
    if os.path.exists(token_file):
        os.remove(token_file)


@pytest.fixture
def isolated_db(tmp_path):
    """Provides a fresh isolated DatabaseManager on a temporary SQLite database."""
    db_file = str(tmp_path / "challenger_m5.db")
    db = database.DatabaseManager(db_file)
    return db


def create_sweep_curve(freqs=None, base_spl=85.0, peak_hz=None, peak_spl=8.0, noise_std=0.0):
    if freqs is None:
        freqs = np.linspace(20.0, 24000.0, 2400, dtype=np.float64)
    mag = base_spl - (freqs / 1000.0) * 0.4
    if peak_hz is not None:
        mag += peak_spl * np.exp(-0.5 * ((freqs - peak_hz) / 350.0) ** 2)
    if noise_std > 0:
        mag += np.random.normal(0.0, noise_std, size=len(mag))
    phase = np.zeros_like(mag)
    return freqs, mag, phase


# ===========================================================================
# 1. HELMHOLTZ RESONANCE PEAK DETECTION STRESS SUITE
# ===========================================================================

class TestAdversarialHelmholtzPeakDetection:
    """Stress-tests @staticmethod detect_helmholtz_peak with hostile and boundary inputs."""

    def test_multiple_local_peaks_strictly_filters_window(self):
        """
        Adversarial: Signal with peak at 5.0 kHz (100 dB), true peak at 8.2 kHz (85 dB),
        and peak at 12.0 kHz (95 dB).
        Must strictly ignore out-of-band peaks and return the maximum in [6000, 10000] Hz.
        """
        freqs = np.linspace(20.0, 20000.0, 4000, dtype=np.float64)
        mag = np.full_like(freqs, 60.0)

        # Huge peak at 5000 Hz (< 6000 Hz)
        idx_5k = np.argmin(np.abs(freqs - 5000.0))
        mag[idx_5k] = 100.0

        # True resonance peak at 8200 Hz (inside [6000, 10000] Hz)
        idx_82k = np.argmin(np.abs(freqs - 8200.0))
        mag[idx_82k] = 85.0

        # Huge peak at 12000 Hz (> 10000 Hz)
        idx_12k = np.argmin(np.abs(freqs - 12000.0))
        mag[idx_12k] = 95.0

        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is not None
        assert abs(peak - 8200.0) < 15.0
        assert 6000.0 <= peak <= 10000.0

    def test_competing_peaks_inside_window(self):
        """
        Adversarial: Two peaks within [6000, 10000] Hz window.
        Returns the absolute maximum peak.
        """
        freqs = np.linspace(20.0, 20000.0, 4000, dtype=np.float64)
        mag = np.full_like(freqs, 70.0)

        idx_68k = np.argmin(np.abs(freqs - 6800.0))
        mag[idx_68k] = 82.0

        idx_84k = np.argmin(np.abs(freqs - 8400.0))
        mag[idx_84k] = 88.0  # Dominant peak

        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is not None
        assert abs(peak - 8400.0) < 15.0

    def test_boundary_exact_peaks_at_6000_and_10000(self):
        """
        Adversarial: Test boundary frequencies exactly at 6000.0 Hz and 10000.0 Hz.
        Both must be included within the filter mask.
        """
        freqs = np.linspace(5000.0, 11000.0, 6001, dtype=np.float64)

        # Boundary at 6000 Hz
        mag_low = np.full_like(freqs, 60.0)
        idx_6k = np.argmin(np.abs(freqs - 6000.0))
        mag_low[idx_6k] = 90.0
        peak_low = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag_low)
        assert peak_low is not None
        assert abs(peak_low - 6000.0) < 2.0

        # Boundary at 10000 Hz
        mag_high = np.full_like(freqs, 60.0)
        idx_10k = np.argmin(np.abs(freqs - 10000.0))
        mag_high[idx_10k] = 90.0
        peak_high = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag_high)
        assert peak_high is not None
        assert abs(peak_high - 10000.0) < 2.0

    def test_completely_flat_response(self):
        """
        Adversarial: Flat response across the entire spectrum.
        Must return a valid float in [6000, 10000] without exception.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        mag = np.full_like(freqs, 85.0)

        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is not None
        assert isinstance(peak, float)
        assert 6000.0 <= peak <= 10000.0

    def test_noisy_curves_various_snr(self):
        """
        Adversarial: Signal with Gaussian noise added. Peak should remain stable.
        """
        np.random.seed(42)
        freqs = np.linspace(20.0, 20000.0, 4000, dtype=np.float64)
        for noise in [0.5, 1.5, 3.0]:
            _, mag, _ = create_sweep_curve(freqs, peak_hz=7950.0, peak_spl=10.0, noise_std=noise)
            peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
            assert peak is not None
            assert abs(peak - 7950.0) < 100.0

    def test_all_nan_values_returns_none(self):
        """
        Adversarial: Array containing all NaNs.
        Must not raise ValueError ('All-NaN slice encountered') and return None.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        mag = np.full_like(freqs, np.nan)
        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is None

    def test_sparse_nans_in_window_finds_valid_peak(self):
        """
        Adversarial: Array with 50% NaNs inside [6000, 10000] Hz, but a valid peak at 8050 Hz.
        np.nanargmax should skip NaNs and identify the peak.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        mag = np.full_like(freqs, 70.0)
        # Alternate NaNs
        mag[::2] = np.nan
        idx_8050 = np.argmin(np.abs(freqs - 8050.0))
        mag[idx_8050] = 95.0

        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is not None
        assert abs(peak - 8050.0) < 25.0

    def test_all_nan_in_window_valid_outside_returns_none(self):
        """
        Adversarial: Valid data outside [6000, 10000] Hz, but all NaNs in [6000, 10000] Hz.
        Must return None safely.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        mag = np.full_like(freqs, 80.0)
        in_win = (freqs >= 6000.0) & (freqs <= 10000.0)
        mag[in_win] = np.nan

        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is None

    def test_infinite_values_resilience(self):
        """
        Adversarial: Arrays containing +Inf or -Inf values.
        Must return a valid float in [6000, 10000] Hz without throwing.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)

        mag_pos_inf = np.full_like(freqs, np.inf)
        peak_pos = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag_pos_inf)
        assert peak_pos is not None
        assert 6000.0 <= peak_pos <= 10000.0

        mag_neg_inf = np.full_like(freqs, -np.inf)
        peak_neg = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag_neg_inf)
        assert peak_neg is not None
        assert 6000.0 <= peak_neg <= 10000.0

    def test_inverted_curve_notch(self):
        """
        Adversarial: Inverted curve with a deep notch at 8000 Hz.
        Maximum is at the boundary of [6000, 10000] Hz.
        """
        freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        mag = -10.0 / (1.0 + ((freqs - 8000.0) / 200.0) ** 2)
        peak = TipAnalysisCardWidget.detect_helmholtz_peak(freqs, mag)
        assert peak is not None
        assert 6000.0 <= peak <= 10000.0

    def test_empty_short_and_invalid_arrays(self):
        """
        Adversarial: Empty arrays, arrays with < 10 points, length mismatches, and None inputs.
        All must return None.
        """
        assert TipAnalysisCardWidget.detect_helmholtz_peak(None, None) is None
        assert TipAnalysisCardWidget.detect_helmholtz_peak(np.array([]), np.array([])) is None
        assert TipAnalysisCardWidget.detect_helmholtz_peak(np.array([1000.0, 2000.0]), np.array([80.0, 80.0])) is None
        assert TipAnalysisCardWidget.detect_helmholtz_peak(np.ones(20), np.ones(15)) is None
        assert TipAnalysisCardWidget.detect_helmholtz_peak("not_array", "not_array") is None

    def test_frequencies_strictly_outside_window_returns_none(self):
        """
        Adversarial: Frequency range entirely below 6000 Hz or entirely above 10000 Hz.
        Must return None (no frequencies in window).
        """
        f_low = np.linspace(20.0, 5000.0, 500, dtype=np.float64)
        m_low = np.full_like(f_low, 80.0)
        assert TipAnalysisCardWidget.detect_helmholtz_peak(f_low, m_low) is None

        f_high = np.linspace(11000.0, 24000.0, 500, dtype=np.float64)
        m_high = np.full_like(f_high, 80.0)
        assert TipAnalysisCardWidget.detect_helmholtz_peak(f_high, m_high) is None


# ===========================================================================
# 2. HELMHOLTZ FALLBACK & DELTA REPRESENTATION SUITE
# ===========================================================================

class TestAdversarialHelmholtzFallbackAndDelta:
    """Stress-tests historical fallback and delta badge representation in TipAnalysisCardWidget."""

    def test_fallback_to_db_when_live_sweep_is_none(self, qapp, isolated_db):
        """
        When live sweep is None, TipAnalysisCardWidget falls back to db.get_tip_target_peak(iem_id, tip_id).
        """
        f = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        p = np.zeros_like(f)
        ml = np.full_like(f, 75.0)
        ml[np.argmin(np.abs(f - 7850.0))] = 92.0
        mr = np.full_like(f, 75.0)
        mr[np.argmin(np.abs(f - 8150.0))] = 94.0

        for _ in range(3):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=ml, mag_r=mr, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2, freqs=None, mag_l=None, mag_r=None)
        card.show()
        qapp.processEvents()

        assert "784" in card.lbl_peak_l.text() or "785" in card.lbl_peak_l.text()
        assert "814" in card.lbl_peak_r.text() or "815" in card.lbl_peak_r.text()

    def test_fallback_to_db_when_live_sweep_is_out_of_band(self, qapp, isolated_db):
        """
        When live sweep frequencies are restricted to 20-5000 Hz, detect_helmholtz_peak
        returns None and widget falls back to DB historical median.
        """
        f_full = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        p_full = np.zeros_like(f_full)
        ml = np.full_like(f_full, 75.0)
        ml[np.argmin(np.abs(f_full - 7850.0))] = 92.0
        mr = np.full_like(f_full, 75.0)
        mr[np.argmin(np.abs(f_full - 8150.0))] = 94.0

        for _ in range(3):
            isolated_db.save_measurement(iem_id=1, freqs=f_full, mag_l=ml, mag_r=mr, phase_l=p_full, phase_r=p_full, tip_id=2)

        # Live sweep has no 6-10k data
        f_low = np.linspace(20.0, 5000.0, 500, dtype=np.float64)
        m_low = np.full_like(f_low, 80.0)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2, freqs=f_low, mag_l=m_low, mag_r=m_low)
        card.show()
        qapp.processEvents()

        assert "784" in card.lbl_peak_l.text() or "785" in card.lbl_peak_l.text()
        assert "814" in card.lbl_peak_r.text() or "815" in card.lbl_peak_r.text()

    def test_partial_live_sweep_fallback(self, qapp, isolated_db):
        """
        Left channel has live sweep (8300 Hz), Right channel is None.
        Left should use live peak, Right should fall back to DB (8150 Hz).
        """
        f = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        p = np.zeros_like(f)
        ml = np.full_like(f, 75.0)
        ml[np.argmin(np.abs(f - 7850.0))] = 92.0
        mr = np.full_like(f, 75.0)
        mr[np.argmin(np.abs(f - 8150.0))] = 94.0

        for _ in range(3):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=ml, mag_r=mr, phase_l=p, phase_r=p, tip_id=2)

        # Live data: Left peak at 8300 Hz, Right is None
        ml_live = np.full_like(f, 75.0)
        ml_live[np.argmin(np.abs(f - 8300.0))] = 98.0

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2, freqs=f, mag_l=ml_live, mag_r=None)
        card.show()
        qapp.processEvents()

        assert "829" in card.lbl_peak_l.text() or "830" in card.lbl_peak_l.text()
        assert "814" in card.lbl_peak_r.text() or "815" in card.lbl_peak_r.text()

    def test_no_data_empty_state_display(self, qapp, isolated_db):
        """
        When neither live sweep nor DB has data for (iem_id, tip_id),
        labels show '— Hz' and delta shows '—'.
        """
        card = TipAnalysisCardWidget(db=isolated_db, iem_id=999, tip_id=999, freqs=None, mag_l=None, mag_r=None)
        card.show()
        qapp.processEvents()

        assert card.lbl_peak_l.text() == "L: — Hz"
        assert card.lbl_peak_r.text() == "R: — Hz"
        assert card.badge_peak_delta_l.text() == "—"
        assert card.badge_peak_delta_r.text() == "—"

    def test_delta_badge_thresholds_and_styling(self, qapp):
        """
        Tests the 3 delta threshold tiers:
        - Optimal (<= 200 Hz): green badge (#065f46, #34d399)
        - Acceptable (201-500 Hz): amber badge (#451a03, #fbbf24)
        - Warning (> 500 Hz): red badge (#7f1d1d, #f87171)
        """
        f = np.linspace(20.0, 20000.0, 20000, dtype=np.float64)

        # 1. Optimal: 8000 Hz (delta=0) and 8150 Hz (delta=+150)
        m_l = np.full_like(f, 60.0)
        m_l[np.argmin(np.abs(f - 8000.0))] = 90.0
        m_r = np.full_like(f, 60.0)
        m_r[np.argmin(np.abs(f - 8150.0))] = 90.0

        c1 = TipAnalysisCardWidget(freqs=f, mag_l=m_l, mag_r=m_r)
        c1.show()
        qapp.processEvents()
        assert "Δ +0 Hz" in c1.badge_peak_delta_l.text()
        assert "#065f46" in c1.badge_peak_delta_l.styleSheet()
        assert "Δ +150 Hz" in c1.badge_peak_delta_r.text()
        assert "#065f46" in c1.badge_peak_delta_r.styleSheet()

        # 2. Moderate shift: 8350 Hz (delta=+350) and 7700 Hz (delta=-300)
        m_l2 = np.full_like(f, 60.0)
        m_l2[np.argmin(np.abs(f - 8350.0))] = 90.0
        m_r2 = np.full_like(f, 60.0)
        m_r2[np.argmin(np.abs(f - 7700.0))] = 90.0

        c2 = TipAnalysisCardWidget(freqs=f, mag_l=m_l2, mag_r=m_r2)
        c2.show()
        qapp.processEvents()
        assert "Δ +350 Hz" in c2.badge_peak_delta_l.text()
        assert "#451a03" in c2.badge_peak_delta_l.styleSheet()
        assert "Δ -300 Hz" in c2.badge_peak_delta_r.text()
        assert "#451a03" in c2.badge_peak_delta_r.styleSheet()

        # 3. Severe shift: 9000 Hz (delta=+1000) and 7200 Hz (delta=-800)
        m_l3 = np.full_like(f, 60.0)
        m_l3[np.argmin(np.abs(f - 9000.0))] = 90.0
        m_r3 = np.full_like(f, 60.0)
        m_r3[np.argmin(np.abs(f - 7200.0))] = 90.0

        c3 = TipAnalysisCardWidget(freqs=f, mag_l=m_l3, mag_r=m_r3)
        c3.show()
        qapp.processEvents()
        assert "Δ +1000 Hz" in c3.badge_peak_delta_l.text()
        assert "#7f1d1d" in c3.badge_peak_delta_l.styleSheet()
        assert "Δ -800 Hz" in c3.badge_peak_delta_r.text()
        assert "#7f1d1d" in c3.badge_peak_delta_r.styleSheet()


# ===========================================================================
# 3. REPRODUCIBILITY SCORE SAMPLE SIZE THRESHOLDS SUITE
# ===========================================================================

class TestAdversarialReproducibilityThresholds:
    """Stress-tests strict sample size thresholds for Reproducibility Score."""

    def test_n_zero_measurements_empty_warning(self, qapp, isolated_db):
        """
        N=0: empty state visible, warning label says minimum 5 measurements required (N=0),
        score widgets and preliminary badge hidden.
        """
        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is True
        assert "min. 5 measurements required, currently N=0" in card.lbl_repro_warning.text()
        assert card.repro_scores_widget.isVisible() is False
        assert card.badge_repro_status.isVisible() is False
        assert card.lbl_score_l.text() == "L: —"
        assert card.lbl_score_r.text() == "R: —"

    def test_n_one_measurement_empty_warning(self, qapp, isolated_db):
        """
        N=1: empty state visible, warning label reports N=1.
        """
        f, m, p = create_sweep_curve()
        isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is True
        assert "min. 5 measurements required, currently N=1" in card.lbl_repro_warning.text()
        assert card.repro_scores_widget.isVisible() is False
        assert card.badge_repro_status.isVisible() is False

    def test_n_four_measurements_boundary_empty_warning(self, qapp, isolated_db):
        """
        N=4: exactly at the boundary before 5. Still empty state, warning reports N=4.
        """
        f, m, p = create_sweep_curve()
        for _ in range(4):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is True
        assert "min. 5 measurements required, currently N=4" in card.lbl_repro_warning.text()
        assert card.repro_scores_widget.isVisible() is False
        assert card.badge_repro_status.isVisible() is False

    def test_n_five_measurements_first_valid_preliminary_amber(self, qapp, isolated_db):
        """
        N=5: exactly at threshold. Scores visible, preliminary badge visible (amber styling).
        """
        f, m, p = create_sweep_curve()
        for _ in range(5):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = isolated_db.get_reproducibility_scores(1, 2)
        assert scores is not None
        assert scores["left"]["is_preliminary"] is True
        assert scores["left"]["count"] == 5

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is False
        assert card.repro_scores_widget.isVisible() is True
        assert card.badge_repro_status.isVisible() is True
        assert card.badge_repro_status.text() == "⚠ Preliminary (N=5)"
        assert "#451a03" in card.badge_repro_status.styleSheet()
        assert "#fbbf24" in card.badge_repro_status.styleSheet()

    def test_n_nine_measurements_upper_preliminary_boundary(self, qapp, isolated_db):
        """
        N=9: upper preliminary boundary. Still preliminary badge (amber styling).
        """
        f, m, p = create_sweep_curve()
        for _ in range(9):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = isolated_db.get_reproducibility_scores(1, 2)
        assert scores is not None
        assert scores["left"]["is_preliminary"] is True
        assert scores["left"]["count"] == 9

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is False
        assert card.repro_scores_widget.isVisible() is True
        assert card.badge_repro_status.isVisible() is True
        assert card.badge_repro_status.text() == "⚠ Preliminary (N=9)"
        assert "#451a03" in card.badge_repro_status.styleSheet()

    def test_n_ten_measurements_stable_boundary_green(self, qapp, isolated_db):
        """
        N=10: lower stable boundary. Stable badge visible (green styling).
        """
        f, m, p = create_sweep_curve()
        for _ in range(10):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = isolated_db.get_reproducibility_scores(1, 2)
        assert scores is not None
        assert scores["left"]["is_preliminary"] is False
        assert scores["left"]["count"] == 10

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is False
        assert card.repro_scores_widget.isVisible() is True
        assert card.badge_repro_status.isVisible() is True
        assert card.badge_repro_status.text() == "✓ Stable (N=10)"
        assert "#065f46" in card.badge_repro_status.styleSheet()
        assert "#34d399" in card.badge_repro_status.styleSheet()

    def test_n_fifty_measurements_large_sample_green(self, qapp, isolated_db):
        """
        N=50: large sample size. Stable badge visible (green styling).
        """
        f, m, p = create_sweep_curve()
        for _ in range(50):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = isolated_db.get_reproducibility_scores(1, 2)
        assert scores is not None
        assert scores["left"]["is_preliminary"] is False
        assert scores["left"]["count"] == 50

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_repro_warning.isVisible() is False
        assert card.badge_repro_status.text() == "✓ Stable (N=50)"
        assert "#065f46" in card.badge_repro_status.styleSheet()


# ===========================================================================
# 4. L / R CHANNEL SEPARATION & BAND-LIMITING SUITE
# ===========================================================================

class TestAdversarialLRChannelSeparation:
    """Stress-tests that Left and Right channel metrics never bleed into one another."""

    def test_left_varying_right_identical_no_bleed(self, qapp, isolated_db):
        """
        Left channel has varying curves (std dev ~ 2.83 dB), Right channel has identical curves (std dev = 0.00 dB).
        Verify Left score never bleeds into Right label and vice-versa.
        """
        f, m_base, p = create_sweep_curve()
        offsets = [0.0, 2.0, 4.0, -2.0, -4.0]
        for off in offsets:
            ml = m_base + off
            mr = m_base.copy()
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=ml, mag_r=mr, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        txt_l = card.lbl_score_l.text()
        txt_r = card.lbl_score_r.text()

        assert "±2.83 dB" in txt_l
        assert "59.2%" in txt_l
        assert "±0.00 dB" in txt_r
        assert "100.0%" in txt_r

        # Anti-bleed check
        assert "±0.00 dB" not in txt_l
        assert "±2.83 dB" not in txt_r

    def test_right_varying_left_identical_no_bleed(self, qapp, isolated_db):
        """
        Right channel has varying curves, Left channel has identical curves.
        Verify Right score never bleeds into Left label.
        """
        f, m_base, p = create_sweep_curve()
        offsets = [0.0, 1.5, 3.0, -1.5, -3.0]
        for off in offsets:
            ml = m_base.copy()
            mr = m_base + off
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=ml, mag_r=mr, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        txt_l = card.lbl_score_l.text()
        txt_r = card.lbl_score_r.text()

        assert "±0.00 dB" in txt_l
        assert "100.0%" in txt_l
        assert "±2.12 dB" in txt_r
        assert "69.5%" in txt_r

        # Anti-bleed check
        assert "±2.12 dB" not in txt_l
        assert "±0.00 dB" not in txt_r

    def test_asymmetric_channel_data_left_only(self, qapp, isolated_db):
        """
        Left channel has 5 valid measurements, Right channel is completely None.
        Left label shows score; Right label shows 'R: —'.
        """
        f, m, p = create_sweep_curve()
        for _ in range(5):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=None, phase_l=p, phase_r=None, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_score_l.text() == "L: 100.0% (±0.00 dB)"
        assert card.lbl_score_r.text() == "R: —"

    def test_asymmetric_channel_data_right_only(self, qapp, isolated_db):
        """
        Right channel has 5 valid measurements, Left channel is completely None.
        Right label shows score; Left label shows 'L: —'.
        """
        f, m, p = create_sweep_curve()
        for _ in range(5):
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=None, mag_r=m, phase_l=None, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_score_l.text() == "L: —"
        assert card.lbl_score_r.text() == "R: 100.0% (±0.00 dB)"

    def test_reproducibility_band_limiting_strictly_ignores_above_8khz(self, qapp, isolated_db):
        """
        Adversarial: 5 measurements have 100% IDENTICAL curves from 20 Hz to 8000 Hz,
        but massive 60 dB chaos from 8001 Hz to 24000 Hz.
        Band-limited score MUST be strictly 0.00 dB std dev (100.0%).
        """
        f = np.linspace(20.0, 24000.0, 2400, dtype=np.float64)
        p = np.zeros_like(f)
        base_curve = 85.0 - (f / 1000.0) * 0.3

        mask_hf = f > 8000.0
        chaos_offsets = [0.0, 25.0, -40.0, 60.0, -50.0]

        for off in chaos_offsets:
            m = base_curve.copy()
            m[mask_hf] += off  # Wild variations only above 8 kHz
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=m, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        scores = isolated_db.get_reproducibility_scores(1, 2)
        assert scores is not None
        assert scores["left"]["score"] == 0.0
        assert scores["left"]["std_dev"] == 0.0
        assert scores["right"]["score"] == 0.0
        assert scores["right"]["std_dev"] == 0.0

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert card.lbl_score_l.text() == "L: 100.0% (±0.00 dB)"
        assert card.lbl_score_r.text() == "R: 100.0% (±0.00 dB)"


# ===========================================================================
# 5. WIDGET REACTIVITY & PROKIT GATE SUITE
# ===========================================================================

class TestAdversarialWidgetReactivity:
    """Stress-tests dynamic combo switching, IEM changes, and ProKit visibility gate."""

    def test_prokit_gate_visibility(self, qapp, isolated_data_dir):
        """
        Widget initial visibility adheres strictly to config.is_prokit_unlocked().
        """
        assert config.is_prokit_unlocked() is False
        card_locked = TipAnalysisCardWidget()
        assert card_locked.isVisible() is False

        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        assert config.is_prokit_unlocked() is True
        card_unlocked = TipAnalysisCardWidget()
        assert card_unlocked.isVisible() is True

    def test_tip_combobox_switching_updates_and_emits(self, qapp, isolated_db):
        """
        Switching the combo box updates tip_id and emits tip_changed signal.
        """
        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=1)
        card.show()
        qapp.processEvents()

        emitted = []
        card.tip_changed.connect(lambda t_id: emitted.append(t_id))

        # Select second item (e.g. Kein Aufsatz or V26)
        card.cb_tip_selector.setCurrentIndex(1)
        qapp.processEvents()

        assert len(emitted) == 1
        assert card.tip_id == emitted[0]

    def test_set_active_iem_and_tip_methods(self, qapp, isolated_db):
        """
        set_active_iem and set_active_tip dynamically update internal IDs and refresh metrics.
        """
        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=1)
        card.show()
        qapp.processEvents()

        card.set_active_iem(42)
        assert card.iem_id == 42

        card.set_active_tip(3)
        assert card.tip_id == 3

    def test_seal_history_trend_chips(self, qapp, isolated_db):
        """
        Seal history generates summary text and trend chips for L and R channels.
        """
        f, m, p = create_sweep_curve()
        # 3 OK measurements and 1 LEAK measurement
        for i in range(4):
            ml = m.copy()
            if i == 3:  # leak on 4th
                ml[(f >= 35) & (f <= 45)] -= 25.0
            isolated_db.save_measurement(iem_id=1, freqs=f, mag_l=ml, mag_r=m, phase_l=p, phase_r=p, tip_id=2)

        card = TipAnalysisCardWidget(db=isolated_db, iem_id=1, tip_id=2)
        card.show()
        qapp.processEvents()

        assert "3/4 OK (75%)" in card.lbl_seal_summary_l.text()
        assert "4/4 OK (100%)" in card.lbl_seal_summary_r.text()
        assert card.trend_chips_layout.count() > 0
