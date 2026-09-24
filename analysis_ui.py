import sys
import numpy as np
import theme
import config
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSplitter, QTabWidget, QComboBox, QDial, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal, QTimer
import pyqtgraph as pg

class FreqAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if not values: return []
        strings = []
        is_zoomed_out = (max(values) - min(values)) >= 0.9
        allowed_labels = {20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000}
        for v in values:
            hz = int(round(10**v))
            if is_zoomed_out and hz not in allowed_labels:
                strings.append("")
                continue
            if hz >= 1000:
                strings.append(f"{hz//1000}k" if hz % 1000 == 0 else f"{hz/1000:g}k")
            else:
                strings.append(f"{hz}")
        return strings

class RelativeDial(QDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._last_y = 0

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_y = event.pos().y()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = self._last_y - event.pos().y()
            self._last_y = event.pos().y()
            # Sensitivity: 1 pixel = 2 steps (out of 1000)
            # This makes a full sweep take ~500 pixels of vertical drag
            new_val = self.value() + delta * 3
            self.setValue(new_val)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
        else:
            super().mouseReleaseEvent(event)

class FloatKnob(QWidget):
    valueChanged = Signal(float)
    def __init__(self, title, min_val, max_val, default_val, scale='linear', suffix=""):
        super().__init__()
        self.min_val, self.max_val, self.scale, self.suffix = min_val, max_val, scale, suffix
        self.steps = 1000
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 8px; color: #888; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(self.lbl_title)
        
        self.dial = RelativeDial()
        self.dial.wheelEvent = lambda event: event.ignore()
        self.dial.setMinimum(0)
        self.dial.setMaximum(self.steps)
        self.dial.setWrapping(False)
        self.dial.setNotchesVisible(True)
        self.dial.setFixedSize(45, 45)
        self.dial.setStyleSheet("QDial { background-color: #2a2a2a; }")
        layout.addWidget(self.dial, alignment=Qt.AlignCenter)
        
        self.txt_val = QLineEdit()
        self.txt_val.setAlignment(Qt.AlignCenter)
        self.txt_val.setStyleSheet("QLineEdit { font-size: 10px; font-weight: bold; color: #ccc; border: 1px solid transparent; background: transparent; padding: 0px; } QLineEdit:focus { border: 1px solid #555; background: #222; }")
        self.txt_val.setFixedWidth(50)
        self.txt_val.editingFinished.connect(self._on_txt_changed)
        layout.addWidget(self.txt_val, alignment=Qt.AlignCenter)
        
        self._last_dial_val = self._val_to_dial(default_val)
        self.dial.valueChanged.connect(self._on_dial_changed)
        self.setValue(default_val)
        
    def _dial_to_val(self, d):
        if self.scale == 'log': return self.min_val * (self.max_val / self.min_val) ** (d / self.steps)
        else: return self.min_val + d * (self.max_val - self.min_val) / self.steps
            
    def _val_to_dial(self, v):
        if self.scale == 'log': return int(self.steps * np.log(v / self.min_val) / np.log(self.max_val / self.min_val))
        else: return int(self.steps * (v - self.min_val) / (self.max_val - self.min_val))
            
    def _on_dial_changed(self, val):
        # Anti-wrap guard: reject jumps > 50% of range (only happens on wrap-around)
        jump = abs(val - self._last_dial_val)
        if jump > self.steps * 0.5:
            # Clamp to nearest endpoint
            clamped = 0 if val > self.steps // 2 else self.steps
            self.dial.blockSignals(True)
            self.dial.setValue(clamped)
            self.dial.blockSignals(False)
            val = clamped
        self._last_dial_val = val
        
        real_val = self._dial_to_val(val)
        if self.suffix == "Hz":
            txt = f"{real_val/1000:.1f}k" if real_val >= 1000 else f"{int(real_val)}"
        elif self.suffix == "dB": txt = f"{real_val:+.1f}"
        else: txt = f"{real_val:.2f}"
        self.txt_val.setText(txt + self.suffix)
        self.valueChanged.emit(real_val)
        
    def _on_txt_changed(self):
        txt = self.txt_val.text().replace(self.suffix, '').replace(',', '.').strip()
        try:
            if 'k' in txt.lower():
                val = float(txt.lower().replace('k', '')) * 1000
            else:
                val = float(txt)
            val = max(self.min_val, min(self.max_val, val))
            self.setValue(val)
        except ValueError:
            self.setValue(self.value()) # reset to current if invalid
            
    def value(self): return self._dial_to_val(self.dial.value())
    def setValue(self, v):
        d = self._val_to_dial(v)
        self._last_dial_val = d
        self.dial.blockSignals(True)
        self.dial.setValue(d)
        self.dial.blockSignals(False)
        self._on_dial_changed(d)

from analysis import Analyzer

class AutoWrapLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(10, 10)

class StableTabWidget(QTabWidget):
    def sizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().sizeHint()
        return QSize(345, hint.height())
        
    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().minimumSizeHint()
        return QSize(220, 0)


class TipAnalysisCardWidget(QFrame):
    """
    ProKit Ear Tip Analysis & Acoustic Coupling Card for Diagnostics.
    Features:
    1. 8 kHz Helmholtz resonance peak detection within [6 kHz, 10 kHz] (L & R separate).
       Falls back to historical median peak from db.get_tip_target_peak(iem_id, tip_id).
    2. Band-limited reproducibility score (20 Hz - 8,000 Hz, L & R separate).
       Threshold: >= 5 measurements required. If < 5, shows empty state with current count.
       If 5-9 measurements, shows preliminary warning badge.
       If >= 10 measurements, shows stable badge.
    3. Acoustic seal history trend (40 Hz vs 500 Hz delta, L & R separate).
       Shows summaries and micro-chips.
    """
    tip_changed = Signal(int)

    TARGET_HELMHOLTZ_HZ = 8000.0

    @staticmethod
    def detect_helmholtz_peak(freqs, mag):
        """Detect local peak frequency in 6,000 Hz - 10,000 Hz window."""
        if freqs is None or mag is None:
            return None
        try:
            from scipy.signal import find_peaks
            f = np.asarray(freqs, dtype=np.float64)
            m = np.asarray(mag, dtype=np.float64)
            if len(f) != len(m) or len(f) < 10:
                return None
            mask = (f >= 6000.0) & (f <= 10000.0)
            if not np.any(mask):
                return None
            sub_f = f[mask]
            sub_m = m[mask]
            
            # Use find_peaks to ensure it's a true local peak, not just a steep slope
            peaks, properties = find_peaks(sub_m, prominence=3.0, width=60)
            
            if len(peaks) > 0:
                # Find the highest peak among the true local peaks
                best_peak_idx = peaks[np.argmax(properties['prominences'])]
                return float(sub_f[best_peak_idx])
            else:
                return None
        except Exception:
            return None

    def __init__(self, parent=None, db=None, iem_id=1, tip_id=1, freqs=None, mag_l=None, mag_r=None):
        super().__init__(parent)
        self.setObjectName("tip_analysis_card")
        self.db = db
        self.iem_id = iem_id if iem_id is not None else 1
        self.tip_id = tip_id if tip_id is not None else 1
        self.freqs = freqs
        self.mag_l = mag_l
        self.mag_r = mag_r

        self.setVisible(config.is_prokit_unlocked())
        self._init_ui()
        self.populate_tips()
        self.refresh_metrics()

    def _init_ui(self):
        self.setStyleSheet("""
            QFrame#tip_analysis_card {
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(4)

        # ── Header Row ──────────────────────────────────────────────
        hdr_layout = QVBoxLayout()
        hdr_layout.setContentsMargins(0, 0, 0, 0)
        hdr_layout.setSpacing(4)

        tag_lbl = QLabel("PROKIT")
        tag_lbl.setStyleSheet("background: #1a3040; color: #5b8fa8; font-size: 8px; font-weight: bold; border-radius: 4px; padding: 2px 6px; letter-spacing: 1px;")
        tag_container = QHBoxLayout()
        tag_container.setContentsMargins(0, 0, 0, 0)
        tag_container.addWidget(tag_lbl)
        tag_container.addStretch()
        hdr_layout.addLayout(tag_container)

        self.cb_tip_selector = QComboBox()
        self.cb_tip_selector.setObjectName("cb_tip_selector")
        self.cb_tip_selector.currentIndexChanged.connect(self._on_tip_combo_changed)
        self.cb_tip_selector.hide()
        
        card_layout.addLayout(hdr_layout)

        # ── Section 1: Helmholtz Resonance Peak (6-10 kHz) ──────────
        sec1 = QFrame()
        sec1.setObjectName("sec_helmholtz")
        sec1.setStyleSheet("QFrame#sec_helmholtz { background-color: #1a1a1e; border: 1px solid #2a2a2e; border-left: 2px solid #5b8fa8; border-radius: 4px; }")
        s1_layout = QVBoxLayout(sec1)
        s1_layout.setContentsMargins(8, 8, 8, 8)
        s1_layout.setSpacing(4)

        s1_title = QLabel("HELMHOLTZ PEAK")
        s1_title.setStyleSheet("color: #5b8fa8; font-size: 10px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none;")
        s1_layout.addWidget(s1_title)

        grid1 = QVBoxLayout()
        grid1.setSpacing(4)

        # Left Peak Box
        self.lbl_peak_l = QLabel("L: — Hz")
        self.lbl_peak_l.setObjectName("lbl_peak_l")
        self.lbl_peak_l.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.badge_peak_delta_l = QLabel("—")
        self.badge_peak_delta_l.setStyleSheet("background: #1a1a1e; color: #666666; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
        box_l = QVBoxLayout()
        box_l.setSpacing(2)
        box_l.addWidget(self.lbl_peak_l)
        box_l.addWidget(self.badge_peak_delta_l)
        grid1.addLayout(box_l)

        # Right Peak Box
        self.lbl_peak_r = QLabel("R: — Hz")
        self.lbl_peak_r.setObjectName("lbl_peak_r")
        self.lbl_peak_r.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.badge_peak_delta_r = QLabel("—")
        self.badge_peak_delta_r.setStyleSheet("background: #1a1a1e; color: #666666; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
        box_r = QVBoxLayout()
        box_r.setSpacing(2)
        box_r.addWidget(self.lbl_peak_r)
        box_r.addWidget(self.badge_peak_delta_r)
        grid1.addLayout(box_r)

        s1_layout.addLayout(grid1)

        self.lbl_peak_target = QLabel("Target: 8,000 Hz")
        self.lbl_peak_target.setWordWrap(True)
        self.lbl_peak_target.setStyleSheet("color: #666666; font-size: 9px; background: transparent; border: none;")
        s1_layout.addWidget(self.lbl_peak_target)
        card_layout.addWidget(sec1)

        # ── Section 2: Reproducibility Score (20 Hz - 8 kHz) ────────
        sec2 = QFrame()
        sec2.setObjectName("sec_reproducibility")
        sec2.setStyleSheet("QFrame#sec_reproducibility { background-color: #1a1a1e; border: 1px solid #2a2a2e; border-left: 2px solid #6b9080; border-radius: 4px; }")
        s2_layout = QVBoxLayout(sec2)
        s2_layout.setContentsMargins(8, 8, 8, 8)
        s2_layout.setSpacing(4)

        s2_hdr = QVBoxLayout()
        s2_hdr.setSpacing(2)
        s2_title = QLabel("REPRODUCIBILITY")
        s2_title.setStyleSheet("color: #6b9080; font-size: 10px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none;")
        s2_hdr.addWidget(s2_title)

        self.badge_repro_status = QLabel("")
        self.badge_repro_status.setObjectName("badge_repro_preliminary")
        self.badge_repro_preliminary = self.badge_repro_status
        self.badge_repro_status.setStyleSheet("background: transparent; border: none;")
        self.badge_repro_status.hide()
        s2_hdr.addWidget(self.badge_repro_status)
        s2_layout.addLayout(s2_hdr)

        self.lbl_repro_warning = QLabel("")
        self.lbl_repro_warning.setObjectName("lbl_repro_warning")
        self.lbl_repro_empty = self.lbl_repro_warning
        self.lbl_repro_warning.setWordWrap(True)
        self.lbl_repro_warning.setStyleSheet("background: transparent; border: 1px dashed #444444; border-radius: 4px; padding: 4px 8px; color: #555555; font-size: 9px;")
        self.lbl_repro_warning.hide()
        s2_layout.addWidget(self.lbl_repro_warning)

        self.repro_scores_widget = QWidget()
        self.repro_scores_widget.setStyleSheet("background: transparent; border: none;")
        scores_layout = QVBoxLayout(self.repro_scores_widget)
        scores_layout.setContentsMargins(0, 0, 0, 0)
        scores_layout.setSpacing(4)

        self.lbl_score_l = QLabel("L: —")
        self.lbl_score_l.setObjectName("lbl_score_l")
        self.lbl_score_l.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.lbl_score_r = QLabel("R: —")
        self.lbl_score_r.setObjectName("lbl_score_r")
        self.lbl_score_r.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")

        scores_layout.addWidget(self.lbl_score_l)
        scores_layout.addWidget(self.lbl_score_r)
        s2_layout.addWidget(self.repro_scores_widget)
        card_layout.addWidget(sec2)

        # ── Section 3: Acoustic Seal History (40 Hz vs 500 Hz) ──────
        sec3 = QFrame()
        sec3.setObjectName("sec_seal_history")
        sec3.setStyleSheet("QFrame#sec_seal_history { background-color: #1a1a1e; border: 1px solid #2a2a2e; border-left: 2px solid #8b7ba8; border-radius: 4px; }")
        s3_layout = QVBoxLayout(sec3)
        s3_layout.setContentsMargins(8, 8, 8, 8)
        s3_layout.setSpacing(4)

        s3_title = QLabel("SEAL HISTORY")
        s3_title.setStyleSheet("color: #8b7ba8; font-size: 10px; font-weight: 900; letter-spacing: 1px; background: transparent; border: none;")
        s3_layout.addWidget(s3_title)

        seal_grid = QVBoxLayout()
        seal_grid.setSpacing(4)

        self.lbl_seal_summary_l = QLabel("L: —")
        self.lbl_seal_summary_l.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.lbl_seal_summary_r = QLabel("R: —")
        self.lbl_seal_summary_r.setStyleSheet("color: #ffffff; font-size: 11px; font-weight: bold; background: transparent; border: none;")

        seal_grid.addWidget(self.lbl_seal_summary_l)
        seal_grid.addWidget(self.lbl_seal_summary_r)
        s3_layout.addLayout(seal_grid)

        self.trend_chips_layout = QVBoxLayout()
        self.trend_chips_layout.setSpacing(3)
        s3_layout.addLayout(self.trend_chips_layout)
        card_layout.addWidget(sec3)

    def populate_tips(self):
        """Populate the tip selector dropdown from DatabaseManager catalog."""
        self.cb_tip_selector.blockSignals(True)
        self.cb_tip_selector.clear()
        if not self.db or not hasattr(self.db, 'get_all_tips'):
            self.cb_tip_selector.addItem("Unknown", userData=1)
            self.cb_tip_selector.blockSignals(False)
            return
        try:
            tips = self.db.get_all_tips(include_unknown=True)
            cur_idx = 0
            for i, tip in enumerate(tips):
                t_id = tip.get('id')
                name = tip.get('name', 'Unknown')
                icon = tip.get('icon_char', '?')
                mat = tip.get('material', '')
                mat_str = f" ({mat})" if mat else ""
                display = f"{icon} {name}{mat_str}"
                self.cb_tip_selector.addItem(display, userData=t_id)
                if t_id == self.tip_id:
                    cur_idx = i
            self.cb_tip_selector.setCurrentIndex(cur_idx)
        except Exception:
            self.cb_tip_selector.addItem("Unknown", userData=1)
        finally:
            self.cb_tip_selector.blockSignals(False)

    def _on_tip_combo_changed(self, idx):
        selected_tip_id = self.cb_tip_selector.currentData()
        if selected_tip_id is not None:
            self.tip_id = int(selected_tip_id)
            self.tip_changed.emit(self.tip_id)
            self.refresh_metrics()

    def set_active_iem(self, iem_id):
        if iem_id is not None:
            self.iem_id = int(iem_id)
            self.refresh_metrics()

    def set_active_tip(self, tip_id):
        if tip_id is not None:
            self.tip_id = int(tip_id)
            idx = self.cb_tip_selector.findData(self.tip_id)
            if idx != -1:
                self.cb_tip_selector.blockSignals(True)
                self.cb_tip_selector.setCurrentIndex(idx)
                self.cb_tip_selector.blockSignals(False)
            self.refresh_metrics()

    def update_theme(self):
        bg = theme.get_color("bg_panel")
        border = theme.get_color("border")
        fg = theme.get_color("text_primary")
        
        self.setStyleSheet(f"QFrame#tip_card {{ background-color: {bg}; border: 1px solid {border}; border-radius: 6px; }}")
        if hasattr(self, 'lbl_title'):
            self.lbl_title.setStyleSheet(f"color: {fg}; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        
        # We find children by object name instead of keeping references
        from PySide6.QtWidgets import QFrame
        sec1 = self.findChild(QFrame, "sec_helmholtz")
        if sec1: sec1.setStyleSheet(f"QFrame#sec_helmholtz {{ background-color: {theme.get_color('bg_main')}; border: 1px solid {border}; border-left: 2px solid #0ea5e9; border-radius: 4px; }}")
        
        sec2 = self.findChild(QFrame, "sec_reproducibility")
        if sec2: sec2.setStyleSheet(f"QFrame#sec_reproducibility {{ background-color: {theme.get_color('bg_main')}; border: 1px solid {border}; border-left: 2px solid #10b981; border-radius: 4px; }}")
        
        sec3 = self.findChild(QFrame, "sec_seal_history")
        if sec3: sec3.setStyleSheet(f"QFrame#sec_seal_history {{ background-color: {theme.get_color('bg_main')}; border: 1px solid {border}; border-left: 2px solid #8b5cf6; border-radius: 4px; }}")

    def update_data(self, iem_id=None, tip_id=None, freqs=None, mag_l=None, mag_r=None):
        if iem_id is not None:
            self.iem_id = int(iem_id)
        if tip_id is not None:
            self.tip_id = int(tip_id)
            idx = self.cb_tip_selector.findData(self.tip_id)
            if idx != -1:
                self.cb_tip_selector.blockSignals(True)
                self.cb_tip_selector.setCurrentIndex(idx)
                self.cb_tip_selector.blockSignals(False)
        if freqs is not None:
            self.freqs = freqs
        if mag_l is not None:
            self.mag_l = mag_l
        if mag_r is not None:
            self.mag_r = mag_r
        self.refresh_metrics()

    def refresh_metrics(self):
        """Query DB and update all sections: Helmholtz Peak, Reproducibility, and Seal History."""
        # 1. Helmholtz Resonance Peak
        peak_l = None
        peak_r = None
        if getattr(self, 'freqs', None) is not None:
            if getattr(self, 'mag_l', None) is not None:
                peak_l = self.detect_helmholtz_peak(self.freqs, self.mag_l)
            if getattr(self, 'mag_r', None) is not None:
                peak_r = self.detect_helmholtz_peak(self.freqs, self.mag_r)

        # Fallback to historical median peak if live data not available
        if (peak_l is None or peak_r is None) and self.db and hasattr(self.db, 'get_tip_target_peak'):
            try:
                hist_peaks = self.db.get_tip_target_peak(self.iem_id, self.tip_id)
                if hist_peaks:
                    if peak_l is None and hist_peaks.get('left') is not None:
                        peak_l = hist_peaks['left']
                    if peak_r is None and hist_peaks.get('right') is not None:
                        peak_r = hist_peaks['right']
            except Exception:
                pass

        def update_peak_display(lbl_val, badge_delta, peak_val, chan_name):
            if peak_val is not None:
                lbl_val.setText(f"{chan_name}: {int(round(peak_val))} Hz")
                delta_hz = peak_val - self.TARGET_HELMHOLTZ_HZ
                sign = "+" if delta_hz >= 0 else ""
                badge_delta.setText(f"Δ {sign}{int(round(delta_hz))} Hz")
                abs_d = abs(delta_hz)
                if abs_d <= 200:
                    badge_delta.setStyleSheet("background: #065f46; color: #34d399; border: 1px solid #10b981; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Peak aligns closely with 8 kHz coupler target (Optimal depth).")
                elif abs_d <= 500:
                    badge_delta.setStyleSheet("background: #451a03; color: #fbbf24; border: 1px solid #f59e0b; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Moderate resonance shift (Acceptable coupling).")
                else:
                    badge_delta.setStyleSheet("background: #7f1d1d; color: #f87171; border: 1px solid #ef4444; border-radius: 3px; padding: 1px 4px; font-size: 9px; font-weight: bold;")
                    badge_delta.setToolTip("Resonance peak shifted > 500 Hz (Check insertion depth / seal).")
            else:
                lbl_val.setText(f"{chan_name}: — Hz")
                badge_delta.setText("—")
                badge_delta.setStyleSheet("background: #27272a; color: #71717a; border-radius: 3px; padding: 1px 4px; font-size: 9px;")
                badge_delta.setToolTip("No peak detected.")

        update_peak_display(self.lbl_peak_l, self.badge_peak_delta_l, peak_l, "L")
        update_peak_display(self.lbl_peak_r, self.badge_peak_delta_r, peak_r, "R")

        # 2. Reproducibility Score (Band-limited to 20-8000 Hz)
        scores = None
        if self.db and hasattr(self.db, 'get_reproducibility_scores'):
            try:
                scores = self.db.get_reproducibility_scores(self.iem_id, self.tip_id)
            except Exception:
                scores = None

        if scores is None:
            # Query measurement count for empty state message
            count = 0
            if self.db and hasattr(self.db, 'db_path'):
                try:
                    import sqlite3
                    conn = sqlite3.connect(self.db.db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM Measurements WHERE iem_id = ? AND tip_id = ?", (self.iem_id, self.tip_id))
                    row = cur.fetchone()
                    if row:
                        count = row[0]
                    conn.close()
                except Exception:
                    count = 0

            self.lbl_repro_warning.setText(f"Not enough data (min. 5 measurements required, currently N={count})")
            self.lbl_repro_warning.show()
            self.repro_scores_widget.hide()
            self.badge_repro_status.hide()
            self.lbl_score_l.setText("L: —")
            self.lbl_score_r.setText("R: —")
        else:
            self.lbl_repro_warning.hide()
            self.repro_scores_widget.show()

            left_data = scores.get('left')
            right_data = scores.get('right')

            count = 0
            if left_data and 'count' in left_data:
                count = max(count, left_data['count'])
            if right_data and 'count' in right_data:
                count = max(count, right_data['count'])

            def format_score_str(sc_dict):
                if not sc_dict:
                    return "—"
                std = sc_dict.get('std_dev', sc_dict.get('score', 0.0))
                pct = max(0.0, min(100.0, 100.0 - (std * 14.4)))
                return f"{pct:.1f}% (±{std:.2f} dB)"

            self.lbl_score_l.setText(f"L: {format_score_str(left_data)}")
            self.lbl_score_r.setText(f"R: {format_score_str(right_data)}")

            if count < 10:
                self.badge_repro_status.setText(f"⚠ Preliminary (N={count})")
                self.badge_repro_status.setStyleSheet("background: #451a03; color: #fbbf24; border: 1px solid #f59e0b; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: bold;")
                self.badge_repro_status.setToolTip("Score is preliminary (5–9 measurements). 10+ recommended for stable statistics.")
                self.badge_repro_status.show()
            else:
                self.badge_repro_status.setText(f"✓ Stable (N={count})")
                self.badge_repro_status.setStyleSheet("background: #065f46; color: #34d399; border: 1px solid #10b981; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: bold;")
                self.badge_repro_status.setToolTip("Verified sample size (≥ 10 measurements).")
                self.badge_repro_status.show()

        # 3. Acoustic Seal History Trend (40 Hz vs 500 Hz)
        while self.trend_chips_layout.count():
            item = self.trend_chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        seal_data = {"left": [], "right": []}
        if self.db and hasattr(self.db, 'get_seal_history'):
            try:
                seal_data = self.db.get_seal_history(self.iem_id, self.tip_id) or {"left": [], "right": []}
            except Exception:
                pass

        hist_l = seal_data.get("left", [])
        hist_r = seal_data.get("right", [])

        def summarize_seal(hist, chan_name):
            n = len(hist)
            if n == 0:
                return f"{chan_name}: No data"
            ok_cnt = sum(1 for e in hist if e.get("seal_ok"))
            pct = (ok_cnt / n) * 100.0
            mean_delta = float(np.mean([e.get("delta_db", 0.0) for e in hist]))
            return f"{chan_name}: {ok_cnt}/{n} OK ({pct:.0f}%) | Mean Δ: {mean_delta:+.1f} dB"

        self.lbl_seal_summary_l.setText(summarize_seal(hist_l, "L"))
        self.lbl_seal_summary_r.setText(summarize_seal(hist_r, "R"))

        if hist_l:
            tag_l = QLabel("L:")
            tag_l.setStyleSheet("color: #3b82f6; font-size: 8px; font-weight: bold;")
            self.trend_chips_layout.addWidget(tag_l)
            for idx, entry in enumerate(hist_l[-8:]):
                chip = QLabel(f"#{idx+1}")
                is_ok = entry.get("seal_ok", True)
                delta = entry.get("delta_db", 0.0)
                status = entry.get("status", "OK")
                ts = entry.get("timestamp", "")
                if is_ok:
                    chip.setStyleSheet("background: #065f46; color: #34d399; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
                else:
                    chip.setStyleSheet("background: #7f1d1d; color: #f87171; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
                chip.setToolTip(f"Left Take #{idx+1} ({ts})\nSeal: {status}\nDelta: {delta:+.1f} dB")
                self.trend_chips_layout.addWidget(chip)

        if hist_r:
            tag_r = QLabel("R:")
            tag_r.setStyleSheet("color: #ef4444; font-size: 8px; font-weight: bold; margin-left: 6px;")
            self.trend_chips_layout.addWidget(tag_r)
            for idx, entry in enumerate(hist_r[-8:]):
                chip = QLabel(f"#{idx+1}")
                is_ok = entry.get("seal_ok", True)
                delta = entry.get("delta_db", 0.0)
                status = entry.get("status", "OK")
                ts = entry.get("timestamp", "")
                if is_ok:
                    chip.setStyleSheet("background: #065f46; color: #34d399; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
                else:
                    chip.setStyleSheet("background: #7f1d1d; color: #f87171; border-radius: 3px; padding: 1px 4px; font-size: 8px; font-weight: bold;")
                chip.setToolTip(f"Right Take #{idx+1} ({ts})\nSeal: {status}\nDelta: {delta:+.1f} dB")
                self.trend_chips_layout.addWidget(chip)

        self.trend_chips_layout.addStretch()


class AnalysisWidget(QWidget):
    request_measurement = Signal()
    request_stress_test = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("AnalysisRoot")
        self.setStyleSheet("#AnalysisRoot { background-color: transparent; color: white; }")
        
        self.tip_analysis_card = None
        self.current_iem_id = None
        self.current_tip_id = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- 2026 UI: No giant headers, just a clean rigid layout ---
        self.split_layout = QSplitter(Qt.Horizontal)
        self.split_layout.setContentsMargins(0, 0, 0, 0)
        self.split_layout.setHandleWidth(1)
        self.split_layout.setChildrenCollapsible(False)
        self.layout.addWidget(self.split_layout)
        
        # --- Left Pane ---
        left_pane_widget = QWidget()
        left_pane_layout = QVBoxLayout(left_pane_widget)
        left_pane_layout.setContentsMargins(4, 4, 4, 0)
        left_pane_layout.setSpacing(6)
        

        
        # --- Left Pane: Graphs (QTabWidget) ---
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setElideMode(Qt.ElideNone)
        self.graph_tabs.setUsesScrollButtons(True)
        self.graph_tabs.currentChanged.connect(lambda _: self.render_diagnostics())
        
        # 1. FR Graph
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(4, 4, 4, 4)
        fr_layout.setSpacing(4)
        
        # --- Smart Toolbar logic (extracted to main.py) ---
        from PySide6.QtWidgets import QLabel
        vis_layout = QVBoxLayout()
        vis_layout.setSpacing(2)
        vis_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_chan_l = QPushButton("L")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #0ea5e9; color: white; border-color: #0ea5e9; }")
        
        self.btn_chan_r = QPushButton("R")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #ef4444; color: white; border-color: #ef4444; }")

        self.cb_ana_target = QComboBox()
        self.cb_ana_target.hide()
        self.cb_ana_target.addItem("-- Target --")
        self.cb_ana_target.setToolTip("Select a target curve for analysis.")
        self.cb_ana_target.setMinimumWidth(120)
        
        self.cb_ana_history = QComboBox()
        self.cb_ana_history.hide()
        self.cb_ana_history.addItem("-- History --")
        self.cb_ana_history.setToolTip("Select a historical measurement.")
        self.cb_ana_history.setMinimumWidth(120)
        
        self.btn_chan_l.toggled.connect(self.refresh_view)
        self.btn_chan_l.toggled.connect(lambda _: self.render_diagnostics())
        self.btn_chan_r.toggled.connect(self.refresh_view)
        self.btn_chan_r.toggled.connect(lambda _: self.render_diagnostics())

        
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setBackground('#18181b')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.getAxis('bottom').setHeight(25)
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
        self.plot_widget.getAxis('left').setWidth(45)
        self.plot_widget.setXRange(np.log10(20), np.log10(20000))
        self.plot_widget.setYRange(40, 110)
        self.plot_widget.addLegend(offset=(10, 10))
        self.eq_tf_line = self.plot_widget.plot(pen=pg.mkPen('#06b6d4', width=2, style=Qt.DashLine), name="EQ Curve (0dB = 60dB)")
        self.eq_tf_line.setZValue(10)
        self.eq_tf_line.hide()
        
        # --- Crosshair Setup ---
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color=(255, 255, 255, 120), width=1))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color=(255, 255, 255, 120), width=1))
        self.crosshair_label = pg.TextItem(anchor=(0, 1), color=(255, 255, 255, 200), fill=(24, 24, 27, 200))
        self.vLine.hide()
        self.hLine.hide()
        self.crosshair_label.hide()
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        self.plot_widget.addItem(self.crosshair_label, ignoreBounds=True)
        self.plot_widget.scene().sigMouseMoved.connect(self.mouseMoved)
        
        fr_layout.addWidget(self.plot_widget)
        
        self.graph_tabs.addTab(self.fr_container, "Freq Response")
        
        # 2. THD Graph + Stress Test
        thd_container = QWidget()
        thd_layout = QVBoxLayout(thd_container)
        thd_layout.setContentsMargins(0, 0, 0, 0)
        thd_layout.setSpacing(4)
        
        self.thd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.thd_widget.setClipToView(True)
        self.thd_widget.setDownsampling(auto=True, mode='peak')
        self.thd_widget.setBackground('#18181b')
        self.thd_widget.setLogMode(x=True, y=False)
        self.thd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.thd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.thd_widget.getAxis('bottom').setHeight(25)
        self.thd_widget.setLabel('left', 'THD', units='%')
        self.thd_widget.getAxis('left').setWidth(45)
        self.thd_widget.setXRange(np.log10(20), np.log10(10000))
        self.thd_widget.setYRange(0, 5)
        self.thd_widget.addLegend(offset=(10, 10))
        
        # HOHD overlay line (hidden until stress test runs)
        self.hohd_line = self.thd_widget.plot(pen=pg.mkPen('#ef4444', width=2, style=Qt.DashLine), name="R&B (HOHD)")
        self.hohd_line.hide()
        
        thd_layout.addWidget(self.thd_widget)
        
        # Stress test button bar
        stress_bar = QHBoxLayout()
        self.btn_stress_test = QPushButton("STRESS TEST")
        self.btn_stress_test.setEnabled(False)
        self.btn_stress_test.setToolTip("Run Output Level Calibration in Settings first.")
        self.btn_stress_test.setProperty("class", "danger")
        self.btn_stress_test.clicked.connect(self.request_stress_test.emit)
        stress_bar.addStretch()
        stress_bar.addWidget(self.btn_stress_test)
        thd_layout.addLayout(stress_bar)
        
        self.graph_tabs.addTab(thd_container, "Distortion (THD)")
        # 3. CSD Graph
        self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.csd_widget.setClipToView(True)
        self.csd_widget.setDownsampling(auto=True, mode='peak')
        self.csd_widget.setBackground('#18181b')
        self.csd_widget.setLogMode(x=True, y=False)
        self.csd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.csd_widget.getAxis('bottom').setHeight(25)
        self.csd_widget.setLabel('left', 'Magnitude (dB)')
        self.csd_widget.getAxis('left').setWidth(45)
        self.csd_widget.setXRange(np.log10(200), np.log10(20000))
        self.csd_widget.setYRange(-60, 20)
        self.csd_widget.getViewBox().disableAutoRange()
        self.graph_tabs.addTab(self.csd_widget, "Waterfall (CSD)")
        
        left_pane_layout.addWidget(self.graph_tabs)
        self.split_layout.addWidget(left_pane_widget)
        
        # --- Right Pane: Tools (QTabWidget) ---
        self.right_pane_wrapper = QWidget()
        self.right_pane_wrapper.setMinimumWidth(0)  # Allow splitter to collapse to just button
        self.right_pane_wrapper.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.right_pane_layout = QHBoxLayout(self.right_pane_wrapper)
        self.right_pane_layout.setContentsMargins(0,0,0,0)
        self.right_pane_layout.setSpacing(0)
        
        self.btn_toggle_tools = QPushButton("▶")
        self.btn_toggle_tools.setFixedWidth(16)
        self.btn_toggle_tools.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_toggle_tools.setStyleSheet("QPushButton { background-color: #2a2a2f; color: #888; border: none; border-left: 1px solid #3f3f46; font-size: 10px; } QPushButton:hover { background-color: #3f3f46; color: white; }")
        self.btn_toggle_tools.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_tools.clicked.connect(self.toggle_tools_pane)
        self.right_pane_layout.addWidget(self.btn_toggle_tools)
        
        self.tools_tabs = StableTabWidget()
        # self.tools_tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.tools_tabs.setElideMode(Qt.ElideNone)
        self.tools_tabs.setUsesScrollButtons(False)
        self.tools_tabs.setMinimumWidth(0)   # Let splitter control width, not minimumWidth
        self.tools_tabs.setMaximumWidth(400)
        self.right_pane_layout.addWidget(self.tools_tabs)
        

        # 1. Diagnostics Tool
        self.diag_container = QWidget()
        diag_layout = QVBoxLayout(self.diag_container)
        diag_layout.setContentsMargins(4, 4, 4, 4)
        
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.report_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.report_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_scroll.setWidget(self.report_container)
        diag_layout.addWidget(self.report_scroll)
        self.tools_tabs.addTab(self.diag_container, "Diag")
        

        
        # 2. Hardware DSP Tool (Ultra Compact 2026 UI)
        self.dsp_container_widget = QWidget()
        dsp_layout = QVBoxLayout(self.dsp_container_widget)
        dsp_layout.setContentsMargins(6, 6, 6, 6)
        dsp_layout.setSpacing(4)
        
        self.dsp_container = QScrollArea()
        self.dsp_container.setWidgetResizable(True)
        self.dsp_container.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dsp_container.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dsp_container.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.dsp_container.setWidget(self.dsp_container_widget)
        

        
        # --- Master Bypass ---
        self.btn_dsp_master = QPushButton("DSP BYPASSED")
        self.btn_dsp_master.setCheckable(True)
        self.btn_dsp_master.setStyleSheet("QPushButton { background: #3f3f46; color: #a1a1aa; font-weight: bold; font-size: 11px; padding: 4px; border-radius: 4px; } QPushButton:checked { background: #059669; color: white; border: 2px solid #34d399; }")
        dsp_layout.addWidget(self.btn_dsp_master)
        
        # --- EQ Bands (Horizontal, ultra compact) ---
        self.peq_bands = []
        for i in reversed(range(5)):
            band_frame = QFrame()
            band_frame.setStyleSheet("QFrame { background: #18181b; border: 1px solid #333; border-radius: 4px; }")
            bl = QHBoxLayout(band_frame)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(6)
            
            # Left side: ON + Name
            left_info = QVBoxLayout()
            left_info.setSpacing(2)
            left_info.setAlignment(Qt.AlignCenter)
            lbl = QLabel(f"B{i+1}\n{'LS' if i==0 else 'HS' if i==4 else 'PEQ'}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 9px; font-weight: bold; color: #888; border: none; background: transparent;")
            cb_on = QPushButton("ON")
            cb_on.setCheckable(True)
            cb_on.setChecked(True)
            cb_on.setFixedSize(26, 14)
            cb_on.setStyleSheet("QPushButton { background: #444; color: #888; font-size: 8px; border-radius: 4px; font-weight: bold; } QPushButton:checked { background: #0ea5e9; color: white; }")
            left_info.addWidget(lbl)
            left_info.addWidget(cb_on)
            bl.addLayout(left_info)
            
            # Space them evenly
            bl.addStretch()
            
            # Knobs
            knob_f = FloatKnob("FREQ", 20, 20000, [60, 250, 1000, 4000, 8000][i], 'log', 'Hz')
            knob_g = FloatKnob("GAIN", -24, 24, 0, 'linear', 'dB')
            knob_q = FloatKnob("Q", 0.1, 10, 0.7 if i==0 or i==4 else 1.41, 'log', '')
            
            bl.addWidget(knob_f)
            bl.addStretch()
            bl.addWidget(knob_g)
            bl.addStretch()
            bl.addWidget(knob_q)
            bl.addStretch()
            
            dsp_layout.addWidget(band_frame)
            self.peq_bands.insert(0, {'on': cb_on, 'f': knob_f, 'g': knob_g, 'q': knob_q, 'type': 'peq' if i>0 and i<4 else ('lowshelf' if i==0 else 'highshelf')})
            
            def update_dsp(val=0, idx=i):
                from eq_math import dsp_engine
                filters = []
                for b in self.peq_bands:
                    filters.append({
                        'enabled': b['on'].isChecked(),
                        'freq': b['f'].value(),
                        'gain': b['g'].value(),
                        'q': b['q'].value(),
                        'type': b['type']
                    })
                dsp_engine.set_filters(filters)
                dsp_engine.set_master(self.btn_dsp_master.isChecked())
                
                if hasattr(self, 'eq_tf_line') and self.eq_tf_line is not None:
                    import numpy as np
                    f_pure = np.logspace(np.log10(20), np.log10(20000), 200)
                    pure_delta = dsp_engine.get_magnitude_response(f_pure, 48000)
                    self.eq_tf_line.setData(f_pure, 60.0 + pure_delta)
                    if self.btn_dsp_master.isChecked():
                        self.eq_tf_line.show()
                    else:
                        self.eq_tf_line.hide()
                        
                if hasattr(self, 'current_freqs') and self.current_freqs is not None:
                    if hasattr(self, 'virtual_eq_line') and self.virtual_eq_line is not None:
                        eq_delta = dsp_engine.get_magnitude_response(self.current_freqs, 48000)
                        base_mag = self.current_mag_l if self.current_mag_l is not None else self.current_mag_r
                        if base_mag is not None:
                            from audio_engine import AudioEngine
                            f_eq, m_eq, _ = AudioEngine.smooth_spectrum(self.current_freqs, base_mag + eq_delta, points=getattr(self, "current_smoothing_pts", 240))
                            self.virtual_eq_line.setData(f_eq, m_eq)
                            if self.btn_dsp_master.isChecked():
                                self.virtual_eq_line.show()
                            else:
                                self.virtual_eq_line.hide()
                                
            cb_on.toggled.connect(update_dsp)
            knob_f.valueChanged.connect(update_dsp)
            knob_g.valueChanged.connect(update_dsp)
            knob_q.valueChanged.connect(update_dsp)
            
        
        def on_master_toggle(checked):
            self.btn_dsp_master.setText("DSP ACTIVE (LIVE)" if checked else "DSP BYPASSED")
            if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
                self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())
                
        self.btn_dsp_master.toggled.connect(on_master_toggle)
        
        # --- EQ PRESET CARDS AREA ---
        from PySide6.QtWidgets import QLineEdit
        
        save_layout = QHBoxLayout()
        self.le_preset_name = QLineEdit()
        self.le_preset_name.setPlaceholderText("New Preset Name...")
        self.le_preset_name.setStyleSheet("QLineEdit { background: #111; color: white; border: 1px solid #333; padding: 4px; border-radius: 4px; font-size: 11px; }")
        self.btn_save_eq = QPushButton("Save Current")
        self.btn_save_eq.setProperty("class", "accent")
        save_layout.addWidget(self.le_preset_name)
        save_layout.addWidget(self.btn_save_eq)
        dsp_layout.addLayout(save_layout)
        
        self.preset_cards_scroll = QScrollArea()
        self.preset_cards_scroll.setWidgetResizable(True)
        self.preset_cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preset_cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preset_cards_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.preset_cards_container = QWidget()
        self.preset_cards_layout = QVBoxLayout(self.preset_cards_container)
        self.preset_cards_layout.setContentsMargins(0, 5, 0, 0)
        self.preset_cards_layout.setSpacing(4)
        self.preset_cards_layout.setAlignment(Qt.AlignTop)
        self.preset_cards_scroll.setWidget(self.preset_cards_container)
        dsp_layout.addWidget(self.preset_cards_scroll, stretch=1)
        
        self.tools_tabs.addTab(self.dsp_container, "EQ")
        
        self.tips_scroll = QScrollArea()
        self.tips_scroll.setWidgetResizable(True)
        self.tips_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tips_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tips_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.tips_container = QWidget()
        self.tips_container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.tips_layout = QVBoxLayout(self.tips_container)
        self.tips_layout.setAlignment(Qt.AlignTop)
        self.tips_layout.setContentsMargins(4, 4, 4, 4)
        
        self.tip_analysis_card = TipAnalysisCardWidget(
            parent=self.tips_container,
            db=getattr(self, 'db', None),
            iem_id=getattr(self, 'current_iem_id', 1),
            tip_id=getattr(self, 'current_tip_id', 1),
            freqs=getattr(self, 'current_freqs', None),
            mag_l=getattr(self, 'current_mag_l', None),
            mag_r=getattr(self, 'current_mag_r', None)
        )
        self.tips_layout.addWidget(self.tip_analysis_card)
        self.tips_scroll.setWidget(self.tips_container)
        
        self.tools_tabs.addTab(self.tips_scroll, "Tips")
        tips_idx = self.tools_tabs.indexOf(self.tips_scroll)
        self.tools_tabs.setTabVisible(tips_idx, config.is_prokit_unlocked())

        self.split_layout.addWidget(self.right_pane_wrapper)
        self.split_layout.setStretchFactor(0, 1)
        self.split_layout.setStretchFactor(1, 0)
        
        self.init_eq_db()
        self.load_eq_presets()
        self.btn_save_eq.clicked.connect(self.save_eq_preset)
        self.update_theme()
        self._initial_shown = False  # Flag for first showEvent


    def reset_zoom(self):
        import numpy as np
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.plot_widget.setYRange(40, 110, padding=0.0)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.thd_widget.plotItem.vb.autoRange(padding=0.1)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setXRange(np.log10(200), np.log10(20000), padding=0.0)
            self.csd_widget.plotItem.vb.autoRange(padding=0.1)

    def zoom_graph(self, min_f, max_f):
        import numpy as np
        if hasattr(self, 'current_main_widget'):
            self.current_main_widget.setXRange(np.log10(min_f), np.log10(max_f), padding=0.1)
        else:
            self.plot_widget.setXRange(np.log10(min_f), np.log10(max_f), padding=0.1)

    def mouseMoved(self, evt):
        import numpy as np
        if not hasattr(self, 'vLine'): return
        
        pos = evt[0] if isinstance(evt, tuple) else evt
        # Only show crosshair on Freq Response tab
        if self.plot_widget.plotItem.vb.sceneBoundingRect().contains(pos) and self.graph_tabs.currentIndex() == 0:
            mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            
            if self.vLine not in self.plot_widget.plotItem.items:
                self.plot_widget.addItem(self.vLine, ignoreBounds=True)
                self.plot_widget.addItem(self.hLine, ignoreBounds=True)
                self.plot_widget.addItem(self.crosshair_label, ignoreBounds=True)
                
            x_log = mousePoint.x()
            
            closest_dist = float('inf')
            closest_x_log = None
            closest_y = None
            
            for item in self.plot_widget.plotItem.items:
                if isinstance(item, pg.PlotDataItem) and item.name() not in ["EQ Curve (0dB = 60dB)", 'Simulated EQ']:
                    try:
                        x_data, y_data = item.getData()
                    except Exception:
                        continue
                    if x_data is not None and len(x_data) > 0:
                        # x_data is already in log10 space because setLogMode(x=True)
                        idx = (np.abs(x_data - x_log)).argmin()
                        curve_x_log = x_data[idx]
                        curve_mag = y_data[idx]
                        
                        dist = abs(curve_x_log - x_log)
                        if dist < closest_dist:
                            closest_dist = dist
                            closest_x_log = curve_x_log
                            closest_y = curve_mag
                            
            if closest_x_log is not None:
                self.vLine.setPos(closest_x_log)
                self.hLine.setPos(closest_y)
                
                closest_freq = 10**closest_x_log
                freq_str = f"{closest_freq:.0f} Hz" if closest_freq < 1000 else f"{closest_freq/1000:.2f} kHz"
                self.crosshair_label.setText(f"{freq_str} | {closest_y:+.1f} dB")
                self.crosshair_label.setPos(closest_x_log, closest_y)
                
                self.vLine.show()
                self.hLine.show()
                self.crosshair_label.show()
            else:
                self.vLine.hide()
                self.hLine.hide()
                self.crosshair_label.hide()
        else:
            self.vLine.hide()
            self.hLine.hide()
            self.crosshair_label.hide()
        
    def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None, ir_l=None, ir_r=None, sweep_count="1x", smoothing_pts=240, noise_freqs=None, noise_floor_db=None, is_stress=False):
        self._last_data = (freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r, sweep_count, smoothing_pts)
        self._noise_freqs = noise_freqs
        self._noise_floor_db = noise_floor_db
        self._is_stress = is_stress
        
        # Auto-switch to the channel that actually has data
        if mag_l is None and mag_r is not None:
            self.btn_chan_r.setChecked(True)
        elif mag_r is None and mag_l is not None:
            self.btn_chan_l.setChecked(True)
            
        self.refresh_view()
        
    def render_diagnostics(self):
        import numpy as np
        # Prevent any auto-range drift by explicitly re-asserting bounds
        tab_idx = self.graph_tabs.currentIndex()
        if tab_idx == 2:
            if hasattr(self, '_csd_max_peak'):
                p = self._csd_max_peak
                self.csd_widget.setXRange(np.log10(200), np.log10(20000), padding=0)
                self.csd_widget.setYRange(p - 45, p + 5, padding=0)
            else:
                self.csd_widget.setXRange(np.log10(200), np.log10(20000), padding=0)
                self.csd_widget.setYRange(-60, 20, padding=0)
        """Render compact diagnostics report cards, filtered by active graph tab."""
        if not hasattr(self, 'report_layout'):
            return
        while self.report_layout.count():
            item = self.report_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            db = getattr(self, 'db', None)
            if db is None and hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'db'):
                db = self.main_window.db

            iem_id = getattr(self, 'current_iem_id', None)
            if iem_id is None and hasattr(self, 'main_window') and self.main_window:
                if hasattr(self.main_window, 'current_iem_id'):
                    iem_id = self.main_window.current_iem_id
            if iem_id is None:
                iem_id = 1

            tip_id = None
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'combo_tip') and self.main_window.combo_tip:
                combo_data = self.main_window.combo_tip.currentData()
                if combo_data is not None:
                    tip_id = combo_data
            if tip_id is None:
                tip_id = getattr(self, 'current_tip_id', 1)

            self.tip_analysis_card.db = db
            self.tip_analysis_card.update_data(
                iem_id=iem_id,
                tip_id=tip_id,
                freqs=getattr(self, 'current_freqs', None),
                mag_l=getattr(self, 'current_mag_l', None),
                mag_r=getattr(self, 'current_mag_r', None)
            )

        is_light = theme.is_light()
        status_style = {
            'OK':   ('#dcfce7' if is_light else '#0d3320', '#16a34a' if is_light else '#22c55e', '✓'),
            'WARN': ('#fef3c7' if is_light else '#422006', '#d97706' if is_light else '#f59e0b', '⚠'),
            'FAIL': ('#fee2e2' if is_light else '#450a0a', '#dc2626' if is_light else '#ef4444', '✗'),
        }

        left_items = []
        right_items = []
        gen_items = []
        
        report_items = getattr(self, '_last_report', None) or []
        active_cat = None
        tab_idx = self.graph_tabs.currentIndex()
        if tab_idx == 0:
            active_cat = 'FR'
        elif tab_idx == 1:
            active_cat = 'THD'
        elif tab_idx == 2:
            active_cat = 'CSD'
            
        show_l = self.btn_chan_l.isChecked()
        show_r = self.btn_chan_r.isChecked()
        
        for item in report_items:
            cat = item.get('category', 'FR')
            if active_cat is not None and cat not in (active_cat, 'ENV'):
                continue
                
            title = item.get('title', '')
            if title.startswith('Left '):
                if show_l:
                    left_items.append(item)
            elif title.startswith('Right '):
                if show_r:
                    right_items.append(item)
            else:
                gen_items.append(item)
                
        def create_header(text, color="#06b6d4"):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color}; font-weight: 900; font-size: 10px; letter-spacing: 2px; padding-top: 8px; padding-bottom: 2px;")
            return lbl

        def render_group(items, header_text, header_color):
            if not items: return
            self.report_layout.addWidget(create_header(header_text, header_color))
            for item in items:
                status = item.get('status', 'OK')
                bg, accent, icon = status_style.get(status, status_style['OK'])
                band = item.get('band')
                cat = item.get('category', 'FR')

                card = QFrame()
                card.setCursor(Qt.PointingHandCursor if band else Qt.ArrowCursor)
                card.setStyleSheet(f"QFrame {{ background: {bg}; border-left: 3px solid {accent}; border-radius: 3px; padding: 3px 6px; margin: 1px 0; }}")
                cl = QVBoxLayout(card)
                cl.setContentsMargins(4, 2, 4, 2)
                cl.setSpacing(0)

                hdr = AutoWrapLabel(f"<span style='color:{accent};font-weight:bold;'>{icon}</span>  <b>{item.get('title','')}</b>  <span style='color:{'#52525b' if is_light else '#666'};font-size:9px;'>[{cat}]</span>")
                hdr.setStyleSheet(f"color: {accent}; font-size: 11px; background: transparent; border: none;")
                cl.addWidget(hdr)

                desc = AutoWrapLabel(item.get('desc', ''))
                desc.setStyleSheet(f"color: {'#3f3f47' if is_light else '#999'}; font-size: 10px; background: transparent; border: none; padding-left: 16px;")
                cl.addWidget(desc)

                if band:
                    def make_zoom(b=band, c=cat):
                        def zoom_handler(event):
                            f_min, f_max = b
                            if c == 'THD':
                                self.graph_tabs.setCurrentIndex(1)
                                self.thd_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                            elif c == 'CSD':
                                self.graph_tabs.setCurrentIndex(2)
                                self.csd_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                            else:
                                self.graph_tabs.setCurrentIndex(0)
                                self.plot_widget.setXRange(np.log10(f_min), np.log10(f_max), padding=0.1)
                        return zoom_handler
                    card.mousePressEvent = make_zoom(band, cat)

                self.report_layout.addWidget(card)
                
        render_group(left_items, "LEFT EAR", "#3b82f6")
        render_group(right_items, "RIGHT EAR", "#ef4444")
        render_group(gen_items, "STEREO / GENERAL", "#10b981")

        if hasattr(self, '_noise_freqs') and self._noise_freqs is not None and getattr(self, '_noise_floor_db', None) is not None:
            nf = self._noise_freqs
            ndb = self._noise_floor_db
            mask = (nf >= 500) & (nf <= 2000)
            if np.any(mask):
                noise_avg = np.mean(ndb[mask])
                if noise_avg < -45:
                    n_status = 'OK'
                    n_title = "Room Noise: Quiet"
                elif noise_avg < -35:
                    n_status = 'WARN'
                    n_title = "Background noise detected"
                else:
                    n_status = 'FAIL'
                    n_title = "Too noisy for accurate THD"
                
                render_group([{
                    'status': n_status,
                    'title': n_title,
                    'desc': f"Avg Floor: {noise_avg:.1f} dBFS",
                    'category': 'ENV'
                }], "ENVIRONMENT", "#a855f7")

        self.report_layout.addStretch()

    def update_prokit_visibility(self):
        """Re-evaluates ProKit card visibility upon license state transitions."""
        is_unlocked = config.is_prokit_unlocked()
        if hasattr(self, 'tips_scroll'):
            idx = self.tools_tabs.indexOf(self.tips_scroll)
            if idx != -1:
                self.tools_tabs.setTabVisible(idx, is_unlocked)
        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            self.tip_analysis_card.setVisible(is_unlocked)
        self.render_diagnostics()

    def set_active_iem(self, iem_id):
        self.current_iem_id = iem_id
        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            self.tip_analysis_card.set_active_iem(iem_id)

    def set_active_tip(self, tip_id):
        self.current_tip_id = tip_id
        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            self.tip_analysis_card.set_active_tip(tip_id)

    def refresh_view(self):
        print('[DEBUG] refresh_view called!')
        if not hasattr(self, '_last_data'): return
        sweep_count = "1x"
        smoothing_pts = 240
        try:
            freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r, sweep_count, smoothing_pts = self._last_data
        except ValueError:
            try:
                freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r, sweep_count = self._last_data
            except ValueError:
                try:
                    freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r = self._last_data
                except ValueError:
                    freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self._last_data
                    ir_l = None
                    ir_r = None
        self.current_smoothing_pts = smoothing_pts
        
        if freqs is None:
            self.plot_widget.clear()
            self.thd_widget.clear()
            self.csd_widget.clear()
            self._last_report = []  # Clear stale diagnostics so tab-switch doesn't re-render them
            for i in reversed(range(self.report_layout.count())): 
                w = self.report_layout.itemAt(i).widget()
                if w: w.deleteLater()
            return
            
        # Filter based on toggle independently!
        show_l = self.btn_chan_l.isChecked()
        show_r = self.btn_chan_r.isChecked()
        mag_l = orig_mag_l if show_l else None
        mag_r = orig_mag_r if show_r else None
        ir_l_f = ir_l if show_l else None
        ir_r_f = ir_r if show_r else None
        

                
        # Determine best reference
        best_ref_l = None
        best_ref_r = None
        
        if tgt_freqs is not None and tgt_mags is not None and freqs is not None:
            interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
            idx_1k = (np.abs(freqs - 1000)).argmin()
            meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
            if meas_val < 30 or meas_val > 140:
                meas_val = 80  # Prevent aligning target to silence or garbage
            tgt_val = interp_tgt[idx_1k]
            interp_tgt += (meas_val - tgt_val)
            best_ref_l = interp_tgt
            best_ref_r = interp_tgt
        elif ref_mag_l is not None or ref_mag_r is not None:
            best_ref_l = ref_mag_l
            best_ref_r = ref_mag_r
            
        ref_type = 'target' if (tgt_freqs is not None and tgt_mags is not None) else 'history'
        
        if mag_l is None and mag_r is None:
            report = [{'title': 'No Live Measurement', 'status': 'OK', 'desc': 'Run a measurement sweep to generate diagnostics.', 'band': None, 'category': 'FR'}]
        elif sweep_count == "1x":
            report = [{'title': 'Need 3x+ Sweeps for Diagnostics', 'status': 'WARN', 'desc': 'Diagnostics require at least 3 sweeps to reduce noise and false positives.', 'band': None, 'category': 'FR'}]
        else:
            report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data, csd_data, ref_type)
        
        # Save for virtual EQ
        self.current_freqs = freqs
        self.current_mag_l = mag_l
        self.current_mag_r = mag_r
        
        # --- Update Diagnostics Plot ---
        self.plot_widget.clear()
        
        import pyqtgraph as pg
        from PySide6.QtCore import Qt
        
        # Re-create EQ TF Line (which was wiped by clear)
        self.eq_tf_line = self.plot_widget.plot(pen=pg.mkPen('#06b6d4', width=2, style=Qt.DashLine), name="EQ Curve (0dB = 60dB)")
        self.eq_tf_line.setZValue(10)
        self.eq_tf_line.hide()
        
        # Re-apply any current EQ
        if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
            self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())
        
        # Create virtual EQ line
        self.virtual_eq_line = self.plot_widget.plot(pen=pg.mkPen('#00FFFF', width=3, style=Qt.DotLine), name='Simulated EQ')
        self.virtual_eq_line.hide()
        if self.plot_widget.plotItem.legend:
            self.plot_widget.plotItem.legend.clear()
        
        if freqs is not None:
            from audio_engine import AudioEngine
            if mag_l is not None:
                f_l, m_l, _ = AudioEngine.smooth_spectrum(freqs, mag_l, points=getattr(self, "current_smoothing_pts", 240))
                self.plot_widget.plot(f_l, m_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left')
            if mag_r is not None:
                f_r, m_r, _ = AudioEngine.smooth_spectrum(freqs, mag_r, points=getattr(self, "current_smoothing_pts", 240))
                self.plot_widget.plot(f_r, m_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right')
                
            # Plot Target (CSV)
            if tgt_freqs is not None and tgt_mags is not None:
                interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                idx_1k = (np.abs(freqs - 1000)).argmin()
                meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                tgt_val = interp_tgt[idx_1k]
                interp_tgt += (meas_val - tgt_val)
                f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=getattr(self, "current_smoothing_pts", 240))
                self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')
                
            # Plot History (DB)
            hist_pen = pg.mkPen((255, 165, 0, 150), width=2, style=Qt.DashLine)
            if ref_mag_l is not None and show_l:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=getattr(self, "current_smoothing_pts", 240))
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            if ref_mag_r is not None and show_r:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=getattr(self, "current_smoothing_pts", 240))
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')
                
        self._last_report = report
        self.render_diagnostics()
            
        # --- Update THD Plot ---
        self.thd_widget.clear()
        if self.thd_widget.plotItem.legend:
            self.thd_widget.plotItem.legend.clear()
        if thd_data is not None:
            hohd_l, hohd_r = None, None
            if len(thd_data) == 5:
                thd_freqs, orig_thd_l, orig_thd_r, hohd_l, hohd_r = thd_data
            else:
                thd_freqs, orig_thd_l, orig_thd_r = thd_data
            
            show_l = self.btn_chan_l.isChecked()
            show_r = self.btn_chan_r.isChecked()
            thd_l = orig_thd_l if show_l else None
            thd_r = orig_thd_r if show_r else None
            
            if thd_l is not None:
                self.thd_widget.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_widget.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')
                
            if getattr(self, '_is_stress', False):
                self.hohd_line.show()
                active_hohd = hohd_r if (show_r and hohd_r is not None) else (hohd_l if show_l else None)
                if active_hohd is not None:
                    self.hohd_line.setData(thd_freqs, active_hohd)
            else:
                self.hohd_line.hide()
                
        # --- Update CSD Plot ---
        self.csd_widget.clear()
        if self.csd_widget.plotItem.legend:
            self.csd_widget.plotItem.legend.clear()
        if csd_data is not None:
            show_l = self.btn_chan_l.isChecked()
            show_r = self.btn_chan_r.isChecked()
            
            active_csd = None
            is_right = False
            
            if show_l and show_r:
                # If both are checked, Waterfall can only show one cleanly. Default to Left.
                if 'L' in csd_data:
                    active_csd = csd_data['L']
                    is_right = False
                elif 'R' in csd_data:
                    active_csd = csd_data['R']
                    is_right = True
            elif show_l and 'L' in csd_data:
                active_csd = csd_data['L']
                is_right = False
            elif show_r and 'R' in csd_data:
                active_csd = csd_data['R']
                is_right = True
            
            if not active_csd:
                # If everything is unchecked or data is missing, draw nothing.
                pass
            print(f"[CSD DEBUG] csd_data keys={list(csd_data.keys())}, show_l={show_l}, show_r={show_r}, active_csd={'YES' if active_csd else 'NONE'}")
            if active_csd:
                csd_freqs, csd_times, orig_csd_slices = active_csd
                
                # 1. Reduziere die Anzahl gezeichneter Slices (jeden 3. nehmen)
                csd_slices = orig_csd_slices[::3]
                num_slices = len(csd_slices)
                
                # 4. Y-Range dynamisch basierend auf dem höchsten Peak
                if num_slices > 0:
                    max_peak = float(np.max(csd_slices[0]))
                    self._csd_max_peak = max_peak
                    self.csd_widget.setYRange(max_peak - 45, max_peak + 5)
                
                try:
                    base_rgb = theme.get_color('curve_right_rgb') if is_right else theme.get_color('curve_left_rgb')
                except Exception:
                    base_rgb = (255, 0, 85) if is_right else (0, 255, 255)
                    
                # 4. Fill-Opacity reduzieren
                # Draw from back (t=0) to front (t>0) to allow proper occlusion
                for i in range(num_slices):
                    slice_mag = csd_slices[i]
                    
                    # Clean 2D Spectral Decay (no artificial isometric frequency distortion)
                    shift_freqs = csd_freqs
                    # Apply a small visual Y-offset so the time slices separate vertically
                    shift_mag = slice_mag - (i * 1.5)
                
                    # 6. Farb-Gradient
                    blend = i / max(1, num_slices - 1)
                    r = int(base_rgb[0] * (1 - blend) + 30 * blend)
                    g = int(base_rgb[1] * (1 - blend) + 30 * blend)
                    b = int(base_rgb[2] * (1 - blend) + 40 * blend)
                    
                    # Beautiful shaded body fill for 3D effect
                    fill_brush = pg.mkBrush(pg.mkColor(r, g, b, 255))
                    
                    # 5. Distinct contour lines (black/dark) so the ridges are clearly visible!
                    pen_color = pg.mkColor(20, 20, 25, 255)
                
                    self.csd_widget.plot(
                        shift_freqs, 
                        shift_mag, 
                        pen=pg.mkPen(pen_color, width=1.5),
                        fillLevel=-100, 
                        brush=fill_brush,
                        name=f"CSD_{'R' if is_right else 'L'}_{i}" if i==0 else None
                    )
        # Trigger EQ update to draw the virtual curve
        if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
            # We call the first band's toggled slot manually to force an update
            self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())

    def init_eq_db(self):
        import sqlite3
        try:
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS eq_presets (id INTEGER PRIMARY KEY, name TEXT UNIQUE, data TEXT)")
            conn.commit()
            conn.close()
        except:
            pass

    def load_eq_presets(self):
        import sqlite3
        from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
        
        # Clear existing cards
        for i in reversed(range(self.preset_cards_layout.count())): 
            w = self.preset_cards_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        try:
            import json, numpy as np
            import pyqtgraph as pg
            from eq_math import DSPEngine
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute("SELECT name, data FROM eq_presets ORDER BY name")
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                name, data_str = row
                bands = json.loads(data_str) if data_str else []
                
                card = QFrame()
                card.setFixedHeight(40)
                card.setStyleSheet("QFrame { background: #222; border: 1px solid #333; border-radius: 6px; }")
                cl = QHBoxLayout(card)
                cl.setContentsMargins(8, 4, 8, 4)
                
                lbl = QLabel(name)
                lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.get_color('text_primary')}; border: none;")
                
                # Mini Graph
                mini_plot = pg.PlotWidget()
                mini_plot.setFixedSize(120, 28)
                mini_plot.hideAxis('bottom')
                mini_plot.hideAxis('left')
                mini_plot.setBackground(theme.get_color('bg_main'))
                mini_plot.setMouseEnabled(x=False, y=False)
                mini_plot.setMenuEnabled(False)
                mini_plot.setLogMode(x=True, y=False)
                mini_plot.setXRange(np.log10(20), np.log10(20000))
                mini_plot.setYRange(-12, 12)
                
                temp_dsp = DSPEngine()
                temp_filters = []
                for b in bands:
                    temp_filters.append({
                        'enabled': b.get('on', True),
                        'freq': b.get('f', 1000),
                        'gain': b.get('g', 0),
                        'q': b.get('q', 1.41),
                        'type': b.get('type', 'peq')
                    })
                temp_dsp.set_filters(temp_filters)
                
                f_mini = np.logspace(np.log10(20), np.log10(20000), 60)
                delta = temp_dsp.get_magnitude_response(f_mini, 48000)
                mini_plot.plot(f_mini, delta, pen=pg.mkPen(theme.get_color('accent'), width=2))
                
                btn_load = QPushButton("Load")
                btn_load.setProperty("class", "accent")
                btn_load.clicked.connect(lambda checked, n=name: self.apply_eq_preset(n))
                
                btn_del = QPushButton("X")
                btn_del.setProperty("class", "danger")
                btn_del.clicked.connect(lambda checked, n=name: self.delete_eq_preset(n))
                
                cl.addWidget(lbl, stretch=1)
                cl.addWidget(mini_plot)
                cl.addWidget(btn_load)
                cl.addWidget(btn_del)
                
                self.preset_cards_layout.addWidget(card)
        except:
            pass

    def save_eq_preset(self):
        from PySide6.QtWidgets import QMessageBox
        import sqlite3, json
        name = self.le_preset_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Name Required", "Please give your EQ preset a name before saving.")
            return
            
        data = []
        for b in self.peq_bands:
            data.append({
                'on': b['on'].isChecked(),
                'f': b['f'].value(),
                'g': b['g'].value(),
                'q': b['q'].value()
            })
        try:
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO eq_presets (name, data) VALUES (?, ?)", (name, json.dumps(data)))
            conn.commit()
            conn.close()
            self.le_preset_name.clear()
            self.load_eq_presets()
        except Exception as e:
            QMessageBox.warning(self, "Couldn't Save Preset", f"We couldn't save the EQ preset. Please try again.\n\nTechnical detail: {str(e)}")


    def delete_eq_preset(self, name):
        from PySide6.QtWidgets import QMessageBox
        import sqlite3
        if QMessageBox.question(self, "Delete EQ Preset", f"Are you sure you want to delete the preset '{name}'? This cannot be undone.") == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(self.db.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM eq_presets WHERE name = ?", (name,))
                conn.commit()
                conn.close()
                self.load_eq_presets()
            except:
                pass

    def apply_eq_preset(self, name):
        import sqlite3, json
        try:
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute("SELECT data FROM eq_presets WHERE name = ?", (name,))
            row = c.fetchone()
            conn.close()
            if row:
                data = json.loads(row[0])
                for i, b in enumerate(self.peq_bands):
                    if i < len(data):
                        b['on'].setChecked(data[i]['on'])
                        b['f'].setValue(data[i]['f'])
                        b['g'].setValue(data[i]['g'])
                        b['q'].setValue(data[i]['q'])
        except:
            pass

    def update_theme(self):
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        self.setStyleSheet(f"#AnalysisRoot {{ background-color: transparent; color: {fg}; }}")
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        active = theme.get_color('bg_hover')
        text_sec = theme.get_color('text_secondary')
        
        
        # Update Channel Buttons
        btn_bg = theme.get_color('bg_main')
        if hasattr(self, 'btn_chan_l'):
            self.btn_chan_l.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {text_sec}; border: 1px solid {border}; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: #0ea5e9; color: white; border-color: #0ea5e9; }}")
        if hasattr(self, 'btn_chan_r'):
            self.btn_chan_r.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {text_sec}; border: 1px solid {border}; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: #ef4444; color: white; border-color: #ef4444; }}")
        
        # Update Tabs
        self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        if hasattr(self, 'tools_tabs'):
            self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 40px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
            
        # Update Graph Backgrounds
        pg_bg = theme.get_color('pg_bg')
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setBackground(pg_bg)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setBackground(pg_bg)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setBackground(pg_bg)
            
        if hasattr(self, 'btn_toggle_tools'):
            btn_bg = theme.get_color('bg_hover')
            btn_border = theme.get_color('border')
            self.btn_toggle_tools.setStyleSheet(f"QPushButton {{ background-color: {btn_bg}; color: {fg}; border: none; border-left: 1px solid {btn_border}; font-size: 10px; }} QPushButton:hover {{ background-color: {border}; color: {fg}; }}")
            
        # Update EQ mini plots and labels
        if hasattr(self, 'preset_cards_layout'):
            for i in range(self.preset_cards_layout.count()):
                item = self.preset_cards_layout.itemAt(i)
                if item and item.widget():
                    card = item.widget()
                    # Reapply styling to the card to trigger the patched setter
                    if hasattr(card, '_original_qss'):
                        card.setStyleSheet(card._original_qss)
                    from PySide6.QtWidgets import QLabel
                    for child in card.findChildren(QLabel):
                        if hasattr(child, '_original_qss'):
                            child.setStyleSheet(child._original_qss)
                    # The mini plots need explicit updating
                    import pyqtgraph as pg
                    for child in card.findChildren(pg.PlotWidget):
                        child.setBackground(theme.get_color('bg_main'))
                        
        if hasattr(self, 'tip_analysis_card') and self.tip_analysis_card:
            self.tip_analysis_card.update_theme()
            
        # Redraw diagnostics cards to refresh their light/dark color palette
        self.render_diagnostics()

    def showEvent(self, event):
        """On first real show: fix splitter sizes so sidebar is open at 250px."""
        super().showEvent(event)
        if not self._initial_shown:
            self._initial_shown = True
            total = self.split_layout.width()
            if total > 0:
                self.split_layout.setSizes([total - 250, 250])

    def toggle_tools_pane(self):
        is_visible = self.tools_tabs.isVisible()
        self.tools_tabs.setVisible(not is_visible)
        total = self.split_layout.width()
        if is_visible:
            self.btn_toggle_tools.setText("◀")
            self.split_layout.setSizes([total, 0])
        else:
            self.btn_toggle_tools.setText("▶")
            self.split_layout.setSizes([total - 250, 250])
