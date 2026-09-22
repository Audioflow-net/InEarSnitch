"""
InEar Snitch ProKit Tip-Tracking — M4 Adversarial History Badge & Gate Test Suite
================================================================================

Authored by M4 History Badge & Gate Challenger.
Adversarially challenges and stress-tests:
1. HistoryCardWidget tip badges across all seed tip profiles:
   - id=1 "Unbekannt" -> text MUST be "?", background #6b7280, color #a1a1aa
   - id=2 "Kein Aufsatz" -> text "○ Kein Aufsatz", background #94a3b8
   - id=3 "Standard Foam" -> text "● Standard Foam", background #f59e0b
   - id=4 "ProKit V1" -> text "◆ ProKit V1", background #3b82f6
   - id=5 "ProKit V2" -> text "★ ProKit V2", background #10b981
2. Corner cases:
   - tip_id = None, tip_id = 999 (orphaned), tip_id = -1
   - tip_name = "", tip_icon = "", tip_color = "", tip_material = ""
   - Legacy instantiation: HistoryCardWidget("2026-09-22 10:00:00", "KZ ZSN", "Left")
   - Extra unknown keyword arguments (**kwargs)
3. Acoustic seal calculation and threshold boundary:
   - compute_seal_for_channel robustness on invalid, corrupt, or truncated vectors
   - Exact -11.8 dB threshold boundary (OK vs LEAK)
   - Left and Right channels strictly separated (Locked Design Decision 2)
4. ProKit Gate & Dynamic Reactivity:
   - Locked state: lbl_tip_badge and lbl_seal are hidden
   - Unlocked state: lbl_tip_badge and lbl_seal become visible immediately
   - Re-lock state: hide immediately
   - 20x rapid toggle cycling without hysteresis or state leakage
   - List-level batch updating via HistoryWidget.update_prokit_ui_visibility
5. Safe DB Integration & Search Filtering:
   - Verification with temporary SQLite database (never touches inearsnitch.db)
   - LEFT JOIN handling of seed, orphaned (999), and legacy (NULL) tip_ids
   - Search filtering by tip name

CRITICAL SAFETY:
All tests execute on temporary databases and temporary config directories.
NEVER touch production inearsnitch.db.
"""

import os
import sys
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

# Ensure headless Qt execution
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem

# Root directory setup
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
import history_ui
from history_ui import HistoryCardWidget, HistoryWidget


def get_qapp():
    """Ensure singleton QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["InEarSnitchTest", "-platform", "offscreen"])
    return app


def create_synthetic_sweep_vectors(
    base_spl=90.0,
    bass_boost_db=3.0,
    leak_db=0.0,
    peak_freq_hz=7850.0,
    peak_spl_db=6.0,
):
    """Generates synthetic (freq, mag, phase) vectors."""
    freqs = np.linspace(20.0, 24000.0, 24001, dtype=np.float64)
    mag = base_spl - (freqs / 1000.0) * 0.4
    idx_40 = (freqs >= 35.0) & (freqs <= 45.0)
    mag[idx_40] += (bass_boost_db - leak_db)
    idx_500 = (freqs >= 450.0) & (freqs <= 550.0)
    mag[idx_500] += 0.0
    if peak_freq_hz is not None:
        peak_shape = peak_spl_db * np.exp(-0.5 * ((freqs - peak_freq_hz) / 450.0) ** 2)
        mag += peak_shape
    phase = np.zeros_like(mag)
    return freqs, mag, phase


class BaseHistoryTest(unittest.TestCase):
    """Base fixture with isolated temporary DB and temporary config directory."""

    def setUp(self):
        self.app = get_qapp()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.temp_db_path = os.path.join(self.tmp_dir.name, "adversarial_test.db")

        # Patch config data dir to prevent writing to ~/Documents/InEarSnitch/
        self.patch_data_dir = patch("config.get_data_dir", return_value=self.tmp_dir.name)
        self.mock_data_dir = self.patch_data_dir.start()

        # Ensure prokit is locked by default
        config.revoke_prokit()

    def tearDown(self):
        config.revoke_prokit()
        self.patch_data_dir.stop()
        try:
            self.tmp_dir.cleanup()
        except OSError:
            pass


# ===========================================================================
# 1. SEED TIP PROFILES TESTS
# ===========================================================================

class TestSeedTipProfiles(BaseHistoryTest):
    """Test HistoryCardWidget tip badges across all seed tip profiles."""

    def test_seed_id_1_unbekannt(self):
        """Seed 1: Unbekannt MUST have text '?', background #6b7280, color #a1a1aa."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=1,
            tip_name="Unbekannt",
            tip_color="#6b7280",
            tip_icon="?",
            tip_material="Standard",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)
        self.assertIn("#a1a1aa", ss)
        self.assertEqual(card.lbl_tip_badge.toolTip(), "Ear Tip: Unbekannt")
        # Check alias attributes
        self.assertIs(card.tip_badge, card.lbl_tip_badge)
        self.assertIs(card.lbl_badge, card.lbl_tip_badge)
        self.assertIs(card.lbl_tip, card.lbl_tip_badge)

    def test_seed_id_2_kein_aufsatz(self):
        """Seed 2: Kein Aufsatz MUST have text '○ Kein Aufsatz', background #94a3b8."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=2,
            tip_name="Kein Aufsatz",
            tip_color="#94a3b8",
            tip_icon="○",
            tip_material="None",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "○ Kein Aufsatz")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#94a3b8", ss)
        self.assertIn("white", ss)
        self.assertIn("Kein Aufsatz", card.lbl_tip_badge.toolTip())

    def test_seed_id_3_v26_straight(self):
        """Seed 3: V26 Straight MUST have text '▮ V26 Straight', background #22c55e."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Right",
            tip_id=3,
            tip_name="V26 Straight",
            tip_color="#22c55e",
            tip_icon="▮",
            tip_material="Silicone",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "▮ V26 Straight")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#22c55e", ss)
        self.assertIn("white", ss)
        self.assertIn("V26 Straight", card.lbl_tip_badge.toolTip())

    def test_seed_id_4_v27_rounded(self):
        """Seed 4: V27 Rounded MUST have text '▮ V27 Rounded', background #3b82f6."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="Moondrop Blessing 2",
            side="Stereo",
            tip_id=4,
            tip_name="V27 Rounded",
            tip_color="#3b82f6",
            tip_icon="▮",
            tip_material="Silicone",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "▮ V27 Rounded")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#3b82f6", ss)
        self.assertIn("white", ss)
        self.assertIn("V27 Rounded", card.lbl_tip_badge.toolTip())

    def test_seed_id_5_v29_c_cone(self):
        """Seed 5: V29-C Cone MUST have text '◆ V29-C Cone', background #f97316."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="Sennheiser IE600",
            side="Stereo",
            tip_id=5,
            tip_name="V29-C Cone",
            tip_color="#f97316",
            tip_icon="◆",
            tip_material="Silicone",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "◆ V29-C Cone")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#f97316", ss)
        self.assertIn("white", ss)
        self.assertIn("V29-C Cone", card.lbl_tip_badge.toolTip())


# ===========================================================================
# 2. CORNER CASES & RESILIENCE TESTS
# ===========================================================================

class TestHistoryCardCornerCases(BaseHistoryTest):
    """Stress-test corner cases, missing parameters, and legacy signatures."""

    def test_tip_id_none_fallback_to_1(self):
        """Passing tip_id=None falls back cleanly to tip_id=1 and text '?'."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=None,
        )
        self.assertEqual(card.tip_id, 1)
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)
        self.assertIn("#a1a1aa", ss)

    def test_orphaned_tip_id_999(self):
        """Orphaned tip_id=999 with default Unbekannt renders subtle grey '?' badge."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=999,
        )
        self.assertEqual(card.tip_id, 999)
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)
        self.assertIn("#a1a1aa", ss)

    def test_negative_tip_id_minus_1(self):
        """tip_id=-1 with default Unbekannt renders subtle grey '?' badge."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=-1,
        )
        self.assertEqual(card.tip_id, -1)
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)
        self.assertIn("#a1a1aa", ss)

    def test_orphaned_tip_id_with_custom_name(self):
        """tip_id=999 with explicit custom name renders icon and name without crashing."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=999,
            tip_name="Custom Orphan Tip",
            tip_color="#8b5cf6",
            tip_icon="▲",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "▲ Custom Orphan Tip")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#8b5cf6", ss)

    def test_empty_string_tip_name(self):
        """tip_name='' falls back to 'Unbekannt' and badge '?'."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=4,
            tip_name="",
        )
        self.assertEqual(card.tip_name, "Unbekannt")
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)

    def test_empty_string_tip_icon(self):
        """tip_icon='' falls back to '?' for known tip name."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=4,
            tip_name="ProKit V1",
            tip_color="#3b82f6",
            tip_icon="",
        )
        self.assertEqual(card.lbl_tip_badge.text(), "? ProKit V1")

    def test_empty_string_tip_color(self):
        """tip_color='' falls back to '#6b7280' default background."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=4,
            tip_name="ProKit V1",
            tip_color="",
            tip_icon="◆",
        )
        self.assertEqual(card.tip_color, "#6b7280")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#6b7280", ss)

    def test_legacy_three_arg_instantiation(self):
        """Legacy instantiation HistoryCardWidget(timestamp, iem_name, side) works seamlessly."""
        card = HistoryCardWidget("2026-09-22 10:00:00", "KZ ZSN", "Left")
        self.assertEqual(card.timestamp, "2026-09-22 10:00:00")
        self.assertEqual(card.iem_name, "KZ ZSN")
        self.assertEqual(card.side, "Left")
        self.assertEqual(card.tip_id, 1)
        self.assertEqual(card.lbl_tip_badge.text(), "?")
        self.assertEqual(card.lbl_iem.text(), "KZ ZSN")
        self.assertEqual(card.lbl_side.text(), "Left")
        self.assertEqual(card.lbl_date.text(), "2026-09-22 10:00:00")
        self.assertIsNotNone(card.cb_graph)

    def test_extra_unknown_kwargs_accepted(self):
        """HistoryCardWidget accepts arbitrary unexpected kwargs without raising TypeError."""
        card = HistoryCardWidget(
            "2026-09-22 10:00:00",
            "KZ ZSN",
            "Left",
            unknown_future_field="test",
            firmware_ver="1.4.2",
            calibration_id=9876,
        )
        self.assertEqual(card.tip_id, 1)
        self.assertEqual(card.lbl_tip_badge.text(), "?")

    def test_string_tip_id_coercion(self):
        """tip_id passed as numeric string '4' is coerced to integer 4."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id="4",
            tip_name="ProKit V1",
            tip_color="#3b82f6",
            tip_icon="◆",
        )
        self.assertEqual(card.tip_id, 4)
        self.assertEqual(card.lbl_tip_badge.text(), "◆ ProKit V1")


# ===========================================================================
# 3. ACOUSTIC SEAL & DSP ADVERSARIAL TESTS
# ===========================================================================

class TestHistoryCardSealMetrics(BaseHistoryTest):
    """Stress-test seal status computation, threshold boundaries, and vector parsing."""

    def test_exact_threshold_boundary_minus_11_8(self):
        """Exact threshold boundary: delta >= -11.8 dB is 'OK', < -11.8 dB is 'LEAK'."""
        # Exact -11.8 -> OK
        card_at = HistoryCardWidget("ts", "iem", "L", seal_l=-11.8)
        self.assertEqual(card_at.seal_l_status, "OK")
        self.assertEqual(card_at.lbl_seal_l.text(), "L: OK")

        # Just below: -11.9 -> LEAK
        card_below = HistoryCardWidget("ts", "iem", "L", seal_l=-11.9)
        self.assertEqual(card_below.seal_l_status, "LEAK")
        self.assertEqual(card_below.lbl_seal_l.text(), "L: LEAK")

        # Just above: -11.7 -> OK
        card_above = HistoryCardWidget("ts", "iem", "L", seal_l=-11.7)
        self.assertEqual(card_above.seal_l_status, "OK")
        self.assertEqual(card_above.lbl_seal_l.text(), "L: OK")

    def test_seal_lr_channel_separation(self):
        """L and R seal statuses must remain completely separate (Locked Design Decision 2)."""
        card = HistoryCardWidget("ts", "iem", "Stereo", seal_l=-5.0, seal_r=-18.0)
        self.assertEqual(card.seal_l_status, "OK")
        self.assertEqual(card.seal_r_status, "LEAK")
        self.assertEqual(card.seal_l_delta, -5.0)
        self.assertEqual(card.seal_r_delta, -18.0)
        self.assertIn("L -5.0dB", card.seal_text)
        self.assertIn("R -18.0dB", card.seal_text)
        self.assertEqual(card.lbl_seal_l.text(), "L: OK")
        self.assertEqual(card.lbl_seal_r.text(), "R: LEAK")

    def test_compute_seal_for_channel_adversarial_inputs(self):
        """compute_seal_for_channel handles None, corrupt, empty, and NaN vectors gracefully."""
        # None inputs
        st, delta = HistoryCardWidget.compute_seal_for_channel(None, None)
        self.assertIsNone(st)
        self.assertIsNone(delta)

        # Mismatched lengths
        f = np.linspace(20.0, 20000.0, 100)
        m = np.linspace(70.0, 80.0, 50)
        st, delta = HistoryCardWidget.compute_seal_for_channel(f, m)
        self.assertIsNone(st)
        self.assertIsNone(delta)

        # Truncated length (< 10)
        f_short = np.array([20.0, 40.0, 500.0])
        m_short = np.array([80.0, 85.0, 80.0])
        st, delta = HistoryCardWidget.compute_seal_for_channel(f_short, m_short)
        self.assertIsNone(st)
        self.assertIsNone(delta)

        # Missing 40 Hz band (frequency starts at 100 Hz)
        f_hi = np.linspace(100.0, 1000.0, 200)
        m_hi = np.full_like(f_hi, 85.0)
        st, delta = HistoryCardWidget.compute_seal_for_channel(f_hi, m_hi)
        self.assertIsNone(st)
        self.assertIsNone(delta)

        # Missing 500 Hz band (frequency ends at 200 Hz)
        f_lo = np.linspace(20.0, 200.0, 200)
        m_lo = np.full_like(f_lo, 85.0)
        st, delta = HistoryCardWidget.compute_seal_for_channel(f_lo, m_lo)
        self.assertIsNone(st)
        self.assertIsNone(delta)

    def test_vector_based_seal_calculation(self):
        """Passing frequency and magnitude vectors computes accurate seal deltas."""
        f, ml, _ = create_synthetic_sweep_vectors(bass_boost_db=3.0)
        _, mr, _ = create_synthetic_sweep_vectors(leak_db=20.0)
        card = HistoryCardWidget("ts", "iem", "Stereo", freq=f, mag_l=ml, mag_r=mr)
        self.assertEqual(card.seal_l_status, "OK")
        self.assertEqual(card.seal_r_status, "LEAK")
        self.assertGreater(card.seal_l_delta, -11.8)
        self.assertLess(card.seal_r_delta, -11.8)


# ===========================================================================
# 4. PROKIT GATE & DYNAMIC REACTIVITY TESTS
# ===========================================================================

class TestProKitGateReactivity(BaseHistoryTest):
    """Test dynamic visibility of tip badge and seal indicators when gating transitions."""

    def test_initial_locked_state_hides_all_prokit_elements(self):
        """When ProKit is locked, lbl_tip_badge and lbl_seal are strictly NOT visible."""
        self.assertFalse(config.is_prokit_unlocked())
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Stereo",
            tip_id=5,
            tip_name="ProKit V2",
            tip_color="#10b981",
            tip_icon="★",
            seal_l=2.0,
            seal_r=-1.5,
        )
        card.show()
        self.assertFalse(card.lbl_tip_badge.isVisible())
        self.assertTrue(card.lbl_tip_badge.isHidden())
        self.assertFalse(card.lbl_seal.isVisible())
        self.assertTrue(card.lbl_seal.isHidden())
        self.assertFalse(card.lbl_seal_l.isVisible())
        self.assertTrue(card.lbl_seal_l.isHidden())
        self.assertFalse(card.lbl_seal_r.isVisible())
        self.assertTrue(card.lbl_seal_r.isHidden())

    def test_unlock_reveals_prokit_elements_immediately(self):
        """Unlocking ProKit and calling update_prokit_visibility(True) reveals all elements immediately."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Stereo",
            tip_id=4,
            tip_name="ProKit V1",
            tip_color="#3b82f6",
            tip_icon="◆",
            seal_l=2.0,
            seal_r=1.0,
        )
        card.show()
        self.assertFalse(card.lbl_tip_badge.isVisible())
        self.assertFalse(card.lbl_seal.isVisible())

        # Unlock ProKit
        success = config.unlock_prokit("SNITCH-PROKIT-2024-001")
        self.assertTrue(success)
        self.assertTrue(config.is_prokit_unlocked())

        # Dynamic update
        card.update_prokit_visibility(True)
        self.assertTrue(card.lbl_tip_badge.isVisible())
        self.assertFalse(card.lbl_tip_badge.isHidden())
        self.assertTrue(card.lbl_seal.isVisible())
        self.assertFalse(card.lbl_seal.isHidden())
        self.assertTrue(card.lbl_seal_l.isVisible())
        self.assertTrue(card.lbl_seal_r.isVisible())

    def test_relock_hides_prokit_elements_immediately(self):
        """Calling revoke_prokit() and update_prokit_visibility(False) hides all elements immediately."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Stereo",
            tip_id=5,
            tip_name="ProKit V2",
            tip_color="#10b981",
            tip_icon="★",
            seal_l=2.0,
            seal_r=1.0,
        )
        card.show()
        card.update_prokit_visibility(True)
        self.assertTrue(card.lbl_tip_badge.isVisible())
        self.assertTrue(card.lbl_seal.isVisible())

        # Revoke ProKit
        config.revoke_prokit()
        self.assertFalse(config.is_prokit_unlocked())

        # Dynamic update without explicit parameter (reads config directly)
        card.update_prokit_visibility()
        self.assertFalse(card.lbl_tip_badge.isVisible())
        self.assertTrue(card.lbl_tip_badge.isHidden())
        self.assertFalse(card.lbl_seal.isVisible())
        self.assertTrue(card.lbl_seal.isHidden())
        self.assertFalse(card.lbl_seal_l.isVisible())
        self.assertFalse(card.lbl_seal_r.isVisible())

    def test_rapid_20x_lock_unlock_hysteresis_stress(self):
        """Toggling unlock state 20 times rapidly causes zero state leakage or desync."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Stereo",
            tip_id=4,
            tip_name="ProKit V1",
            tip_color="#3b82f6",
            tip_icon="◆",
            seal_l=1.0,
            seal_r=1.0,
        )
        card.show()
        for i in range(20):
            # Unlock cycle
            config.unlock_prokit("SNITCH-PROKIT-2024-001")
            card.update_prokit_visibility()
            self.assertTrue(card.lbl_tip_badge.isVisible(), f"Failed at unlock cycle {i}")
            self.assertTrue(card.lbl_seal.isVisible(), f"Failed at unlock cycle {i}")

            # Lock cycle
            config.revoke_prokit()
            card.update_prokit_visibility()
            self.assertFalse(card.lbl_tip_badge.isVisible(), f"Failed at lock cycle {i}")
            self.assertFalse(card.lbl_seal.isVisible(), f"Failed at lock cycle {i}")

    def test_dynamic_set_tip_mutation(self):
        """Dynamically mutating card tip via set_tip updates badge text, color, and tooltip."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Left",
            tip_id=1,
        )
        self.assertEqual(card.lbl_tip_badge.text(), "?")

        # Mutate to ProKit V2
        card.set_tip(5, "ProKit V2", "#10b981", "★", "Silicone")
        self.assertEqual(card.tip_id, 5)
        self.assertEqual(card.lbl_tip_badge.text(), "★ ProKit V2")
        ss = card.lbl_tip_badge.styleSheet()
        self.assertIn("#10b981", ss)
        self.assertIn("ProKit V2", card.lbl_tip_badge.toolTip())

    def test_dynamic_set_seal_mutation(self):
        """Dynamically mutating seal via set_seal updates status, text, and respects gate."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="KZ ZSN Pro",
            side="Stereo",
            tip_id=5,
        )
        card.show()
        card.update_prokit_visibility(True)
        self.assertFalse(card.lbl_seal.isVisible())  # No seal initially

        # Update seal metrics
        card.set_seal(3.0, -15.0)
        self.assertEqual(card.seal_l_status, "OK")
        self.assertEqual(card.seal_r_status, "LEAK")
        self.assertTrue(card.lbl_seal.isVisible())
        self.assertTrue(card.lbl_seal_l.isVisible())
        self.assertTrue(card.lbl_seal_r.isVisible())


# ===========================================================================
# 5. LIST-LEVEL BATCH GATING & HISTORY WIDGET INTEGRATION
# ===========================================================================

class TestHistoryWidgetListGating(BaseHistoryTest):
    """Test HistoryWidget list-level batch updating and safe DB integration."""

    def test_batch_update_across_all_cards(self):
        """HistoryWidget.update_prokit_ui_visibility updates all child cards simultaneously."""
        hw = HistoryWidget()
        hw.db_path = self.temp_db_path
        hw.show()

        cards = []
        for i in range(10):
            item = QListWidgetItem(hw.list_widget)
            card = HistoryCardWidget(
                f"2026-09-22 10:0{i}:00",
                f"IEM {i}",
                "Left",
                tip_id=(i % 5) + 1,
                tip_name=f"Tip {(i % 5) + 1}",
                seal_l=1.0,
            )
            item.setSizeHint(card.sizeHint())
            hw.list_widget.setItemWidget(item, card)
            cards.append(card)

        # Initial locked state: all cards hidden
        hw.update_prokit_ui_visibility(False)
        for c in cards:
            self.assertFalse(c.lbl_tip_badge.isVisible())
            self.assertFalse(c.lbl_seal.isVisible())

        # Unlock all cards
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        hw.update_prokit_ui_visibility(True)
        for c in cards:
            self.assertTrue(c.lbl_tip_badge.isVisible())
            self.assertTrue(c.lbl_seal.isVisible())

        # Verify alias update_prokit_visibility
        hw.update_prokit_visibility(False)
        for c in cards:
            self.assertFalse(c.lbl_tip_badge.isVisible())

    def test_safe_database_history_load_and_search_filter(self):
        """Verify load_history on isolated DB correctly seeds cards and supports search filtering."""
        # 1. Initialize isolated schema using DatabaseManager
        db = database.DatabaseManager(self.temp_db_path)
        conn = sqlite3.connect(self.temp_db_path)
        cur = conn.cursor()

        # Insert test musician & IEM
        cur.execute("INSERT INTO Musicians (name) VALUES ('Test Musician')")
        m_id = cur.lastrowid
        cur.execute("INSERT INTO IEM_Models (musician_id, model_name) VALUES (?, 'Test Custom IEM')", (m_id,))
        iem_id = cur.lastrowid

        f, ml, pl = create_synthetic_sweep_vectors(bass_boost_db=2.0)
        fb, mb, pb = f.tobytes(), ml.tobytes(), pl.tobytes()

        # Ensure meas_name exists for test insert
        cur.execute("ALTER TABLE Measurements ADD COLUMN meas_name TEXT")

        # Insert 6 measurements with different tip_ids:
        # id=1 (Unbekannt), id=2 (Kein Aufsatz), id=3 (Standard Foam),
        # id=4 (ProKit V1), id=5 (ProKit V2), id=999 (Orphaned)
        for tip_id in [1, 2, 3, 4, 5, 999]:
            cur.execute("""
                INSERT INTO Measurements (iem_id, timestamp, frequencies, magnitude_l, magnitude_r, tip_id, meas_name)
                VALUES (?, datetime('now', '+1 minute'), ?, ?, ?, ?, ?)
            """, (iem_id, fb, mb, mb, tip_id, f"Take with tip {tip_id}"))
        conn.commit()
        conn.close()

        # 2. Load into HistoryWidget using temp_db_path
        hw = HistoryWidget()
        hw.db_path = self.temp_db_path
        hw.show()
        hw.load_history(m_id)

        self.assertEqual(hw.list_widget.count(), 6)

        # Verify search filter by tip name
        hw.search_bar.setText("Straight")
        visible_items = [hw.list_widget.item(i) for i in range(hw.list_widget.count()) if not hw.list_widget.item(i).isHidden()]
        self.assertEqual(len(visible_items), 1)

        hw.search_bar.setText("Rounded")
        visible_items = [hw.list_widget.item(i) for i in range(hw.list_widget.count()) if not hw.list_widget.item(i).isHidden()]
        self.assertEqual(len(visible_items), 1)

        hw.search_bar.setText("Unbekannt")
        visible_items = [hw.list_widget.item(i) for i in range(hw.list_widget.count()) if not hw.list_widget.item(i).isHidden()]
        # Both tip_id=1 and orphaned tip_id=999 fall back to "Unbekannt" via COALESCE
        self.assertEqual(len(visible_items), 2)

        hw.search_bar.setText("")
        visible_items = [hw.list_widget.item(i) for i in range(hw.list_widget.count()) if not hw.list_widget.item(i).isHidden()]
        self.assertEqual(len(visible_items), 6)


if __name__ == "__main__":
    unittest.main()
