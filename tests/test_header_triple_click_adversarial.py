"""
Adversarial Stress Test Suite: Header Logo Triple-Click & ProKit Unlock Flow
=============================================================================

Mission:
Adversarially challenge and stress-test the header logo triple-click event filter
and unlock flow in main.py:
1. Rapid clicks (<600ms): 3 clicks triggers unlock dialog.
2. Slow clicks (>600ms pause): click counter resets, dialog does NOT open.
3. Only 1 or 2 clicks: dialog does NOT open.
4. Right clicks or middle clicks: completely ignored, counter does NOT advance.
5. Click spamming (e.g. 10 rapid clicks): only opens dialog once without crashing
   or stacking dialogs (re-entrancy protection).
6. Mouse events on adjacent header widgets (buttons, theme selector, titles):
   zero event consumption or blocking.
7. Dialog unlock roundtrip: invalid codes, whitespace, valid codes, and immediate UI refresh.

SAFETY:
All tests MUST use isolated temporary directories and databases. NEVER touch inearsnitch.db!
"""

import os
import sys
import time
import pytest
import sqlite3
import hashlib
from unittest.mock import MagicMock, patch

# Ensure headless Qt execution
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QPoint, QPointF, QEvent, QObject
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QMessageBox,
    QInputDialog,
)

# Root directory setup
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
from main import LogoTripleClickFilter, MainWindow


# ---------------------------------------------------------------------------
# Test Fixtures & Safety Guards
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    """Provides a singleton headless QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["InEarSnitchAdversarial", "-platform", "offscreen"])
    return app


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """
    CRITICAL SAFETY FIXTURE:
    - Redirects config.get_data_dir() to tmp_path/app_data
    - Intercepts all sqlite3.connect calls to redirect inearsnitch.db to tmp_path/test_inearsnitch.db
    - Monkeypatches database.DatabaseManager to use tmp_path/test_inearsnitch.db
    - Initializes the temporary database with full schema and seed catalog
    - Records inearsnitch.db state before and after test to guarantee zero tampering
    """
    data_dir = str(tmp_path / "app_data")
    os.makedirs(data_dir, exist_ok=True)
    monkeypatch.setattr(config, "get_data_dir", lambda: data_dir)

    temp_db_path = str(tmp_path / "test_inearsnitch.db")

    # Global intercept on sqlite3.connect across all modules
    orig_sqlite3_connect = sqlite3.connect

    def safe_sqlite3_connect(database_arg, *args, **kwargs):
        if database_arg == "inearsnitch.db" or database_arg is None:
            database_arg = temp_db_path
        return orig_sqlite3_connect(database_arg, *args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", safe_sqlite3_connect)

    # Intercept DatabaseManager __init__
    orig_db_init = database.DatabaseManager.__init__

    def safe_db_init(self, db_path="inearsnitch.db"):
        if db_path == "inearsnitch.db" or db_path is None:
            db_path = temp_db_path
        orig_db_init(self, db_path)

    monkeypatch.setattr(database.DatabaseManager, "__init__", safe_db_init)

    # Pre-seed the temporary database schema
    init_db = database.DatabaseManager(temp_db_path)
    del init_db

    # Record production inearsnitch.db stats if present
    prod_db = os.path.join(REPO_ROOT, "inearsnitch.db")
    prod_stat_before = None
    if os.path.exists(prod_db):
        prod_stat_before = (os.path.getsize(prod_db), os.path.getmtime(prod_db))

    yield {
        "data_dir": data_dir,
        "db_path": temp_db_path,
        "prod_db": prod_db,
    }

    # Verify production DB was completely untouched
    if prod_stat_before is not None:
        assert os.path.exists(prod_db), "FATAL: inearsnitch.db was removed!"
        prod_stat_after = (os.path.getsize(prod_db), os.path.getmtime(prod_db))
        assert prod_stat_before == prod_stat_after, (
            f"FATAL SAFETY VIOLATION: inearsnitch.db modified! Before: {prod_stat_before}, After: {prod_stat_after}"
        )


def make_mouse_event(event_type, button=Qt.LeftButton, pos=QPoint(10, 10)):
    """Helper to construct QMouseEvent instances for PySide6."""
    return QMouseEvent(
        event_type,
        QPointF(pos),
        QPointF(pos),
        button,
        button,
        Qt.NoModifier,
    )


# ---------------------------------------------------------------------------
# SUITE 1: LogoTripleClickFilter Direct Unit & Stress Tests
# ---------------------------------------------------------------------------

class TestLogoTripleClickFilterUnit:
    """Stress tests on the LogoTripleClickFilter component directly."""

    def test_rapid_three_presses_triggers_callback(self, qapp):
        """1. Rapid clicks (<600ms): 3 LeftButton presses trigger callback exactly once."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)
        target.installEventFilter(filter_obj)

        e1 = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        e2 = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        e3 = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        # Clicks 1 and 2 return False (not consumed)
        res1 = filter_obj.eventFilter(target, e1)
        assert res1 is False
        assert callback.call_count == 0
        assert len(filter_obj.clicks) == 1

        res2 = filter_obj.eventFilter(target, e2)
        assert res2 is False
        assert callback.call_count == 0
        assert len(filter_obj.clicks) == 2

        # Click 3 returns True (consumed and triggered)
        res3 = filter_obj.eventFilter(target, e3)
        assert res3 is True
        assert callback.call_count == 1
        assert len(filter_obj.clicks) == 0  # Reset after trigger

    def test_qt_realistic_double_click_sequence(self, qapp):
        """Qt sends MouseButtonDblClick for 2nd press. Sequence: Press, DblClick, Press."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        e_press1 = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        e_rel1 = make_mouse_event(QEvent.MouseButtonRelease, Qt.LeftButton)
        e_dbl2 = make_mouse_event(QEvent.MouseButtonDblClick, Qt.LeftButton)
        e_rel2 = make_mouse_event(QEvent.MouseButtonRelease, Qt.LeftButton)
        e_press3 = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        assert filter_obj.eventFilter(target, e_press1) is False
        assert filter_obj.eventFilter(target, e_rel1) is False  # Releases ignored
        assert filter_obj.eventFilter(target, e_dbl2) is False
        assert filter_obj.eventFilter(target, e_rel2) is False
        assert filter_obj.eventFilter(target, e_press3) is True  # Triggers on 3rd

        assert callback.call_count == 1
        assert len(filter_obj.clicks) == 0

    def test_slow_clicks_pause_resets_counter(self, qapp):
        """2. Slow clicks (>600ms pause): click counter resets, dialog does NOT open."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        cur_time = 1000.0

        def mock_time():
            return cur_time

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        with patch("time.monotonic", side_effect=mock_time):
            # Click 1 at t=1000.0
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1

            # Pause 650ms (> 600ms)
            cur_time += 0.65

            # Click 2 at t=1000.65 -> counter resets to 1
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1
            assert callback.call_count == 0

            # Pause another 650ms
            cur_time += 0.65

            # Click 3 at t=1001.30 -> counter resets to 1
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1
            assert callback.call_count == 0

        # Verify callback was NEVER invoked
        assert callback.call_count == 0

    def test_slow_pause_between_click_2_and_3(self, qapp):
        """Pause >600ms after click 2 resets counter; subsequent clicks must re-accumulate 3."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        cur_time = 500.0

        def mock_time():
            return cur_time

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        with patch("time.monotonic", side_effect=mock_time):
            # Click 1 at 500.0
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1

            # Click 2 at 500.2 (200ms pause, within 600ms)
            cur_time += 0.2
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 2

            # Pause 700ms (>600ms threshold)
            cur_time += 0.7

            # Click 3 at 501.1 -> resets to [501.1]
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1
            assert callback.call_count == 0

            # Click 4 at 501.2 (100ms pause)
            cur_time += 0.1
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 2

            # Click 5 at 501.3 (100ms pause) -> triggers!
            cur_time += 0.1
            filter_obj.eventFilter(target, e_press)
            assert callback.call_count == 1
            assert len(filter_obj.clicks) == 0

    def test_boundary_exact_timing_599ms_vs_601ms(self, qapp):
        """Exact boundary tests: 599ms pause preserves counter, 601ms pause resets."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        # Test A: 599ms delta (<= 0.600) -> should NOT reset
        cur_time = 100.0
        with patch("time.monotonic", lambda: cur_time):
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1

            cur_time += 0.599
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 2

            cur_time += 0.599
            filter_obj.eventFilter(target, e_press)
            assert callback.call_count == 1
            assert len(filter_obj.clicks) == 0

        # Test B: 601ms delta (> 0.600) -> should reset
        cur_time = 200.0
        callback.reset_mock()
        with patch("time.monotonic", lambda: cur_time):
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1

            cur_time += 0.601
            filter_obj.eventFilter(target, e_press)
            assert len(filter_obj.clicks) == 1
            assert callback.call_count == 0

    def test_only_one_or_two_clicks_does_not_open_dialog(self, qapp):
        """3. Only 1 or 2 clicks: dialog does NOT open."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        # 1 click
        res1 = filter_obj.eventFilter(target, e_press)
        assert res1 is False
        assert callback.call_count == 0
        assert len(filter_obj.clicks) == 1

        # 2 clicks
        res2 = filter_obj.eventFilter(target, e_press)
        assert res2 is False
        assert callback.call_count == 0
        assert len(filter_obj.clicks) == 2

    def test_right_and_middle_clicks_completely_ignored(self, qapp):
        """4. Right clicks or middle clicks: completely ignored, counter does NOT advance."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        # Test Right Click
        e_right = make_mouse_event(QEvent.MouseButtonPress, Qt.RightButton)
        res_right = filter_obj.eventFilter(target, e_right)
        assert res_right is False
        assert len(filter_obj.clicks) == 0

        # Test Middle Click
        e_mid = make_mouse_event(QEvent.MouseButtonPress, Qt.MiddleButton)
        res_mid = filter_obj.eventFilter(target, e_mid)
        assert res_mid is False
        assert len(filter_obj.clicks) == 0

        # Test Right Double Click
        e_right_dbl = make_mouse_event(QEvent.MouseButtonDblClick, Qt.RightButton)
        assert filter_obj.eventFilter(target, e_right_dbl) is False
        assert len(filter_obj.clicks) == 0

        # Interleaved: Left, Right, Middle, Left, Right, Left -> Must succeed!
        e_left = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        filter_obj.eventFilter(target, e_left)       # Left 1
        assert len(filter_obj.clicks) == 1

        filter_obj.eventFilter(target, e_right)      # Right (ignored)
        assert len(filter_obj.clicks) == 1

        filter_obj.eventFilter(target, e_mid)        # Mid (ignored)
        assert len(filter_obj.clicks) == 1

        filter_obj.eventFilter(target, e_left)       # Left 2
        assert len(filter_obj.clicks) == 2

        filter_obj.eventFilter(target, e_right)      # Right (ignored)
        assert len(filter_obj.clicks) == 2

        filter_obj.eventFilter(target, e_left)       # Left 3 -> triggers!
        assert callback.call_count == 1
        assert len(filter_obj.clicks) == 0

    def test_non_mouse_events_completely_ignored(self, qapp):
        """Other event types (MouseMove, Wheel, KeyPress) do not advance counter."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        assert filter_obj.eventFilter(target, QEvent(QEvent.MouseMove)) is False
        assert filter_obj.eventFilter(target, QEvent(QEvent.Wheel)) is False
        assert filter_obj.eventFilter(target, QEvent(QEvent.KeyPress)) is False
        assert filter_obj.eventFilter(target, QEvent(QEvent.Paint)) is False
        assert len(filter_obj.clicks) == 0
        assert callback.call_count == 0

    def test_click_spamming_reentrancy_protection_during_modal_dialog(self, qapp):
        """5. Click spamming (e.g. 10 rapid clicks): only opens dialog once (re-entrancy protection)."""
        target = QLabel("Logo")
        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        dialog_invocations = 0
        clicks_during_dialog = 7

        def mock_modal_dialog_callback():
            nonlocal dialog_invocations
            dialog_invocations += 1
            # Verify internal re-entrancy flag is active
            assert filter_obj._dialog_active is True
            # Simulate spam clicks while dialog is actively displaying
            for _ in range(clicks_during_dialog):
                res = filter_obj.eventFilter(target, e_press)
                # During active dialog, clicks must return False and not increment clicks
                assert res is False
            assert len(filter_obj.clicks) == 0

        filter_obj = LogoTripleClickFilter(target, mock_modal_dialog_callback, max_interval=0.6)

        # Clicks 1 & 2
        filter_obj.eventFilter(target, e_press)
        filter_obj.eventFilter(target, e_press)
        # Click 3 triggers callback (which simulates 7 more rapid clicks during modal exec)
        filter_obj.eventFilter(target, e_press)

        # Total clicks processed: 3 + 7 = 10 clicks!
        # Assert callback was invoked EXACTLY ONCE
        assert dialog_invocations == 1
        # Assert re-entrancy flag was reset
        assert filter_obj._dialog_active is False
        # Assert residual clicks list is empty
        assert len(filter_obj.clicks) == 0

    def test_click_spamming_rapid_sequential_no_modal_pause(self, qapp):
        """10 rapid clicks without modal delay trigger cleanly every 3 clicks (3 times total)."""
        callback = MagicMock()
        target = QLabel("Logo")
        filter_obj = LogoTripleClickFilter(target, callback, max_interval=0.6)

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        # Send 10 rapid clicks in quick loop
        results = [filter_obj.eventFilter(target, e_press) for _ in range(10)]

        # Clicks 3, 6, 9 should return True (1-indexed: index 2, 5, 8)
        assert results == [False, False, True, False, False, True, False, False, True, False]
        assert callback.call_count == 3
        assert len(filter_obj.clicks) == 1  # 1 residual click

    def test_callback_exception_safety(self, qapp):
        """If callback raises an unhandled exception, _dialog_active must reset via finally."""
        target = QLabel("Logo")

        def broken_callback():
            raise RuntimeError("Simulated UI crash in callback")

        filter_obj = LogoTripleClickFilter(target, broken_callback, max_interval=0.6)
        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        filter_obj.eventFilter(target, e_press)
        filter_obj.eventFilter(target, e_press)

        with pytest.raises(RuntimeError, match="Simulated UI crash"):
            filter_obj.eventFilter(target, e_press)

        # Guard flag MUST be cleanly reset despite exception
        assert filter_obj._dialog_active is False
        assert len(filter_obj.clicks) == 0

        # And filter must remain functional for subsequent clicks
        filter_obj.callback = MagicMock()
        filter_obj.eventFilter(target, e_press)
        filter_obj.eventFilter(target, e_press)
        filter_obj.eventFilter(target, e_press)
        assert filter_obj.callback.call_count == 1


# ---------------------------------------------------------------------------
# SUITE 2: MainWindow Integration & Adjacent Header Widgets
# ---------------------------------------------------------------------------

class TestMainWindowHeaderIntegration:
    """Integration tests on MainWindow header logo, sublogo, and adjacent widgets."""

    @pytest.fixture
    def main_window(self, qapp, isolated_env):
        """Creates an isolated MainWindow instance safe from inearsnitch.db."""
        win = MainWindow()
        win.show()
        yield win
        win.close()
        win.deleteLater()

    def test_header_logo_installed_event_filters(self, main_window):
        """Verify lbl_logo and lbl_sublogo have logo_triple_click_filter installed."""
        assert hasattr(main_window, "lbl_logo")
        assert hasattr(main_window, "lbl_sublogo")
        assert hasattr(main_window, "logo_triple_click_filter")

        filter_obj = main_window.logo_triple_click_filter
        assert isinstance(filter_obj, LogoTripleClickFilter)
        assert filter_obj.max_interval == 0.6

    def test_mainwindow_lbl_logo_three_clicks_triggers_prompt(self, main_window, monkeypatch):
        """3 rapid clicks on lbl_logo via QApplication.sendEvent triggers prompt_prokit_unlock."""
        mock_prompt = MagicMock(return_value=True)
        monkeypatch.setattr(main_window, "prompt_prokit_unlock", mock_prompt)
        main_window.logo_triple_click_filter.callback = mock_prompt

        lbl = main_window.lbl_logo
        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        QApplication.sendEvent(lbl, e_press)
        QApplication.sendEvent(lbl, e_press)
        assert mock_prompt.call_count == 0

        QApplication.sendEvent(lbl, e_press)
        assert mock_prompt.call_count == 1

    def test_mainwindow_lbl_sublogo_three_clicks_triggers_prompt(self, main_window, monkeypatch):
        """3 rapid clicks on lbl_sublogo ('DIAGNOSTICS') also triggers prompt_prokit_unlock."""
        mock_prompt = MagicMock(return_value=True)
        monkeypatch.setattr(main_window, "prompt_prokit_unlock", mock_prompt)
        main_window.logo_triple_click_filter.callback = mock_prompt

        lbl = main_window.lbl_sublogo
        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        QApplication.sendEvent(lbl, e_press)
        QApplication.sendEvent(lbl, e_press)
        assert mock_prompt.call_count == 0

        QApplication.sendEvent(lbl, e_press)
        assert mock_prompt.call_count == 1

    def test_mainwindow_cross_label_clicks_combined(self, main_window, monkeypatch):
        """Clicking across lbl_logo and lbl_sublogo shares the single filter instance cleanly."""
        mock_prompt = MagicMock(return_value=True)
        monkeypatch.setattr(main_window, "prompt_prokit_unlock", mock_prompt)
        main_window.logo_triple_click_filter.callback = mock_prompt

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)

        # Click 1 on logo, Click 2 on sublogo, Click 3 on logo
        QApplication.sendEvent(main_window.lbl_logo, e_press)
        assert len(main_window.logo_triple_click_filter.clicks) == 1

        QApplication.sendEvent(main_window.lbl_sublogo, e_press)
        assert len(main_window.logo_triple_click_filter.clicks) == 2

        QApplication.sendEvent(main_window.lbl_logo, e_press)
        assert mock_prompt.call_count == 1
        assert len(main_window.logo_triple_click_filter.clicks) == 0

    def test_adjacent_widgets_zero_event_consumption_or_blocking(self, main_window):
        """
        6. Mouse events on adjacent header widgets: zero event consumption or blocking.
        - btn_theme ('🌓'): clicks toggle theme, not blocked, do NOT increment logo clicks.
        - btn_top_settings ('Settings'): clicks toggle settings panel, not blocked, do NOT increment logo clicks.
        """
        assert hasattr(main_window, "btn_theme")
        assert hasattr(main_window, "btn_top_settings")

        filter_obj = main_window.logo_triple_click_filter

        # Record theme state
        initial_clicks = len(filter_obj.clicks)

        # 1. Click Theme button
        theme_clicked = MagicMock()
        main_window.btn_theme.clicked.connect(theme_clicked)

        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        e_rel = make_mouse_event(QEvent.MouseButtonRelease, Qt.LeftButton)

        QApplication.sendEvent(main_window.btn_theme, e_press)
        QApplication.sendEvent(main_window.btn_theme, e_rel)

        assert theme_clicked.call_count >= 1
        # Logo filter clicks must NOT have changed!
        assert len(filter_obj.clicks) == initial_clicks

        # 2. Click Settings button
        settings_clicked = MagicMock()
        main_window.btn_top_settings.clicked.connect(settings_clicked)

        QApplication.sendEvent(main_window.btn_top_settings, e_press)
        QApplication.sendEvent(main_window.btn_top_settings, e_rel)

        assert settings_clicked.call_count >= 1
        assert len(filter_obj.clicks) == initial_clicks

    def test_clicking_adjacent_widget_does_not_advance_or_reset_logo_counter(self, main_window):
        """Clicking adjacent buttons does not contaminate the logo filter."""
        filter_obj = main_window.logo_triple_click_filter
        e_press = make_mouse_event(QEvent.MouseButtonPress, Qt.LeftButton)
        e_rel = make_mouse_event(QEvent.MouseButtonRelease, Qt.LeftButton)

        # 1 click on logo
        QApplication.sendEvent(main_window.lbl_logo, e_press)
        assert len(filter_obj.clicks) == 1

        # Click on settings button
        QApplication.sendEvent(main_window.btn_top_settings, e_press)
        QApplication.sendEvent(main_window.btn_top_settings, e_rel)
        assert len(filter_obj.clicks) == 1

        # Click on theme button
        QApplication.sendEvent(main_window.btn_theme, e_press)
        QApplication.sendEvent(main_window.btn_theme, e_rel)
        assert len(filter_obj.clicks) == 1


# ---------------------------------------------------------------------------
# SUITE 3: Dialog Unlock Roundtrip & Immediate UI Refresh
# ---------------------------------------------------------------------------

class TestUnlockDialogRoundtripAndUIRefresh:
    """7. Dialog unlock roundtrip: invalid codes, whitespace, valid codes, immediate UI refresh."""

    @pytest.fixture
    def main_window(self, qapp, isolated_env):
        """Creates an isolated MainWindow instance safe from inearsnitch.db."""
        config.revoke_prokit()
        win = MainWindow()
        win.show()
        yield win
        win.close()
        win.deleteLater()

    def test_unlock_dialog_cancel_action(self, main_window, monkeypatch):
        """User cancels input dialog (ok=False) -> returns False, UI remains locked."""
        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("", False))
        mock_info = MagicMock()
        mock_warn = MagicMock()
        monkeypatch.setattr(QMessageBox, "information", mock_info)
        monkeypatch.setattr(QMessageBox, "warning", mock_warn)

        res = main_window.prompt_prokit_unlock()
        assert res is False
        assert config.is_prokit_unlocked() is False
        assert main_window.combo_tip.isHidden() is True
        assert main_window.tip_container.isHidden() is True
        assert mock_info.call_count == 0
        assert mock_warn.call_count == 0

    def test_unlock_dialog_invalid_code(self, main_window, monkeypatch):
        """User enters invalid code -> returns False, warning shown, UI remains locked."""
        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("WRONG-CODE-999", True))
        mock_info = MagicMock()
        mock_warn = MagicMock()
        monkeypatch.setattr(QMessageBox, "information", mock_info)
        monkeypatch.setattr(QMessageBox, "warning", mock_warn)

        res = main_window.prompt_prokit_unlock()
        assert res is False
        assert config.is_prokit_unlocked() is False
        assert main_window.combo_tip.isHidden() is True
        assert main_window.tip_container.isHidden() is True
        assert mock_warn.call_count == 1
        assert mock_info.call_count == 0

    def test_unlock_dialog_valid_code_with_surrounding_whitespace(self, main_window, monkeypatch):
        """Valid code with whitespace '  SNITCH-PROKIT-2024-001  ' -> succeeds, immediate UI refresh."""
        code = "   SNITCH-PROKIT-2024-001   \t\n"
        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: (code, True))
        mock_info = MagicMock()
        mock_warn = MagicMock()
        monkeypatch.setattr(QMessageBox, "information", mock_info)
        monkeypatch.setattr(QMessageBox, "warning", mock_warn)

        assert config.is_prokit_unlocked() is False
        assert main_window.combo_tip.isHidden() is True

        res = main_window.prompt_prokit_unlock()
        assert res is True
        assert config.is_prokit_unlocked() is True
        assert mock_info.call_count == 1
        assert mock_warn.call_count == 0

        # Immediate UI refresh checks:
        assert main_window.combo_tip.isHidden() is False
        assert main_window.tip_container.isHidden() is False
        assert main_window.combo_tip.isVisible() is True
        assert main_window.tip_container.isVisible() is True
        # ComboBox must be populated from TipProfiles table
        assert main_window.combo_tip.count() >= 7
        # Verify items contain catalog tips
        tip_names = [main_window.combo_tip.itemText(i) for i in range(main_window.combo_tip.count())]
        assert any("V26 Straight" in name for name in tip_names)
        assert any("V27 Rounded" in name for name in tip_names)

    def test_unlock_dialog_lowercase_normalization(self, main_window, monkeypatch):
        """Lowercase valid code 'snitch-prokit-2024-005' -> succeeds, immediate UI refresh."""
        code = "snitch-prokit-2024-005"
        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: (code, True))
        monkeypatch.setattr(QMessageBox, "information", MagicMock())
        monkeypatch.setattr(QMessageBox, "warning", MagicMock())

        res = main_window.prompt_prokit_unlock()
        assert res is True
        assert config.is_prokit_unlocked() is True
        assert main_window.combo_tip.isHidden() is False
        assert main_window.combo_tip.isVisible() is True

    def test_revoke_and_ui_refresh_roundtrip(self, main_window):
        """Unlocking then revoking cleanly hides UI elements upon refresh."""
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        main_window.update_prokit_ui_visibility()
        assert main_window.combo_tip.isHidden() is False
        assert main_window.combo_tip.isVisible() is True
        assert main_window.tip_container.isHidden() is False
        assert main_window.tip_container.isVisible() is True

        config.revoke_prokit()
        assert config.is_prokit_unlocked() is False

        main_window.update_prokit_ui_visibility()
        assert main_window.combo_tip.isHidden() is True
        assert main_window.combo_tip.isVisible() is False
        assert main_window.tip_container.isHidden() is True
        assert main_window.tip_container.isVisible() is False

    def test_aliases_open_prokit_unlock_dialog_and_on_logo_triple_clicked(self, main_window, monkeypatch):
        """Verify alias methods exist and execute prompt_prokit_unlock without blocking."""
        assert hasattr(main_window, "open_prokit_unlock_dialog")
        assert hasattr(main_window, "on_logo_triple_clicked")

        monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("SNITCH-PROKIT-2024-001", True))
        monkeypatch.setattr(QMessageBox, "information", MagicMock())

        # Test open_prokit_unlock_dialog
        res1 = main_window.open_prokit_unlock_dialog()
        assert res1 is True
        assert config.is_prokit_unlocked() is True

        config.revoke_prokit()
        assert config.is_prokit_unlocked() is False

        # Test on_logo_triple_clicked
        res2 = main_window.on_logo_triple_clicked()
        assert res2 is True
        assert config.is_prokit_unlocked() is True
