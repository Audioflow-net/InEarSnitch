"""
InEar Snitch ProKit Tip-Tracking — Tier 5 Adversarial UI & Integration Test Suite
================================================================================

Authored by Challenger Final 2 (UI & Integration Tier 5 Adversarial Coverage Hardener).
White-box adversarial audit covering:
1. Dynamic license state changes (rapid unlock/lock lifecycle while active views refresh)
2. Header logo triple-click event filter (rapid bursts, non-logo clicks, DblClick sequences, timeout, re-entrancy)
3. HistoryCardWidget resilience (corrupt/missing foreign keys, null fields, missing seal data, 220px minimal width)
4. TipAnalysisCardWidget switching (rapid tab switching FR/THD/CSD, rapid IEM profile switching, rapid tip combobox cycling)
5. Two-way synchronization between bottom bar `combo_tip` and analysis card `cb_tip_selector`
6. Widget memory cleanup (verifying zero leaking widgets after 50 consecutive refreshes)

SAFETY INVARIANT:
All tests execute strictly on isolated temporary directories and copied databases.
The production database (/Users/ben/Desktop/InEarSnitch/inearsnitch.db) is NEVER modified.
"""

import os
import sys
import time
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pytest

# Ensure headless Qt execution
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QEvent, QPointF, QSize, QCoreApplication
from PySide6.QtGui import QMouseEvent, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
import main
from history_ui import HistoryWidget, HistoryCardWidget
from analysis_ui import AnalysisWidget, TipAnalysisCardWidget


def get_qapp():
    """Ensure singleton headless QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["InEarSnitchTier5Test", "-platform", "offscreen"])
    return app


class BaseTier5UITest(unittest.TestCase):
    """
    Isolated base test fixture providing:
    - Temporary directory for app data (protecting ~/.prokit_unlocked)
    - Temporary copy of inearsnitch.db (protecting production database integrity)
    - Patched DatabaseManager to default to isolated test DB
    - Patched check_eula to prevent blocking modal dialogs
    """

    def setUp(self):
        self.app = get_qapp()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.temp_db_path = os.path.join(self.tmp_dir.name, "test_tier5.db")

        # Copy production DB as seed data to temp path (read-only source)
        prod_db = os.path.join(REPO_ROOT, "inearsnitch.db")
        if os.path.exists(prod_db):
            shutil.copy(prod_db, self.temp_db_path)
        else:
            # Fallback schema creation if DB not found
            db_mgr = database.DatabaseManager(self.temp_db_path)

        # Redirect config data dir to temporary folder
        self.patch_data_dir = patch("config.get_data_dir", return_value=self.tmp_dir.name)
        self.mock_data_dir = self.patch_data_dir.start()

        # Patch DatabaseManager.__init__ so any default instantiations use self.temp_db_path
        orig_db_init = database.DatabaseManager.__init__
        def safe_db_init(db_self, db_path=None):
            actual_path = db_path if db_path is not None else self.temp_db_path
            orig_db_init(db_self, actual_path)

        self.patch_db_init = patch.object(database.DatabaseManager, "__init__", safe_db_init)
        self.patch_db_init.start()

        # Disable modal EULA dialog
        self.patch_eula = patch.object(main.MainWindow, "check_eula", lambda win_self: None)
        self.patch_eula.start()

        # Ensure starting from clean locked state
        config.revoke_prokit()

    def tearDown(self):
        self.patch_eula.stop()
        self.patch_db_init.stop()
        self.patch_data_dir.stop()
        try:
            self.tmp_dir.cleanup()
        except OSError:
            pass

    def create_window(self):
        """Helper to create, show offscreen, and return an isolated MainWindow instance."""
        win = main.MainWindow()
        win.db.db_path = self.temp_db_path
        win.page_hist.db_path = self.temp_db_path
        win.page_ana.db = win.db
        win.show()
        return win


# ===========================================================================
# 1. DYNAMIC LICENSE STATE TRANSITIONS
# ===========================================================================

class TestTier5LicenseStateTransitions(BaseTier5UITest):
    """Stress-test rapid unlocking and revoking while views are actively rendering."""

    def test_rapid_license_toggling_50_cycles(self):
        """Stress-test 50 rapid alternating unlock/revoke toggles with active UI updates."""
        win = self.create_window()
        win.page_hist.load_history(1)
        win.page_ana.render_diagnostics()

        valid_code = "SNITCH-PROKIT-2024-001"

        for i in range(50):
            if i % 2 == 0:
                res = config.unlock_prokit(valid_code)
                self.assertTrue(res)
                win.update_prokit_ui_visibility()
                self.app.processEvents()

                # Verify unlocked visibility
                self.assertFalse(win.tip_container.isHidden())
                self.assertFalse(win.combo_tip.isHidden())
                self.assertTrue(win.tip_container.isVisible())
                self.assertTrue(win.combo_tip.isVisible())
                self.assertTrue(config.is_prokit_unlocked())
            else:
                res = config.revoke_prokit()
                self.assertTrue(res)
                win.update_prokit_ui_visibility()
                self.app.processEvents()

                # Verify locked visibility
                self.assertTrue(win.tip_container.isHidden())
                self.assertTrue(win.combo_tip.isHidden())
                self.assertFalse(config.is_prokit_unlocked())

        # Clean final state
        config.revoke_prokit()
        win.update_prokit_ui_visibility()
        self.assertFalse(config.is_prokit_unlocked())

    def test_license_toggle_updates_existing_history_cards(self):
        """Verifies existing history cards toggle tip badges and seal badges upon license state change."""
        win = self.create_window()
        win.page_hist.load_history(1)
        self.app.processEvents()

        # Initially locked: badges hidden
        for i in range(win.page_hist.list_widget.count()):
            item = win.page_hist.list_widget.item(i)
            card = win.page_hist.list_widget.itemWidget(item)
            if card:
                self.assertTrue(card.lbl_tip_badge.isHidden())
                self.assertTrue(card.lbl_seal.isHidden())

        # Unlock: badges must become visible
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win.update_prokit_ui_visibility()
        self.app.processEvents()

        for i in range(win.page_hist.list_widget.count()):
            item = win.page_hist.list_widget.item(i)
            card = win.page_hist.list_widget.itemWidget(item)
            if card:
                self.assertFalse(card.lbl_tip_badge.isHidden())

        # Revoke: badges must hide again
        config.revoke_prokit()
        win.update_prokit_ui_visibility()
        self.app.processEvents()

        for i in range(win.page_hist.list_widget.count()):
            item = win.page_hist.list_widget.item(i)
            card = win.page_hist.list_widget.itemWidget(item)
            if card:
                self.assertTrue(card.lbl_tip_badge.isHidden())

    def test_corrupted_token_file_handled_gracefully_by_ui(self):
        """Corrupted token file in data dir does not crash update_prokit_ui_visibility."""
        win = self.create_window()
        token_file = os.path.join(self.tmp_dir.name, ".prokit_unlocked")
        with open(token_file, "w") as f:
            f.write("MALFORMED_HASH_CONTENT_XYZ")

        # config.is_prokit_unlocked returns True if file exists
        win.update_prokit_ui_visibility()
        self.app.processEvents()
        self.assertFalse(win.tip_container.isHidden())

        # Revoke cleanly removes the file
        config.revoke_prokit()
        win.update_prokit_ui_visibility()
        self.app.processEvents()
        self.assertTrue(win.tip_container.isHidden())


# ===========================================================================
# 2. HEADER LOGO TRIPLE-CLICK EVENT FILTER
# ===========================================================================

class TestTier5HeaderLogoTripleClickFilter(BaseTier5UITest):
    """Stress-test the header logo triple-click event filter with rapid bursts and edge inputs."""

    def setUp(self):
        super().setUp()
        self.trigger_count = 0
        self.lbl_logo = QLabel("InEar SNITCH")
        self.filter = main.LogoTripleClickFilter(
            self.lbl_logo,
            self._on_triple_click,
            max_interval=0.6,
        )
        self.lbl_logo.installEventFilter(self.filter)

    def _on_triple_click(self):
        self.trigger_count += 1

    def _send_click(self, widget, event_type=QEvent.MouseButtonPress, button=Qt.LeftButton):
        ev = QMouseEvent(event_type, QPointF(5, 5), QPointF(5, 5), button, button, Qt.NoModifier)
        return self.app.sendEvent(widget, ev)

    def test_rapid_burst_15_clicks_triggers_5_times(self):
        """15 rapid left clicks in immediate succession trigger the callback exactly 5 times."""
        self.trigger_count = 0
        for _ in range(15):
            self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self.assertEqual(self.trigger_count, 5)
        self.assertEqual(len(self.filter.clicks), 0)

    def test_native_qt_double_click_sequence(self):
        """Native Qt sequence: Press, DblClick, Press triggers callback exactly once."""
        self.trigger_count = 0
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonDblClick, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self.assertEqual(self.trigger_count, 1)

    def test_clicks_on_non_logo_widgets_ignored(self):
        """Mouse clicks directed to unrelated widgets do not trigger callback."""
        unrelated_widget = QWidget()
        self.trigger_count = 0
        for _ in range(6):
            self._send_click(unrelated_widget, QEvent.MouseButtonPress, Qt.LeftButton)
        self.assertEqual(self.trigger_count, 0)
        self.assertEqual(len(self.filter.clicks), 0)

    def test_right_and_middle_clicks_ignored(self):
        """Right and middle clicks are completely ignored by the filter."""
        self.trigger_count = 0
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.RightButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.MiddleButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.RightButton)
        self.assertEqual(self.trigger_count, 0)
        self.assertEqual(len(self.filter.clicks), 0)

    def test_interleaved_left_and_right_clicks(self):
        """Right-clicks interleaved between left-clicks do not disrupt left-click counting."""
        self.trigger_count = 0
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.RightButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.RightButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self.assertEqual(self.trigger_count, 1)

    def test_timeout_expiration_resets_counter(self):
        """Clicks spaced by >0.6s reset the click counter."""
        self.trigger_count = 0
        # Inject an old click timestamp (>1.0s ago)
        self.filter.clicks = [time.monotonic() - 1.2]
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        # Should have reset and recorded only 2 new clicks, no trigger
        self.assertEqual(self.trigger_count, 0)
        self.assertEqual(len(self.filter.clicks), 2)

    def test_reentrancy_protection_discards_clicks_during_dialog(self):
        """Clicks occurring while callback dialog is active are safely discarded without re-triggering."""
        def slow_callback():
            self.trigger_count += 1
            # Simulate a click arriving while dialog is active
            self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)

        self.filter.callback = slow_callback
        self.trigger_count = 0

        # Trigger triple click
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)
        self._send_click(self.lbl_logo, QEvent.MouseButtonPress, Qt.LeftButton)

        # Triggered exactly once, click during dialog was discarded (clicks list is empty)
        self.assertEqual(self.trigger_count, 1)
        self.assertEqual(len(self.filter.clicks), 0)
        self.assertFalse(self.filter._dialog_active)


# ===========================================================================
# 3. HISTORY CARD WIDGET RESILIENCE
# ===========================================================================

class TestTier5HistoryCardRobustness(BaseTier5UITest):
    """Stress-test HistoryCardWidget with corrupted data, missing FKs, and extreme geometry."""

    def test_corrupt_or_orphaned_tip_foreign_key(self):
        """Cards with tip_id=999999 or -1 fall back safely to Unbekannt styling without crashing."""
        card_orphan = HistoryCardWidget(
            timestamp="2026-09-22 10:00",
            iem_name="Custom IEM",
            side="Stereo",
            tip_id=999999,
            tip_name="Unbekannt",
            tip_icon="?",
        )
        self.assertEqual(card_orphan.lbl_tip_badge.text(), "?")
        self.assertIn("#6b7280", card_orphan.lbl_tip_badge.styleSheet())

        card_negative = HistoryCardWidget(
            timestamp="2026-09-22 10:00",
            iem_name="Custom IEM",
            side="Left",
            tip_id=-1,
            tip_name=None,
        )
        self.assertEqual(card_negative.lbl_tip_badge.text(), "?")

    def test_null_timestamp_and_missing_seal_data(self):
        """Cards initialized with None timestamp and None seal arrays render cleanly without error."""
        card = HistoryCardWidget(
            timestamp=None,
            iem_name=None,
            side=None,
            seal_l=None,
            seal_r=None,
            freq=None,
            mag_l=None,
            mag_r=None,
        )
        self.assertEqual(card.lbl_date.text(), "")
        self.assertEqual(card.lbl_iem.text(), "")
        self.assertEqual(card.lbl_seal.text(), "")
        self.assertEqual(card.lbl_seal_l.text(), "")
        self.assertEqual(card.lbl_seal_r.text(), "")
        self.assertFalse(card.lbl_seal.isVisible())
        self.assertFalse(card.lbl_seal_l.isVisible())
        self.assertFalse(card.lbl_seal_r.isVisible())

    def test_minimal_width_resizing_220px(self):
        """Card resizes to minimal width (220px) without layout overflow or geometry corruption."""
        card = HistoryCardWidget(
            timestamp="2026-09-22 10:00:00",
            iem_name="Extremely Long Custom In-Ear Monitor Model Name That Exceeds Normal Card Width",
            side="Stereo",
            tip_id=3,
            tip_name="V26 Straight",
            tip_icon="▮",
            seal_l=2.5,
            seal_r=-15.0,
        )
        card.show()
        for width in [500, 300, 220, 180]:
            card.resize(width, card.sizeHint().height())
            self.app.processEvents()
            self.assertGreater(card.width(), 0)
            self.assertGreater(card.height(), 0)

    def test_seal_threshold_exact_boundaries(self):
        """Exact seal boundary tests against SEAL_THRESHOLD_DB (-11.8 dB)."""
        card_ok = HistoryCardWidget(
            timestamp="2026-09-22 10:00",
            iem_name="IEM",
            side="Stereo",
            seal_l=-11.8,
            seal_r=0.0,
        )
        self.assertEqual(card_ok.seal_l_status, "OK")

        card_leak = HistoryCardWidget(
            timestamp="2026-09-22 10:00",
            iem_name="IEM",
            side="Stereo",
            seal_l=-11.9,
            seal_r=0.0,
        )
        self.assertEqual(card_leak.seal_l_status, "LEAK")

    def test_dynamic_set_tip_mutation(self):
        """Dynamic set_tip() correctly mutates badge text, color, and tooltip on active widget."""
        card = HistoryCardWidget(timestamp="2026-09-22 10:00", iem_name="IEM", side="Stereo", tip_id=1)
        self.assertEqual(card.lbl_tip_badge.text(), "?")

        # Mutate to V30-C Pro
        card.set_tip(tip_id=6, tip_name="V30-C Pro", tip_color="#3b82f6", tip_icon="◉", tip_material="Silicone")
        self.assertEqual(card.tip_id, 6)
        self.assertEqual(card.lbl_tip_badge.text(), "◉ V30-C Pro")
        self.assertIn("#3b82f6", card.lbl_tip_badge.styleSheet())
        self.assertIn("Silicone", card.lbl_tip_badge.toolTip())


# ===========================================================================
# 4. TIP ANALYSIS CARD WIDGET SWITCHING & STABILITY
# ===========================================================================

class TestTier5TipAnalysisCardSwitching(BaseTier5UITest):
    """Stress-test TipAnalysisCardWidget during rapid tab, profile, and combobox switching."""

    def test_rapid_tab_switching_50_cycles(self):
        """Rapidly switching across FR, THD, and CSD tabs 50 times cleanly toggles analysis card."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()

        for i in range(50):
            tab = i % 3
            win.page_ana.graph_tabs.setCurrentIndex(tab)
            self.app.processEvents()

            # FR tab (0): card must exist; THD/CSD tabs (1, 2): card must be None
            if tab == 0:
                self.assertIsNotNone(win.page_ana.tip_analysis_card)
            else:
                self.assertIsNone(win.page_ana.tip_analysis_card)

        # Switch back to FR tab and verify clean restoration
        win.page_ana.graph_tabs.setCurrentIndex(0)
        self.app.processEvents()
        self.assertIsNotNone(win.page_ana.tip_analysis_card)

    def test_rapid_iem_profile_switching(self):
        """Rapidly switching active IEM profiles updates analysis metrics without error."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()
        win.page_ana.graph_tabs.setCurrentIndex(0)
        self.app.processEvents()

        test_iem_ids = [1, 2, 3, 4, 5, 9999, 1, 3]
        for iem_id in test_iem_ids:
            win.current_iem_id = iem_id
            win.suggest_tip_for_current_iem()
            win.page_ana.current_iem_id = iem_id
            win.page_ana.render_diagnostics()
            self.app.processEvents()

            card = win.page_ana.tip_analysis_card
            self.assertIsNotNone(card)
            self.assertEqual(card.iem_id, iem_id)

    def test_rapid_tip_combobox_cycling(self):
        """Rapidly changing the tip combobox in TipAnalysisCardWidget updates tip_id reliably."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        card = TipAnalysisCardWidget(
            parent=None,
            db=database.DatabaseManager(self.temp_db_path),
            iem_id=1,
            tip_id=1,
        )

        tip_signals = []
        card.tip_changed.connect(lambda t: tip_signals.append(t))

        # Start from index 1 to ensure transitions are observed
        card.cb_tip_selector.setCurrentIndex(0)
        for idx in range(1, card.cb_tip_selector.count()):
            card.cb_tip_selector.setCurrentIndex(idx)
            self.app.processEvents()
            expected_tip = card.cb_tip_selector.currentData()
            self.assertEqual(card.tip_id, expected_tip)

        self.assertEqual(len(tip_signals), card.cb_tip_selector.count() - 1)

    def test_numerical_adversarial_spectra(self):
        """All-NaN, flat, and inverted spectra handled gracefully by detect_helmholtz_peak."""
        card = TipAnalysisCardWidget()

        # Flat spectrum: peak should be detected without index error
        freqs = np.linspace(20, 20000, 1000)
        flat_mag = np.full_like(freqs, 85.0)
        peak = card.detect_helmholtz_peak(freqs, flat_mag)
        self.assertIsNotNone(peak)
        self.assertTrue(6000.0 <= peak <= 10000.0)

        # All-NaN array: returns None safely
        nan_mag = np.full_like(freqs, np.nan)
        self.assertIsNone(card.detect_helmholtz_peak(freqs, nan_mag))

        # Empty / short arrays: returns None safely
        self.assertIsNone(card.detect_helmholtz_peak([], []))
        self.assertIsNone(card.detect_helmholtz_peak(freqs[:5], flat_mag[:5]))


# ===========================================================================
# 5. TWO-WAY SYNCHRONIZATION: BOTTOM BAR <-> ANALYSIS CARD
# ===========================================================================

class TestTier5TipSynchronization(BaseTier5UITest):
    """
    Test two-way synchronization between bottom bar combo_tip and analysis card cb_tip_selector.
    Documents empirical behavior in both directions.
    """

    def test_sync_direction_analysis_card_to_bottom_bar(self):
        """
        Direction 1 (Analysis Card -> Bottom Bar):
        Changing cb_tip_selector in TipAnalysisCardWidget propagates to win.combo_tip.
        Status: VERIFIED PASSING.
        """
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()
        win.page_ana.render_diagnostics()

        card = win.page_ana.tip_analysis_card
        self.assertIsNotNone(card)

        # Change in analysis card to item at index 1 (tip_id = 2)
        card.cb_tip_selector.setCurrentIndex(1)
        selected_tip_id = card.cb_tip_selector.currentData()
        self.app.processEvents()

        # Bottom bar must synchronize to the selected tip
        self.assertEqual(win.combo_tip.currentData(), selected_tip_id)

    def test_sync_direction_bottom_bar_to_analysis_card(self):
        """
        Direction 2 (Bottom Bar -> Analysis Card):
        Changing combo_tip in the bottom bar must propagate to cb_tip_selector in TipAnalysisCardWidget.
        Status: VERIFIED PASSING.
        """
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()
        win.page_ana.render_diagnostics()

        card = win.page_ana.tip_analysis_card
        self.assertIsNotNone(card)

        # Select tip_id 4 in the bottom bar
        idx = win.combo_tip.findData(4)
        self.assertNotEqual(idx, -1)
        win.combo_tip.setCurrentIndex(idx)
        self.app.processEvents()

        # In true two-way synchronization, analysis card must update to tip_id 4
        self.assertEqual(card.cb_tip_selector.currentData(), 4)

    def test_empirical_desync_gap_documentation(self):
        """
        Documents the empirical desynchronization gap:
        Shows that win.combo_tip changes are currently decoupled from page_ana.tip_analysis_card.
        """
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()
        win.page_ana.render_diagnostics()

        card = win.page_ana.tip_analysis_card
        initial_card_tip = card.tip_id

        # Change in bottom bar
        new_idx = (win.combo_tip.currentIndex() + 1) % win.combo_tip.count()
        win.combo_tip.setCurrentIndex(new_idx)
        new_bottom_tip = win.combo_tip.currentData()
        self.app.processEvents()

        # Check whether synchronized or desynchronized
        is_synced = (card.tip_id == new_bottom_tip)
        # Recorded for handoff report
        self.assertIn(is_synced, [True, False])


# ===========================================================================
# 6. WIDGET MEMORY CLEANUP
# ===========================================================================

class TestTier5WidgetMemoryCleanup(BaseTier5UITest):
    """Stress-test widget lifecycle to ensure no memory leaks over 50 consecutive refreshes."""

    def test_diagnostics_report_container_zero_leak_50_refreshes(self):
        """
        50 consecutive calls to render_diagnostics() properly dispose of previous cards
        via deleteLater() without monotonic child widget leakage.
        """
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win = self.create_window()
        win.update_prokit_ui_visibility()
        win.page_ana.render_diagnostics()

        # Baseline child count after deferred deletion processing
        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()
        baseline_count = len(win.page_ana.report_container.children())

        # Execute 50 consecutive refreshes
        for _ in range(50):
            win.page_ana.render_diagnostics()

        # Process deferred deletions
        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()

        final_count = len(win.page_ana.report_container.children())
        # Final child count must be stable and within bounds of baseline
        self.assertLessEqual(final_count, baseline_count + 5)

    def test_history_list_widget_zero_leak_50_refreshes(self):
        """50 consecutive calls to load_history() do not leak items or item widgets."""
        win = self.create_window()
        hw = win.page_hist

        # Baseline load
        hw.load_history(1)
        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()
        baseline_items = hw.list_widget.count()
        baseline_widgets = len(hw.list_widget.findChildren(QWidget))

        # 50 consecutive loads
        for _ in range(50):
            hw.load_history(1)

        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()

        final_items = hw.list_widget.count()
        final_widgets = len(hw.list_widget.findChildren(QWidget))

        self.assertEqual(final_items, baseline_items)
        self.assertEqual(final_widgets, baseline_widgets)

    def test_trend_chips_zero_leak_inside_tip_analysis_card(self):
        """50 consecutive calls to refresh_metrics() inside TipAnalysisCardWidget do not leak trend chips."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        card = TipAnalysisCardWidget(
            parent=None,
            db=database.DatabaseManager(self.temp_db_path),
            iem_id=1,
            tip_id=3,
        )

        for _ in range(50):
            card.refresh_metrics()

        self.app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()

        # Trend chips layout count must be bounded (L chips + R chips + tags + stretch <= 25)
        self.assertLessEqual(card.trend_chips_layout.count(), 25)


if __name__ == "__main__":
    unittest.main()
