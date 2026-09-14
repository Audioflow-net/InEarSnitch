import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PySide6.QtCore import Qt

import pyqtgraph as pg
import theme


class FreqAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strings = []
        for v in values:
            hz = 10**v
            if hz >= 1000:
                strings.append(f"{hz/1000:g}k")
            else:
                strings.append(f"{hz:g}")
        return strings


from PySide6.QtCore import Signal
import shutil
import os

class CalibrationWidget(QWidget):
    calibration_applied = Signal(str)
    def __init__(self):
        super().__init__()
        
        
        self.layout = QVBoxLayout(self)
        
        self.header_label = QLabel("Microphone Calibration")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.header_label)
        
        self.file_label = QLabel("No calibration file loaded.")
        self.layout.addWidget(self.file_label)
        
        self.plot_widget = pg.PlotWidget(title="Calibration Curve")
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode="peak")
        self.plot_widget.setBackground(theme.get_color('pg_bg'))
        self.plot_widget.getPlotItem().getAxis('left').setPen(theme.get_color('pg_fg'))
        self.plot_widget.getPlotItem().getAxis('bottom').setPen(theme.get_color('pg_fg'))
        self.plot_widget.setLabel('left', 'Amplitude', units='dB')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.setLogMode(x=True, y=False)
        self.layout.addWidget(self.plot_widget)
        
        self.button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Load Calibration File...")
        self.load_button.setStyleSheet("padding: 5px;")
        self.load_button.clicked.connect(self.load_file)
        self.button_layout.addWidget(self.load_button)
        
        self.apply_button = QPushButton("Apply Calibration")
        self.apply_button.setStyleSheet("padding: 5px;")
        self.apply_button.clicked.connect(self.apply_calibration)
        self.apply_button.setEnabled(False)
        self.button_layout.addWidget(self.apply_button)
        
        self.gen_button = QPushButton("Auto-Generate from Reference")
        self.gen_button.setProperty("class", "accent")
        self.gen_button.clicked.connect(self.generate_calibration)
        self.button_layout.addWidget(self.gen_button)
        
        self.layout.addLayout(self.button_layout)
        
        self.freqs = []
        self.amps = []
        
    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Microphone Calibration File", "", "Calibration Files (*.cal *.txt);;All Files (*)", options=options)
        if file_name:
            self.current_file = file_name
            self.file_label.setText(f"Loaded: {os.path.basename(file_name)}")
            self.parse_file(file_name)
            

    def generate_calibration(self):
        import numpy as np
        # 1. Ask for user's measurement
        QMessageBox.information(self, "Step 1: Your Measurement", "Select the CSV file of YOUR measurement (the 'Fake' Coupler).\n\n(You can create this by measuring an IEM and clicking 'Save' in the Measurement tab).")
        my_file, _ = QFileDialog.getOpenFileName(self, "Open YOUR Measurement", "", "CSV Files (*.csv *.txt)")
        if not my_file: return
        
        # 2. Ask for pro measurement
        QMessageBox.information(self, "Step 2: Pro Measurement", "Select the PRO Measurement CSV (the 'True' Reference).\n\n(e.g., from the reference_targets folder).")
        pro_file, _ = QFileDialog.getOpenFileName(self, "Open PRO Measurement", "reference_targets", "CSV Files (*.csv *.txt)")
        if not pro_file: return
        
        try:
            # Load both
            my_data = np.genfromtxt(my_file, delimiter=',', skip_header=1)
            pro_data = np.genfromtxt(pro_file, delimiter=',', skip_header=1)
            
            my_f, my_m = my_data[:, 0], my_data[:, 1]
            pro_f, pro_m = pro_data[:, 0], pro_data[:, 1]
            
            # Interpolate Pro to match My frequencies
            pro_m_interp = np.interp(my_f, pro_f, pro_m)
            
            # Align volume at 500Hz
            idx_500 = (np.abs(my_f - 500)).argmin()
            volume_diff = pro_m_interp[idx_500] - my_m[idx_500]
            my_m_aligned = my_m + volume_diff
            
            # Calculate difference (Pro - My)
            cal_curve = pro_m_interp - my_m_aligned
            
            # Save it
            os.makedirs("calibrations", exist_ok=True)
            out_path = os.path.join("calibrations", "Auto_Generated_Fake711_Cal.txt")
            
            with open(out_path, "w") as out:
                out.write("Frequency,Amplitude\n")
                for f, m in zip(my_f, cal_curve):
                    if f >= 20 and f <= 20000:
                        out.write(f"{f:.2f},{m:.4f}\n")
                        
            QMessageBox.information(self, "Success!", f"Calibration generated successfully!\nSaved to: {out_path}\n\nIt has been automatically loaded.")
            self.parse_file(out_path)
            self.calibration_applied.emit(out_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate calibration:\n{str(e)}")
            

    def parse_file(self, file_name):
        self.freqs = []
        self.amps = []
        try:
            with open(file_name, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            freq = float(parts[0])
                            amp = float(parts[1])
                            self.freqs.append(freq)
                            self.amps.append(amp)
                        except ValueError:
                            continue
                            
            if self.freqs and self.amps:
                self.plot_curve()
                self.apply_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "No valid calibration data found in file.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            
    def plot_curve(self):
        self.plot_widget.clear()
        import numpy as np
        f_log = self.freqs
        self.plot_widget.plot(f_log, self.amps, pen=pg.mkPen(theme.get_color('accent'), width=2))
        
    def apply_calibration(self):
        if not hasattr(self, 'current_file') or not self.current_file:
            return
            
        import os
        import shutil
        
        cal_dir = "calibrations"
        os.makedirs(cal_dir, exist_ok=True)
        
        filename = os.path.basename(self.current_file)
        dest_path = os.path.join(cal_dir, filename)
        
        if self.current_file != dest_path:
            try:
                shutil.copy2(self.current_file, dest_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save calibration: {e}")
                return
                
        self.calibration_applied.emit(dest_path)
        QMessageBox.information(self, "Success", f"Calibration '{filename}' saved and applied!")