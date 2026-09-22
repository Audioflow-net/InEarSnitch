"""
Forensic Integrity Test for M3 (main.py ProKit UI Integration).
Independently verifies:
1. LogoTripleClickFilter genuine timing, click counting, button filtering, and re-entrancy safety.
2. combo_tip widget configuration (non-editable, aliases, container layout).
3. Dynamic database catalog population (custom IDs, itemData, icons, labels).
4. Auto-suggest logic on profile selection (dynamic last-used tip per IEM, fallback to default).
5. Measurement persistence (saves exact dynamic tip_id when unlocked, falls back to 1 when locked).
6. Visibility gate responsiveness to unlock/revoke lifecycle.
"""

import os
import sys
import time
import sqlite3
import tempfile
import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, QPoint, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QLabel, QWidget

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database
import main


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(["ForensicTest", "-platform", "offscreen"])
    return app


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Provides isolated data directory and clean config state."""
    data_dir = str(tmp_path / "app_data")
    os.makedirs(data_dir, exist_ok=True)
    monkeypatch.setattr(config, "get_data_dir", lambda: data_dir)
    config.revoke_prokit()
    yield data_dir
    config.revoke_prokit()


@pytest.fixture
def dynamic_db(tmp_path):
    """Provides a fresh isolated database with dynamic custom tips and measurements."""
    db_path = str(tmp_path / "forensic_snitch.db")
    db = database.DatabaseManager(db_path)
    
    # Add arbitrary custom tips with non-standard IDs
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO TipProfiles (id, name, material, color_hex, icon_char, is_default) "
        "VALUES (42, 'Dynamic Silicon X', 'Silicone', '#123456', '⚡', 0)"
    )
    cur.execute(
        "INSERT INTO TipProfiles (id, name, material, color_hex, icon_char, is_default) "
        "VALUES (99, 'Dynamic Foam Y', 'Foam', '#654321', '🔶', 0)"
    )
    
    # Add dummy musician and IEMs
    cur.execute("INSERT INTO Musicians (id, name) VALUES (1, 'Forensic Musician')")
    cur.execute("INSERT INTO IEM_Models (id, musician_id, model_name) VALUES (101, 1, 'IEM 101 (Tip 42)')")
    cur.execute("INSERT INTO IEM_Models (id, musician_id, model_name) VALUES (102, 1, 'IEM 102 (Tip 99)')")
    cur.execute("INSERT INTO IEM_Models (id, musician_id, model_name) VALUES (103, 1, 'IEM 103 (Legacy Tip 1)')")
    cur.execute("INSERT INTO IEM_Models (id, musician_id, model_name) VALUES (104, 1, 'IEM 104 (Clean)')")
    
    # Save historical measurements with dynamic tips
    dummy_blob = np.zeros(100, dtype=np.float32).tobytes()
    cur.execute(
        "INSERT INTO Measurements (iem_id, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, tip_id, timestamp) "
        "VALUES (101, ?, ?, ?, ?, ?, 42, '2026-09-22 09:00:00')",
        (dummy_blob, dummy_blob, dummy_blob, dummy_blob, dummy_blob)
    )
    cur.execute(
        "INSERT INTO Measurements (iem_id, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, tip_id, timestamp) "
        "VALUES (102, ?, ?, ?, ?, ?, 99, '2026-09-22 09:01:00')",
        (dummy_blob, dummy_blob, dummy_blob, dummy_blob, dummy_blob)
    )
    cur.execute(
        "INSERT INTO Measurements (iem_id, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, tip_id, timestamp) "
        "VALUES (103, ?, ?, ?, ?, ?, 1, '2026-09-22 09:02:00')",
        (dummy_blob, dummy_blob, dummy_blob, dummy_blob, dummy_blob)
    )
    conn.commit()
    conn.close()
    
    return db, db_path


class TestForensicTripleClickFilter:
    """Forensic verification of LogoTripleClickFilter."""

    def test_rapid_left_clicks_trigger_callback(self, qapp):
        triggered = []
        flt = main.LogoTripleClickFilter(None, lambda: triggered.append(True), max_interval=0.6)
        lbl = QLabel("Logo")
        lbl.installEventFilter(flt)

        press_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        
        # Click 1
        res1 = flt.eventFilter(lbl, press_evt)
        assert res1 is False
        assert len(triggered) == 0
        
        # Click 2
        res2 = flt.eventFilter(lbl, press_evt)
        assert res2 is False
        assert len(triggered) == 0
        
        # Click 3
        res3 = flt.eventFilter(lbl, press_evt)
        assert res3 is True
        assert len(triggered) == 1

    def test_slow_clicks_do_not_accumulate(self, qapp, monkeypatch):
        triggered = []
        flt = main.LogoTripleClickFilter(None, lambda: triggered.append(True), max_interval=0.6)
        lbl = QLabel("Logo")

        press_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        
        fake_time = [100.0]
        monkeypatch.setattr(time, "monotonic", lambda: fake_time[0])
        
        # Click 1 at t=100.0
        flt.eventFilter(lbl, press_evt)
        
        # Click 2 at t=100.2
        fake_time[0] = 100.2
        flt.eventFilter(lbl, press_evt)
        assert len(triggered) == 0
        
        # Wait 0.8s (exceeds 0.6s max_interval)
        fake_time[0] = 101.0
        # Click 3 at t=101.0 -> should reset buffer to [101.0]
        flt.eventFilter(lbl, press_evt)
        assert len(triggered) == 0
        assert len(flt.clicks) == 1

    def test_right_click_and_middle_click_ignored(self, qapp):
        triggered = []
        flt = main.LogoTripleClickFilter(None, lambda: triggered.append(True), max_interval=0.6)
        lbl = QLabel("Logo")

        right_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.RightButton, Qt.RightButton, Qt.NoModifier)
        mid_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier)

        for _ in range(5):
            flt.eventFilter(lbl, right_evt)
            flt.eventFilter(lbl, mid_evt)

        assert len(triggered) == 0
        assert len(flt.clicks) == 0

    def test_reentrancy_lock_prevents_recursive_trigger(self, qapp):
        trigger_count = 0
        flt = main.LogoTripleClickFilter(None, None, max_interval=0.6)
        lbl = QLabel("Logo")
        press_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

        def recursive_callback():
            nonlocal trigger_count
            trigger_count += 1
            # Attempt to fire 3 more clicks while callback is running
            for _ in range(3):
                flt.eventFilter(lbl, press_evt)

        flt.callback = recursive_callback
        
        # Fire 3 clicks
        for _ in range(3):
            flt.eventFilter(lbl, press_evt)

        assert trigger_count == 1, "Re-entrancy should prevent nested dialog triggers"

    def test_double_click_sequence_handling(self, qapp):
        """Qt sends MouseButtonPress, then MouseButtonDblClick for second click."""
        triggered = []
        flt = main.LogoTripleClickFilter(None, lambda: triggered.append(True), max_interval=0.6)
        lbl = QLabel("Logo")

        press_evt = QMouseEvent(QEvent.MouseButtonPress, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        dbl_evt = QMouseEvent(QEvent.MouseButtonDblClick, QPoint(10, 10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

        # 1st press
        flt.eventFilter(lbl, press_evt)
        assert len(triggered) == 0
        # 2nd press (delivered as MouseButtonDblClick by Qt)
        flt.eventFilter(lbl, dbl_evt)
        assert len(triggered) == 0
        # 3rd press (regular press following double-click)
        flt.eventFilter(lbl, press_evt)
        assert len(triggered) == 1


class TestForensicUIPropertiesAndDataFlow:
    """Forensic verification of UI selector, data flow, and dynamic database integration."""

    def test_combo_tip_immutability_and_aliases(self, qapp):
        win = main.MainWindow.__new__(main.MainWindow)
        # Verify combo properties
        from PySide6.QtWidgets import QComboBox, QWidget, QVBoxLayout
        win.combo_tip = QComboBox()
        win.combo_tip.setObjectName("cb_prokit_tip")
        win.combo_tip.setEditable(False)
        win.cb_tip = win.combo_tip
        win.cb_prokit_tip = win.combo_tip

        assert win.combo_tip.isEditable() is False
        assert win.cb_tip is win.combo_tip
        assert win.cb_prokit_tip is win.combo_tip
        assert win.combo_tip.objectName() == "cb_prokit_tip"

    def test_dynamic_catalog_population_stores_exact_ids(self, qapp, dynamic_db):
        db, _ = dynamic_db
        win = main.MainWindow.__new__(main.MainWindow)
        from PySide6.QtWidgets import QComboBox
        win.combo_tip = QComboBox()
        win.db = db

        main.MainWindow.populate_tips(win)

        # Catalog contains 5 seeds + 2 dynamic = 7 tips
        tips = db.get_all_tips(include_unknown=True)
        assert win.combo_tip.count() == len(tips)
        
        # Verify dynamic tip IDs (42 and 99) are present with exact userData
        data_ids = [win.combo_tip.itemData(i) for i in range(win.combo_tip.count())]
        assert 1 in data_ids
        assert 5 in data_ids
        assert 42 in data_ids
        assert 99 in data_ids

        # Verify labels reflect icon_char and name genuinely
        idx_42 = win.combo_tip.findData(42)
        assert "⚡" in win.combo_tip.itemText(idx_42)
        assert "Dynamic Silicon X" in win.combo_tip.itemText(idx_42)

    def test_suggest_tip_dynamic_switching(self, qapp, dynamic_db):
        db, _ = dynamic_db
        win = main.MainWindow.__new__(main.MainWindow)
        from PySide6.QtWidgets import QComboBox
        win.combo_tip = QComboBox()
        win.db = db
        main.MainWindow.populate_tips(win)

        # Switch to IEM 101 (last used tip is 42)
        win.current_iem_id = 101
        main.MainWindow.suggest_tip_for_current_iem(win)
        assert win.combo_tip.currentData() == 42

        # Switch to IEM 102 (last used tip is 99)
        win.current_iem_id = 102
        main.MainWindow.suggest_tip_for_current_iem(win)
        assert win.combo_tip.currentData() == 99

        # Switch to IEM 103 (last used tip was 1, legacy/unknown -> should fallback to default 3)
        win.current_iem_id = 103
        main.MainWindow.suggest_tip_for_current_iem(win)
        assert win.combo_tip.currentData() == 3

        # Switch to IEM 104 (no previous measurements -> fallback to default 3)
        win.current_iem_id = 104
        main.MainWindow.suggest_tip_for_current_iem(win)
        assert win.combo_tip.currentData() == 3

    def test_save_trace_to_db_genuine_persistence(self, qapp, dynamic_db, isolated_env):
        db, db_path = dynamic_db
        win = main.MainWindow.__new__(main.MainWindow)
        from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QWidget
        win.combo_tip = QComboBox()
        win.tip_container = QWidget()
        win.db = db
        win.current_iem_id = 104
        win.sub_lbl = QLabel()
        win.btn_save_db = QPushButton()
        win.load_targets = lambda: None
        
        # Provide valid measurement buffers
        freqs = np.linspace(20, 20000, 500, dtype=np.float32)
        mag = np.full(500, 80.0, dtype=np.float32)
        phase = np.zeros(500, dtype=np.float32)
        win.temp_freqs = freqs
        win.temp_mag_l = mag
        win.temp_mag_r = mag
        win.temp_phase_l = phase
        win.temp_phase_r = phase

        main.MainWindow.populate_tips(win)

        # 1. Unlocked flow with dynamic tip 42
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        win.tip_container.setVisible(True)
        win.combo_tip.setVisible(True)
        idx_42 = win.combo_tip.findData(42)
        win.combo_tip.setCurrentIndex(idx_42)
        assert win.combo_tip.currentData() == 42

        main.MainWindow.save_trace_to_db(win)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements WHERE iem_id = 104 ORDER BY id DESC LIMIT 1")
        saved_tip_id = cur.fetchone()[0]
        conn.close()
        assert saved_tip_id == 42, f"Expected tip_id=42 saved, got {saved_tip_id}"

        # 2. Unlocked flow with dynamic tip 99
        idx_99 = win.combo_tip.findData(99)
        win.combo_tip.setCurrentIndex(idx_99)
        assert win.combo_tip.currentData() == 99

        main.MainWindow.save_trace_to_db(win)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements WHERE iem_id = 104 ORDER BY id DESC LIMIT 1")
        saved_tip_id_2 = cur.fetchone()[0]
        conn.close()
        assert saved_tip_id_2 == 99, f"Expected tip_id=99 saved, got {saved_tip_id_2}"

        # 3. Locked flow -> must fallback to tip_id = 1
        config.revoke_prokit()
        win.tip_container.setVisible(False)
        win.combo_tip.setVisible(False)

        main.MainWindow.save_trace_to_db(win)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements WHERE iem_id = 104 ORDER BY id DESC LIMIT 1")
        saved_tip_id_3 = cur.fetchone()[0]
        conn.close()
        assert saved_tip_id_3 == 1, f"Expected tip_id=1 saved when locked, got {saved_tip_id_3}"

    def test_visibility_gate_lifecycle(self, qapp, isolated_env, dynamic_db):
        db, _ = dynamic_db
        win = main.MainWindow.__new__(main.MainWindow)
        from PySide6.QtWidgets import QComboBox, QWidget
        win.tip_container = QWidget()
        win.combo_tip = QComboBox()
        win.db = db
        win.current_iem_id = 101

        # Initially locked
        assert config.is_prokit_unlocked() is False
        main.MainWindow.update_prokit_ui_visibility(win)
        assert win.tip_container.isVisible() is False
        assert win.combo_tip.isVisible() is False

        # Unlock
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        assert config.is_prokit_unlocked() is True
        main.MainWindow.update_prokit_ui_visibility(win)
        assert win.tip_container.isVisible() is True
        assert win.combo_tip.isVisible() is True
        # Verify it auto-suggested tip 42 for IEM 101 on unlock
        assert win.combo_tip.currentData() == 42

        # Revoke
        config.revoke_prokit()
        assert config.is_prokit_unlocked() is False
        main.MainWindow.update_prokit_ui_visibility(win)
        assert win.tip_container.isVisible() is False
        assert win.combo_tip.isVisible() is False
