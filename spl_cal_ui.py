"""
spl_cal_ui.py – SPL Gain Calibration Tab for InEar Snitch
=======================================================

Workflow:
  1. User plays a reference tone (94 dB SPL, 1 kHz) into the measurement mic
     using a pistonphone / sound-level calibrator.
  2. App captures 1 second of audio from the selected input device.
  3. App computes the RMS level of the captured signal and derives the
     sensitivity offset: spl_offset = ref_spl - measured_rms_dbfs
  4. This offset is stored and emitted so AudioEngine can shift all
     measurements into absolute dB SPL.

If no calibrator is available the user can enter the offset manually
from the microphone datasheet.
"""

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QFrame, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal


class SPLCaptureWorker(QThread):
    """Captures 1 second of audio and emits the RMS dBFS value."""
    result = Signal(float)
    error  = Signal(str)

    def __init__(self, in_device_idx, sample_rate=48000, duration=1.0):
        super().__init__()
        self.in_device_idx = in_device_idx
        self.sample_rate = sample_rate
        self.duration = duration

    def run(self):
        try:
            import sounddevice as sd
            frames = int(self.sample_rate * self.duration)
            data = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=1,
                device=self.in_device_idx,
                dtype='float32',
                blocking=True
            )
            rms = float(np.sqrt(np.mean(data ** 2)))
            if rms < 1e-9:
                self.error.emit("Signal too weak – is the microphone connected and the calibrator active?")
                return
            rms_dbfs = 20 * np.log10(rms)
            self.result.emit(rms_dbfs)
        except Exception as e:
            self.error.emit(str(e))


class SPLCalibrationWidget(QWidget):
    """
    Emits spl_offset_changed(float) whenever a new SPL offset is confirmed.
    dB SPL = dBFS_measurement + spl_offset_db
    """
    spl_offset_changed = Signal(float)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #18181b; color: white;")
        self.spl_offset_db = 0.0
        self._in_device_idx = None
        self._capture_worker = None

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("SPL / Gain Calibration")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00FFFF;")
        layout.addWidget(title)

        desc = QLabel(
            "Calibrate the absolute SPL reference of your measurement chain.\n"
            "This ensures that 94 dB on the graph equals 94 dB SPL in reality.\n\n"
            "You need: a pistonphone or sound-level calibrator producing 94 dB SPL @ 1 kHz."
        )
        desc.setStyleSheet("color: #888; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Status frame
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(
            "background-color: #222; border-radius: 8px; padding: 10px;"
        )
        status_layout = QVBoxLayout(self.status_frame)
        self.offset_lbl = QLabel("Current SPL Offset: 0.0 dB  (uncalibrated)")
        self.offset_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFBB00;")
        status_layout.addWidget(self.offset_lbl)
        self.formula_lbl = QLabel("Formula: dB SPL = dBFS + 0.0")
        self.formula_lbl.setStyleSheet("font-size: 11px; color: #888;")
        status_layout.addWidget(self.formula_lbl)
        layout.addWidget(self.status_frame)

        # Method A
        sep_a = QLabel("METHOD A – Auto-Capture (Recommended)")
        sep_a.setStyleSheet("font-size: 13px; font-weight: bold; color: #00FFFF; margin-top: 10px;")
        layout.addWidget(sep_a)

        method_a_desc = QLabel(
            "1. Hold the pistonphone / calibrator to the measurement mic.\n"
            "2. Make sure the correct Input Device is selected in Routing.\n"
            "3. Click Capture Reference Level."
        )
        method_a_desc.setStyleSheet("color: #aaa; font-size: 12px;")
        method_a_desc.setWordWrap(True)
        layout.addWidget(method_a_desc)

        self.ref_spl_spin = QDoubleSpinBox()
        self.ref_spl_spin.setRange(80.0, 120.0)
        self.ref_spl_spin.setValue(94.0)
        self.ref_spl_spin.setSuffix("  dB SPL (reference tone level)")
        self.ref_spl_spin.setDecimals(1)
        self.ref_spl_spin.setStyleSheet(
            "background: #111; color: white; padding: 5px; "
            "border: 1px solid #333; border-radius: 4px; font-size: 13px;"
        )
        layout.addWidget(self.ref_spl_spin)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background: #111; border-radius: 4px; height: 6px; }"
            "QProgressBar::chunk { background: #00FFFF; border-radius: 4px; }"
        )
        layout.addWidget(self.progress_bar)

        self.btn_capture = QPushButton("Capture Reference Level (1 sec)")
        self.btn_capture.setToolTip("Capture and calibrate standard SPL reference")
        self.btn_capture.setStyleSheet(
            "background-color: #006666; color: white; font-weight: bold; "
            "padding: 10px; border-radius: 4px; font-size: 14px;"
        )
        self.btn_capture.setCursor(Qt.PointingHandCursor)
        self.btn_capture.clicked.connect(self._start_capture)
        layout.addWidget(self.btn_capture)

        # Method B
        sep_b = QLabel("METHOD B – Manual Entry")
        sep_b.setStyleSheet("font-size: 13px; font-weight: bold; color: #00FFFF; margin-top: 10px;")
        layout.addWidget(sep_b)

        method_b_desc = QLabel(
            "Enter the sensitivity offset manually (from mic datasheet or external SPL meter).\n"
            "Typical values range from +94 dB (0 dBFS = 1 Pa) to +130 dB."
        )
        method_b_desc.setStyleSheet("color: #aaa; font-size: 12px;")
        method_b_desc.setWordWrap(True)
        layout.addWidget(method_b_desc)

        manual_row = QHBoxLayout()
        self.manual_spin = QDoubleSpinBox()
        self.manual_spin.setRange(-20.0, 200.0)
        self.manual_spin.setValue(0.0)
        self.manual_spin.setSuffix("  dB offset")
        self.manual_spin.setDecimals(2)
        self.manual_spin.setStyleSheet(
            "background: #111; color: white; padding: 5px; "
            "border: 1px solid #333; border-radius: 4px; font-size: 13px;"
        )
        manual_row.addWidget(self.manual_spin, stretch=3)

        btn_apply_manual = QPushButton("Apply Manual Offset")
        btn_apply_manual.setToolTip("Apply a manual SPL calibration offset")
        btn_apply_manual.setStyleSheet(
            "background-color: #333; color: white; padding: 8px 14px; "
            "border-radius: 4px; font-size: 12px;"
        )
        btn_apply_manual.setCursor(Qt.PointingHandCursor)
        btn_apply_manual.clicked.connect(self._apply_manual)
        manual_row.addWidget(btn_apply_manual, stretch=1)
        layout.addLayout(manual_row)

        btn_reset = QPushButton("Reset to Uncalibrated (0 dB offset)")
        btn_reset.setToolTip("Reset SPL calibration to 0 dB offset")
        btn_reset.setStyleSheet(
            "background-color: transparent; color: #888; "
            "padding: 6px; border: 1px solid #444; border-radius: 4px; font-size: 11px;"
        )
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.clicked.connect(self._reset)
        layout.addWidget(btn_reset)

        layout.addStretch()

    def set_input_device(self, device_idx):
        self._in_device_idx = device_idx

    def get_spl_offset(self):
        return self.spl_offset_db

    def _apply_offset(self, offset_db, source="calibrator"):
        self.spl_offset_db = offset_db
        color = "#00FF99" if abs(offset_db) > 0.1 else "#FFBB00"
        status_word = "CALIBRATED" if abs(offset_db) > 0.1 else "uncalibrated"
        self.offset_lbl.setText(f"Current SPL Offset: {offset_db:+.2f} dB  ({status_word})")
        self.offset_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
        self.formula_lbl.setText(
            f"Formula: dB SPL = dBFS + ({offset_db:+.2f})    [source: {source}]"
        )
        self.spl_offset_changed.emit(offset_db)

    def _start_capture(self):
        if self._in_device_idx is None:
            QMessageBox.warning(self, "No Input Device",
                "Please select an Input Device in the Routing tab first.")
            return
        self.btn_capture.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._capture_worker = SPLCaptureWorker(self._in_device_idx)
        self._capture_worker.result.connect(self._on_capture_result)
        self._capture_worker.error.connect(self._on_capture_error)
        self._capture_worker.start()

    def _on_capture_result(self, rms_dbfs):
        self.progress_bar.setVisible(False)
        self.btn_capture.setEnabled(True)
        ref_spl = self.ref_spl_spin.value()
        offset = ref_spl - rms_dbfs
        msg = (
            f"Captured signal RMS: {rms_dbfs:.2f} dBFS\n"
            f"Reference tone: {ref_spl:.1f} dB SPL\n\n"
            f"Computed SPL offset: {offset:+.2f} dB\n\n"
            f"Apply this calibration?"
        )
        reply = QMessageBox.question(self, "SPL Calibration Result", msg,
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._apply_offset(offset, source="auto-capture")
            self.manual_spin.setValue(offset)

    def _on_capture_error(self, err):
        self.progress_bar.setVisible(False)
        self.btn_capture.setEnabled(True)
        QMessageBox.critical(self, "Capture Failed", f"Could not capture reference signal:\n{err}")

    def _apply_manual(self):
        offset = self.manual_spin.value()
        self._apply_offset(offset, source="manual")
        QMessageBox.information(self, "Manual Offset Applied",
            f"SPL offset set to {offset:+.2f} dB.\nAll measurements will be shifted accordingly.")

    def _reset(self):
        self._apply_offset(0.0, source="reset")
        self.manual_spin.setValue(0.0)
