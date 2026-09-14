import sys

with open('analysis_ui.py', 'r') as f:
    lines = f.readlines()

# 1. Insert FloatKnob before class AnalysisWidget
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith("class AnalysisWidget(QWidget):"):
        insert_idx = i
        break

float_knob_code = """
from PyQt5.QtWidgets import QDial, QComboBox
from PyQt5.QtCore import pyqtSignal

class FloatKnob(QWidget):
    valueChanged = pyqtSignal(float)
    
    def __init__(self, title, min_val, max_val, default_val, scale='linear', suffix=""):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.scale = scale
        self.suffix = suffix
        self.steps = 1000
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet("font-size: 10px; color: #888; font-weight: bold;")
        layout.addWidget(self.lbl_title)
        
        self.dial = QDial()
        self.dial.setMinimum(0)
        self.dial.setMaximum(self.steps)
        self.dial.setFixedSize(45, 45)
        self.dial.setStyleSheet("QDial { background-color: #2a2a2a; }")
        layout.addWidget(self.dial, alignment=Qt.AlignCenter)
        
        self.lbl_val = QLabel()
        self.lbl_val.setAlignment(Qt.AlignCenter)
        self.lbl_val.setStyleSheet("font-size: 11px; font-weight: bold; color: #ccc;")
        layout.addWidget(self.lbl_val)
        
        self.dial.valueChanged.connect(self._on_dial_changed)
        self.setValue(default_val)
        
    def _dial_to_val(self, d):
        if self.scale == 'log':
            return self.min_val * (self.max_val / self.min_val) ** (d / self.steps)
        else:
            return self.min_val + d * (self.max_val - self.min_val) / self.steps
            
    def _val_to_dial(self, v):
        if self.scale == 'log':
            return int(self.steps * np.log(v / self.min_val) / np.log(self.max_val / self.min_val))
        else:
            return int(self.steps * (v - self.min_val) / (self.max_val - self.min_val))
            
    def _on_dial_changed(self, val):
        real_val = self._dial_to_val(val)
        if self.suffix == "Hz":
            if real_val >= 1000:
                txt = f"{real_val/1000:.1f}k"
            else:
                txt = f"{int(real_val)}"
        elif self.suffix == "dB":
            txt = f"{real_val:+.1f}"
        else:
            txt = f"{real_val:.2f}"
            
        self.lbl_val.setText(txt + self.suffix)
        self.valueChanged.emit(real_val)
        
    def value(self):
        return self._dial_to_val(self.dial.value())
        
    def setValue(self, v):
        d = self._val_to_dial(v)
        self.dial.blockSignals(True)
        self.dial.setValue(d)
        self.dial.blockSignals(False)
        self._on_dial_changed(d)
"""

lines.insert(insert_idx, float_knob_code)

# Now we need to find the old DSP code to replace
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "self.dsp_container = QWidget()" in line:
        start_idx = i
    if "self.tools_tabs.addTab(self.dsp_container," in line:
        end_idx = i + 1
        break

new_dsp_code = """        # 2. Hardware DSP Tool (Redesigned with Knobs and Presets)
        self.dsp_container = QWidget()
        dsp_layout = QVBoxLayout(self.dsp_container)
        dsp_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- EQ Presets ---
        preset_layout = QHBoxLayout()
        self.cb_eq_preset = QComboBox()
        self.cb_eq_preset.addItem("-- Select Preset --")
        self.cb_eq_preset.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px; font-size: 11px; } QComboBox::drop-down { border: none; }")
        
        self.btn_save_eq = QPushButton("Save")
        self.btn_save_eq.setStyleSheet("background: #059669; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold; font-size: 11px;")
        
        self.btn_del_eq = QPushButton("Del")
        self.btn_del_eq.setStyleSheet("background: #ef4444; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold; font-size: 11px;")
        
        preset_layout.addWidget(self.cb_eq_preset, stretch=1)
        preset_layout.addWidget(self.btn_save_eq)
        preset_layout.addWidget(self.btn_del_eq)
        dsp_layout.addLayout(preset_layout)
        
        # --- Master Bypass ---
        self.btn_dsp_master = QPushButton("DSP BYPASSED")
        self.btn_dsp_master.setCheckable(True)
        self.btn_dsp_master.setStyleSheet("QPushButton { background: #3f3f46; color: #a1a1aa; font-weight: bold; font-size: 14px; padding: 8px; border-radius: 6px; margin-top: 5px; margin-bottom: 5px; } QPushButton:checked { background: #059669; color: white; border: 2px solid #34d399; }")
        dsp_layout.addWidget(self.btn_dsp_master)
        
        # --- EQ Scroll Area ---
        eq_scroll = QScrollArea()
        eq_scroll.setWidgetResizable(True)
        eq_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        eq_scroll_content = QWidget()
        eq_bands_layout = QVBoxLayout(eq_scroll_content)
        eq_bands_layout.setContentsMargins(0, 0, 0, 0)
        eq_bands_layout.setSpacing(6)
        
        self.peq_bands = []
        for i in range(5):
            band_frame = QFrame()
            band_frame.setStyleSheet("QFrame { background: #18181b; border: 1px solid #333; border-radius: 8px; }")
            bl = QVBoxLayout(band_frame)
            bl.setContentsMargins(8, 6, 8, 6)
            
            row1 = QHBoxLayout()
            lbl = QLabel(f"Band {i+1} ({'Low Shelf' if i==0 else 'High Shelf' if i==4 else 'PEQ'})")
            lbl.setStyleSheet("font-weight: bold; color: #ddd; font-size: 11px; border: none;")
            cb_on = QPushButton("ON")
            cb_on.setCheckable(True)
            cb_on.setChecked(True)
            cb_on.setFixedSize(30, 20)
            cb_on.setStyleSheet("QPushButton { background: #444; color: #888; font-size: 10px; border-radius: 10px; font-weight: bold; } QPushButton:checked { background: #0ea5e9; color: white; }")
            row1.addWidget(lbl)
            row1.addStretch()
            row1.addWidget(cb_on)
            bl.addLayout(row1)
            
            row2 = QHBoxLayout()
            knob_f = FloatKnob("FREQ", 20, 20000, [60, 250, 1000, 4000, 8000][i], 'log', 'Hz')
            knob_f.setStyleSheet("border: none;")
            knob_g = FloatKnob("GAIN", -24, 24, 0, 'linear', 'dB')
            knob_g.setStyleSheet("border: none;")
            knob_q = FloatKnob("Q", 0.1, 10, 0.7 if i==0 or i==4 else 1.41, 'log', '')
            knob_q.setStyleSheet("border: none;")
            
            row2.addWidget(knob_f)
            row2.addWidget(knob_g)
            row2.addWidget(knob_q)
            bl.addLayout(row2)
            
            eq_bands_layout.addWidget(band_frame)
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
            
        eq_bands_layout.addStretch()
        eq_scroll.setWidget(eq_scroll_content)
        dsp_layout.addWidget(eq_scroll)
        
        def on_master_toggle(checked):
            self.btn_dsp_master.setText("DSP ACTIVE (LIVE)" if checked else "DSP BYPASSED")
            if hasattr(self, 'peq_bands') and len(self.peq_bands) > 0:
                self.peq_bands[0]['on'].toggled.emit(self.peq_bands[0]['on'].isChecked())
                
        self.btn_dsp_master.toggled.connect(on_master_toggle)
        
        self.tools_tabs.addTab(self.dsp_container, "🎛️ Hardware EQ")
        
        self.init_eq_db()
        self.load_eq_presets()
        self.btn_save_eq.clicked.connect(self.save_eq_preset)
        self.btn_del_eq.clicked.connect(self.delete_eq_preset)
        self.cb_eq_preset.currentIndexChanged.connect(self.apply_eq_preset)
"""

lines = lines[:start_idx] + [new_dsp_code + "\n"] + lines[end_idx:]

# Now we need to append the DB methods to the end of the AnalysisWidget class
db_methods = """
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
        self.cb_eq_preset.blockSignals(True)
        self.cb_eq_preset.clear()
        self.cb_eq_preset.addItem("-- Select Preset --")
        try:
            conn = sqlite3.connect("inearsnitch.db")
            c = conn.cursor()
            c.execute("SELECT name FROM eq_presets ORDER BY name")
            for row in c.fetchall():
                self.cb_eq_preset.addItem(row[0])
            conn.close()
        except:
            pass
        self.cb_eq_preset.blockSignals(False)

    def save_eq_preset(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        import sqlite3, json
        name, ok = QInputDialog.getText(self, "Save EQ Preset", "Preset Name:")
        if ok and name:
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
                self.load_eq_presets()
                self.cb_eq_preset.setCurrentText(name)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def delete_eq_preset(self):
        from PyQt5.QtWidgets import QMessageBox
        import sqlite3
        name = self.cb_eq_preset.currentText()
        if name == "-- Select Preset --": return
        if QMessageBox.question(self, "Delete Preset", f"Delete '{name}'?") == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("inearsnitch.db")
                c = conn.cursor()
                c.execute("DELETE FROM eq_presets WHERE name = ?", (name,))
                conn.commit()
                conn.close()
                self.load_eq_presets()
                self.cb_eq_preset.setCurrentIndex(0)
            except:
                pass

    def apply_eq_preset(self):
        import sqlite3, json
        name = self.cb_eq_preset.currentText()
        if name == "-- Select Preset --": return
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
"""

lines.append(db_methods)

with open('analysis_ui.py', 'w') as f:
    f.writelines(lines)
