import re

with open('main.py', 'r') as f:
    content = f.read()

logic_code = """
    def toggle_live_seal(self, checked):
        from PyQt5.QtWidgets import QMessageBox
        if checked:
            if self.selected_in_idx is None or self.selected_out_idx is None:
                QMessageBox.critical(self, "Hardware Not Configured", "Audio Interface not configured!")
                self.btn_live_seal.setChecked(False)
                return
            
            cal_f, cal_m = None, None
            cal_path = self.mic_cal_combo.currentData()
            if cal_path:
                try:
                    import numpy as np
                    data = np.genfromtxt(cal_path, invalid_raise=False)
                    if data.ndim > 1 and data.shape[1] >= 2:
                        cal_f = data[:, 0]
                        cal_m = data[:, 1]
                except Exception:
                    pass

            self.sub_lbl.setText("Status: LIVE SEAL CHECK (Pink Noise)")
            self.sub_lbl.setStyleSheet("color: #db2777; font-size: 13px; font-weight: bold;")
            self.btn_capture.setEnabled(False)
            
            # Setup plot line for RTA
            if not hasattr(self, 'live_rta_line'):
                import pyqtgraph as pg
                self.live_rta_line = pg.PlotCurveItem(pen=pg.mkPen('#db2777', width=2))
                self.plot_widget.addItem(self.live_rta_line)
            self.live_rta_line.show()
            
            self.live_worker = LiveSealWorker(self.selected_in_idx, self.selected_out_idx, cal_f, cal_m)
            self.live_worker.update_signal.connect(self.update_live_rta)
            self.live_worker.error.connect(self.on_measurement_error)
            self.live_worker.start()
        else:
            if hasattr(self, 'live_worker'):
                self.live_worker.stop()
                self.live_worker.wait()
            if hasattr(self, 'live_rta_line'):
                self.live_rta_line.hide()
            self.sub_lbl.setText("Status: Ready")
            self.sub_lbl.setStyleSheet("color: #a1a1aa; font-size: 12px;")
            self.btn_capture.setEnabled(True)

    def update_live_rta(self, freqs, mag_db):
        import numpy as np
        # Only plot 20 Hz to 20 kHz
        mask = (freqs >= 20) & (freqs <= 20000)
        # Shift magnitude so it looks visually comparable to the target (around 80-90dB)
        # Pink noise RTA raw FFT values usually sit very low depending on blocksize.
        # We find the mean around 1kHz and shift it to 85dB.
        idx_1k = (np.abs(freqs - 1000)).argmin()
        shift = 85.0 - mag_db[idx_1k]
        self.live_rta_line.setData(freqs[mask], mag_db[mask] + shift)

    def run_measurement(self):"""

content = content.replace("    def run_measurement(self):", logic_code)

with open('main.py', 'w') as f:
    f.write(content)
