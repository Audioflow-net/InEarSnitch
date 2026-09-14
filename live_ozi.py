import sys
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton
from PySide6.QtCore import QTimer

class LiveOzi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Ozi & RTA (Bass-Detektor)")
        self.resize(1000, 700)
        
        w = QWidget()
        self.setCentralWidget(w)
        layout = QVBoxLayout(w)
        
        # Device Selector
        self.combo = QComboBox()
        self.devices = [d for d in sd.query_devices() if d['max_input_channels'] > 0]
        for idx, d in enumerate(self.devices):
            self.combo.addItem(f"[{idx}] {d['name']}", d['name'])
        layout.addWidget(self.combo)
        
        self.btn = QPushButton("Start Live View")
        self.btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #00FF99; color: black;")
        self.btn.clicked.connect(self.toggle)
        layout.addWidget(self.btn)
        
        # Waveform Plot
        self.plot_wave = pg.PlotWidget(title="Waveform (Zeit) - Puste oder kratze ans Mikro!")
        self.plot_wave.setYRange(-0.5, 0.5)
        self.plot_wave.showGrid(x=True, y=True, alpha=0.3)
        self.curve_wave = self.plot_wave.plot(pen=pg.mkPen('#00FF99', width=2))
        layout.addWidget(self.plot_wave)
        
        # Spectrum Plot
        self.plot_fft = pg.PlotWidget(title="Frequenzgang (Bass ist GANZ LINKS bei 20-100 Hz)")
        self.plot_fft.setLogMode(x=True, y=False)
        self.plot_fft.setYRange(-100, 0)
        self.plot_fft.setXRange(np.log10(10), np.log10(20000))
        self.plot_fft.showGrid(x=True, y=True, alpha=0.3)
        self.curve_fft = self.plot_fft.plot(pen=pg.mkPen('#FF0055', width=2))
        layout.addWidget(self.plot_fft)
        
        self.stream = None
        self.fs = 48000
        self.chunk = 4096
        self.audio_data = np.zeros(self.chunk)
        
        # GUI Update Timer (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        
    def toggle(self):
        if self.stream is None:
            dev_name = self.combo.currentData()
            try:
                self.stream = sd.InputStream(samplerate=self.fs, channels=1, device=dev_name, 
                                             blocksize=self.chunk, callback=self.audio_cb)
                self.stream.start()
                self.btn.setText("STOP")
                self.btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #FF0055; color: white;")
                self.timer.start(30)
            except Exception as e:
                self.btn.setText(f"Error: {e}")
        else:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.timer.stop()
            self.btn.setText("Start Live View")
            self.btn.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #00FF99; color: black;")
            
    def audio_cb(self, indata, frames, time, status):
        # Kopiere die Daten in den Buffer
        self.audio_data = indata[:, 0].copy()
        
    def update_plots(self):
        # Update Waveform
        self.curve_wave.setData(self.audio_data)
        
        # Update FFT (RTA)
        window = np.hanning(len(self.audio_data))
        fft_res = np.fft.rfft(self.audio_data * window)
        freqs = np.fft.rfftfreq(len(self.audio_data), 1 / self.fs)
        
        mag = 20 * np.log10(np.abs(fft_res) + 1e-12)
        
        valid = freqs > 5
        self.curve_fft.setData(freqs[valid], mag[valid])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LiveOzi()
    win.show()
    sys.exit(app.exec())
