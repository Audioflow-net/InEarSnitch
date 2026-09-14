import sys
import numpy as np
import theme
from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSplitter, QTabWidget, QComboBox, QDial, QLineEdit
from PySide6.QtCore import Qt, Signal
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
        
        self.dial = QDial()
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

class AnalysisWidget(QWidget):
    request_measurement = Signal()
    request_stress_test = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("AnalysisRoot")
        self.setStyleSheet("#AnalysisRoot { background-color: transparent; color: white; }")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # --- 2026 UI: No giant headers, just a clean rigid layout ---
        self.split_layout = QHBoxLayout()
        self.split_layout.setContentsMargins(0, 0, 0, 0)
        self.split_layout.setSpacing(0)
        self.layout.addLayout(self.split_layout)
        
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
        
        # --- Smart Toolbar (Inline) ---
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(6)
        
        from PySide6.QtWidgets import QLabel
        vis_layout = QVBoxLayout()
        vis_layout.setSpacing(2)
        vis_layout.setContentsMargins(0, 0, 0, 0)

        self.seg_widget = QWidget()
        seg_layout = QHBoxLayout(self.seg_widget)
        seg_layout.setContentsMargins(0,0,0,0)
        seg_layout.setSpacing(0)

        self.btn_chan_l = QPushButton("Left")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #0ea5e9; color: white; border-color: #0ea5e9; }")
        
        self.btn_chan_r = QPushButton("Right")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #ef4444; color: white; border-color: #ef4444; }")

        seg_layout.addWidget(self.btn_chan_l)
        seg_layout.addWidget(self.btn_chan_r)
        
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
        
        self.btn_reset_zoom = QPushButton("🔍 Autozoom")
        self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)
        
        self.btn_run_sweep = QPushButton("▶ MEASURE")
        self.btn_run_sweep.hide()
        self.btn_run_sweep.setStyleSheet("QPushButton { background: #db2777; color: #ffffff; border-radius: 4px; padding: 2px 12px; font-weight: bold; font-size: 11px; margin-left: 8px; } QPushButton:hover { background: #be185d; }")
        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        self.btn_run_sweep.setToolTip("Run a new Sine Sweep measurement from within the Analysis tab")
        
        self.btn_chan_l.clicked.connect(self.refresh_view)
        self.btn_chan_r.clicked.connect(self.refresh_view)
        
        zoom_layout.addWidget(self.seg_widget)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addWidget(self.btn_run_sweep)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)
        # zoom_layout is intentionally not added to left_pane_layout to avoid double toolbar
        # We will extract its buttons into the tab corner widget in main.py
        
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setBackground('#18181b')
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
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
        self.thd_widget.setLabel('left', 'THD', units='%')
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
        self.csd_widget.setLabel('left', 'Magnitude (dB)')
        self.csd_widget.setXRange(np.log10(200), np.log10(20000))
        self.csd_widget.setYRange(-60, 20)
        self.graph_tabs.addTab(self.csd_widget, "Waterfall (CSD)")
        
        left_pane_layout.addWidget(self.graph_tabs)
        self.split_layout.addWidget(left_pane_widget, stretch=1)
        
        # --- Right Pane: Tools (QTabWidget) ---
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setElideMode(Qt.ElideNone)
        self.tools_tabs.setUsesScrollButtons(True)
        self.tools_tabs.setFixedWidth(345) # Exactly matches RTA(110) + Gap(15) + RUN(220)
        
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
        self.tools_tabs.addTab(self.diag_container, "Diagnostics")
        

        
        # 2. Hardware DSP Tool (Ultra Compact 2026 UI)
        self.dsp_container = QWidget()
        dsp_layout = QVBoxLayout(self.dsp_container)
        dsp_layout.setContentsMargins(6, 6, 6, 6)
        dsp_layout.setSpacing(4)
        

        
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
        self.preset_cards_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.preset_cards_container = QWidget()
        self.preset_cards_layout = QVBoxLayout(self.preset_cards_container)
        self.preset_cards_layout.setContentsMargins(0, 5, 0, 0)
        self.preset_cards_layout.setSpacing(4)
        self.preset_cards_layout.setAlignment(Qt.AlignTop)
        self.preset_cards_scroll.setWidget(self.preset_cards_container)
        dsp_layout.addWidget(self.preset_cards_scroll, stretch=1)
        
        self.tools_tabs.addTab(self.dsp_container, "EQ")
        self.split_layout.addWidget(self.tools_tabs)
        
        self.init_eq_db()
        self.load_eq_presets()
        self.btn_save_eq.clicked.connect(self.save_eq_preset)
        self.update_theme()


    def reset_zoom(self):
        import numpy as np
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.plot_widget.setYRange(40, 110, padding=0.0)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.thd_widget.setYRange(0, 5, padding=0.0)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setXRange(np.log10(2000), np.log10(20000), padding=0.0)
            self.csd_widget.setYRange(-60, 20, padding=0.0)

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
        
    def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None, ir_l=None, ir_r=None, sweep_count="1x"):
        self._last_data = (freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r, sweep_count)
        
        # Auto-switch to the channel that actually has data
        if mag_l is None and mag_r is not None:
            self.btn_chan_r.setChecked(True)
        elif mag_r is None and mag_l is not None:
            self.btn_chan_l.setChecked(True)
            
        self.refresh_view()
        
    def render_diagnostics(self):
        """Render compact diagnostics report cards, filtered by active graph tab."""
        if not hasattr(self, 'report_layout'):
            return
        for i in reversed(range(self.report_layout.count())):
            w = self.report_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not hasattr(self, '_last_report') or not self._last_report:
            return

        from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout as QVL
        from PySide6.QtCore import Qt
        import numpy as np

        # Filter cards by current graph tab
        tab_idx = self.graph_tabs.currentIndex()
        tab_cat_map = {0: 'FR', 1: 'THD', 2: 'CSD'}
        active_cat = tab_cat_map.get(tab_idx, None)  # None = show all

        import theme
        is_light = theme.is_light()
        status_style = {
            'OK':   ('#dcfce7' if is_light else '#0d3320', '#16a34a' if is_light else '#22c55e', '✓'),
            'WARN': ('#fef3c7' if is_light else '#422006', '#d97706' if is_light else '#f59e0b', '⚠'),
            'FAIL': ('#fee2e2' if is_light else '#450a0a', '#dc2626' if is_light else '#ef4444', '✗'),
        }

        for item in self._last_report:
            cat = item.get('category', 'FR')
            # Filter: show only matching category, or all if no specific tab
            if active_cat is not None and cat != active_cat:
                continue

            status = item.get('status', 'OK')
            bg, accent, icon = status_style.get(status, status_style['OK'])
            band = item.get('band')

            card = QFrame()
            card.setCursor(Qt.PointingHandCursor if band else Qt.ArrowCursor)
            card.setStyleSheet(f"QFrame {{ background: {bg}; border-left: 3px solid {accent}; border-radius: 3px; padding: 3px 6px; margin: 1px 0; }}")
            cl = QVL(card)
            cl.setContentsMargins(4, 2, 4, 2)
            cl.setSpacing(0)

            hdr = QLabel(f"<span style='color:{accent};font-weight:bold;'>{icon}</span>  <b>{item.get('title','')}</b>  <span style='color:{'#52525b' if is_light else '#666'};font-size:9px;'>[{cat}]</span>")
            hdr.setStyleSheet(f"color: {accent}; font-size: 11px; background: transparent; border: none;")
            cl.addWidget(hdr)

            desc = QLabel(item.get('desc', ''))
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {'#3f3f47' if is_light else '#999'}; font-size: 10px; background: transparent; border: none; padding-left: 16px;")
            cl.addWidget(desc)

            # Click-to-zoom: zoom the correct graph for this card's category
            if band:
                def make_zoom(b=band, c=cat):
                    def zoom_handler(event):
                        f_min, f_max = b
                        # Pick the right widget for the category
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

    def refresh_view(self):
        if not hasattr(self, '_last_data'): return
        sweep_count = "1x"
        try:
            freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r, sweep_count = self._last_data
        except ValueError:
            try:
                freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r = self._last_data
            except ValueError:
                freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self._last_data
                ir_l = None
                ir_r = None
        
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
            report = [{'title': 'Diagnostics Disabled (1x Sweep)', 'status': 'WARN', 'desc': 'Diagnostics require at least a 3x sweep to reduce background noise and avoid false positives. Please select 3x or 5x and run the measurement again.', 'band': None, 'category': 'FR'}]
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
                f_l, m_l, _ = AudioEngine.smooth_spectrum(freqs, mag_l, points=240)
                self.plot_widget.plot(f_l, m_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left')
            if mag_r is not None:
                f_r, m_r, _ = AudioEngine.smooth_spectrum(freqs, mag_r, points=240)
                self.plot_widget.plot(f_r, m_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right')
                
            # Plot Target (CSV)
            if tgt_freqs is not None and tgt_mags is not None:
                interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                idx_1k = (np.abs(freqs - 1000)).argmin()
                meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                tgt_val = interp_tgt[idx_1k]
                interp_tgt += (meas_val - tgt_val)
                f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=240)
                self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')
                
            # Plot History (DB)
            hist_pen = pg.mkPen((255, 165, 0, 150), width=2, style=Qt.DashLine)
            if ref_mag_l is not None and show_l:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            if ref_mag_r is not None and show_r:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')
                
        self._last_report = report
        self.render_diagnostics()
            
        # --- Update THD Plot ---
        self.thd_widget.clear()
        if self.thd_widget.plotItem.legend:
            self.thd_widget.plotItem.legend.clear()
        if thd_data is not None:
            # Expected format: (thd_freqs, orig_thd_l, orig_thd_r)
            thd_freqs, orig_thd_l, orig_thd_r = thd_data
            
            show_l = self.btn_chan_l.isChecked()
            show_r = self.btn_chan_r.isChecked()
            thd_l = orig_thd_l if show_l else None
            thd_r = orig_thd_r if show_r else None
            
            if thd_l is not None:
                self.thd_widget.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_widget.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')
                
        # --- Update CSD Plot ---
        self.csd_widget.clear()
        if self.csd_widget.plotItem.legend:
            self.csd_widget.plotItem.legend.clear()
        if csd_data is not None:
            show_l = self.btn_chan_l.isChecked()
            show_r = self.btn_chan_r.isChecked()
            # Prefer R if R is checked, else L
            if show_r and 'R' in csd_data:
                active_csd = csd_data.get('R')
            elif show_l and 'L' in csd_data:
                active_csd = csd_data.get('L')
            else:
                active_csd = csd_data.get('L') or csd_data.get('R')
            print(f"[CSD DEBUG] csd_data keys={list(csd_data.keys())}, show_l={show_l}, show_r={show_r}, active_csd={'YES' if active_csd else 'NONE'}")
            if active_csd:
                csd_freqs, csd_times, orig_csd_slices = active_csd
                
                # 1. Reduziere die Anzahl gezeichneter Slices (jeden 3. nehmen)
                csd_slices = orig_csd_slices[::3]
                num_slices = len(csd_slices)
                print(f"[CSD DEBUG] num_slices={num_slices}, freqs_shape={csd_freqs.shape}, slice_shape={csd_slices[0].shape}")
                
                # 4. Y-Range dynamisch basierend auf dem höchsten Peak
                if num_slices > 0:
                    max_peak = float(np.max(csd_slices[0]))
                    self.csd_widget.setYRange(max_peak - 45, max_peak + 5)
                
                # 4. Fill-Opacity reduzieren
                fill_brush = pg.mkBrush(24, 24, 27, 200)
                
                # Draw from back to front (i.e. oldest/last slice first) to allow occlusion
                for i in range(num_slices - 1, -1, -1):
                    slice_mag = csd_slices[i]
                    
                    # 3 & 2: Freq-Shift 0.99, Y-Offset 1.5 dB
                    shift_freqs = csd_freqs * (0.99 ** i)
                    shift_mag = slice_mag - (i * 1.5) 
                
                    # 6. Farb-Gradient: Vorne = voll Cyan, Hinten = dunkel transparent
                    blend = i / max(1, num_slices - 1)
                    r = 0
                    g = int(255 * (1 - blend) + 30 * blend)
                    b = int(255 * (1 - blend) + 40 * blend)
                    a = int(255 * (1 - blend) + 50 * blend)
                    color = pg.mkColor(r, g, b, a)
                    
                    # 5. Linienbreite: vorne 2.0, hinten 1.0
                    pen_width = 2.0 - (1.0 * blend)
                
                    self.csd_widget.plot(
                        shift_freqs, 
                        shift_mag, 
                        pen=pg.mkPen(color, width=pen_width),
                        fillLevel=-100,
                        brush=fill_brush
                    )
                
        # Trigger EQ update to draw the virtual curve
        if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
            # We call the first band's toggled slot manually to force an update
            self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())

    def init_eq_db(self):
        import sqlite3
        try:
            conn = sqlite3.connect("inearsnitch.db")
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
            conn = sqlite3.connect("inearsnitch.db")
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
            QMessageBox.warning(self, "Error", "Please enter a preset name!")
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
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO eq_presets (name, data) VALUES (?, ?)", (name, json.dumps(data)))
            conn.commit()
            conn.close()
            self.le_preset_name.clear()
            self.load_eq_presets()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def delete_eq_preset(self, name):
        from PySide6.QtWidgets import QMessageBox
        import sqlite3
        if QMessageBox.question(self, "Delete Preset", f"Delete '{name}'?") == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("inearsnitch.db")
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
            conn = sqlite3.connect("inearsnitch.db")
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
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        active = theme.get_color('bg_hover')
        text_sec = theme.get_color('text_secondary')
        
        # Update Tabs
        self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        if hasattr(self, 'tools_tabs'):
            self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
            
        # Update Graph Backgrounds
        pg_bg = theme.get_color('pg_bg')
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setBackground(pg_bg)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setBackground(pg_bg)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setBackground(pg_bg)
            
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
                        
        # Redraw diagnostics cards to refresh their light/dark color palette
        self.render_diagnostics()


