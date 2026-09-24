import os
import sqlite3
import numpy as np
import theme
import config
from PySide6.QtWidgets import (
    QPushButton, QLineEdit, QListWidget, QListWidgetItem, QWidget, QFrame, QTabWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QCheckBox, QAbstractItemView, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

import pyqtgraph as pg

class FreqAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if not values:
            return []
            
        strings = []
        is_zoomed_out = (max(values) - min(values)) >= 0.9
        allowed_labels = {20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000}
        
        for v in values:
            hz = int(round(10**v))
            if is_zoomed_out and hz not in allowed_labels:
                strings.append("")
                continue
                
            if hz >= 1000:
                if hz % 1000 == 0:
                    strings.append(f"{hz//1000}k")
                else:
                    strings.append(f"{hz/1000:g}k")
            else:
                strings.append(f"{hz}")
        return strings


# Fallback for AudioEngine if not available
try:
    from audio_engine import AudioEngine
except ImportError:
    class AudioEngine:
        @staticmethod
        def smooth_spectrum(f, m, points=240):
            # Dummy fallback if audio_engine doesn't exist
            return f, m


class HistoryCardWidget(QWidget):
    SEAL_THRESHOLD_DB = -11.8

    @staticmethod
    def compute_seal_for_channel(freq, mag):
        """
        Computes acoustic seal status and delta from frequency and magnitude vectors.
        val_40: mean in 35-45 Hz band
        val_500: mean in 450-550 Hz band
        delta_db = val_40 - val_500
        Threshold: delta_db >= -11.8 dB -> 'OK', else 'LEAK'.
        Returns (status: str, delta_db: float) or (None, None).
        """
        if freq is None or mag is None:
            return None, None
        try:
            if len(freq) < 10 or len(mag) != len(freq):
                return None, None
            mask_40 = (freq >= 35.0) & (freq <= 45.0)
            mask_500 = (freq >= 450.0) & (freq <= 550.0)
            if not np.any(mask_40) or not np.any(mask_500):
                return None, None
            val_40 = float(np.mean(mag[mask_40]))
            val_500 = float(np.mean(mag[mask_500]))
            delta = val_40 - val_500
            delta_db = float(round(delta, 1))
            status = "OK" if delta_db >= HistoryCardWidget.SEAL_THRESHOLD_DB else "LEAK"
            return status, delta_db
        except Exception:
            return None, None

    def __init__(
        self,
        timestamp,
        iem_name,
        side,
        parent=None,
        tip_id=1,
        tip_name="Unknown",
        tip_color="#6b7280",
        tip_icon="?",
        tip_material="Standard",
        seal_l=None,
        seal_r=None,
        seal_text="",
        freq=None,
        mag_l=None,
        mag_r=None,
        **kwargs
    ):
        super().__init__(parent)
        self.timestamp = timestamp
        self.iem_name = iem_name
        self.side = side
        self.tip_id = int(tip_id) if tip_id is not None else 1
        self.tip_name = tip_name if tip_name else "Unknown"
        self.tip_color = tip_color if tip_color else "#6b7280"
        self.tip_icon = tip_icon if tip_icon else "?"
        self.tip_material = tip_material if tip_material else "Standard"

        # Compute seal metrics if not explicitly passed
        # (LOCKED DESIGN DECISION 2: L and R channels ALWAYS SEPARATE)
        if seal_l is not None:
            self.seal_l_delta = float(round(seal_l, 1))
            self.seal_l_status = "OK" if self.seal_l_delta >= self.SEAL_THRESHOLD_DB else "LEAK"
        elif freq is not None and mag_l is not None:
            self.seal_l_status, self.seal_l_delta = self.compute_seal_for_channel(freq, mag_l)
        else:
            self.seal_l_status, self.seal_l_delta = None, None

        if seal_r is not None:
            self.seal_r_delta = float(round(seal_r, 1))
            self.seal_r_status = "OK" if self.seal_r_delta >= self.SEAL_THRESHOLD_DB else "LEAK"
        elif freq is not None and mag_r is not None:
            self.seal_r_status, self.seal_r_delta = self.compute_seal_for_channel(freq, mag_r)
        else:
            self.seal_r_status, self.seal_r_delta = None, None

        # Determine formatted seal text
        if seal_text:
            self.seal_text = seal_text
        else:
            if self.seal_l_delta is not None and self.seal_r_delta is not None:
                self.seal_text = f"Seal: L {self.seal_l_delta:+.1f}dB | R {self.seal_r_delta:+.1f}dB"
            elif self.seal_l_delta is not None:
                self.seal_text = f"Seal L: {self.seal_l_delta:+.1f}dB"
            elif self.seal_r_delta is not None:
                self.seal_text = f"Seal R: {self.seal_r_delta:+.1f}dB"
            else:
                self.seal_text = ""

        fg = "white"
        text_sec = "#888"

        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(10, 6, 10, 6)
        card_layout.setSpacing(3)

        # Row 1: IEM Name, Channel Badge, Graph Checkbox
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        self.lbl_iem = QLabel(iem_name)
        self.lbl_iem.setObjectName("lbl_iem")
        self.lbl_iem.setMinimumWidth(1)
        self.lbl_iem.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.lbl_iem.setStyleSheet(f"background-color: transparent; font-weight: bold; font-size: 13px; color: {fg};")
        row1.addWidget(self.lbl_iem, stretch=1)

        # Channel Badge
        self.lbl_side = QLabel(side)
        self.lbl_side.setObjectName("lbl_side")
        side_lower = side.lower() if side else ""
        if side_lower == "left":
            self.lbl_side.setStyleSheet(f"background-color: #3b82f6; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        elif side_lower == "right":
            self.lbl_side.setStyleSheet(f"background-color: #ef4444; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_side.setStyleSheet(f"background-color: #10b981; color: {fg}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        row1.addWidget(self.lbl_side)

        # Graph Checkbox
        self.cb_graph = QCheckBox("Graph")
        self.cb_graph.setObjectName("cb_graph")
        self.cb_graph.setStyleSheet(f"QCheckBox {{ background-color: transparent; color: {text_sec}; font-size: 11px; font-weight: bold; }}")
        row1.addWidget(self.cb_graph)
        card_layout.addLayout(row1)

        # Row 2: Date & Seal Text on Left, Tip Badge & L/R Seal Badges on Right
        row2 = QHBoxLayout()
        row2.setSpacing(5)

        date_seal_layout = QVBoxLayout()
        date_seal_layout.setSpacing(1)

        self.lbl_date = QLabel(timestamp)
        self.lbl_date.setObjectName("lbl_date")
        self.lbl_date.setMinimumWidth(1)
        self.lbl_date.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.lbl_date.setStyleSheet(f"background-color: transparent; font-size: 10px; color: {text_sec};")
        date_seal_layout.addWidget(self.lbl_date)

        self.lbl_seal = QLabel(self.seal_text)
        self.lbl_seal.setObjectName("lbl_seal")
        self.lbl_seal.setStyleSheet("background-color: transparent; font-size: 10px; color: #a1a1aa;")
        self.seal_badge = self.lbl_seal
        date_seal_layout.addWidget(self.lbl_seal)
        row2.addLayout(date_seal_layout)

        row2.addStretch(1)

        # Tip Badge
        self.lbl_tip_badge = QLabel()
        self.lbl_tip_badge.setObjectName("lbl_tip_badge")
        self.tip_badge = self.lbl_tip_badge
        self.lbl_badge = self.lbl_tip_badge
        self.lbl_tip = self.lbl_tip_badge
        self._configure_tip_badge()
        row2.addWidget(self.lbl_tip_badge)

        # Left Seal Indicator (L: OK / LEAK)
        self.lbl_seal_l = QLabel()
        self.lbl_seal_l.setObjectName("lbl_seal_l")
        if self.seal_l_status is not None:
            self.lbl_seal_l.setText(f"L: {self.seal_l_status}")
            delta_str = f"{self.seal_l_delta:+.1f} dB" if self.seal_l_delta is not None else ""
            self.lbl_seal_l.setToolTip(f"Left Seal Delta (40Hz vs 500Hz): {delta_str} ({self.seal_l_status})")
            if self.seal_l_status == "OK":
                self.lbl_seal_l.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_l.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        row2.addWidget(self.lbl_seal_l)

        # Right Seal Indicator (R: OK / LEAK)
        self.lbl_seal_r = QLabel()
        self.lbl_seal_r.setObjectName("lbl_seal_r")
        if self.seal_r_status is not None:
            self.lbl_seal_r.setText(f"R: {self.seal_r_status}")
            delta_str = f"{self.seal_r_delta:+.1f} dB" if self.seal_r_delta is not None else ""
            self.lbl_seal_r.setToolTip(f"Right Seal Delta (40Hz vs 500Hz): {delta_str} ({self.seal_r_status})")
            if self.seal_r_status == "OK":
                self.lbl_seal_r.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_r.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        row2.addWidget(self.lbl_seal_r)

        card_layout.addLayout(row2)

        # ProKit Gating
        try:
            is_unlocked = config.is_prokit_unlocked()
        except Exception:
            is_unlocked = False

        self.lbl_tip_badge.setVisible(is_unlocked)
        self.lbl_seal.setVisible(is_unlocked and bool(self.seal_text))
        self.lbl_seal_l.setVisible(is_unlocked and self.seal_l_status is not None)
        self.lbl_seal_r.setVisible(is_unlocked and self.seal_r_status is not None)

    def _configure_tip_badge(self):
        """Format badge text, tooltip, and stylesheet based on tip identity."""
        if self.tip_id == 1 or self.tip_name == "Unknown":
            self.lbl_tip_badge.setText("?")
            self.lbl_tip_badge.setStyleSheet(
                "background-color: #6b7280; color: #a1a1aa; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"
            )
            self.lbl_tip_badge.setToolTip("Ear Tip: Unknown")
        else:
            icon = self.tip_icon if self.tip_icon else "?"
            self.lbl_tip_badge.setText(f"{icon} {self.tip_name}")
            self.lbl_tip_badge.setStyleSheet(
                f"background-color: {self.tip_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;"
            )
            self.lbl_tip_badge.setToolTip(f"Ear Tip: {self.tip_name} ({self.tip_material})")

    def set_tip(self, tip_id, tip_name="Unknown", tip_color="#6b7280", tip_icon="?", tip_material="Standard"):
        """Dynamically update tip information."""
        self.tip_id = int(tip_id) if tip_id is not None else 1
        self.tip_name = tip_name if tip_name else "Unknown"
        self.tip_color = tip_color if tip_color else "#6b7280"
        self.tip_icon = tip_icon if tip_icon else "?"
        self.tip_material = tip_material if tip_material else "Standard"
        self._configure_tip_badge()

    def set_seal(self, seal_l, seal_r):
        """Dynamically update acoustic seal status."""
        if seal_l is not None:
            self.seal_l_delta = float(round(seal_l, 1))
            self.seal_l_status = "OK" if self.seal_l_delta >= self.SEAL_THRESHOLD_DB else "LEAK"
        else:
            self.seal_l_delta, self.seal_l_status = None, None

        if seal_r is not None:
            self.seal_r_delta = float(round(seal_r, 1))
            self.seal_r_status = "OK" if self.seal_r_delta >= self.SEAL_THRESHOLD_DB else "LEAK"
        else:
            self.seal_r_delta, self.seal_r_status = None, None

        if self.seal_l_delta is not None and self.seal_r_delta is not None:
            self.seal_text = f"Seal: L {self.seal_l_delta:+.1f}dB | R {self.seal_r_delta:+.1f}dB"
        elif self.seal_l_delta is not None:
            self.seal_text = f"Seal L: {self.seal_l_delta:+.1f}dB"
        elif self.seal_r_delta is not None:
            self.seal_text = f"Seal R: {self.seal_r_delta:+.1f}dB"
        else:
            self.seal_text = ""

        self.lbl_seal.setText(self.seal_text)
        if self.seal_l_status is not None:
            self.lbl_seal_l.setText(f"L: {self.seal_l_status}")
            delta_str = f"{self.seal_l_delta:+.1f} dB" if self.seal_l_delta is not None else ""
            self.lbl_seal_l.setToolTip(f"Left Seal Delta (40Hz vs 500Hz): {delta_str} ({self.seal_l_status})")
            if self.seal_l_status == "OK":
                self.lbl_seal_l.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_l.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        if self.seal_r_status is not None:
            self.lbl_seal_r.setText(f"R: {self.seal_r_status}")
            delta_str = f"{self.seal_r_delta:+.1f} dB" if self.seal_r_delta is not None else ""
            self.lbl_seal_r.setToolTip(f"Right Seal Delta (40Hz vs 500Hz): {delta_str} ({self.seal_r_status})")
            if self.seal_r_status == "OK":
                self.lbl_seal_r.setStyleSheet("background-color: #065f46; color: #34d399; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #10b981;")
            else:
                self.lbl_seal_r.setStyleSheet("background-color: #7f1d1d; color: #f87171; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid #ef4444;")
        self.update_prokit_visibility()

    def update_prokit_visibility(self, unlocked=None):
        """Update visibility of tip badge and seal indicators according to ProKit gate."""
        if unlocked is None:
            try:
                import config
                unlocked = config.is_prokit_unlocked()
            except Exception:
                unlocked = False

        if hasattr(self, "lbl_tip_badge") and self.lbl_tip_badge:
            self.lbl_tip_badge.setVisible(unlocked)
        if hasattr(self, "lbl_seal") and self.lbl_seal:
            self.lbl_seal.setVisible(unlocked and bool(self.seal_text))
        if hasattr(self, "lbl_seal_l") and self.lbl_seal_l:
            self.lbl_seal_l.setVisible(unlocked and self.seal_l_status is not None)
        if hasattr(self, "lbl_seal_r") and self.lbl_seal_r:
            self.lbl_seal_r.setVisible(unlocked and self.seal_r_status is not None)

class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryRoot")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        bg = theme.get_color("bg_sec")
        active = theme.get_color("bg_hover")
        border = theme.get_color("border")
        fg = "white"
        text_sec = "#888"
        bg_hover = "#2a2a2a"
        accent = "#00FFFF"
        bg_input = "#1f1f23"
        
        split_layout = QHBoxLayout()
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(0)

        # --- LEFT PANE ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(4, 4, 4, 0)
        left_layout.setSpacing(6)
        
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setElideMode(Qt.ElideNone)
        self.graph_tabs.setUsesScrollButtons(True)
        self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(4, 4, 4, 4)
        fr_layout.setSpacing(4)
        
        # Corner Widget (Top Right)
        from PySide6.QtWidgets import QComboBox
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(15)
        corner_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        
        chan_vis_widget = QWidget()
        chan_vis_layout = QHBoxLayout(chan_vis_widget)
        chan_vis_layout.setContentsMargins(0,0,0,0)
        chan_vis_layout.setSpacing(0)
        
        self.btn_chan_l = QPushButton("Left")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet(f"QPushButton {{ background-color: {bg_hover}; color: {text_sec}; border: 1px solid #333; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")
        
        self.btn_chan_r = QPushButton("Right")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet(f"QPushButton {{ background-color: {bg_hover}; color: {text_sec}; border: 1px solid #333; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")
        
        chan_vis_layout.addWidget(self.btn_chan_l)
        chan_vis_layout.addWidget(self.btn_chan_r)
        
        self.btn_chan_l.clicked.connect(self.on_item_checked)
        self.btn_chan_r.clicked.connect(self.on_item_checked)
        corner_layout.addWidget(chan_vis_widget)
        
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        view_layout.setContentsMargins(0,0,0,0)
        view_layout.setSpacing(8)
        
        self.cb_smooth = QComboBox()
        self.cb_smooth.addItems(["1/24 Oct", "1/48 Oct", "1/12 Oct", "1/6 Oct", "Raw"])
        self.cb_smooth.setStyleSheet("QComboBox { background-color: #222; color: {fg}; border: 1px solid #444; padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; min-height: 20px; }")
        self.cb_smooth.currentIndexChanged.connect(self.on_item_checked)
        view_layout.addWidget(self.cb_smooth)
        
        self.btn_reset_zoom = QPushButton("AUTOZOOM")
        self.btn_reset_zoom.setToolTip("Autozoom graph to fit curves")
        self.btn_reset_zoom.setMinimumWidth(90)
        self.btn_reset_zoom.setStyleSheet("QPushButton { background-color: #222; color: {fg}; border: 1px solid #444; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: {active}; }")
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)
        view_layout.addWidget(self.btn_reset_zoom)
        
        corner_layout.addWidget(view_widget)
        self.graph_tabs.setCornerWidget(corner_widget, Qt.TopRightCorner)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setBackground(theme.get_color("pg_bg"))
        self.plot_widget.setLabel('left', 'Magnitude', units='dB', color=theme.get_color("pg_fg"))
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz', color=theme.get_color("pg_fg"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.addLegend()
        self.reset_zoom()
        
        fr_layout.addWidget(self.plot_widget)
        self.graph_tabs.addTab(self.fr_container, "Measurement History")
        left_layout.addWidget(self.graph_tabs, stretch=1)
        
        # Edit Area (Under Graph)
        self.edit_container = QFrame()
        self.edit_container.setFixedHeight(113)
        self.edit_container.setObjectName("EditContainer")
        bg_panel = "#222"
        self.edit_container.setStyleSheet(f"#EditContainer {{ background-color: {bg}; border: 1px solid {border}; border-radius: 4px; }}")
        
        edit_layout = QHBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(0)
        
                # Left Edit Pane (Matches graph width)
        left_edit = QFrame()
        left_edit_layout = QVBoxLayout(left_edit)
        left_edit_layout.setContentsMargins(15, 8, 15, 8)
        left_edit_layout.setSpacing(6)
        
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(10)
        
        self.edit_meas_name = QLineEdit()
        self.edit_meas_name.setPlaceholderText("Measurement Name (Leave blank for default IEM name)")
        self.edit_meas_name.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        
        self.edit_meas_date = QLineEdit()
        self.edit_meas_date.setPlaceholderText("Date/Time (YYYY-MM-DD HH:MM:SS)")
        self.edit_meas_date.setStyleSheet(f"background-color: {bg_hover}; color: {text_sec}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        self.edit_meas_date.setFixedWidth(160)
        
        meta_layout.addWidget(self.edit_meas_name, stretch=1)
        meta_layout.addWidget(self.edit_meas_date)
        
        from PySide6.QtWidgets import QPlainTextEdit
        self.txt_notes = QPlainTextEdit()
        self.txt_notes.setPlaceholderText("Measurement Notes...")
        self.txt_notes.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px 10px; border-radius: 6px; font-size: 12px;")
        
        self.notes_timer = QTimer(self)
        self.notes_timer.setSingleShot(True)
        self.notes_timer.setInterval(1000)
        self.notes_timer.timeout.connect(self.save_notes)
        
        self.txt_notes.textChanged.connect(self.notes_timer.start)
        self.edit_meas_name.textChanged.connect(self.notes_timer.start)
        self.edit_meas_date.textChanged.connect(self.notes_timer.start)
        
        left_edit_layout.addLayout(meta_layout)
        left_edit_layout.addWidget(self.txt_notes, stretch=1)
        
        # Right Edit Pane (Matches tools_tabs width)
        right_edit = QFrame()
        right_edit.setMaximumWidth(345)
        right_edit.setMinimumWidth(220)
        right_edit_layout = QHBoxLayout(right_edit)
        right_edit_layout.setContentsMargins(15, 12, 15, 12)
        right_edit_layout.setSpacing(6)
        right_edit_layout.setAlignment(Qt.AlignCenter)
        
        btn_style_base = "QPushButton { background-color: #222; color: #888; font-weight: bold; padding: 6px 6px; border-radius: 4px; border: 1px solid #444; font-size: 11px;} QPushButton:disabled { color: #555; border-color: #333; }"
        
        self.btn_import_history = QPushButton("+ Import")
        self.btn_import_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #f59e0b; border-color: #f59e0b; background-color: #111; }")
        self.btn_import_history.clicked.connect(self.show_import_menu)

        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #0ea5e9; border-color: #0ea5e9; background-color: #111; }")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save Target")
        self.btn_save_target.setStyleSheet(btn_style_base + " QPushButton:hover { color: #10b981; border-color: #10b981; background-color: #111; }")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("🗑 Delete")
        self.btn_delete_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #ef4444; border-color: #ef4444; background-color: #111; }")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        
        right_edit_layout.addStretch()
        right_edit_layout.addWidget(self.btn_import_history)
        right_edit_layout.addWidget(self.btn_export_history)
        right_edit_layout.addWidget(self.btn_save_target)
        right_edit_layout.addWidget(self.btn_delete_history)
        right_edit_layout.addStretch()
        
        edit_layout.addWidget(left_edit, stretch=1)
        edit_layout.addWidget(right_edit)
        
        split_layout.addWidget(left_pane, stretch=1)
        
        # --- RIGHT PANE ---
        self.right_pane_wrapper = QWidget()
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
        
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setMaximumWidth(345)
        self.tools_tabs.setMinimumWidth(220)
        self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        self.right_pane_layout.addWidget(self.tools_tabs)
        
        target_tab = QWidget()
        target_layout = QVBoxLayout(target_tab)
        target_layout.setContentsMargins(8, 8, 8, 8)
        target_layout.setSpacing(10)
        
        # Search & Add Bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(6)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search history...")
        self.search_bar.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
        self.search_bar.textChanged.connect(self.filter_history)
        
        search_layout.addWidget(self.search_bar, stretch=1)
        target_layout.addLayout(search_layout)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"QListWidget {{ background-color: transparent; border: none; outline: none; }} QListWidget::item {{ padding: 2px; }} QListWidget::item:selected {{ background-color: {bg_hover}; border-radius: 6px; border: 1px solid {active}; }}")
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        target_layout.addWidget(self.list_widget, stretch=1)
        self.tools_tabs.addTab(target_tab, "ARCHIVE")
        split_layout.addWidget(self.right_pane_wrapper)
        self.layout.addLayout(split_layout)
        
        bottom_container = QVBoxLayout()
        bottom_container.setContentsMargins(0, 0, 0, 0)
        bottom_container.addWidget(self.edit_container)
        self.layout.addLayout(bottom_container)
        self.set_edit_controls_enabled(False)
        
        self.measurements = []
        self.colors = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', 
            '#8b5cf6', '#ec4899', '#06b6d4'
        ]
        self.db_path = "inearsnitch.db"
        self.cached_photo_path = None
        self.cached_pixmap = None


    def update_theme(self):
        bg = theme.get_color("bg_panel")
        active = theme.get_color("bg_hover")
        border = theme.get_color("border")
        fg = theme.get_color("text_primary")
        text_sec = theme.get_color("text_secondary")
        bg_hover = theme.get_color("bg_hover")
        bg_main = theme.get_color("bg_main")
        
        self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        self.btn_chan_l.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")
        self.btn_chan_r.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; }} QPushButton:checked {{ background-color: {active}; color: {fg}; border-color: {border}; }}")
        self.cb_smooth.setStyleSheet(f"QComboBox {{ background-color: {bg_main}; color: {fg}; border: 1px solid {border}; padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; min-height: 20px; }}")
        self.btn_reset_zoom.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {fg}; border: 1px solid {border}; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; }} QPushButton:hover {{ background-color: {active}; }}")
        
        self.edit_container.setStyleSheet(f"#EditContainer {{ background-color: {bg}; border: 1px solid {border}; border-radius: 4px; }}")
        self.edit_meas_name.setStyleSheet(f"background-color: {bg_main}; color: {fg}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        self.edit_meas_date.setStyleSheet(f"background-color: {bg_main}; color: {text_sec}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        self.txt_notes.setStyleSheet(f"background-color: {bg_main}; color: {fg}; border: 1px solid {border}; padding: 6px 10px; border-radius: 6px; font-size: 12px;")
        
        btn_style_base = f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; font-weight: bold; padding: 6px 6px; border-radius: 4px; border: 1px solid {border}; font-size: 11px;}} QPushButton:disabled {{ color: #555; border-color: {border}; }}"
        self.btn_import_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #f59e0b; border-color: #f59e0b; background-color: " + bg_hover + "; }")
        self.btn_export_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #3b82f6; border-color: #3b82f6; background-color: " + bg_hover + "; }")
        self.btn_save_target.setStyleSheet(btn_style_base + " QPushButton:hover { color: #10b981; border-color: #10b981; background-color: " + bg_hover + "; }")
        self.btn_delete_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #ef4444; border-color: #ef4444; background-color: " + bg_hover + "; }")
        
        self.btn_toggle_tools.setStyleSheet(f"QPushButton {{ background-color: {bg_main}; color: {text_sec}; border: none; border-left: 1px solid {border}; font-size: 10px; }} QPushButton:hover {{ background-color: {active}; color: {fg}; }}")
        self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        
        self.search_bar.setStyleSheet(f"background-color: {bg_main}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
        self.list_widget.setStyleSheet(f"QListWidget {{ background-color: {bg}; border: none; outline: none; }} QListWidget::item {{ padding: 2px; }} QListWidget::item:selected {{ background-color: {bg_hover}; border-radius: 6px; border: 1px solid {theme.get_color('accent')}; }}")
        self.list_widget.parentWidget().setStyleSheet(f"background-color: {bg};")

        self.plot.setBackground(theme.get_color("pg_bg"))
        self.plot.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        for ax in [self.plot.getAxis('left'), self.plot.getAxis('bottom')]:
            ax.setPen(theme.get_color("pg_fg"))
            ax.setTextPen(theme.get_color("pg_fg"))

    def show_import_menu(self):

        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QCursor
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #222; color: white; border: 1px solid #444; } QMenu::item { padding: 6px 24px; } QMenu::item:selected { background-color: #333; }")
        
        act_stereo = menu.addAction("Import as Stereo (L+R)")
        act_left = menu.addAction("Import as Left Channel")
        act_right = menu.addAction("Import as Right Channel")
        
        action = menu.exec(QCursor.pos())
        if action == act_stereo: self.do_import_csv("stereo")
        elif action == act_left: self.do_import_csv("left")
        elif action == act_right: self.do_import_csv("right")

    def do_import_csv(self, mode="stereo"):
        import __main__
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import numpy as np
        import sqlite3
        import os
        
        if not hasattr(__main__, 'window') or not getattr(__main__.window, 'current_iem_id', None):
            QMessageBox.warning(self, "Import CSV", "Please select a specific IEM from the Musician Profile in the sidebar first, so we know where to save the imported data.")
            return
            
        iem_id = __main__.window.current_iem_id
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv *.txt)")
        if not path: return
        
        try:
            # First try parsing as comma separated, then fallback to tab/space if needed
            data = np.genfromtxt(path, delimiter=',', skip_header=0, invalid_raise=False)
            if np.isnan(data).all():
                # Try space/tab separated (common in REW/Squiglink exports)
                data = np.genfromtxt(path, skip_header=0, invalid_raise=False)
                
            # If the first row is strings (header), skip_header=0 makes them nan.
            # We filter out rows that are entirely nan
            data = data[~np.isnan(data).all(axis=1)]
            
            if data.ndim != 2 or data.shape[1] < 2:
                QMessageBox.critical(self, "Import Error", "CSV format must be at least two columns (Freq, Mag).")
                return
                
            freqs = data[:, 0]
            
            if mode == "left":
                mag_l = data[:, 1]
                mag_r = None
            elif mode == "right":
                mag_l = None
                mag_r = data[:, 1]
            else:
                # Stereo
                mag_l = data[:, 1]
                mag_r = data[:, 2] if data.shape[1] > 2 else data[:, 1] # fallback to mono if no 3rd column
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            filename = os.path.basename(path)
            notes = f"Imported: {filename}"
            
            ml = mag_l.tobytes() if mag_l is not None else b''
            mr = mag_r.tobytes() if mag_r is not None else b''
            pl = b''
            pr = b''
            fb = freqs.tobytes()
            
            c.execute("""
                INSERT INTO Measurements 
                (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (iem_id, "Auto", fb, ml, mr, pl, pr, notes, ""))
            c.execute("SELECT musician_id FROM IEM_Models WHERE id = ?", (iem_id,))
            res = c.fetchone()
            m_id = res[0] if res else None
            conn.commit()
            conn.close()
            
            if m_id is not None:
                self.load_history(m_id)
            
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Import Error", f"Failed to import file: {e}")

    def reset_zoom(self):
        import numpy as np
        self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
        self.plot_widget.setYRange(40, 110, padding=0.0)

    def load_history(self, m_id):
        self.last_m_id = m_id
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self.measurements = []
        self.plot_widget.clear()
        self.set_edit_controls_enabled(False)
        self.txt_notes.clear()
        
        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} not found.")
            return

        try:
            import sqlite3
            import numpy as np
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure meas_name exists
            cursor.execute("PRAGMA table_info(Measurements)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'meas_name' not in columns:
                cursor.execute("ALTER TABLE Measurements ADD COLUMN meas_name TEXT")
                conn.commit()
            if 'tip_id' not in columns:
                try:
                    cursor.execute("ALTER TABLE Measurements ADD COLUMN tip_id INTEGER DEFAULT 1")
                    cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
                    conn.commit()
                except Exception:
                    pass

            cursor.execute('''
                SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name, m.meas_name, COALESCE(m.tip_id, 1) AS tip_id, COALESCE(t.name, 'Unknown') AS tip_name, COALESCE(t.icon_char, '?') AS tip_icon, COALESCE(t.color_hex, '#6b7280') AS tip_color FROM Measurements m JOIN IEM_Models iem ON m.iem_id = iem.id LEFT JOIN TipProfiles t ON m.tip_id = t.id WHERE iem.musician_id = ? ORDER BY m.timestamp DESC LIMIT 100
            ''', (m_id,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                (timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob,
                 iem_name, custom_name, meas_name,
                 raw_tip_id, raw_tip_name, raw_tip_icon, raw_tip_color) = row
                base_name = custom_name if custom_name else iem_name
                display_name = meas_name if meas_name else base_name
                
                tip_id = int(raw_tip_id) if raw_tip_id is not None else 1
                tip_name = raw_tip_name if raw_tip_name else "Unknown"
                tip_icon = raw_tip_icon if raw_tip_icon else "?"
                tip_color = raw_tip_color if raw_tip_color else "#6b7280"

                # Parse blobs
                freq = None
                mag_l = None
                mag_r = None
                
                try:
                    if freq_blob: freq = np.frombuffer(freq_blob, dtype=np.float64)
                    if mag_l_blob: mag_l = np.frombuffer(mag_l_blob, dtype=np.float64)
                    if mag_r_blob: mag_r = np.frombuffer(mag_r_blob, dtype=np.float64)
                except Exception as e:
                    print(f"Error parsing BLOBs: {e}")

                # Determine side text
                side_text = "Stereo"
                if mag_l is not None and mag_r is None: side_text = "Left"
                if mag_r is not None and mag_l is None: side_text = "Right"
                
                # Compute acoustic seal metrics
                seal_l_status, seal_l_delta = HistoryCardWidget.compute_seal_for_channel(freq, mag_l)
                seal_r_status, seal_r_delta = HistoryCardWidget.compute_seal_for_channel(freq, mag_r)

                if seal_l_delta is not None and seal_r_delta is not None:
                    seal_text = f"Seal: L {seal_l_delta:+.1f}dB | R {seal_r_delta:+.1f}dB"
                elif seal_l_delta is not None:
                    seal_text = f"Seal L: {seal_l_delta:+.1f}dB"
                elif seal_r_delta is not None:
                    seal_text = f"Seal R: {seal_r_delta:+.1f}dB"
                else:
                    seal_text = ""

                data_dict = {
                    'timestamp': timestamp,
                    'notes': notes,
                    'photo_path': photo_path,
                    'freq': freq,
                    'mag_l': mag_l,
                    'mag_r': mag_r,
                    'iem_name': display_name,
                    'meas_name': meas_name if meas_name else '',
                    'base_name': base_name,
                    'side': side_text,
                    'tip_id': tip_id,
                    'tip_name': tip_name,
                    'tip_icon': tip_icon,
                    'tip_color': tip_color,
                    'seal_l': seal_l_delta,
                    'seal_r': seal_r_delta,
                    'seal_l_status': seal_l_status,
                    'seal_r_status': seal_r_status,
                    'seal_text': seal_text,
                }
                
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.UserRole, data_dict)
                
                card = HistoryCardWidget(
                    timestamp=timestamp,
                    iem_name=display_name,
                    side=side_text,
                    parent=None,
                    tip_id=tip_id,
                    tip_name=tip_name,
                    tip_color=tip_color,
                    tip_icon=tip_icon,
                    seal_l=seal_l_delta,
                    seal_r=seal_r_delta,
                    seal_text=seal_text,
                    freq=freq,
                    mag_l=mag_l,
                    mag_r=mag_r,
                )
                card.cb_graph.stateChanged.connect(self.refresh_view)
                
                # Ensure the item is big enough for the card
                item.setSizeHint(card.sizeHint())
                self.list_widget.setItemWidget(item, card)
                
            conn.close()
            
        except Exception as e:
            print(e)
        
        self.list_widget.blockSignals(False)
        self.refresh_view()
        self.filter_history()

    def update_prokit_ui_visibility(self, unlocked=None):
        """Update visibility of tip badges and seal indicators across all active history cards."""
        if unlocked is None:
            try:
                import config
                unlocked = config.is_prokit_unlocked()
            except Exception:
                unlocked = False

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            card = self.list_widget.itemWidget(item)
            if card and hasattr(card, "update_prokit_visibility"):
                card.update_prokit_visibility(unlocked)
                item.setSizeHint(card.sizeHint())

    update_prokit_visibility = update_prokit_ui_visibility

    def filter_history(self):
        query = self.search_bar.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.UserRole)
            if not data: continue
            
            tip_match = query in data.get('tip_name', '').lower()
            match = query in data['iem_name'].lower() or query in data['timestamp'].lower() or tip_match
            item.setHidden(not match)

    def set_edit_controls_enabled(self, enabled):
        self.txt_notes.setEnabled(enabled)
        self.edit_meas_name.setEnabled(enabled)
        self.edit_meas_date.setEnabled(enabled)
        self.btn_export_history.setEnabled(enabled)
        self.btn_save_target.setEnabled(enabled)
        self.btn_delete_history.setEnabled(enabled)

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        if not items:
            self.set_edit_controls_enabled(False)
            self.txt_notes.clear()
            self.edit_meas_name.clear()
            self.edit_meas_date.clear()
            return
            
        self.set_edit_controls_enabled(True)
        data = items[0].data(Qt.UserRole)
        
        self.txt_notes.blockSignals(True)
        self.edit_meas_name.blockSignals(True)
        self.edit_meas_date.blockSignals(True)
        
        self.txt_notes.setPlainText(data.get('notes', ''))
        self.edit_meas_name.setText(data.get('meas_name', ''))
        self.edit_meas_date.setText(data.get('timestamp', ''))
        
        self.txt_notes.blockSignals(False)
        self.edit_meas_name.blockSignals(False)
        self.edit_meas_date.blockSignals(False)

    def save_notes(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        old_ts = data['timestamp']
        
        new_notes = self.txt_notes.toPlainText()
        new_name = self.edit_meas_name.text().strip()
        new_ts = self.edit_meas_date.text().strip()
        
        # fallback if empty
        if not new_ts: new_ts = old_ts
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # If timestamp changed, check if new one exists to prevent collision
            if new_ts != old_ts:
                cursor.execute("SELECT 1 FROM Measurements WHERE timestamp = ?", (new_ts,))
                if cursor.fetchone():
                    # Collision! Revert UI to old timestamp
                    self.edit_meas_date.blockSignals(True)
                    self.edit_meas_date.setText(old_ts)
                    self.edit_meas_date.blockSignals(False)
                    new_ts = old_ts
            
            cursor.execute('UPDATE Measurements SET notes = ?, meas_name = ?, timestamp = ? WHERE timestamp = ?', 
                           (new_notes, new_name, new_ts, old_ts))
            conn.commit()
            conn.close()
            
            # Update item data
            data['notes'] = new_notes
            data['meas_name'] = new_name
            data['timestamp'] = new_ts
            data['iem_name'] = new_name if new_name else data.get('base_name', '')
            items[0].setData(Qt.UserRole, data)
            
            # Update Card UI
            from PySide6.QtWidgets import QLabel
            card = self.list_widget.itemWidget(items[0])
            if card:
                lbl_iem = card.findChild(QLabel, "lbl_iem")
                lbl_date = card.findChild(QLabel, "lbl_date")
                if lbl_iem: lbl_iem.setText(data['iem_name'])
                if lbl_date: lbl_date.setText(data['timestamp'])
                
        except Exception as e:
            print(f"Error autosaving: {e}")

    def on_item_checked(self):
        self.refresh_view()

    def refresh_view(self):
        self.plot_widget.clear()
        
        import numpy as np
        from audio_engine import AudioEngine
        # from theme import theme
        from PySide6.QtCore import Qt, QTimer
        import pyqtgraph as pg
        
        color_idx = 0
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            card = self.list_widget.itemWidget(item)
            
            if card and card.cb_graph.isChecked():
                data = item.data(Qt.UserRole)
                freq = data['freq']
                mag_l = data['mag_l']
                mag_r = data['mag_r']
                ts = data['timestamp']
                
                if freq is not None:
                    color = self.colors[color_idx % len(self.colors)]
                    
                    show_l = self.btn_chan_l.isChecked()
                    show_r = self.btn_chan_r.isChecked()
                    smooth_txt = self.cb_smooth.currentText()
                    
                    pts = 240
                    if smooth_txt == "Raw": pts = None
                    elif smooth_txt == "1/6 Oct": pts = 60
                    elif smooth_txt == "1/12 Oct": pts = 120
                    elif smooth_txt == "1/24 Oct": pts = 240
                    elif smooth_txt == "1/48 Oct": pts = 480
                    
                    if mag_l is not None and show_l:
                        f_plot, m_plot = freq, mag_l
                        if pts is not None:
                            try:
                                res = AudioEngine.smooth_spectrum(freq, mag_l, points=pts)
                                if len(res) == 3: f_plot, m_plot, _ = res
                                else: f_plot, m_plot = res
                            except Exception: pass
                        
                        self.plot_widget.plot(f_plot, m_plot, pen=pg.mkPen(color=color, width=2), name=f"{ts} (L)")
                        
                    if mag_r is not None and show_r:
                        f_plot, m_plot = freq, mag_r
                        if pts is not None:
                            try:
                                res = AudioEngine.smooth_spectrum(freq, mag_r, points=pts)
                                if len(res) == 3: f_plot, m_plot, _ = res
                                else: f_plot, m_plot = res
                            except Exception: pass
                        
                        self.plot_widget.plot(f_plot, m_plot, pen=pg.mkPen(color=color, width=2, style=Qt.DashLine), name=f"{ts} (R)")
                    
                    color_idx += 1

    def delete_selected(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        ts = data['timestamp']
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, 'Delete Measurement', f"Are you sure you want to delete this measurement?\n{ts}", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Measurements WHERE timestamp = ?', (ts,))
                conn.commit()
                conn.close()
                self.load_history(self.last_m_id)
            except Exception as e:
                print(e)

    def export_selected_csv(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        freq = data['freq']
        mag_l = data['mag_l']
        mag_r = data['mag_r']
        
        if freq is None: return
        
        from PySide6.QtWidgets import QFileDialog
        import numpy as np
        
        file_name, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write("Frequency,Magnitude_L,Magnitude_R\n")
                    for i in range(len(freq)):
                        l_val = mag_l[i] if mag_l is not None else ''
                        r_val = mag_r[i] if mag_r is not None else ''
                        f.write(f"{freq[i]},{l_val},{r_val}\n")
            except Exception as e:
                print(e)

    def save_as_target(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        freq = data['freq']
        mag_l = data['mag_l']
        mag_r = data['mag_r']
        iem = data['iem_name']
        side = data['side']
        
        if freq is None: return
        
        from PySide6.QtWidgets import QInputDialog
        import os
        
        # Decide which side to save if both are present. For Squiglink format, typically we just save one channel or average.
        mag_to_save = mag_l if mag_l is not None else mag_r
        if mag_l is not None and mag_r is not None:
            # Simple average if both are present? Or just ask the user. We'll default to left.
            mag_to_save = mag_l
            
        target_name, ok = QInputDialog.getText(self, "Save Target", "Target Name:", text=f"{iem} Target")
        if ok and target_name:
            try:
                os.makedirs("Reference Targets", exist_ok=True)
                target_path = os.path.join("Reference Targets", f"{target_name.replace('/', '_')}.csv")
                with open(target_path, 'w') as f:
                    for i in range(len(freq)):
                        f.write(f"{freq[i]:.2f},{mag_to_save[i]:.2f}\n")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Target Saved", f"Target saved to {target_path}")
            except Exception as e:
                print(e)

    def toggle_tools_pane(self):
        is_visible = self.tools_tabs.isVisible()
        self.tools_tabs.setVisible(not is_visible)
        if is_visible:
            self.btn_toggle_tools.setText("◀")
        else:
            self.btn_toggle_tools.setText("▶")
