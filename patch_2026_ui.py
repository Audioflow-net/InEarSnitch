import sys

with open('analysis_ui.py', 'r') as f:
    lines = f.readlines()

# Find the exact index of `def zoom_graph(self, min_f, max_f):`
end_idx = 0
for i, line in enumerate(lines):
    if "def zoom_graph(" in line:
        end_idx = i
        break

new_ui = """import sys
import numpy as np
import theme
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSplitter, QTabWidget, QComboBox, QDial
from PyQt5.QtCore import Qt, pyqtSignal
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

class FloatKnob(QWidget):
    valueChanged = pyqtSignal(float)
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
        
        self.dial = QDial()
        self.dial.setMinimum(0)
        self.dial.setMaximum(self.steps)
        self.dial.setFixedSize(28, 28)
        self.dial.setStyleSheet("QDial { background-color: #2a2a2a; }")
        layout.addWidget(self.dial, alignment=Qt.AlignCenter)
        
        self.lbl_val = QLabel()
        self.lbl_val.setAlignment(Qt.AlignCenter)
        self.lbl_val.setStyleSheet("font-size: 9px; font-weight: bold; color: #ccc; border: none; background: transparent;")
        layout.addWidget(self.lbl_val)
        
        self.dial.valueChanged.connect(self._on_dial_changed)
        self.setValue(default_val)
        
    def _dial_to_val(self, d):
        if self.scale == 'log': return self.min_val * (self.max_val / self.min_val) ** (d / self.steps)
        else: return self.min_val + d * (self.max_val - self.min_val) / self.steps
            
    def _val_to_dial(self, v):
        if self.scale == 'log': return int(self.steps * np.log(v / self.min_val) / np.log(self.max_val / self.min_val))
        else: return int(self.steps * (v - self.min_val) / (self.max_val - self.min_val))
            
    def _on_dial_changed(self, val):
        real_val = self._dial_to_val(val)
        if self.suffix == "Hz":
            txt = f"{real_val/1000:.1f}k" if real_val >= 1000 else f"{int(real_val)}"
        elif self.suffix == "dB": txt = f"{real_val:+.1f}"
        else: txt = f"{real_val:.2f}"
        self.lbl_val.setText(txt + self.suffix)
        self.valueChanged.emit(real_val)
        
    def value(self): return self._dial_to_val(self.dial.value())
    def setValue(self, v):
        d = self._val_to_dial(v)
        self.dial.blockSignals(True)
        self.dial.setValue(d)
        self.dial.blockSignals(False)
        self._on_dial_changed(d)

from analysis import Analyzer

class AnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("AnalysisRoot")
        self.setStyleSheet("#AnalysisRoot { background-color: transparent; color: white; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- 2026 UI: No giant headers, just a clean splitter ---
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # --- Left Pane: Graphs (QTabWidget) ---
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; border-radius: 4px; } QTabBar::tab { background: #222; color: #888; padding: 6px 12px; border: 1px solid #333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; } QTabBar::tab:selected { background: #333; color: white; }")
        
        # 1. FR Graph
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(4, 4, 4, 4)
        fr_layout.setSpacing(4)
        
        # --- Smart Toolbar (Inline) ---
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(6)
        
        self.btn_chan_l = QPushButton("L")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(26, 22)
        self.btn_chan_l.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #0ea5e9; color: white; }")
        
        self.btn_chan_r = QPushButton("R")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(26, 22)
        self.btn_chan_r.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #ef4444; color: white; }")
        
        self.cb_ana_target = QComboBox()
        self.cb_ana_target.addItem("-- Target --")
        self.cb_ana_target.setToolTip("Select a target curve for analysis.")
        self.cb_ana_target.setMinimumWidth(120)
        self.cb_ana_target.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 6px; border-radius: 4px; font-size: 11px; }")
        
        self.cb_ana_history = QComboBox()
        self.cb_ana_history.addItem("-- History --")
        self.cb_ana_history.setToolTip("Select a historical measurement.")
        self.cb_ana_history.setMinimumWidth(120)
        self.cb_ana_history.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 6px; border-radius: 4px; font-size: 11px; }")
        
        self.btn_reset_zoom = QPushButton("Reset Zoom")
        self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
        
        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)
        fr_layout.addLayout(zoom_layout)
        
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setBackground('#18181b')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
        self.plot_widget.setXRange(np.log10(20), np.log10(20000))
        self.plot_widget.setYRange(40, 110)
        self.plot_widget.addLegend(offset=(10, 10))
        fr_layout.addWidget(self.plot_widget)
        
        self.graph_tabs.addTab(self.fr_container, "📊 Freq Response")
        
        # 2. THD Graph
        self.thd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.thd_widget.setBackground('#18181b')
        self.thd_widget.setLogMode(x=True, y=False)
        self.thd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.thd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.thd_widget.setLabel('left', 'THD', units='%')
        self.thd_widget.setXRange(np.log10(20), np.log10(10000))
        self.thd_widget.setYRange(0, 5)
        self.thd_widget.addLegend(offset=(10, 10))
        self.graph_tabs.addTab(self.thd_widget, "📉 Distortion (THD)")
        
        # 3. CSD Graph
        self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.csd_widget.setBackground('#18181b')
        self.csd_widget.setLogMode(x=True, y=False)
        self.csd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.csd_widget.setLabel('left', 'Decay (ms)')
        self.csd_widget.setXRange(np.log10(200), np.log10(20000))
        self.graph_tabs.addTab(self.csd_widget, "🌊 Waterfall (CSD)")
        
        self.splitter.addWidget(self.graph_tabs)
        
        # --- Right Pane: Tools (QTabWidget) ---
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; border-radius: 4px; } QTabBar::tab { background: #222; color: #888; padding: 6px 12px; border: 1px solid #333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; } QTabBar::tab:selected { background: #333; color: white; }")
        
        # 1. Diagnostics Tool
        self.diag_container = QWidget()
        diag_layout = QVBoxLayout(self.diag_container)
        diag_layout.setContentsMargins(4, 4, 4, 4)
        
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setAlignment(Qt.AlignTop)
        self.report_scroll.setWidget(self.report_container)
        diag_layout.addWidget(self.report_scroll)
        self.tools_tabs.addTab(self.diag_container, "🩺 Diagnostics")
        
        # 2. Hardware DSP Tool (Ultra Compact 2026 UI)
        self.dsp_container = QWidget()
        dsp_layout = QVBoxLayout(self.dsp_container)
        dsp_layout.setContentsMargins(6, 6, 6, 6)
        dsp_layout.setSpacing(4)
        
        # --- EQ Presets ---
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(4)
        self.cb_eq_preset = QComboBox()
        self.cb_eq_preset.addItem("-- Preset --")
        self.cb_eq_preset.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; border-radius: 4px; padding: 2px 6px; font-size: 11px; } QComboBox::drop-down { border: none; }")
        
        self.btn_save_eq = QPushButton("Save")
        self.btn_save_eq.setStyleSheet("background: #059669; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 10px;")
        
        self.btn_del_eq = QPushButton("Del")
        self.btn_del_eq.setStyleSheet("background: #ef4444; color: white; border-radius: 4px; padding: 2px 6px; font-weight: bold; font-size: 10px;")
        
        preset_layout.addWidget(self.cb_eq_preset, stretch=1)
        preset_layout.addWidget(self.btn_save_eq)
        preset_layout.addWidget(self.btn_del_eq)
        dsp_layout.addLayout(preset_layout)
        
        # --- Master Bypass ---
        self.btn_dsp_master = QPushButton("DSP BYPASSED")
        self.btn_dsp_master.setCheckable(True)
        self.btn_dsp_master.setStyleSheet("QPushButton { background: #3f3f46; color: #a1a1aa; font-weight: bold; font-size: 11px; padding: 4px; border-radius: 4px; } QPushButton:checked { background: #059669; color: white; border: 2px solid #34d399; }")
        dsp_layout.addWidget(self.btn_dsp_master)
        
        # --- EQ Bands (Horizontal, ultra compact) ---
        self.peq_bands = []
        for i in range(5):
            band_frame = QFrame()
            band_frame.setStyleSheet("QFrame { background: #18181b; border: 1px solid #333; border-radius: 4px; }")
            bl = QHBoxLayout(band_frame)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(6)
            
            # Left side: ON + Name
            left_info = QVBoxLayout()
            left_info.setSpacing(2)
            left_info.setAlignment(Qt.AlignCenter)
            lbl = QLabel(f"B{i+1}\\n{'LS' if i==0 else 'HS' if i==4 else 'PEQ'}")
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
            
            bl.addStretch()
            
            # Knobs
            knob_f = FloatKnob("FREQ", 20, 20000, [60, 250, 1000, 4000, 8000][i], 'log', 'Hz')
            knob_g = FloatKnob("GAIN", -24, 24, 0, 'linear', 'dB')
            knob_q = FloatKnob("Q", 0.1, 10, 0.7 if i==0 or i==4 else 1.41, 'log', '')
            
            bl.addWidget(knob_f)
            bl.addWidget(knob_g)
            bl.addWidget(knob_q)
            
            dsp_layout.addWidget(band_frame)
            self.peq_bands.append({'on': cb_on, 'f': knob_f, 'g': knob_g, 'q': knob_q, 'type': 'peq' if i>0 and i<4 else ('lowshelf' if i==0 else 'highshelf')})
            
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
                
                if hasattr(self, 'current_freqs') and self.current_freqs is not None:
                    if hasattr(self, 'virtual_eq_line') and self.virtual_eq_line is not None:
                        eq_delta = dsp_engine.get_magnitude_response(self.current_freqs, 48000)
                        base_mag = self.current_mag_l if self.current_mag_l is not None else self.current_mag_r
                        if base_mag is not None:
                            from audio_engine import AudioEngine
                            f_eq, m_eq, _ = AudioEngine.smooth_spectrum(self.current_freqs, base_mag + eq_delta, points=240)
                            self.virtual_eq_line.setData(f_eq, m_eq)
                            if self.btn_dsp_master.isChecked():
                                self.virtual_eq_line.show()
                            else:
                                self.virtual_eq_line.hide()
                                
            cb_on.toggled.connect(update_dsp)
            knob_f.valueChanged.connect(update_dsp)
            knob_g.valueChanged.connect(update_dsp)
            knob_q.valueChanged.connect(update_dsp)
            
        dsp_layout.addStretch()
        
        def on_master_toggle(checked):
            self.btn_dsp_master.setText("DSP ACTIVE (LIVE)" if checked else "DSP BYPASSED")
            if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
                self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())
                
        self.btn_dsp_master.toggled.connect(on_master_toggle)
        
        self.tools_tabs.addTab(self.dsp_container, "🎛️ Hardware EQ")
        
        self.splitter.addWidget(self.tools_tabs)
        self.splitter.setSizes([750, 250])
        
        self.init_eq_db()
        self.load_eq_presets()
        self.btn_save_eq.clicked.connect(self.save_eq_preset)
        self.btn_del_eq.clicked.connect(self.delete_eq_preset)
        self.cb_eq_preset.currentIndexChanged.connect(self.apply_eq_preset)
\n"""

lines = [new_ui] + lines[end_idx:]

with open('analysis_ui.py', 'w') as f:
    f.writelines(lines)
