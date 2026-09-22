"""
InEar Snitch ProKit Tip-Tracking — M4 Acoustic Seal Challenger Test Suite
========================================================================

Adversarially challenge and stress-test acoustic seal computation and
Locked Design Decision 2 (L and R ALWAYS separate) in history_ui.py:

1. Seal Calculation Accuracy & Thresholds:
   - Synthetic sweeps crossing -11.8 dB threshold:
     - delta = -11.7 dB -> 'OK'
     - delta = -11.8 dB -> 'OK'
     - delta = -11.9 dB -> 'LEAK'
   - Dedicated lbl_seal_l and lbl_seal_r reflect statuses accurately (text, tooltip, CSS).

2. Locked Design Decision 2 (L and R ALWAYS separate):
   - Asymmetric stereo: L delta = -5.0 dB ('OK'), R delta = -15.0 dB ('LEAK').
   - lbl_seal_l shows 'OK', lbl_seal_r shows 'LEAK'.
   - NEVER averaged (average = -10.0 dB which is OK; averaging would falsely hide right leak).

3. Mono and Malformed BLOB Tests:
   - Mono Left (mag_r is None): lbl_seal_l visible, lbl_seal_r hidden, lbl_seal.text() is "Seal L: ...".
   - Mono Right (mag_l is None): lbl_seal_r visible, lbl_seal_l hidden, lbl_seal.text() is "Seal R: ...".
   - Empty frequencies/magnitudes: no crash, seal labels gracefully hidden.
   - Truncated frequencies: missing 40 Hz or 500 Hz -> no crash, seal labels hidden.

4. ProKit Gate Integration:
   - ProKit locked hides all seal widgets and tip badges.
   - ProKit unlocked reveals appropriate badges.

5. Database Integration & HistoryWidget.load_history():
   - Isolated temporary SQLite database. NEVER touch inearsnitch.db.
"""

import os
import sys
import tempfile
import sqlite3
import unittest
from unittest.mock import patch

import numpy as np

# Ensure headless Qt execution
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure root directory is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
import history_ui
from history_ui import HistoryCardWidget, HistoryWidget


def get_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(["InEarSnitchAcousticSealTest", "-platform", "offscreen"])
    return app


def make_sweep_with_exact_delta(delta_db, base_spl=90.0):
    """
    Constructs frequency and magnitude vectors where:
    mean(mag[35..45 Hz]) - mean(mag[450..550 Hz]) == delta_db
    """
    freqs = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
    mag = np.full_like(freqs, base_spl)
    # Set 40 Hz band (35 to 45 Hz) to base_spl + delta_db
    mask_40 = (freqs >= 35.0) & (freqs <= 45.0)
    mag[mask_40] = base_spl + delta_db
    # 500 Hz band (450 to 550 Hz) remains base_spl
    return freqs, mag


class TestSealCalculationThresholds(unittest.TestCase):
    """Adversarial stress testing of the -11.8 dB seal threshold boundary."""

    def setUp(self):
        self.app = get_qapp()

    def test_exact_threshold_ok_11_7(self):
        """delta = -11.7 dB -> status is OK."""
        freq, mag = make_sweep_with_exact_delta(-11.7)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.7)
        self.assertEqual(status, "OK")

    def test_exact_threshold_boundary_11_8(self):
        """delta = -11.8 dB -> boundary condition, status is strictly OK."""
        freq, mag = make_sweep_with_exact_delta(-11.8)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.8)
        self.assertEqual(status, "OK")

    def test_exact_threshold_leak_11_9(self):
        """delta = -11.9 dB -> status is strictly LEAK."""
        freq, mag = make_sweep_with_exact_delta(-11.9)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.9)
        self.assertEqual(status, "LEAK")

    def test_fractional_boundaries_around_threshold(self):
        """Test fine sub-tenth decibel boundaries."""
        # -11.74 rounds to -11.7 -> OK
        freq, mag = make_sweep_with_exact_delta(-11.74)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.7)
        self.assertEqual(status, "OK")

        # -11.84 rounds to -11.8 -> OK
        freq, mag = make_sweep_with_exact_delta(-11.84)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.8)
        self.assertEqual(status, "OK")

        # -11.86 rounds to -11.9 -> LEAK
        freq, mag = make_sweep_with_exact_delta(-11.86)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(delta, -11.9)
        self.assertEqual(status, "LEAK")

    def test_extreme_positive_and_negative_deltas(self):
        """Strong acoustic seal vs severe acoustic leak."""
        # Strong seal (+6 dB bass boost)
        freq_ok, mag_ok = make_sweep_with_exact_delta(+6.0)
        status_ok, delta_ok = HistoryCardWidget.compute_seal_for_channel(freq_ok, mag_ok)
        self.assertEqual(status_ok, "OK")
        self.assertEqual(delta_ok, 6.0)

        # Severe leak (-30 dB bass drop)
        freq_leak, mag_leak = make_sweep_with_exact_delta(-30.0)
        status_leak, delta_leak = HistoryCardWidget.compute_seal_for_channel(freq_leak, mag_leak)
        self.assertEqual(status_leak, "LEAK")
        self.assertEqual(delta_leak, -30.0)

    def test_card_widget_reflects_threshold_labels_and_styling(self):
        """Verify HistoryCardWidget lbl_seal_l and lbl_seal_r labels, tooltips, and styles."""
        with patch.object(config, "is_prokit_unlocked", return_value=True):
            # Left = -11.8 (OK), Right = -11.9 (LEAK)
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Test IEM",
                side="Stereo",
                seal_l=-11.8,
                seal_r=-11.9,
            )
            card.show()
            self.assertEqual(card.seal_l_status, "OK")
            self.assertEqual(card.seal_r_status, "LEAK")
            self.assertEqual(card.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card.lbl_seal_r.text(), "R: LEAK")
            self.assertFalse(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_r.isHidden())
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())
            self.assertIn("#065f46", card.lbl_seal_l.styleSheet())  # Green bg for OK
            self.assertIn("#7f1d1d", card.lbl_seal_r.styleSheet())  # Red bg for LEAK
            self.assertIn("-11.8 dB (OK)", card.lbl_seal_l.toolTip())
            self.assertIn("-11.9 dB (LEAK)", card.lbl_seal_r.toolTip())


class TestLockedDesignDecision2(unittest.TestCase):
    """
    Locked Design Decision 2:
    L and R channels ALWAYS separate. All scores, badges, and analyses must be
    computed separately for magnitude_l and magnitude_r. Never combine into a single value.
    """

    def setUp(self):
        self.app = get_qapp()

    def test_asymmetric_stereo_no_averaging(self):
        """
        Left: delta = -5.0 dB (OK)
        Right: delta = -15.0 dB (LEAK)
        Averaging would yield (-5 + -15)/2 = -10.0 dB (which is >= -11.8 dB, falsely OK!).
        Verify that averaging is NEVER performed: Left MUST be OK, Right MUST be LEAK.
        """
        freq_l, mag_l = make_sweep_with_exact_delta(-5.0)
        freq_r, mag_r = make_sweep_with_exact_delta(-15.0)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Asymmetric IEM",
                side="Stereo",
                freq=freq_l,
                mag_l=mag_l,
                mag_r=mag_r,
            )
            card.show()

            # Check individual channel metrics
            self.assertEqual(card.seal_l_delta, -5.0)
            self.assertEqual(card.seal_l_status, "OK")
            self.assertEqual(card.seal_r_delta, -15.0)
            self.assertEqual(card.seal_r_status, "LEAK")

            # Check UI labels
            self.assertEqual(card.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card.lbl_seal_r.text(), "R: LEAK")
            self.assertFalse(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_r.isHidden())
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())

            # Check summary text preserves both channels separately
            self.assertEqual(card.seal_text, "Seal: L -5.0dB | R -15.0dB")
            self.assertEqual(card.lbl_seal.text(), "Seal: L -5.0dB | R -15.0dB")

            # Verify that the average (-10.0 dB) is NOT shown anywhere
            self.assertNotIn("-10.0", card.seal_text)
            self.assertNotEqual(card.lbl_seal_r.text(), "R: OK")

    def test_inverted_asymmetric_stereo(self):
        """Left: delta = -18.0 dB (LEAK), Right: delta = +2.0 dB (OK)."""
        freq_l, mag_l = make_sweep_with_exact_delta(-18.0)
        freq_r, mag_r = make_sweep_with_exact_delta(+2.0)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Asymmetric IEM Inverted",
                side="Stereo",
                freq=freq_l,
                mag_l=mag_l,
                mag_r=mag_r,
            )
            card.show()
            self.assertEqual(card.seal_l_status, "LEAK")
            self.assertEqual(card.seal_r_status, "OK")
            self.assertEqual(card.lbl_seal_l.text(), "L: LEAK")
            self.assertEqual(card.lbl_seal_r.text(), "R: OK")
            self.assertEqual(card.seal_text, "Seal: L -18.0dB | R +2.0dB")
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())

    def test_dynamic_set_seal_preserves_separation(self):
        """Dynamically updating seal via set_seal maintains L/R separation."""
        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Dynamic IEM",
                side="Stereo",
            )
            card.show()
            # Update dynamically
            card.set_seal(-4.0, -16.0)
            self.assertEqual(card.seal_l_status, "OK")
            self.assertEqual(card.seal_r_status, "LEAK")
            self.assertEqual(card.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card.lbl_seal_r.text(), "R: LEAK")
            self.assertEqual(card.lbl_seal.text(), "Seal: L -4.0dB | R -16.0dB")
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())


class TestMonoAndMalformedBlobs(unittest.TestCase):
    """Stress-test mono measurements, empty BLOBs, truncated frequencies, and malformed inputs."""

    def setUp(self):
        self.app = get_qapp()

    def test_mono_left_measurement(self):
        """Mono Left (mag_r is None): lbl_seal_l visible, lbl_seal_r hidden, lbl_seal.text() is 'Seal L: ...'."""
        freq, mag_l = make_sweep_with_exact_delta(-5.0)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Mono Left IEM",
                side="Left",
                freq=freq,
                mag_l=mag_l,
                mag_r=None,
            )
            card.show()
            self.assertEqual(card.seal_l_status, "OK")
            self.assertIsNone(card.seal_r_status)
            self.assertEqual(card.seal_l_delta, -5.0)
            self.assertIsNone(card.seal_r_delta)

            # Left visible, Right hidden
            self.assertFalse(card.lbl_seal_l.isHidden())
            self.assertTrue(card.lbl_seal_r.isHidden())
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertFalse(card.lbl_seal_r.isVisible())

            # Seal text format
            self.assertEqual(card.lbl_seal.text(), "Seal L: -5.0dB")
            self.assertTrue(card.lbl_seal.isVisible())
            self.assertNotIn("R ", card.lbl_seal.text())
            self.assertNotIn("|", card.lbl_seal.text())

    def test_mono_right_measurement(self):
        """Mono Right (mag_l is None): lbl_seal_r visible, lbl_seal_l hidden, lbl_seal.text() is 'Seal R: ...'."""
        freq, mag_r = make_sweep_with_exact_delta(-15.0)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Mono Right IEM",
                side="Right",
                freq=freq,
                mag_l=None,
                mag_r=mag_r,
            )
            card.show()
            self.assertIsNone(card.seal_l_status)
            self.assertEqual(card.seal_r_status, "LEAK")
            self.assertIsNone(card.seal_l_delta)
            self.assertEqual(card.seal_r_delta, -15.0)

            # Right visible, Left hidden
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_r.isHidden())
            self.assertFalse(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())

            # Seal text format
            self.assertEqual(card.lbl_seal.text(), "Seal R: -15.0dB")
            self.assertTrue(card.lbl_seal.isVisible())
            self.assertNotIn("L ", card.lbl_seal.text())
            self.assertNotIn("|", card.lbl_seal.text())

    def test_empty_frequencies_or_magnitudes(self):
        """Empty vectors produce (None, None) and hide seal labels gracefully without crash."""
        status, delta = HistoryCardWidget.compute_seal_for_channel(np.array([]), np.array([]))
        self.assertIsNone(status)
        self.assertIsNone(delta)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Empty BLOB IEM",
                side="Stereo",
                freq=np.array([]),
                mag_l=np.array([]),
                mag_r=np.array([]),
            )
            card.show()
            self.assertIsNone(card.seal_l_status)
            self.assertIsNone(card.seal_r_status)
            self.assertEqual(card.seal_text, "")
            self.assertTrue(card.lbl_seal.isHidden())
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertTrue(card.lbl_seal_r.isHidden())
            self.assertFalse(card.lbl_seal.isVisible())
            self.assertFalse(card.lbl_seal_l.isVisible())
            self.assertFalse(card.lbl_seal_r.isVisible())

    def test_truncated_frequencies_missing_40hz(self):
        """Truncated sweep from 100 Hz to 10 kHz (missing 40 Hz band) -> returns (None, None)."""
        freq = np.linspace(100.0, 10000.0, 1000)
        mag = np.full_like(freq, 85.0)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertIsNone(status)
        self.assertIsNone(delta)

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="No 40Hz IEM",
                side="Stereo",
                freq=freq,
                mag_l=mag,
                mag_r=mag,
            )
            card.show()
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertTrue(card.lbl_seal_r.isHidden())
            self.assertTrue(card.lbl_seal.isHidden())
            self.assertFalse(card.lbl_seal_l.isVisible())
            self.assertFalse(card.lbl_seal_r.isVisible())
            self.assertFalse(card.lbl_seal.isVisible())

    def test_truncated_frequencies_missing_500hz(self):
        """Truncated sweep from 20 Hz to 100 Hz (missing 500 Hz reference band) -> returns (None, None)."""
        freq = np.linspace(20.0, 100.0, 500)
        mag = np.full_like(freq, 85.0)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertIsNone(status)
        self.assertIsNone(delta)

    def test_fewer_than_10_points(self):
        """Fewer than 10 frequency points -> returns (None, None)."""
        freq = np.array([35.0, 40.0, 45.0, 450.0, 500.0, 550.0])
        mag = np.array([90.0, 90.0, 90.0, 90.0, 90.0, 90.0])
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertIsNone(status)
        self.assertIsNone(delta)

    def test_mismatched_vector_lengths(self):
        """freq and mag length mismatch -> returns (None, None)."""
        freq = np.linspace(20.0, 20000.0, 500)
        mag = np.full(300, 85.0)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertIsNone(status)
        self.assertIsNone(delta)

    def test_none_inputs(self):
        """None inputs return (None, None)."""
        s1, d1 = HistoryCardWidget.compute_seal_for_channel(None, None)
        s2, d2 = HistoryCardWidget.compute_seal_for_channel(np.linspace(20, 20000, 100), None)
        s3, d3 = HistoryCardWidget.compute_seal_for_channel(None, np.full(100, 80.0))
        self.assertIsNone(s1)
        self.assertIsNone(d1)
        self.assertIsNone(s2)
        self.assertIsNone(d2)
        self.assertIsNone(s3)
        self.assertIsNone(d3)

    def test_nan_or_infinite_values(self):
        """NaN or Inf values in magnitude array do not cause unhandled crash."""
        freq = np.linspace(20.0, 20000.0, 1000)
        mag_nan = np.full_like(freq, 85.0)
        mask_40 = (freq >= 35.0) & (freq <= 45.0)
        mag_nan[mask_40] = np.nan
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag_nan)
        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="NaN IEM",
                side="Stereo",
                freq=freq,
                mag_l=mag_nan,
                mag_r=mag_nan,
            )
            card.show()
            # Must not crash


class TestProKitGating(unittest.TestCase):
    """Test that all seal indicators and tip badges strictly obey ProKit unlock state."""

    def setUp(self):
        self.app = get_qapp()

    def test_locked_state_hides_all_prokit_widgets(self):
        """When ProKit is locked, lbl_seal, lbl_seal_l, lbl_seal_r, and lbl_tip_badge are hidden."""
        with patch.object(config, "is_prokit_unlocked", return_value=False):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Gated IEM",
                side="Stereo",
                seal_l=-2.0,
                seal_r=-4.0,
                tip_id=4,
                tip_name="ProKit V1",
            )
            card.show()
            self.assertTrue(card.lbl_tip_badge.isHidden())
            self.assertTrue(card.lbl_seal.isHidden())
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertTrue(card.lbl_seal_r.isHidden())
            self.assertFalse(card.lbl_tip_badge.isVisible())
            self.assertFalse(card.lbl_seal.isVisible())
            self.assertFalse(card.lbl_seal_l.isVisible())
            self.assertFalse(card.lbl_seal_r.isVisible())

    def test_unlocked_state_shows_prokit_widgets(self):
        """When ProKit is unlocked, lbl_seal, lbl_seal_l, lbl_seal_r, and lbl_tip_badge are visible."""
        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Gated IEM",
                side="Stereo",
                seal_l=-2.0,
                seal_r=-4.0,
                tip_id=4,
                tip_name="ProKit V1",
            )
            card.show()
            self.assertFalse(card.lbl_tip_badge.isHidden())
            self.assertFalse(card.lbl_seal.isHidden())
            self.assertFalse(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_r.isHidden())
            self.assertTrue(card.lbl_tip_badge.isVisible())
            self.assertTrue(card.lbl_seal.isVisible())
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())

    def test_dynamic_unlock_toggle(self):
        """Calling update_prokit_visibility dynamically switches visibility on existing card."""
        with patch.object(config, "is_prokit_unlocked", return_value=False):
            card = HistoryCardWidget(
                timestamp="2026-09-22 10:00:00",
                iem_name="Gated IEM",
                side="Stereo",
                seal_l=-2.0,
                seal_r=-4.0,
            )
            card.show()
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_l.isVisible())

            # Now unlock dynamically
            card.update_prokit_visibility(unlocked=True)
            self.assertFalse(card.lbl_seal_l.isHidden())
            self.assertTrue(card.lbl_seal_l.isVisible())
            self.assertTrue(card.lbl_seal_r.isVisible())
            self.assertTrue(card.lbl_seal.isVisible())

            # Re-lock
            card.update_prokit_visibility(unlocked=False)
            self.assertTrue(card.lbl_seal_l.isHidden())
            self.assertFalse(card.lbl_seal_l.isVisible())
            self.assertFalse(card.lbl_seal_r.isVisible())
            self.assertFalse(card.lbl_seal.isVisible())


class TestHistoryWidgetDatabaseIntegration(unittest.TestCase):
    """
    CRITICAL SAFETY:
    Full integration testing of HistoryWidget.load_history() against an isolated temporary database.
    NEVER touches inearsnitch.db.
    """

    def setUp(self):
        self.app = get_qapp()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_history.db")

        # Initialize isolated database with full schema
        self.db = database.DatabaseManager(self.db_path)

        # Create test musician and IEM
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO Musicians (name) VALUES ('Test Musician')")
        self.musician_id = cur.lastrowid
        cur.execute("INSERT INTO IEM_Models (musician_id, model_name) VALUES (?, 'Test InEar')", (self.musician_id,))
        self.iem_id = cur.lastrowid
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_load_history_asymmetric_and_mono_measurements(self):
        """
        Populate isolated DB with:
        1. Asymmetric stereo: L = -5.0 dB (OK), R = -15.0 dB (LEAK), tip_id=4 (ProKit V1)
        2. Threshold test: L = -11.8 dB (OK), R = -11.9 dB (LEAK), tip_id=5 (ProKit V2)
        3. Mono Left: L = -2.0 dB (OK), R = None, tip_id=3 (Standard Foam)
        4. Mono Right: L = None, R = -16.0 dB (LEAK), tip_id=1 (Unbekannt)
        5. Corrupted/Empty BLOB: frequencies empty, tip_id=1
        Verify HistoryWidget.load_history() creates correct cards with exact seal & tip properties.
        """
        # 1. Asymmetric stereo
        f, ml_1 = make_sweep_with_exact_delta(-5.0)
        _, mr_1 = make_sweep_with_exact_delta(-15.0)
        phase = np.zeros_like(f)
        self.db.save_measurement(self.iem_id, f, ml_1, mr_1, phase, phase, tip_id=4)

        # 2. Threshold boundary
        _, ml_2 = make_sweep_with_exact_delta(-11.8)
        _, mr_2 = make_sweep_with_exact_delta(-11.9)
        self.db.save_measurement(self.iem_id, f, ml_2, mr_2, phase, phase, tip_id=5)

        # 3. Mono Left
        _, ml_3 = make_sweep_with_exact_delta(-2.0)
        self.db.save_measurement(self.iem_id, f, ml_3, None, phase, None, tip_id=3)

        # 4. Mono Right
        _, mr_4 = make_sweep_with_exact_delta(-16.0)
        self.db.save_measurement(self.iem_id, f, None, mr_4, None, phase, tip_id=1)

        # 5. Corrupted / Empty
        empty_f = np.array([], dtype=np.float64)
        empty_m = np.array([], dtype=np.float64)
        self.db.save_measurement(self.iem_id, empty_f, empty_m, empty_m, empty_m, empty_m, tip_id=1)

        # Set distinct timestamps so order is completely predictable
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM Measurements ORDER BY id ASC")
        ids = [r[0] for r in cur.fetchall()]
        self.assertEqual(len(ids), 5)
        timestamps = [
            "2026-09-22 10:01:00",  # Asymmetric (id=ids[0])
            "2026-09-22 10:02:00",  # Threshold (id=ids[1])
            "2026-09-22 10:03:00",  # Mono Left (id=ids[2])
            "2026-09-22 10:04:00",  # Mono Right (id=ids[3])
            "2026-09-22 10:05:00",  # Corrupt / Empty (id=ids[4])
        ]
        for mid, ts in zip(ids, timestamps):
            cur.execute("UPDATE Measurements SET timestamp = ? WHERE id = ?", (ts, mid))
        conn.commit()
        conn.close()

        # Instantiate HistoryWidget pointing strictly to isolated db
        hw = HistoryWidget()
        hw.db_path = self.db_path
        hw.show()

        with patch.object(config, "is_prokit_unlocked", return_value=True):
            hw.load_history(self.musician_id)
            self.assertEqual(hw.list_widget.count(), 5)

            # SQLite queries ORDER BY timestamp DESC, so items are in reverse timestamp order:
            # Index 0: Corrupted / Empty (10:05:00)
            # Index 1: Mono Right (10:04:00)
            # Index 2: Mono Left (10:03:00)
            # Index 3: Threshold (10:02:00)
            # Index 4: Asymmetric (10:01:00)

            # Item 0: Corrupted / Empty
            item_corrupt = hw.list_widget.item(0)
            card_corrupt = hw.list_widget.itemWidget(item_corrupt)
            card_corrupt.show()
            self.assertTrue(card_corrupt.lbl_seal_l.isHidden())
            self.assertTrue(card_corrupt.lbl_seal_r.isHidden())
            self.assertTrue(card_corrupt.lbl_seal.isHidden())

            # Item 1: Mono Right (L=None, R=-16.0 dB LEAK)
            item_mr = hw.list_widget.item(1)
            card_mr = hw.list_widget.itemWidget(item_mr)
            card_mr.show()
            self.assertTrue(card_mr.lbl_seal_l.isHidden())
            self.assertFalse(card_mr.lbl_seal_r.isHidden())
            self.assertEqual(card_mr.lbl_seal_r.text(), "R: LEAK")
            self.assertEqual(card_mr.lbl_seal.text(), "Seal R: -16.0dB")

            # Item 2: Mono Left (L=-2.0 dB OK, R=None)
            item_ml = hw.list_widget.item(2)
            card_ml = hw.list_widget.itemWidget(item_ml)
            card_ml.show()
            self.assertFalse(card_ml.lbl_seal_l.isHidden())
            self.assertTrue(card_ml.lbl_seal_r.isHidden())
            self.assertEqual(card_ml.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card_ml.lbl_seal.text(), "Seal L: -2.0dB")

            # Item 3: Threshold boundary (L=-11.8 dB OK, R=-11.9 dB LEAK)
            item_thresh = hw.list_widget.item(3)
            card_thresh = hw.list_widget.itemWidget(item_thresh)
            card_thresh.show()
            self.assertFalse(card_thresh.lbl_seal_l.isHidden())
            self.assertFalse(card_thresh.lbl_seal_r.isHidden())
            self.assertEqual(card_thresh.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card_thresh.lbl_seal_r.text(), "R: LEAK")
            self.assertEqual(card_thresh.seal_text, "Seal: L -11.8dB | R -11.9dB")

            # Item 4: Asymmetric stereo (L=-5.0 dB OK, R=-15.0 dB LEAK)
            item_asym = hw.list_widget.item(4)
            card_asym = hw.list_widget.itemWidget(item_asym)
            card_asym.show()
            self.assertFalse(card_asym.lbl_seal_l.isHidden())
            self.assertFalse(card_asym.lbl_seal_r.isHidden())
            self.assertEqual(card_asym.lbl_seal_l.text(), "L: OK")
            self.assertEqual(card_asym.lbl_seal_r.text(), "R: LEAK")
            self.assertEqual(card_asym.seal_text, "Seal: L -5.0dB | R -15.0dB")
            # Verify tip badge
            self.assertFalse(card_asym.lbl_tip_badge.isHidden())
            self.assertIn("V27 Rounded", card_asym.lbl_tip_badge.text())

            # Now test update_prokit_ui_visibility(False)
            hw.update_prokit_ui_visibility(unlocked=False)
            for i in range(5):
                card = hw.list_widget.itemWidget(hw.list_widget.item(i))
                self.assertTrue(card.lbl_seal_l.isHidden(), f"Card {i} seal_l should be hidden when locked")
                self.assertTrue(card.lbl_seal_r.isHidden(), f"Card {i} seal_r should be hidden when locked")
                self.assertTrue(card.lbl_seal.isHidden(), f"Card {i} seal should be hidden when locked")
                self.assertTrue(card.lbl_tip_badge.isHidden(), f"Card {i} tip badge should be hidden when locked")

            # Re-unlock
            hw.update_prokit_ui_visibility(unlocked=True)
            self.assertFalse(card_asym.lbl_seal_l.isHidden())
            self.assertFalse(card_asym.lbl_seal_r.isHidden())
            self.assertFalse(card_asym.lbl_tip_badge.isHidden())


class TestAdversarialFuzzAndStress(unittest.TestCase):
    """Deep adversarial stress, fuzzing, and corrupted BLOB tests."""

    def setUp(self):
        self.app = get_qapp()

    def test_randomized_monte_carlo_sweeps(self):
        """100 randomized sweeps with random base SPL, random deltas, and noise."""
        np.random.seed(42)
        for i in range(100):
            target_delta = np.random.uniform(-35.0, 15.0)
            base_spl = np.random.uniform(50.0, 110.0)
            freq, mag = make_sweep_with_exact_delta(target_delta, base_spl)
            status, computed_delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
            expected_delta = float(round(target_delta, 1))
            self.assertEqual(computed_delta, expected_delta)
            if expected_delta >= -11.8:
                self.assertEqual(status, "OK", f"Iteration {i}: delta {expected_delta} should be OK")
            else:
                self.assertEqual(status, "LEAK", f"Iteration {i}: delta {expected_delta} should be LEAK")

    def test_corrupted_byte_lengths_in_blob_decoding(self):
        """Corrupted byte lengths (e.g. 7 bytes, 13 bytes) that cannot decode as float64."""
        corrupted_bytes = b"CORRUPT" # 7 bytes, not multiple of 8
        try:
            arr = np.frombuffer(corrupted_bytes, dtype=np.float64)
        except ValueError:
            arr = None
        # Should gracefully return None, None
        status, delta = HistoryCardWidget.compute_seal_for_channel(arr, arr)
        self.assertIsNone(status)
        self.assertIsNone(delta)

    def test_rapid_dynamic_updates_stress(self):
        """Stress update set_seal 100 times rapidly with alternating values."""
        with patch.object(config, "is_prokit_unlocked", return_value=True):
            card = HistoryCardWidget("ts", "iem", "Stereo")
            card.show()
            for i in range(100):
                l_val = -5.0 if i % 2 == 0 else -15.0
                r_val = -15.0 if i % 2 == 0 else -5.0
                card.set_seal(l_val, r_val)
                expected_l = "OK" if l_val >= -11.8 else "LEAK"
                expected_r = "OK" if r_val >= -11.8 else "LEAK"
                self.assertEqual(card.seal_l_status, expected_l)
                self.assertEqual(card.seal_r_status, expected_r)
                self.assertEqual(card.lbl_seal_l.text(), f"L: {expected_l}")
                self.assertEqual(card.lbl_seal_r.text(), f"R: {expected_r}")

    def test_extreme_magnitude_values(self):
        """Extreme magnitude values (+300 dB, -300 dB) handled without numerical overflow."""
        freq, mag = make_sweep_with_exact_delta(500.0, base_spl=0.0)
        status, delta = HistoryCardWidget.compute_seal_for_channel(freq, mag)
        self.assertEqual(status, "OK")
        self.assertEqual(delta, 500.0)

        freq_low, mag_low = make_sweep_with_exact_delta(-500.0, base_spl=0.0)
        status_low, delta_low = HistoryCardWidget.compute_seal_for_channel(freq_low, mag_low)
        self.assertEqual(status_low, "LEAK")
        self.assertEqual(delta_low, -500.0)


if __name__ == "__main__":
    unittest.main()
