import sys
import os

# --- PATH RESOLUTION FOR STANDALONE APP ---
if getattr(sys, 'frozen', False):
    home = os.path.expanduser("~")
    app_dir = os.path.join(home, "Documents", "InEarSnitch")
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir)
        except Exception:
            pass
    # Set the working directory to the user's documents folder
    # so all relative paths (inearsnitch.db, reference_targets, etc) are saved there.
    os.chdir(app_dir)
    
    # Sync bundled files from the PyInstaller payload to the Documents folder
    import shutil
    import glob
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        # 1. Sync manual files (always overwrite with latest)
        #    Also create MANUAL.md (= English version) which the browser looks for.
        for manual in glob.glob(os.path.join(meipass, "manual_*.md")):
            shutil.copy2(manual, app_dir)
        # Create MANUAL.md as the English version so the in-app browser finds it
        manual_en_src = os.path.join(meipass, "manual_en.md")
        manual_en_dst = os.path.join(app_dir, "manual_en.md")
        if os.path.exists(manual_en_dst):
            shutil.copy2(manual_en_dst, os.path.join(app_dir, "MANUAL.md"))
        elif os.path.exists(manual_en_src):
            shutil.copy2(manual_en_src, os.path.join(app_dir, "MANUAL.md"))

        def _sync_dir(src, dst):
            """Copy files from src to dst recursively, file-by-file.
            More robust than shutil.copytree on Windows with special chars in filenames."""
            os.makedirs(dst, exist_ok=True)
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                try:
                    if os.path.isdir(s):
                        _sync_dir(s, d)
                    else:
                        shutil.copy2(s, d)
                except Exception:
                    pass  # Skip files that fail (permissions, long paths, etc.)

        # 2. Sync reference targets
        src_targets = os.path.join(meipass, "reference_targets")
        dst_targets = os.path.join(app_dir, "reference_targets")
        if os.path.exists(src_targets):
            _sync_dir(src_targets, dst_targets)

        # 3. Sync calibrations
        src_cals = os.path.join(meipass, "calibrations")
        dst_cals = os.path.join(app_dir, "calibrations")
        if os.path.exists(src_cals):
            _sync_dir(src_cals, dst_cals)
# ------------------------------------------

import theme
import traceback
import numpy as np
import pyqtgraph as pg
import time
import config
from PySide6.QtWidgets import (QApplication, QMainWindow, QButtonGroup, QSizePolicy, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QComboBox, 
                               QSplitter, QFrame, QLineEdit, QInputDialog,
                               QStackedWidget, QMessageBox, QGridLayout, QFileDialog, QScrollArea)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QTimer, QEvent
from PySide6.QtGui import QColor, QFont
import sqlite3
import numpy as np
import sounddevice as sd
from scipy.signal import fftconvolve
import pyqtgraph as pg

from analysis_ui import AnalysisWidget
from calibration_ui import CalibrationWidget

from PySide6.QtCore import QObject, Signal

class LogStream(QObject):
    message_written = Signal(str, bool)

    def __init__(self, original_stream, is_error=False):
        super().__init__()
        self.original_stream = original_stream
        self.is_error = is_error

    def write(self, text):
        self.original_stream.write(text)
        if text.strip() != "":
            self.message_written.emit(text, self.is_error)

    def flush(self):
        self.original_stream.flush()

# Set pyqtgraph global config before importing other UI components
pg.setConfigOption('background', '#18181b')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('antialias', True)  # Smoother curves
pg.setConfigOption('useOpenGL', False) # Disable OpenGL to prevent macOS crashes, software rendering is extremely fast in Qt6 anyway

# Global performance tweaks for pyqtgraph
pg.setConfigOption('useCupy', False)
pg.setConfigOption('useNumba', False)


class FreqAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if not values:
            return []
            
        strings = []
        # Check if we are zoomed out (range covers more than 1 decade)
        is_zoomed_out = (max(values) - min(values)) >= 0.9
        allowed_labels = {20, 30, 40, 50, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000}
        
        for v in values:
            hz = int(round(10**v))
            
            # If zoomed out, skip cluttered intermediate labels
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

def style_button(btn, base_bg, text_col, hover_bg, pressed_bg, bold=False):
    fw = "bold" if bold else "normal"
    btn.setStyleSheet(f"""
        QPushButton {{ background-color: {base_bg}; color: {text_col}; font-weight: {fw}; padding: 8px 16px; border-radius: 4px; border: none; }}
        QPushButton:hover {{ background-color: {hover_bg}; }}
        QPushButton:pressed {{ background-color: {pressed_bg}; }}
        QPushButton:disabled {{ background-color: #333; color: #666; }}
    """)

def log_debug(msg):
    with open("app_debug.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

def global_exception_handler(exctype, value, tb):
    err = "".join(traceback.format_exception(exctype, value, tb))
    log_debug(f"CRASH: {err}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_exception_handler

from audio_engine import AudioEngine
from database import DatabaseManager
from analysis import Analyzer
from dialogs import AddProfileDialog

from PySide6.QtCore import Signal
class AvatarButton(QLabel):
    def __init__(self, iem_id, iem_name, pic_path, abbr, color, parent_card):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.iem_id = iem_id
        self.iem_name = iem_name
        self.abbr = abbr
        self.color = color if color else "#2a2a2a"
        self.parent_card = parent_card
        self.has_pic = False
        self.update_style(False)
        
        self.setFixedSize(36, 36)
        self.setToolTip(iem_name)
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        self.setFocusPolicy(Qt.NoFocus)
        
        if pic_path:
            from PySide6.QtGui import QImageReader, QPixmap
            from PySide6.QtCore import QSize
            from profile_ui import create_circular_pixmap
            reader = QImageReader(pic_path)
            reader.setAutoTransform(True)
            circ = create_circular_pixmap(reader, 36)
            if circ:
                self.setPixmap(circ)
                self.has_pic = True
            else:
                self.set_abbr_text()
        else:
            self.set_abbr_text()
            
    def set_abbr_text(self):
        if self.abbr:
            text = self.abbr[:2].upper()
        else:
            parts = self.iem_name.split()
            if len(parts) >= 2:
                text = (parts[0][0] + parts[1][0]).upper()
            else:
                text = self.iem_name[:2].upper()
        self.setText(text)
            
        self.update_style(False)
        
    def _get_text_color_for_bg(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return "#000000" if luminance > 0.5 else "#ffffff"
        return "#ffffff"
        
    def update_style(self, selected):
        import theme
        
        if selected:
            bg = "transparent" if self.has_pic else ("#0284c7" if theme.CURRENT_MODE == "light" else "#00FFFF")
            text_col = "#ffffff" if theme.CURRENT_MODE == "light" else "#000000"
            border_col = "#0284c7" if theme.CURRENT_MODE == "light" else "#00FFFF"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; color: {text_col}; border: 2px solid {border_col}; border-radius: 18px; font-weight: bold; font-size: 14px; outline: none; }}")
        else:
            bg = "transparent" if self.has_pic else self.color
            text_col = "#ffffff" if self.has_pic else self._get_text_color_for_bg(self.color)
            border_col = "#e4e4e7" if theme.CURRENT_MODE == "light" else "#2d2d34"
            self.setStyleSheet(f"QLabel {{ background-color: {bg}; border: 2px solid {border_col}; border-radius: 18px; color: {text_col}; font-weight: bold; font-size: 14px; outline: none; }}")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent_card.select_iem(self.iem_id, self.iem_name, self)

class MusicianCard(QWidget):
    iem_changed = Signal()
    
    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(80, 80)
    
    def select_iem(self, iem_id, iem_name, btn):
        self.current_iem_id = iem_id
        self.current_iem_name = iem_name

        for b_id, b in self.avatar_btns:
            b.update_style(b_id == iem_id)
        self.iem_changed.emit()

    def on_menu_triggered(self, action):
        self.current_iem_id = action.data()
        self.current_iem_name = action.text().replace("", "")
        self.iem_btn.setText(f"{self.current_iem_name} ▾")
        self.iem_changed.emit()


    def __init__(self, name, role, iems, status="Ready", profile_pic=None):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 10, 8, 10)
        self.name = name
        
        self.avatar = QLabel()
        self.avatar.setFixedSize(60, 60)
        self.avatar.setFocusPolicy(Qt.NoFocus)
        
        if profile_pic:
            from PySide6.QtGui import QImageReader, QPixmap
            from profile_ui import create_circular_pixmap
            reader = QImageReader(profile_pic)
            reader.setAutoTransform(True)
            circ = create_circular_pixmap(reader, 60)
            if circ:
                self.avatar.setPixmap(circ)
                self.avatar.setStyleSheet("background-color: transparent; border: none; outline: none;")
            else:
                self.avatar.setStyleSheet("background-color: #444; border-radius: 30px; border: none; outline: none;")
        else:
            self.avatar.setStyleSheet("background-color: #444; border-radius: 30px; border: none; outline: none;")
        
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        self.name_lbl = QLabel(name)
        self.name_lbl.setProperty("class", "title")
        self.name_lbl.setStyleSheet("background-color: transparent; border: none; outline: none;")
        self.name_lbl.setFocusPolicy(Qt.NoFocus)
        self.name_lbl.setMinimumWidth(1)
        self.role_lbl = QLabel(role)
        self.role_lbl.setProperty("class", "subtitle")
        self.role_lbl.setStyleSheet("background-color: transparent; border: none; outline: none;")
        self.role_lbl.setFocusPolicy(Qt.NoFocus)
        self.role_lbl.setMinimumWidth(1)
        
        self.bottom_info = QHBoxLayout()
        self.bottom_info.setContentsMargins(0, 0, 0, 0)
        self.bottom_info.setSpacing(4)
        
        self.iems_data = iems
        self.current_iem_id = iems[0][0] if iems else -1
        self.current_iem_name = (iems[0][4] if (iems and len(iems[0])>4 and iems[0][4]) else iems[0][1]) if iems else "Unknown IEM"
        
        self.avatar_btns = []
        from PySide6.QtGui import QImageReader, QIcon, QPixmap
        from PySide6.QtCore import QSize
        from profile_ui import create_circular_pixmap
        from PySide6.QtWidgets import QGridLayout
        self.avatars_container = QWidget()
        self.avatars_container.setStyleSheet("background-color: transparent; border: none;")
        self.avatars_layout = QGridLayout(self.avatars_container)
        self.avatars_layout.setContentsMargins(0, 0, 0, 0)
        self.avatars_layout.setSpacing(4)
        
        row, col = 0, 0
        for item in iems:
            if len(item) == 6:
                iem_id, iem_name, pic_path, abbr, custom_name, color = item
            else:
                iem_id, iem_name, pic_path, abbr, custom_name = item
                color = "#2a2a2a"
            display_name = custom_name if custom_name else iem_name
            btn = AvatarButton(iem_id, display_name, pic_path, abbr, color, self)
            self.avatar_btns.append((iem_id, btn))
            self.avatars_layout.addWidget(btn, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
            
        self.bottom_info.addWidget(self.avatars_container)
            
        self.bottom_info.addStretch()
        
        if self.avatar_btns:
            self.select_iem(self.current_iem_id, self.current_iem_name, self.avatar_btns[0][1])

        
        info_layout.addWidget(self.name_lbl)
        info_layout.addWidget(self.role_lbl)
        info_layout.addLayout(self.bottom_info)
        
        self.layout.addWidget(self.avatar)
        self.layout.addLayout(info_layout)
        
        self.setObjectName("musicianCardObj")
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        
        for child in [self.avatar, self.name_lbl, self.role_lbl]:
            child.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            
        self._update_layout(self.width())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout(event.size().width())
        
    def _update_layout(self, width):
        from PySide6.QtWidgets import QBoxLayout
        # print(f"MusicianCard width: {width}")
        if width < 200:
            self.avatar.hide()
            self.role_lbl.hide()
            self.layout.setDirection(QBoxLayout.TopToBottom)
            self.name_lbl.setAlignment(Qt.AlignCenter)
        else:
            self.avatar.show()
            self.role_lbl.show()
            self.layout.setDirection(QBoxLayout.LeftToRight)
            self.name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        import theme
        if theme.CURRENT_MODE == "light":
            self.setStyleSheet("#musicianCardObj { background-color: #ffffff; border-radius: 8px; border: none; outline: none; }")
        else:
            self.setStyleSheet("#musicianCardObj { background-color: #2d2d34; border-radius: 8px; border: none; outline: none; }")
        # AvatarButtons keep their own click handlers (select_iem)

from PySide6.QtCore import QObject

class MeasurementAnimator(QObject):
    def __init__(self, plot_widget):
        super().__init__()
        import math
        self.plot_widget = plot_widget
        
        # 1. Sweep Region (Schatten hinter dem Laser)
        self.region = pg.LinearRegionItem([math.log10(20), math.log10(20)], brush=pg.mkBrush((0, 255, 255, 30)), pen=None, movable=False)
        self.region.hide()
        self.plot_widget.addItem(self.region)
        
        # 2. Laser Line
        self.sweep_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(theme.get_color('accent'), width=4))
        self.sweep_line.hide()
        self.plot_widget.addItem(self.sweep_line)
        
        # 3. HUD Text
        self.lbl = pg.TextItem(html='', anchor=(0.5, 0.5))
        self.lbl.setZValue(100)
        self.lbl.hide()
        self.lbl.setParentItem(self.plot_widget.getViewBox())
        
        self.lbl_sub = pg.TextItem(html='', anchor=(0.5, 0.5))
        self.lbl_sub.setZValue(100)
        self.lbl_sub.hide()
        self.lbl_sub.setParentItem(self.plot_widget.getViewBox())
        
        self.sweeps = 1
        
    def start(self, sweeps):
        self.sweeps = sweeps
        self.last_sweep_num = None
        self.region.show()
        self.sweep_line.show()
        self.lbl.show()
        
        vb = self.plot_widget.getViewBox()
        rect = vb.boundingRect()
        self.lbl.setPos(rect.width()/2, rect.height()/2 - 40)
        self.lbl_sub.setPos(rect.width()/2, rect.height()/2 + 40)
        
        self.set_text("SCANNING")
        
    def set_text(self, txt, sub_txt=""):
        accent = theme.get_color('accent')
        self.lbl.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: {accent}; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;"><center>{txt}</center></div>')
        if sub_txt:
            self.lbl_sub.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: {accent}; font-weight: 900; letter-spacing: 5px;"><center>{sub_txt}</center></div>')
            self.lbl_sub.show()
        else:
            self.lbl_sub.hide()
        
    def update_anim_sync(self, t_elapsed, sweep_num):
        import math
        
        # Center the HUD text dynamically
        vb = self.plot_widget.getViewBox()
        if not vb:
            return
            
        rect = vb.boundingRect()
        if getattr(self, 'last_rect', None) != rect:
            if self.sweeps > 1:
                self.lbl.setPos(rect.width()/2, rect.height()/2 - 40)
                self.lbl_sub.setPos(rect.width()/2, rect.height()/2 + 40)
            else:
                self.lbl.setPos(rect.width()/2, rect.height()/2)
            self.last_rect = rect
            
        if self.sweeps > 1:
            if getattr(self, 'last_sweep_num', None) != sweep_num:
                self.set_text("SCANNING", f"{sweep_num} / {self.sweeps}")
                self.last_sweep_num = sweep_num
            
        if t_elapsed <= 1.0:
            freq = 20 * (1000 ** t_elapsed)
            # Clamp freq just in case
            freq = max(20, min(20000, freq))
            x_pos = math.log10(freq)
            self.sweep_line.setValue(x_pos)
            self.region.setRegion([math.log10(20), x_pos])
            self.sweep_line.show()
            self.region.show()
        else:
            self.sweep_line.hide()
            self.region.hide()
            
    def stop(self):
        self.sweep_line.hide()
        self.region.hide()
        self.lbl.hide()
        self.lbl_sub.hide()



class LiveSealWorker(QThread):
    update_signal = Signal(object, object)
    error = Signal(str)

    def __init__(self, in_idx, out_idx, cal_f=None, cal_m=None, target_channel="Left"):
        super().__init__()
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.target_channel = target_channel
        self.running = True
        self.fs = 48000
        self.blocksize = 8192

    def set_target_channel(self, target_channel):
        self.target_channel = target_channel

    def run(self):
        import sounddevice as sd
        import numpy as np
        from scipy import interpolate
        
        # Precompute Pink Noise Buffer (4 seconds to avoid obvious repeating patterns)
        N_noise = self.fs * 4
        X_white = np.fft.rfft(np.random.randn(N_noise))
        S = np.sqrt(np.arange(X_white.size) + 1.0)
        y = np.fft.irfft(X_white / S, n=N_noise)
        # Use calibrated amplitude if available, otherwise 0.15
        cal_amp = getattr(self, '_cal_amp', 0.15)
        pink_noise_full = (y / np.max(np.abs(y))) * cal_amp
        self.noise_idx = 0
        
        # Precompute frequencies and calibration curve
        freqs = np.fft.rfftfreq(self.blocksize, 1/self.fs)
        cal_offset = np.zeros_like(freqs)
        if self.cal_f is not None and self.cal_m is not None:
            interp_func = interpolate.interp1d(self.cal_f, self.cal_m, bounds_error=False, fill_value=0.0)
            cal_offset = interp_func(freqs)
            
        # Precompute Hanning window
        window = np.hanning(self.blocksize)

        def callback(indata, outdata, frames, time, status):
            if not self.running:
                raise sd.CallbackStop
            try:
                # Grab a chunk of precomputed pink noise
                end_idx = self.noise_idx + frames
                if end_idx <= N_noise:
                    pn = pink_noise_full[self.noise_idx:end_idx].copy()
                    self.noise_idx = end_idx
                else:
                    # Wrap around
                    pn = np.empty(frames)
                    rem = N_noise - self.noise_idx
                    pn[:rem] = pink_noise_full[self.noise_idx:]
                    pn[rem:] = pink_noise_full[:frames-rem]
                    self.noise_idx = frames - rem
                
                # Apply Hardware DSP if enabled
                from eq_math import dsp_engine
                if dsp_engine.master_enabled:
                    pn = dsp_engine.process(pn, self.fs)
                    
                if self.target_channel == "Left":
                    outdata[:, 0] = pn
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = 0.0
                else:
                    outdata[:, 0] = 0.0
                    if outdata.shape[1] > 1:
                        outdata[:, 1] = pn
                    
                sig = indata[:, 0].copy()
                sig_w = sig * window[:len(sig)] if len(sig) <= len(window) else sig * np.hanning(len(sig))
                
                mag = np.abs(np.fft.rfft(sig_w))
                # Simple smoothing
                kernel_size = 15
                kernel = np.ones(kernel_size) / kernel_size
                mag_smooth = np.convolve(mag, kernel, mode='same')
                
                mag_db = 20 * np.log10(mag_smooth + 1e-12)
                mag_db += cal_offset
                    
                self.update_signal.emit(freqs, mag_db)
            except Exception as e:
                print(f"[LiveSealWorker Error] {e}")
                self.error.emit(str(e))
                raise sd.CallbackAbort

        try:
            with sd.Stream(device=(self.in_idx, self.out_idx),
                           samplerate=self.fs, blocksize=self.blocksize,
                           channels=(1, 2), callback=callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))
            
    def stop(self):
        self.running = False

class MeasurementWorker(QThread):
    finished = Signal(object, object, object, object, str, object, object, object)
    error = Signal(str)
    progress = Signal(str)
    sweep_progress = Signal(float, int)

    def __init__(self, audio_engine, in_idx, out_idx, target_channel, cal_f=None, cal_m=None, sweeps=1, spl_offset_db=0.0):
        super().__init__()
        self.audio_engine = audio_engine
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.target_channel = target_channel
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.sweeps = sweeps
        self.spl_offset_db = spl_offset_db

    def run(self):
        try:
            import numpy as np
            import time
            mags, phases, irs, noises = [], [], [], []
            freqs = None
            
            self.progress.emit("Status: 🎤 Listening to room noise...")
            try:
                noise_f, noise_m = self.audio_engine.measure_noise_floor(self.in_idx, duration=0.5)
            except Exception as e:
                print(f"[NOISE] Floor measurement failed: {e}")
                noise_f, noise_m = None, None
                
            for i in range(self.sweeps):
                self.progress.emit(f"Status: MEASURING {self.target_channel}... ({i+1}/{self.sweeps})")
                res = self.audio_engine.measure(self.in_idx, self.out_idx, 
                                                target_channel=self.target_channel, 
                                                duration=1.0,
                                                mic_cal_freqs=self.cal_f,
                                                mic_cal_mags=self.cal_m,
                                                spl_offset_db=self.spl_offset_db,
                                                progress_callback=lambda t, s=i+1: self.sweep_progress.emit(t, s))
                freqs = res[0]
                mags.append(res[1])
                phases.append(res[2])
                irs.append(res[3])
                noises.append(res[4])
                if self.sweeps > 1 and i < self.sweeps - 1:
                    self.sweep_progress.emit(1.1, i+1) # Hide bar during sleep
                    time.sleep(1.0) # safely let PortAudio tear down the previous stream
            
            avg_mag = np.mean(mags, axis=0)
            avg_phase = np.mean(phases, axis=0)
            avg_ir = np.mean(irs, axis=0)
            avg_noise = np.mean(noises, axis=0)
            
            self.finished.emit(freqs, avg_mag, avg_phase, avg_ir, self.target_channel, avg_noise, noise_f, noise_m)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))  # Prints to stderr, which LogStream catches!
            self.error.emit(str(e))



class LogoTripleClickFilter(QObject):
    """
    Event filter for triple-click detection on the header logo/title label.
    Detects 3 rapid left-clicks within 600ms.
    Handles press and double-click sequences, ignores non-left clicks,
    resets after triggering, and prevents duplicate re-entrant dialogs.
    """
    def __init__(self, parent, on_triple_click_callback, max_interval=0.6):
        super().__init__(parent)
        self.callback = on_triple_click_callback
        self.max_interval = max_interval
        self.clicks = []
        self._dialog_active = False

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick):
            if event.button() == Qt.LeftButton:
                if self._dialog_active:
                    return False
                now = time.monotonic()
                if self.clicks and (now - self.clicks[-1]) > self.max_interval:
                    self.clicks = []
                self.clicks.append(now)
                if len(self.clicks) >= 3:
                    self.clicks = []
                    self._dialog_active = True
                    try:
                        self.callback()
                    finally:
                        self._dialog_active = False
                    return True
        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.setWindowTitle("InEar SNITCH PRO AUDIO DIAGNOSTICS")
        # Get screen size and adapt dynamically, or just maximize
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = screen.width() * 0.85, screen.height() * 0.85
        self.resize(int(w), int(h))
        
        # Center on screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
        self.audio_engine = AudioEngine()
        self.db = DatabaseManager()
        self.current_iem_id = None
        self.settings_panel = None
        self.selected_in_idx = 0
        self.selected_out_idx = 0
        self.is_measuring = False   # UI Hardening: guard flag during active sweep
        self.worker = None
        
        # Temporary buffers for L/R sequential measurements
        self.temp_freqs = None
        self.temp_mag_l = None
        self.temp_mag_r = None
        self.temp_phase_l = None
        self.temp_phase_r = None
        self.temp_ir_l = None
        self.temp_ir_r = None
        self.ref_freqs = None
        self.ref_mag_l = None
        self.ref_mag_r = None
        self.target_freqs = None
        self.target_mags = None
        self.spl_offset_db = 0.0  # populated by _load_settings()

        self.setup_ui()
        self.apply_theme()
        self.update_prokit_ui_visibility()

        # Keyboard shortcuts
        from PySide6.QtGui import QShortcut
        from PySide6.QtGui import QKeySequence

        QShortcut(QKeySequence("Space"), self).activated.connect(self.btn_capture.click)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_trace_to_db)
        QShortcut(QKeySequence("Cmd+S"), self).activated.connect(self.save_trace_to_db)
        QShortcut(QKeySequence("Backspace"), self).activated.connect(self.clear_trace)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.clear_trace)
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.switch_workspace_tab(0))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.switch_workspace_tab(2))
        
        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.switch_workspace_tab(3))
        
        # Delayed EULA check
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, self.check_eula)


    def check_eula(self):
        from PySide6.QtCore import QSettings
        from PySide6.QtWidgets import QMessageBox
        import sys
        
        s = QSettings("InEarSnitch", "InEarSnitchApp")
        if not s.value("eula_accepted", False, type=bool):
            msg = QMessageBox(self)
            msg.setWindowTitle("Health & Safety Warning")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("<b>WARNING: High-Level Sine Sweeps</b>")
            msg.setInformativeText(
                "This software generates loud, high-frequency audio sweeps which can cause <b>permanent hearing damage</b> "
                "if listened to directly, or <b>hardware damage</b> (blown drivers) if the output level is incorrectly staged.<br><br>"
                "• NEVER wear the In-Ear Monitors (IEMs) while running a measurement.<br>"
                "• ALWAYS double-check your audio interface output volume before clicking RUN.<br><br>"
                "By clicking 'Accept', you confirm you understand these risks and release the developers of InEar SNITCH from any liability regarding hearing loss or equipment damage.<br><br>"
                "This software does not provide medical or audiological advice. Measurement results are for informational purposes only and must not be used for medical diagnosis or treatment decisions."
            )
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
            msg.button(QMessageBox.Ok).setText("Accept")
            msg.button(QMessageBox.Abort).setText("Decline")
            
            ret = msg.exec()
            if ret == QMessageBox.Ok:
                s.setValue("eula_accepted", True)
                s.sync()
            else:
                sys.exit(0)

    def setup_ui(self):
        from PySide6.QtWidgets import QComboBox
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Hardcode a safe maximum size for 13" MacBooks to prevent it going off screen
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        
        # --- TOP BAR ---
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setObjectName("topBar")
        top_bar.setStyleSheet("#topBar { background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a; }")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("InEar SNITCH")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
        sublogo = QLabel("DIAGNOSTICS")
        sublogo.setStyleSheet("color: #666; font-size: 14px; margin-left: 10px;")
        top_layout.addWidget(logo)
        top_layout.addWidget(sublogo)
        
        # ProKit: Header logo references and triple-click unlock filter
        self.lbl_logo = logo
        self.lbl_title = logo
        self.lbl_sublogo = sublogo
        self.logo = logo
        self.sublogo = sublogo
        self.logo_triple_click_filter = LogoTripleClickFilter(
            self,
            self.prompt_prokit_unlock,
            max_interval=0.6
        )
        self.lbl_logo.installEventFilter(self.logo_triple_click_filter)
        self.lbl_sublogo.installEventFilter(self.logo_triple_click_filter)
        
        # Center the profile label
        top_layout.addStretch()
        

        
        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setToolTip("Toggle Light/Dark Mode")
        self.btn_theme.setStyleSheet("background-color: transparent; color: #888; font-size: 18px; border: none; margin-right: 15px;")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.clicked.connect(self.on_theme_toggle)
        top_layout.addWidget(self.btn_theme)
        

        self.btn_top_settings = QPushButton("Settings")
        self.btn_top_settings.setToolTip("Open application settings")
        self.btn_top_settings.setStyleSheet("background-color: transparent; color: #888; font-size: 14px; font-weight: bold; border: none;")
        def _toggle_settings():
            is_visible = self.settings_panel.isVisible()
            self.settings_panel.setVisible(not is_visible)
            if hasattr(self, 'settings_dimmer'):
                self.settings_dimmer.setVisible(not is_visible)
                if not is_visible:
                    self.settings_dimmer.raise_()
                    self.settings_panel.raise_()
            if not is_visible:
                # Reset panel to default width and button label when opening
                self.settings_panel.setMaximumWidth(600)
                if hasattr(self, 'btn_expand'):
                    self.btn_expand.setText("Expand")
                import PySide6.QtGui as QtGui
                self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))
        self.btn_top_settings.clicked.connect(_toggle_settings)

        top_layout.addWidget(self.btn_top_settings)

        
        main_layout.addWidget(top_bar)
        
        # --- MAIN CONTENT ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)
        
        # =========================================================
        # PAGE 0: WORKSPACE (Profiles + Measurement/Analysis/History)
        # =========================================================
        workspace_widget = QWidget()
        workspace_layout = QHBoxLayout(workspace_widget)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        # SIDEBAR 2 (Profiles)
        profile_bar = QWidget()
        profile_bar.setMinimumWidth(170)
        profile_bar.setMaximumWidth(280)
        profile_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        profile_bar.setObjectName("ProfileBar")
        profile_bar.setStyleSheet("#ProfileBar { background-color: #18181b; border-right: 1px solid #222; }")
        prof_layout = QVBoxLayout(profile_bar)
        prof_layout.setContentsMargins(15, 20, 15, 20)
        
        # Profile Header in Sidebar
        header = QFrame()
        header.setObjectName("ProfileHeader")
        header.setStyleSheet("#ProfileHeader { background-color: #222; border-radius: 8px; margin-bottom: 15px; }")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        header_layout.setAlignment(Qt.AlignCenter)
        
        self.header_pic = QLabel()
        self.header_pic.setFixedSize(80, 80)
        self.header_pic.setStyleSheet("background-color: #333; border-radius: 40px;")
        header_layout.addWidget(self.header_pic, alignment=Qt.AlignCenter)
        
        self.ses_lbl = QLabel("No Profile")
        self.ses_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 10px;")
        self.ses_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.ses_lbl)
        
        self.sub_lbl = QLabel("Select to begin")
        self.sub_lbl.setStyleSheet("color: #00FFFF; font-size: 12px;")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.sub_lbl)
        
        self.notes_lbl = QLabel("")
        self.notes_lbl.setStyleSheet("color: {theme.get_color(\"text_secondary\")}; font-size: 11px; font-style: italic;")
        self.notes_lbl.setWordWrap(True)
        self.notes_lbl.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.notes_lbl)
        
        prof_layout.addWidget(header)
        header.hide()
        
        lbl_prof = QLabel("MUSICIAN PROFILES")
        lbl_prof.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        prof_layout.addWidget(lbl_prof)
        
        search_box = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search...")
        search_input.setStyleSheet("background-color: #111; color: white; border: 1px solid #333; padding: 5px; border-radius: 4px;")
        btn_add_prof = QPushButton("+")
        btn_add_prof.setToolTip("Add a new profile")
        btn_add_prof.setFixedSize(25, 25)
        btn_add_prof.setStyleSheet("background-color: #008888; color: white; font-weight: bold; border-radius: 4px;")
        btn_add_prof.clicked.connect(self.open_add_profile_dialog)
        search_box.addWidget(search_input)
        search_box.addWidget(btn_add_prof)
        prof_layout.addLayout(search_box)
        
        self.profile_scroll = QScrollArea()
        self.profile_scroll.setWidgetResizable(True)
        self.profile_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.profile_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.profile_list_container = QWidget()
        self.profile_list_layout = QVBoxLayout(self.profile_list_container)
        self.profile_list_layout.setAlignment(Qt.AlignTop)
        self.profile_list_layout.setContentsMargins(0, 0, 0, 0)
        self.profile_list_layout.setSpacing(5)
        self.profile_scroll.setWidget(self.profile_list_container)
        prof_layout.addWidget(self.profile_scroll)
        self.profile_cards = []
        
        workspace_layout.addWidget(profile_bar, stretch=0)

        # RIGHT CONTENT (Tabs + Active Profile Workspace)
        right_content = QWidget()
        right_content.setStyleSheet("background-color: #1f1f23;")
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(30, 0, 30, 20)  # Top margin set to 0 to push tabs up
        
        # Profile Tabs
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(20)
        
        self.btn_nav_prof = QPushButton("PROFILE")
        self.btn_nav_prof.setToolTip("Navigate to Profile view")
        self.btn_nav_ana = QPushButton("WORKSPACE")
        self.btn_nav_ana.setToolTip("Navigate to Analysis view")
        self.btn_nav_hist = QPushButton("HISTORY")
        self.btn_nav_hist.setToolTip("Navigate to History view")
        
        self.style_tab(self.btn_nav_prof, False)
        self.style_tab(self.btn_nav_ana, True)
        self.style_tab(self.btn_nav_hist, False)
        
        # Order requested: Workspace, History, Profile
        # Align left to anchor them visually with the Freq Response tabs below
        nav_layout.addWidget(self.btn_nav_ana)
        nav_layout.addWidget(self.btn_nav_hist)
        nav_layout.addWidget(self.btn_nav_prof)
        nav_layout.addStretch()  # Stretch after to push to left
        
        right_layout.addWidget(nav_container)
        
        right_layout.addSpacing(20)  # Add back the 20px gap before the graph area
        
        # Workspace Stacked
        self.workspace_stacked = QStackedWidget()
        right_layout.addWidget(self.workspace_stacked)
        
        workspace_layout.addWidget(right_content, stretch=1)
        content_layout.addWidget(workspace_widget, stretch=1)
        
        # =========================================================
        # TAB PAGES FOR WORKSPACE STACKED
        # =========================================================
        
        # --- PROFILE PAGE ---
        try:
            from profile_ui import ProfileWidget
            self.page_prof = ProfileWidget()
            self.page_prof.profile_updated.connect(self.on_profile_data_changed)
            self.page_prof.profile_data_saved.connect(self.on_profile_data_saved_only)
            self.page_prof.load_measurement_requested.connect(self.handle_measure_requested)
            
            # Connect the new deleted signal so the list refreshes
            if hasattr(self.page_prof, 'profile_deleted'):
                self.page_prof.profile_deleted.connect(self.load_profiles_from_db)
                
            self.workspace_stacked.addWidget(self.page_prof)
        except ImportError:
            self.page_prof = QLabel("Profile Widget building...")
            self.page_prof.setStyleSheet("color: white;")
            self.workspace_stacked.addWidget(self.page_prof)
            
        # --- MEASUREMENT PAGE ---
        page_meas = QWidget()
        meas_layout = QVBoxLayout(page_meas)
        meas_layout.setContentsMargins(0, 0, 0, 0)
        
        # TOP HEADER (Smooth & Reset Zoom)
        meas_top_h = QHBoxLayout()
        meas_top_h.setContentsMargins(0, 0, 0, 10)
        
        lbl_meas_title = QLabel("Measurement Studio")
        lbl_meas_title.setProperty("class", "card-title")
        meas_top_h.addWidget(lbl_meas_title)
        
        meas_top_h.addStretch()
        
        lbl_smooth = QLabel("Smooth:")
        lbl_smooth.setProperty("class", "subtitle")
        lbl_smooth.style().unpolish(lbl_smooth)
        lbl_smooth.style().polish(lbl_smooth)
        meas_top_h.addWidget(lbl_smooth)
        
        self.cb_smooth = QComboBox()
        self.cb_smooth.setMinimumWidth(110)
        self.cb_smooth.addItems(["1/24 Oct", "1/48 Oct", "1/12 Oct", "1/6 Oct", "Raw"])
        self.cb_smooth.currentIndexChanged.connect(self.on_smooth_changed)
        meas_top_h.addWidget(self.cb_smooth)
        
        self.btn_reset_view = QPushButton("AUTOZOOM")
        self.btn_reset_view.setToolTip("Autozoom graph to fit curves")
        self.btn_reset_view.setMinimumWidth(90)
        self.btn_reset_view.setStyleSheet("QPushButton { background-color: #222; color: white; border: 1px solid #444; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #333; }")
        self.btn_reset_view.clicked.connect(self.reset_graph_view)
        meas_top_h.addWidget(self.btn_reset_view)
        
        meas_layout.addLayout(meas_top_h)

        

        
        import pyqtgraph as pg
        from main import FreqAxisItem
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        import numpy as np
        import pyqtgraph as pg
        self.plot_widget.setBackground(theme.get_color('pg_bg'))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLabel('left', 'Magnitude dB SPL')
        self.plot_widget.setLabel('bottom', 'Frequency Hz')
        self.plot_widget.setLogMode(x=True, y=False)
        self.meas_overlay = MeasurementAnimator(self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget)
        
        self.plot_widget.addLegend(offset=(20, 20))
        self.plot_widget.setYRange(40, 120)
        
        # Hard lock X-axis from 20 Hz to 20 kHz
        self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0)
        self.plot_widget.setLimits(xMin=np.log10(20), xMax=np.log10(20000))
        self.plot_widget.getViewBox().disableAutoRange(axis=pg.ViewBox.XAxis)
        self.plot_widget.getViewBox().disableAutoRange(axis=pg.ViewBox.YAxis)
        self.plot_widget.setLimits(yMin=20, yMax=140)
        self.plot_widget.hideButtons()
        meas_layout.addWidget(self.plot_widget, stretch=1)
        
        import pyqtgraph as pg
        self.watermark_item = pg.TextItem(html=f'<div style="color: {theme.get_color("watermark")}; font-size: 32px; font-weight: bold; line-height: 1.2;"><center>NO PROFILE<br>Left</center></div>', anchor=(1, 0))
        # Wait, self.page_ana isn't created yet here! We will move this assignment below page_ana creation.
        
        # BOTTOM CONTROLS (Professional Toolbar Layout)
        self.control_panel = QFrame()
        self.control_panel.setObjectName("ControlPanel")
        self.control_panel.setStyleSheet("#ControlPanel { background-color: #222; border: 1px solid #444; border-radius: 4px; }")
        self.control_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setContentsMargins(15, 12, 15, 12)
        control_layout.setSpacing(20)

        # Helper to create segmented buttons (kept from before)
        def create_seg_btn(text, pos, checked_bg="default"):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("class", "seg_btn")
            btn.setProperty("seg_pos", pos)
            btn.setProperty("checked_bg", "green" if checked_bg == "#16a34a" else ("red" if checked_bg == "#dc2626" else "default"))
            btn.setCursor(Qt.PointingHandCursor)
            return btn
            
        def create_group_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #777; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl

        # --- MODULE 1: DATA ACTIONS (Clear / Save) ---
        mod_actions = QVBoxLayout()
        mod_actions.setSpacing(6)
        
        self.btn_trace = QPushButton("✗ CLEAR")
        self.btn_trace.setToolTip("Clear current trace")
        self.btn_trace.setFixedWidth(85)
        self.btn_trace.setStyleSheet("QPushButton { background-color: #222; color: #888; font-weight: bold; padding: 6px 0px; border-radius: 4px; border: 1px solid #444; font-size: 11px;} QPushButton:disabled { color: #555; } QPushButton:hover { color: #ef4444; border-color: #ef4444; }")
        self.btn_trace.clicked.connect(self.clear_trace)
        
        self.btn_save_db = QPushButton("⤓ SAVE")
        self.btn_save_db.setToolTip("Save trace to database")
        self.btn_save_db.setFixedWidth(85)
        self.btn_save_db.setStyleSheet("QPushButton { background-color: #222; color: #888; font-weight: bold; padding: 6px 0px; border-radius: 4px; border: 1px solid #444; font-size: 11px;} QPushButton:disabled { color: #555; } QPushButton:hover { color: #10b981; border-color: #10b981; }")
        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        
        mod_actions.addWidget(self.btn_trace)
        mod_actions.addWidget(self.btn_save_db)
        
        # --- MODULE 2: COMPARE (Target & History) ---
        mod_compare = QVBoxLayout()
        mod_compare.setSpacing(6)
        
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setToolTip("Select a target curve. Type to search.")
        self.cb_meas_target.setMinimumWidth(100)
        self.cb_meas_target.setMaximumWidth(340)
        self.cb_meas_target.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        
        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setToolTip("Select a historical measurement. Type to search.")
        self.cb_meas_history.setMinimumWidth(100)
        self.cb_meas_history.setMaximumWidth(340)
        self.cb_meas_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        
        mod_compare.addWidget(self.cb_meas_target)
        mod_compare.addWidget(self.cb_meas_history)
        
        # --- MODULE 3: CHANNEL & LIVE TOOLS (Chunky & Horizontal) ---
        mod_middle = QVBoxLayout()
        mod_middle.setSpacing(8)
        
        # Row 1: Channel L/R
        chan_widget = QWidget()
        chan_layout = QHBoxLayout(chan_widget)
        chan_layout.setContentsMargins(0,0,0,0)
        chan_layout.setSpacing(0)
        self.btn_grp_chan = QButtonGroup(chan_widget)
        self.btn_l = QPushButton("L")
        self.btn_l.setCheckable(True)
        self.btn_l.setChecked(True)
        self.btn_l.setCursor(Qt.PointingHandCursor)
        self.btn_r = QPushButton("R")
        self.btn_r.setCheckable(True)
        self.btn_r.setCursor(Qt.PointingHandCursor)
        self.btn_l.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-left-radius: 6px; border-bottom-left-radius: 6px; border-right: none; padding: 12px 28px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #16a34a; color: white; border-color: #16a34a; }")
        self.btn_r.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-right-radius: 6px; border-bottom-right-radius: 6px; padding: 12px 28px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #dc2626; color: white; border-color: #dc2626; }")
        self.btn_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_r.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_grp_chan.addButton(self.btn_l, 0)
        self.btn_grp_chan.addButton(self.btn_r, 1)
        chan_layout.addWidget(self.btn_l)
        chan_layout.addWidget(self.btn_r)
        self.btn_grp_chan.buttonClicked.connect(self.update_watermark)
        self.btn_grp_chan.buttonClicked.connect(self.on_target_channel_changed)
        
        # --- PROKIT EAR TIP SELECTOR (next to L/R) ---
        self.combo_tip = QComboBox()
        self.combo_tip.setObjectName("cb_prokit_tip")
        self.combo_tip.setEditable(False)
        self.combo_tip.setMinimumWidth(100)
        self.combo_tip.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.combo_tip.setToolTip("Select ProKit Coupler Ear Tip")
        self.combo_tip.setStyleSheet("""
            QComboBox {
                background-color: #222;
                color: #e4e4e7;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox:hover {
                border-color: #10b981;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #222;
                color: #e4e4e7;
                selection-background-color: #10b981;
                selection-color: black;
                border: 1px solid #444;
                min-width: 180px;
            }
        """)
        # Aliases
        self.cb_tip = self.combo_tip
        self.cb_prokit_tip = self.combo_tip
        
        # Wrap in container for visibility gating
        self.tip_container = QWidget()
        self.tip_container.setObjectName("tip_container")
        tip_h = QHBoxLayout(self.tip_container)
        tip_h.setContentsMargins(8, 0, 0, 0)
        tip_h.setSpacing(0)
        tip_h.addWidget(self.combo_tip)
        
        self.populate_tips()
        self.tip_container.setVisible(config.is_prokit_unlocked())
        
        # --- MODULE 4: LIVE TOOLS (RTA / Depth) ---
        rta_widget = QWidget()
        rta_layout = QVBoxLayout(rta_widget)
        rta_layout.setContentsMargins(0,0,0,0)
        rta_layout.setSpacing(4)
        
        self.btn_rta_raw = QPushButton("RTA")
        self.btn_rta_raw.setToolTip("Start Raw Live RTA")
        self.btn_rta_raw.setCheckable(True)
        self.btn_rta_raw.setFixedWidth(95)
        self.btn_rta_raw.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_rta_raw.setStyleSheet("QPushButton { background-color: #222; color: white; font-weight: bold; font-size: 13px; border-radius: 4px; border: 1px solid #444; padding: 6px 0px;} QPushButton:hover { background-color: #333; } QPushButton:checked { background-color: #0ea5e9; color: black; border: 1px solid #0ea5e9; padding: 6px 0px;}")
        self.btn_rta_raw.clicked.connect(self.on_rta_button_clicked)
        
        self.btn_iec_guide = QPushButton("Depth")
        self.btn_iec_guide.setToolTip("Live RTA: Align 8kHz Resonance Peak (Insertion Depth)")
        self.btn_iec_guide.setCheckable(True)
        self.btn_iec_guide.setFixedWidth(95)
        self.btn_iec_guide.setStyleSheet("QPushButton { background-color: #222; color: white; font-weight: bold; font-size: 13px; border-radius: 4px; border: 1px solid #444; padding: 6px 0px;} QPushButton:hover { background-color: #333; } QPushButton:checked { background-color: #10b981; color: black; border: 1px solid #10b981; padding: 6px 0px;}")
        self.btn_iec_guide.clicked.connect(self.on_rta_button_clicked)
        
        rta_layout.addWidget(self.btn_rta_raw, stretch=1)
        rta_layout.addWidget(self.btn_iec_guide)
        
        # --- MODULE 5: CAPTURE BLOCK (RUN + Sweeps) ---
        mod_capture = QVBoxLayout()
        mod_capture.setSpacing(4)
        
        # Run Button
        self.btn_capture = QPushButton("RUN")
        self.btn_capture.setToolTip("Start measurement capture (Space)")
        self.btn_capture.setFixedWidth(220)
        self.btn_capture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_capture.setStyleSheet("QPushButton { background-color: #10b981; color: black; font-weight: bold; font-size: 24px; border-radius: 6px; padding: 12px 30px;} QPushButton:disabled { background-color: #333; color: #666; } QPushButton:hover { background-color: #34d399; }")
        self.btn_capture.clicked.connect(self.run_measurement)
        mod_capture.addWidget(self.btn_capture, stretch=1)
        
        # Sweeps
        sweeps_widget = QWidget()
        sweeps_widget.setFixedWidth(220)
        sweeps_layout = QHBoxLayout(sweeps_widget)
        sweeps_layout.setContentsMargins(0,0,0,0)
        sweeps_layout.setSpacing(0)
        self.btn_grp_sweeps = QButtonGroup(sweeps_widget)
        btn_1x = create_seg_btn("1x", "left")
        btn_1x.setChecked(True)
        btn_3x = create_seg_btn("3x", "middle")
        btn_5x = create_seg_btn("5x", "right")
        self.btn_grp_sweeps.addButton(btn_1x, 1)
        self.btn_grp_sweeps.addButton(btn_3x, 3)
        self.btn_grp_sweeps.addButton(btn_5x, 5)
        
        sweeps_style = "QPushButton { background-color: #1a1a1a; color: #888; border: 1px solid #333; padding: 6px 10px; font-weight: bold; font-size: 13px; } QPushButton:checked { background-color: #333; color: white; border-color: #444; }"
        btn_1x.setStyleSheet(sweeps_style + " QPushButton { border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; }")
        btn_3x.setStyleSheet(sweeps_style + " QPushButton { border-right: none; }")
        btn_5x.setStyleSheet(sweeps_style + " QPushButton { border-top-right-radius: 4px; border-bottom-right-radius: 4px; }")
        
        sweeps_layout.addWidget(btn_1x)
        sweeps_layout.addWidget(btn_3x)
        sweeps_layout.addWidget(btn_5x)
        mod_capture.addWidget(sweeps_widget)
        
        # --- ASSEMBLE COMPACT LAYOUT ---
        left_group = QHBoxLayout()
        left_group.setSpacing(15)
        left_group.setAlignment(Qt.AlignBottom)
        left_group.addLayout(mod_actions)
        left_group.addLayout(mod_compare)
        left_group.addWidget(chan_widget)
        
        right_group = QHBoxLayout()
        right_group.setSpacing(7) # Pushes RTA 8px to the right to align with the visual edge of the QTabWidget above
        # Tip selector aligned to bottom (next to Depth)
        tip_col = QVBoxLayout()
        tip_col.addStretch()
        tip_col.addWidget(self.tip_container)
        right_group.addLayout(tip_col)
        right_group.addWidget(rta_widget)
        right_group.addLayout(mod_capture)
        
        control_layout.setAlignment(Qt.AlignBottom)
        control_layout.addLayout(left_group)
        control_layout.addStretch()
        control_layout.addLayout(right_group)
        
        # Container without extra top margin
        bottom_container = QVBoxLayout()
        bottom_container.setContentsMargins(0, 0, 0, 0)  # Removed the 15px top margin
        bottom_container.addWidget(self.control_panel)
        
        # Keep meas_layout clean (page_meas is hidden anyway)
        
        
        # --- ANALYSIS PAGE ---
        from analysis_ui import AnalysisWidget
        self.page_ana = AnalysisWidget()
        self.page_ana.main_window = self
        self.page_ana.request_measurement.connect(self.run_measurement)
        self.page_ana.request_stress_test.connect(self.run_stress_test)

        # Synchronize bottom bar tip changes with Analysis Page
        def _on_bottom_bar_tip_changed(idx):
            if hasattr(self, 'combo_tip') and hasattr(self, 'page_ana'):
                t_id = self.combo_tip.currentData()
                if t_id is not None:
                    self.page_ana.current_tip_id = t_id
                    if hasattr(self.page_ana, 'tip_analysis_card') and self.page_ana.tip_analysis_card:
                        self.page_ana.tip_analysis_card.set_active_tip(t_id)

        self.combo_tip.currentIndexChanged.connect(_on_bottom_bar_tip_changed)
        
        self.meas_overlay = MeasurementAnimator(self.page_ana.plot_widget)
        self.stress_overlay = MeasurementAnimator(self.page_ana.thd_widget)
        
        self.watermark_item.setParentItem(self.page_ana.plot_widget.getViewBox())
        def update_wm_pos(vb=None):
            rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            self.watermark_item.setPos(rect.right() - 20, rect.top() + 20)
        self.page_ana.plot_widget.getViewBox().sigResized.connect(update_wm_pos)
        update_wm_pos()
        
        # Inject bottom_container into Analysis tab!
        self.page_ana.layout.addLayout(bottom_container)
        
        # --- TAB CORNER WIDGET (Top Right) ---
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(15)  # Logical grouping by larger space
        corner_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        
        # 1. Filter Group: Left/Right
        chan_vis_widget = QWidget()
        chan_vis_layout = QHBoxLayout(chan_vis_widget)
        chan_vis_layout.setContentsMargins(0,0,0,0)
        chan_vis_layout.setSpacing(0)
        # Styled neutrally to not clash with bottom bar Capture channel selection
        self.page_ana.btn_chan_l.setStyleSheet("QPushButton { background-color: #1a1a1a; color: #666; border: 1px solid #333; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #333; color: white; border-color: #555; }")
        self.page_ana.btn_chan_r.setStyleSheet("QPushButton { background-color: #1a1a1a; color: #666; border: 1px solid #333; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #333; color: white; border-color: #555; }")
        chan_vis_layout.addWidget(self.page_ana.btn_chan_l)
        chan_vis_layout.addWidget(self.page_ana.btn_chan_r)
        corner_layout.addWidget(chan_vis_widget)
        
        # 2. View Group: Smooth / Autozoom
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        view_layout.setContentsMargins(0,0,0,0)
        view_layout.setSpacing(8)
        
        self.cb_smooth.setStyleSheet("QComboBox { background-color: #222; color: white; border: 1px solid #444; padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; min-height: 20px; }")
        view_layout.addWidget(self.cb_smooth)
        view_layout.addWidget(self.btn_reset_view)
        corner_layout.addWidget(view_widget)
        

        self.page_ana.graph_tabs.setCornerWidget(corner_widget, Qt.TopRightCorner)
        
        self.workspace_stacked.addWidget(page_meas)
        self.workspace_stacked.addWidget(self.page_ana)
        
        # --- HISTORY PAGE ---
        try:
            from history_ui import HistoryWidget
            self.page_hist = HistoryWidget()
            self.workspace_stacked.addWidget(self.page_hist)
        except ImportError:
            self.page_hist = QLabel("History Widget building...")
            self.page_hist.setStyleSheet("color: white;")
            self.workspace_stacked.addWidget(self.page_hist)
        self.workspace_stacked.setCurrentIndex(2) # Workspace
            
        self.btn_nav_prof.clicked.connect(lambda: self.switch_workspace_tab(0))
        
        self.btn_nav_ana.clicked.connect(lambda: self.switch_workspace_tab(2))
        self.btn_nav_hist.clicked.connect(lambda: self.switch_workspace_tab(3))
        
        # =========================================================
        # SETTINGS PANEL (OVERLAY)
        # =========================================================
        self.settings_dimmer = QPushButton(central)
        self.settings_dimmer.setStyleSheet("background: rgba(0, 0, 0, 0.6); border: none;")
        self.settings_dimmer.hide()
        self.settings_dimmer.clicked.connect(lambda: self.settings_panel.setVisible(False) or self.settings_dimmer.setVisible(False))
        
        self.page_set = QFrame(central)
        self.page_set.setFixedWidth(600)
        self.page_set.setObjectName("SettingsPanel")
        self.page_set.setStyleSheet(f"#SettingsPanel {{ background-color: {theme.get_color('bg_panel')}; border-left: 1px solid {theme.get_color('border')}; }}")
        self.page_set.hide()
        self.settings_panel = self.page_set
        
        set_layout = QVBoxLayout(self.page_set)
        set_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        set_lbl = QLabel("Configuration & Settings")
        set_lbl.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(set_lbl)
        header_layout.addStretch()

        self.btn_tour = QPushButton("Help / Tour")
        self.btn_tour.setToolTip("Start Guided Tour")
        self.btn_tour.setStyleSheet("background-color: transparent; color: #888; font-size: 14px; font-weight: bold; border: none;")
        self.btn_tour.setCursor(Qt.PointingHandCursor)
        self.btn_tour.clicked.connect(self.start_guided_tour)
        header_layout.addWidget(self.btn_tour)

        # Status label – shows "Saved" feedback without popup
        self.settings_save_lbl = QLabel("")
        self.settings_save_lbl.setStyleSheet("color: #00FF99; font-size: 12px; font-weight: bold; margin-left: 12px;")
        header_layout.addWidget(self.settings_save_lbl)

        set_layout.addLayout(header_layout)
        set_layout.addSpacing(10)


        # --- TAB WIDGET ---
        from PySide6.QtWidgets import QTabWidget
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setUsesScrollButtons(True)
        self.settings_tabs.setElideMode(Qt.ElideNone)
        self.settings_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #333; background: #222; } QTabBar::tab { background: #111; color: #888; padding: 10px 16px; min-width: 70px; } QTabBar::tab:selected { background: #222; color: #00FFFF; }")
        
        # ── TAB 1: Routing ───────────────────────────────────────────────────
        tab_routing = QWidget()
        tab_routing.setStyleSheet("background: #222;")
        routing_layout = QVBoxLayout(tab_routing)
        routing_layout.setSpacing(14)
        routing_layout.setContentsMargins(16, 16, 16, 16)

        lbl_in = QLabel("Input Device (Measurement Mic):")
        lbl_in.setProperty("class", "subtitle")
        lbl_in.style().unpolish(lbl_in)
        lbl_in.style().polish(lbl_in)
        routing_layout.addWidget(lbl_in)
        self.in_combo = QComboBox()
        routing_layout.addWidget(self.in_combo)

        lbl_out = QLabel("Output Device (IEM / Speaker Feed):")
        lbl_out.setProperty("class", "subtitle")
        lbl_out.style().unpolish(lbl_out)
        lbl_out.style().polish(lbl_out)
        routing_layout.addWidget(lbl_out)
        self.out_combo = QComboBox()
        routing_layout.addWidget(self.out_combo)

        # Live-update device indices when user changes combo (no Save needed)
        self.in_combo.currentIndexChanged.connect(lambda: setattr(self, 'selected_in_idx', self.in_combo.currentData()))
        self.out_combo.currentIndexChanged.connect(lambda: setattr(self, 'selected_out_idx', self.out_combo.currentData()))

        # Refresh devices button (for hot-plugged interfaces)
        btn_refresh_dev = QPushButton("Refresh Device List")
        btn_refresh_dev.setToolTip("Refresh audio device list")
        btn_refresh_dev.setStyleSheet(
            "background-color: #1a1a1a; color: #00FFFF; border: 1px solid #333; "
            "padding: 7px; border-radius: 4px; font-size: 12px;"
        )
        btn_refresh_dev.setCursor(Qt.PointingHandCursor)
        btn_refresh_dev.clicked.connect(self.populate_devices)
        routing_layout.addWidget(btn_refresh_dev)
        
        routing_layout.addSpacing(10)
        from PySide6.QtWidgets import QCheckBox
        self.chk_normalize = QCheckBox("Auto-Normalize to 80 dB (Align to Target)")
        self.chk_normalize.setStyleSheet("color: white; font-size: 13px;")
        self.chk_normalize.setChecked(True)
        routing_layout.addWidget(self.chk_normalize)
        
        routing_layout.addStretch()

        self.settings_tabs.addTab(tab_routing, "Routing")

        # ── TAB 2: Coupler Calibration ────────────────────────────────────────
        tab_cal = QWidget()
        tab_cal.setStyleSheet("background: #222;")
        cal_layout = QVBoxLayout(tab_cal)
        cal_layout.setSpacing(10)
        cal_layout.setContentsMargins(16, 16, 16, 16)

        # Active profile selector – lives here now (not in Routing)
        lbl_mic = QLabel("Active Coupler Profile:")
        lbl_mic.setProperty("class", "subtitle")
        lbl_mic.style().unpolish(lbl_mic)
        lbl_mic.style().polish(lbl_mic)
        cal_layout.addWidget(lbl_mic)
        self.mic_cal_combo = QComboBox()
        self.mic_cal_combo.addItem("None (Flat)", "")
        cal_layout.addWidget(self.mic_cal_combo)

        from calibration_ui import CalibrationWidget
        self.cal_widget = CalibrationWidget()
        self.cal_widget.calibration_applied.connect(self.reload_calibrations)
        self.mic_cal_combo.currentIndexChanged.connect(self.update_cal_preview)
        cal_layout.addWidget(self.cal_widget, stretch=1)

        # ── OUTPUT LEVEL CALIBRATION ──
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #444;")
        cal_layout.addWidget(divider)

        lbl_level = QLabel("Output Level Calibration")
        lbl_level.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-top: 8px;")
        cal_layout.addWidget(lbl_level)

        lbl_level_desc = QLabel(
            "Plays ascending test tones to find the optimal output level for your hardware. "
            "Connect your IEM in the coupler before starting."
        )
        lbl_level_desc.setWordWrap(True)
        lbl_level_desc.setStyleSheet("color: #888; font-size: 11px;")
        cal_layout.addWidget(lbl_level_desc)

        self.cal_status_lbl = QLabel("Not calibrated. Using default amplitude (0.1 / -20 dBFS).")
        self.cal_status_lbl.setStyleSheet("color: #f59e0b; font-size: 11px; padding: 4px;")
        cal_layout.addWidget(self.cal_status_lbl)

        self.cal_results_lbl = QLabel("")
        self.cal_results_lbl.setWordWrap(True)
        self.cal_results_lbl.setStyleSheet("color: #d4d4d8; font-size: 11px; font-family: monospace; background: #111; padding: 8px; border-radius: 4px;")
        self.cal_results_lbl.hide()
        cal_layout.addWidget(self.cal_results_lbl)

        self.btn_auto_cal = QPushButton("Start Auto-Calibration")
        self.btn_auto_cal.setCursor(Qt.PointingHandCursor)
        self.btn_auto_cal.setStyleSheet("QPushButton { background-color: #222; color: #0ea5e9; border: 1px solid #0ea5e9; padding: 6px 16px; font-weight: bold; border-radius: 4px; margin-top: 10px; } QPushButton:hover { background-color: #0ea5e9; color: white; }")
        self.btn_auto_cal.clicked.connect(self._run_level_calibration)
        cal_layout.addWidget(self.btn_auto_cal)

        self.settings_tabs.addTab(tab_cal, " Calibration ")

        # ── TAB 3: Manual / Help ──────────────────────────────────────────────
        tab_manual = QWidget()
        tab_manual.setStyleSheet("background: #222;")
        manual_layout = QVBoxLayout(tab_manual)
        manual_layout.setContentsMargins(16, 16, 16, 16)

        manual_top_row = QHBoxLayout()
        self.manual_search = QLineEdit()
        self.manual_search.setPlaceholderText("Search manual...")
        self.manual_search.setStyleSheet(
            "background: #111; color: white; padding: 5px; "
            "border: 1px solid #333; border-radius: 4px;"
        )
        manual_top_row.addWidget(self.manual_search, stretch=4)

        def _reload_manual():
            import os
            if os.path.exists("MANUAL.md"):
                with open("MANUAL.md", "r", encoding="utf-8") as f:
                    self.manual_browser.setMarkdown(f.read())
            else:
                self.manual_browser.setText("MANUAL.md not found.")

        btn_reload_manual = QPushButton("Reload")
        btn_reload_manual.setToolTip("Reload manual from disk")
        btn_reload_manual.setStyleSheet(
            "background: #1a1a1a; color: #00FFFF; border: 1px solid #333; "
            "padding: 5px 10px; border-radius: 4px; font-size: 12px;"
        )
        btn_reload_manual.setCursor(Qt.PointingHandCursor)
        btn_reload_manual.clicked.connect(_reload_manual)
        manual_top_row.addWidget(btn_reload_manual, stretch=1)
        manual_layout.addLayout(manual_top_row)


        import os
        from PySide6.QtWidgets import QTextBrowser
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QTextCursor, QTextOption
        
        self.manual_browser = QTextBrowser()
        self.manual_browser.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; border: 1px solid {theme.get_color('border')}; border-radius: 4px; padding: 10px;")
        
        # --- Force wrap to prevent horizontal scroll ---
        self.manual_browser.setLineWrapMode(QTextBrowser.WidgetWidth)
        self.manual_browser.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.manual_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # --- Fix for missing anchor jumps in Qt Markdown ---
        self.manual_browser.setOpenLinks(False)
        def handle_manual_link(url):
            link = url.toString()
            file_path = link.split("#")[0]
            if file_path.startswith("./"):
                file_path = file_path[2:]
                
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.manual_browser.setMarkdown(f.read())
                
                # If there's a chapter 14 anchor, scroll to it
                if "#14" in link:
                    self.manual_browser.moveCursor(QTextCursor.Start)
                    if self.manual_browser.find("14. "):
                        cursor = self.manual_browser.textCursor()
                        cursor.clearSelection()
                        self.manual_browser.setTextCursor(cursor)
                        # Bring the text to the top of the viewport instead of the bottom edge
                        rect = self.manual_browser.cursorRect(cursor)
                        scrollbar = self.manual_browser.verticalScrollBar()
                        scrollbar.setValue(scrollbar.value() + rect.top() - 20)
                elif "#hardware-guide" in link:
                    self.manual_browser.moveCursor(QTextCursor.Start)
                    found = self.manual_browser.find("Hardware Guide")
                    if not found:
                        self.manual_browser.moveCursor(QTextCursor.Start)
                        found = self.manual_browser.find("Guía de hardware")
                        
                    if found:
                        cursor = self.manual_browser.textCursor()
                        cursor.clearSelection()
                        self.manual_browser.setTextCursor(cursor)
                        rect = self.manual_browser.cursorRect(cursor)
                        scrollbar = self.manual_browser.verticalScrollBar()
                        scrollbar.setValue(scrollbar.value() + rect.top() - 20)
                    
        self.manual_browser.anchorClicked.connect(handle_manual_link)
        
        if os.path.exists("MANUAL.md"):
            with open("MANUAL.md", "r", encoding="utf-8") as f:
                self.manual_browser.setMarkdown(f.read())
        else:
            self.manual_browser.setText("MANUAL.md not found.")
            
        manual_layout.addWidget(self.manual_browser)

        from PySide6.QtGui import QTextCursor
        def on_manual_search():
            text = self.manual_search.text()
            if text:
                if not self.manual_browser.find(text):
                    self.manual_browser.moveCursor(QTextCursor.Start)
                    self.manual_browser.find(text)
        self.manual_search.textChanged.connect(on_manual_search)
        self.manual_search.returnPressed.connect(on_manual_search)

        # ── TAB 4: Database & Targets ───────────────────────────────────────
        tab_db = QWidget()
        tab_db.setStyleSheet("background: #222;")
        tab_db_layout = QVBoxLayout(tab_db)
        tab_db_layout.setSpacing(14)
        tab_db_layout.setContentsMargins(16, 16, 16, 16)
        
        # App Database
        from PySide6.QtWidgets import QGroupBox, QListWidget, QAbstractItemView, QListWidgetItem
        db_group = QGroupBox("App Database (Profiles & Measurements)")
        db_group.setStyleSheet("QGroupBox { color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        db_layout = QHBoxLayout(db_group)
        
        btn_backup = QPushButton("Backup Database")
        btn_backup.setToolTip("Create a safe backup copy of your entire database")
        btn_backup.clicked.connect(self.backup_database)
        db_layout.addWidget(btn_backup)
        
        btn_restore = QPushButton("Restore Database")
        btn_restore.setToolTip("Restore your database from a previously created backup")
        btn_restore.clicked.connect(self.restore_database)
        db_layout.addWidget(btn_restore)
        
        tab_db_layout.addWidget(db_group)
        
        # Target Templates
        tgt_group = QGroupBox("Target Templates (Squiglink / Reference Curves)")
        tgt_group.setStyleSheet("QGroupBox { color: #888; border: 1px solid #333; border-radius: 4px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        tgt_layout = QVBoxLayout(tgt_group)
        
        self.search_targets = QLineEdit()
        self.search_targets.setPlaceholderText("Search targets...")
        self.search_targets.setStyleSheet("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 6px;")
        self.search_targets.textChanged.connect(self.filter_target_list)
        tgt_layout.addWidget(self.search_targets)
        
        self.list_targets = QListWidget()
        self.list_targets.setStyleSheet("background: #111; color: white; border: 1px solid #333; border-radius: 4px; padding: 4px;")
        self.list_targets.setSelectionMode(QAbstractItemView.SingleSelection)
        tgt_layout.addWidget(self.list_targets)
        
        tgt_btn_row = QHBoxLayout()
        btn_import_tgt = QPushButton("Import CSV")
        btn_import_tgt.clicked.connect(self.import_target_template)
        tgt_btn_row.addWidget(btn_import_tgt)
        
        btn_export_tgt = QPushButton("Export Selected")
        btn_export_tgt.clicked.connect(self.export_target_template)
        tgt_btn_row.addWidget(btn_export_tgt)
        
        btn_delete_tgt = QPushButton("Delete Selected")
        btn_delete_tgt.setProperty("class", "danger")
        btn_delete_tgt.clicked.connect(self.delete_target_template)
        tgt_btn_row.addWidget(btn_delete_tgt)
        
        tgt_layout.addLayout(tgt_btn_row)
        tab_db_layout.addWidget(tgt_group)
        
        self.settings_tabs.addTab(tab_db, "Database")
        self.settings_tabs.addTab(tab_manual, "Manual")
        
        # ── TAB 5: Console / Logs ───────────────────────────────────────
        tab_console = QWidget()
        console_layout = QVBoxLayout(tab_console)
        console_layout.setContentsMargins(16, 16, 16, 16)
        
        from PySide6.QtWidgets import QTextBrowser
        self.console_output = QTextBrowser()
        self.console_output.setOpenExternalLinks(True)
        self.console_output.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; font-family: 'Courier New', Courier, monospace; font-size: 11px; padding: 5px; border: 1px solid {theme.get_color('border')}; border-radius: 4px;")
        console_layout.addWidget(self.console_output)
        
        self.settings_tabs.addTab(tab_console, "Console")
        

        set_layout.addWidget(self.settings_tabs)

        privacy_lbl = QLabel("Privacy: All data (musician profiles, measurements, photos) is stored exclusively on this device. No data is transmitted to the internet. No telemetry, no tracking, no analytics.")
        privacy_lbl.setWordWrap(True)
        privacy_lbl.setStyleSheet("font-size: 11px; color: #888888;")
        set_layout.addWidget(privacy_lbl)

        self.reload_calibrations()
        self.update_cal_preview()



        # Save button – no popup, no panel close; inline feedback only
        btn_save_set = QPushButton("Save & Apply Settings")
        btn_save_set.setToolTip("Save and apply settings")
        btn_save_set.setStyleSheet(
            "background-color: #00FF99; color: black; font-weight: bold; "
            "padding: 11px; border-radius: 4px; font-size: 14px;"
        )
        btn_save_set.setCursor(Qt.PointingHandCursor)
        btn_save_set.clicked.connect(self.save_settings)
        set_layout.addWidget(btn_save_set)

        
        
        self.populate_devices()
        self._load_settings()   # Restore QSettings after devices are enumerated
        self.load_profiles_from_db()
        self.page_ana.cb_ana_target.currentIndexChanged.connect(self.on_ana_target_changed)
        self.page_ana.cb_ana_history.currentIndexChanged.connect(self.on_ana_history_changed)
        self.load_targets()
        self.reload_target_list()
        
        # Setup Logger
        self.stdout_logger = LogStream(sys.stdout, is_error=False)
        self.stderr_logger = LogStream(sys.stderr, is_error=True)
        self.stdout_logger.message_written.connect(self.on_log_message)
        self.stderr_logger.message_written.connect(self.on_log_message)
        sys.stdout = self.stdout_logger
        sys.stderr = self.stderr_logger

        self.btn_capture.setEnabled(False)
        self.btn_save_db.setEnabled(False)
        
        # Auto-select the top profile if one exists
        if self.profile_cards:
            self.force_profile_selection(self.profile_cards[0])
            
        self.apply_dynamic_theme_styles()
        
        import os
        from config import get_data_dir
        flag_file = os.path.join(get_data_dir(), "tour_completed.flag")
        if not os.path.exists(flag_file):
            QTimer.singleShot(1500, self.start_guided_tour)

    def on_log_message(self, text, is_error):
        if not hasattr(self, 'console_output'): return
        
        import html
        safe_text = html.escape(text.strip()).replace('\n', '<br>')
        color = "#ff4444" if is_error else "#00ff99"
        
        self.console_output.append(f'<span style="color:{color};">{safe_text}</span>')
        
        sb = self.console_output.verticalScrollBar()
        sb.setValue(sb.maximum())
        
        if is_error and not text.startswith("Warning"):
            if hasattr(self, 'sub_lbl'):
                short_text = text.strip().split('\n')[-1][:60]
                self.sub_lbl.setText("Something went wrong — check the Console in Settings for details.")
                self.sub_lbl.setStyleSheet("color: #ff4444; font-size: 12px; font-weight: bold;")

    def _align_target(self, tgt_f, tgt_m, meas_freqs, meas_mag, anchor_hz=1000):
        """
        Align target curve to measurement at anchor_hz.
        Falls back to 500 Hz if the anchor point has too few neighbors.
        Returns (aligned_mags, actual_anchor_hz_used, offset_db)
        """
        import numpy as np
        # Try anchor, fallback to 500 Hz
        for anchor in [anchor_hz, 500]:
            idx_tgt = (np.abs(tgt_f - anchor)).argmin()
            idx_meas = (np.abs(meas_freqs - anchor)).argmin()
            tgt_val = tgt_m[idx_tgt]
            meas_val = meas_mag[idx_meas]
            if np.isfinite(tgt_val) and np.isfinite(meas_val):
                offset = meas_val - tgt_val
                return tgt_m + offset, anchor, offset
        # Ultimate fallback: center at 80 dB
        idx_tgt = (np.abs(tgt_f - 1000)).argmin()
        offset = 80 - tgt_m[idx_tgt]
        return tgt_m + offset, 0, offset

    def plot_target_curve(self):
        if hasattr(self, 'target_line') and self.target_line is not None:
            self.plot_widget.removeItem(self.target_line)
            self.target_line = None
        if hasattr(self, 'history_line_l') and self.history_line_l is not None:
            self.plot_widget.removeItem(self.history_line_l)
            self.history_line_l = None
        if hasattr(self, 'history_line_r') and self.history_line_r is not None:
            self.plot_widget.removeItem(self.history_line_r)
            self.history_line_r = None
            
        if self.target_freqs is not None and self.target_mags is not None :
            import numpy as np
            import pyqtgraph as pg
            
            # --- SMOOTHING ---
            tgt_f, tgt_m = self.target_freqs.copy(), self.target_mags.copy()
            
            smooth_txt = self.cb_smooth.currentText() if hasattr(self, 'cb_smooth') else "1/24 Oct"
            if smooth_txt == "1/24 Oct": pts = 240
            elif smooth_txt == "1/48 Oct": pts = 480
            elif smooth_txt == "1/12 Oct": pts = 120
            elif smooth_txt == "1/6 Oct": pts = 60
            else: pts = None
            
            if pts is not None and len(tgt_f) > 500:
                try:
                    tgt_f, tgt_m, _ = self.audio_engine.smooth_spectrum(tgt_f, tgt_m, points=pts)
                except Exception as e:
                    print("Could not smooth target:", e)
            
            # --- ALIGNMENT (1kHz preferred, 500Hz fallback) ---
            meas_freqs = getattr(self, 'temp_freqs', None)
            meas_mag_l = getattr(self, 'temp_mag_l', None)
            meas_mag_r = getattr(self, 'temp_mag_r', None)
            
            if meas_freqs is not None and meas_mag_l is not None:
                aligned_mags, anchor, offset = self._align_target(tgt_f, tgt_m, meas_freqs, meas_mag_l)
            elif meas_freqs is not None and meas_mag_r is not None:
                aligned_mags, anchor, offset = self._align_target(tgt_f, tgt_m, meas_freqs, meas_mag_r)
            else:
                # No measurement yet: center at 80 dB @ 1kHz
                idx_1k = (np.abs(tgt_f - 1000)).argmin()
                offset = 80 - tgt_m[idx_1k]
                aligned_mags = tgt_m + offset
                anchor = 0
                
            self.target_line = self.plot_widget.plot(
                tgt_f, 
                aligned_mags, 
                pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), 
                name=f"Target (aligned @{anchor//1000 if anchor>=1000 else anchor}{'kHz' if anchor>=1000 else 'Hz'})" if anchor else "Target"
            )

        if getattr(self, 'history_freqs', None) is not None:
            import pyqtgraph as pg
            from audio_engine import AudioEngine
            
            smooth_txt = self.cb_smooth.currentText()
            if smooth_txt == "1/24 Oct": pts = 240
            elif smooth_txt == "1/48 Oct": pts = 480
            elif smooth_txt == "1/12 Oct": pts = 120
            elif smooth_txt == "1/6 Oct": pts = 60
            else: pts = 0
            
            if getattr(self, 'history_mag_l', None) is not None and self.get_current_channel() == "Left":
                f_h, m_h, _ = AudioEngine.smooth_spectrum(self.history_freqs, self.history_mag_l, points=pts)
                self.history_line_l = self.plot_widget.plot(
                    f_h, m_h,
                    pen=pg.mkPen(theme.get_color('history_l'), width=2, style=Qt.DashLine),
                    name="History L"
                )
            if getattr(self, 'history_mag_r', None) is not None and self.get_current_channel() == "Right":
                f_h, m_h, _ = AudioEngine.smooth_spectrum(self.history_freqs, self.history_mag_r, points=pts)
                self.history_line_r = self.plot_widget.plot(
                    f_h, m_h,
                    pen=pg.mkPen(theme.get_color('history_r'), width=2, style=Qt.DashLine),
                    name="History R"
                )

    def update_cal_preview(self):
        cal_path = self.mic_cal_combo.currentData()
        if not cal_path:
            self.cal_widget.file_label.setText("No calibration file selected (Flat response).")
            self.cal_widget.plot_widget.clear()
            self.cal_widget.freqs = []
            self.cal_widget.amps = []
        else:
            import os
            self.cal_widget.file_label.setText(f"Previewing: {os.path.basename(cal_path)}")
            self.cal_widget.parse_file(cal_path)

    def reload_calibrations(self, select_path=None):
        self.mic_cal_combo.clear()
        self.mic_cal_combo.addItem("None (Flat)", "")
        import os
        cal_dir = "calibrations"
        os.makedirs(cal_dir, exist_ok=True)
        for f in os.listdir(cal_dir):
            if f.endswith('.cal') or f.endswith('.txt'):
                self.mic_cal_combo.addItem(f, os.path.join(cal_dir, f))
                
        if select_path:
            for i in range(self.mic_cal_combo.count()):
                if self.mic_cal_combo.itemData(i) == select_path:
                    self.mic_cal_combo.setCurrentIndex(i)
                    break
        else:
            # Auto-select the 711 calibration if it exists and no setting was previously saved
            for i in range(self.mic_cal_combo.count()):
                if "IEC711" in self.mic_cal_combo.itemText(i):
                    self.mic_cal_combo.setCurrentIndex(i)
                    break

    def redraw_graph(self, *args):
        self.plot_widget.clear()
        self.plot_target_curve()
        
        import pyqtgraph as pg
        from audio_engine import AudioEngine
        
        # Determine smoothing
        smooth_txt = self.cb_smooth.currentText()
        if smooth_txt == "1/24 Oct": pts = 240
        elif smooth_txt == "1/48 Oct": pts = 480
        elif smooth_txt == "1/12 Oct": pts = 120
        elif smooth_txt == "1/6 Oct": pts = 60
        else: pts = None
        
        # Now draw the current live measurement on top
        if self.temp_freqs is not None:
            spl_off = getattr(self, 'spl_offset_db', 0.0)
            if self.temp_mag_l is not None:
                f, m, _ = AudioEngine.smooth_spectrum(self.temp_freqs, self.temp_mag_l, points=pts or 0)
                self.plot_widget.plot(f, m + spl_off, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name="Left")
            if self.temp_mag_r is not None:
                f, m, _ = AudioEngine.smooth_spectrum(self.temp_freqs, self.temp_mag_r, points=pts or 0)
                self.plot_widget.plot(f, m + spl_off, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name="Right")

    def on_smooth_changed(self, *args):
        self.redraw_graph()
        if hasattr(self, 'page_ana'):
            self.update_analysis_view()

    def load_targets(self):
        # We populate the four combo boxes (2 in Meas, 2 in Ana)
        boxes_hist = [self.cb_meas_history, self.page_ana.cb_ana_history]
        boxes_tgt = [self.cb_meas_target, self.page_ana.cb_ana_target]
        
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(True)
            b.clear()
            
        for b in boxes_hist:
            b.addItem("No History Selected", None)
            
        for b in boxes_tgt:
            b.addItem("No Target Selected", None)
            
        # 1. Load DB Measurements into History
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT m.id, mus.name, iem.model_name, m.timestamp, m.notes, iem.abbreviation
            FROM Measurements m
            JOIN IEM_Models iem ON m.iem_id = iem.id
            JOIN Musicians mus ON iem.musician_id = mus.id
            ORDER BY m.timestamp DESC
        ''')
        db_rows = c.fetchall()
        conn.close()
        
        if db_rows:
            from datetime import datetime
            for meas_id, m_name, i_model, ts, notes, abbr in db_rows:
                # Format Timestamp (YYYY-MM-DD HH:MM:SS -> DD.MM. HH:MM)
                date_str = "Unknown"
                if ts:
                    try:
                        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        date_str = dt.strftime("%d.%m. %H:%M")
                    except Exception:
                        date_str = ts.split()[0]
                
                # Determine display name
                display_name = notes.strip() if notes and notes.strip() else (abbr.strip() if abbr and abbr.strip() else i_model)
                
                display = f"{display_name} - {date_str}"
                for b in boxes_hist:
                    b.addItem(display, meas_id)
                
        # 2. Load CSV Files into Target
        import os
        import glob
        target_dir = "reference_targets/Pro_Live_IEMs"
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                name = os.path.basename(f).replace('.csv', '')
                for b in boxes_tgt:
                    b.addItem(name, f)
                
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(False)
            # Make combobox searchable
            b.setEditable(True)
            from PySide6.QtWidgets import QCompleter
            from PySide6.QtCore import Qt
            b.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            completer = b.completer()
            if completer:
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setFilterMode(Qt.MatchContains)
            
            # Styling the line edit inside the combobox
            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                
                # Allow normal click-to-open behavior without eating events
                from PySide6 import QtCore
                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.FocusIn:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        # Remove MouseButtonPress interception so popup opens normally
                        return super().eventFilter(obj, event)
                
                b._focus_filter = FocusSelectFilter(b)
                line_edit.installEventFilter(b._focus_filter)
                # Update placeholder text manually if empty
                if b.count() > 0 and b.currentIndex() == -1:
                    line_edit.setText(b.itemText(0))

    def style_tab(self, btn, active):
        if active:
            btn.setStyleSheet(f"QPushButton {{ color: {theme.get_color('text_primary')}; font-weight: 800; font-size: 14px; letter-spacing: 1px; background-color: transparent; padding: 10px 20px; border: none; border-bottom: 3px solid {theme.get_color('accent')}; }}")
        else:
            btn.setStyleSheet(f"QPushButton {{ color: {theme.get_color('text_secondary')}; font-weight: bold; font-size: 14px; letter-spacing: 1px; background-color: transparent; padding: 10px 20px; border: none; border-bottom: 3px solid transparent; }} QPushButton:hover {{ color: {theme.get_color('text_primary')}; }}")

    def switch_workspace_tab(self, idx):
        self.workspace_stacked.setCurrentIndex(idx)
        self.style_tab(self.btn_nav_prof, idx == 0)
        self.style_tab(self.btn_nav_ana, idx == 2)
        self.style_tab(self.btn_nav_hist, idx == 3)
        
        if idx == 0 and hasattr(self.page_prof, 'load_profile'):
            m_id = None
            if hasattr(self, 'active_card') and self.active_card:
                m_id = self.active_card.m_id
            if m_id is not None:
                self.page_prof.load_profile(self.current_iem_id, m_id)
        if idx == 3 and hasattr(self.page_hist, 'load_history'):
            m_id = None
            if hasattr(self, 'active_card') and self.active_card:
                m_id = self.active_card.m_id
            if m_id is not None:
                self.page_hist.load_history(m_id)


    def handle_measure_requested(self, iem_id):
        if self.page_prof.current_musician_id:
            for c in self.profile_cards:
                if str(getattr(c, 'm_id', '')) == str(getattr(self.page_prof, 'current_musician_id', '')):
                    self.on_profile_selected(c)
                    for b_id, b in c.avatar_btns:
                        if str(b_id) == str(iem_id):
                            c.select_iem(b_id, b.iem_name, b)
                            break
                    break
        self.switch_workspace_tab(2)


    def on_profile_data_saved_only(self):
        # Refresh sidebar list silently
        self.load_profiles_from_db()
        # Update header without reloading the profile tab forms
        if hasattr(self.page_prof, 'current_musician_id') and self.page_prof.current_musician_id:
            for c in self.profile_cards:
                if str(getattr(c, 'm_id', '')) == str(getattr(self.page_prof, 'current_musician_id', '')):
                    # self.lbl_selected_musician.setText(f"{c.name} / {c.band}")  # removed, label no longer exists
                    # Ensure the current IEM is also re-selected visually in the sidebar
                    if hasattr(self, 'current_iem_id') and self.current_iem_id:
                        for b_id, b in c.avatar_btns:
                            if str(b_id) == str(self.current_iem_id):
                                c.current_iem_id = self.current_iem_id
                                c.current_iem_name = b.iem_name
                                for inner_b_id, inner_b in c.avatar_btns:
                                    inner_b.update_style(str(inner_b_id) == str(self.current_iem_id))
                                break
                    break

    def on_profile_data_changed(self):
        # Refresh sidebar list and re-trigger selection to update header
        self.load_profiles_from_db()
        if hasattr(self, 'current_iem_id') and self.current_iem_id:
            for c in self.profile_cards:
                if c.current_iem_id == self.current_iem_id:
                    self.force_profile_selection(c)
                    break

    def populate_devices(self):
        try:
            # Remember currently selected names to restore them after refresh
            old_in_name = self.in_combo.currentText()
            old_out_name = self.out_combo.currentText()
            
            self.in_combo.clear()
            self.out_combo.clear()
            
            # sounddevice caches devices; force a re-query if possible by re-importing or just querying
            import sounddevice as sd
            sd._terminate()
            sd._initialize()
            
            devices = self.audio_engine.get_devices()
            
            for i, d in enumerate(devices):
                if d['max_input_channels'] > 0:
                    self.in_combo.addItem(d['name'], userData=i)
                if d['max_output_channels'] > 0:
                    self.out_combo.addItem(d['name'], userData=i)
                    
            # Try to restore previous selection, otherwise fallback to index 0
            idx_in = self.in_combo.findText(old_in_name)
            if idx_in >= 0:
                self.in_combo.setCurrentIndex(idx_in)
                self.selected_in_idx = self.in_combo.itemData(idx_in)
            elif self.in_combo.count() > 0:
                self.selected_in_idx = self.in_combo.itemData(0)
                
            idx_out = self.out_combo.findText(old_out_name)
            if idx_out >= 0:
                self.out_combo.setCurrentIndex(idx_out)
                self.selected_out_idx = self.out_combo.itemData(idx_out)
            elif self.out_combo.count() > 0:
                self.selected_out_idx = self.out_combo.itemData(0)
                
        except Exception as e:
            print(f"Error enumerating devices: {e}")

    def filter_target_list(self, text):
        search_text = text.lower()
        for i in range(self.list_targets.count()):
            item = self.list_targets.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def reload_target_list(self):
        import os, glob
        if not hasattr(self, 'list_targets'): return
        self.list_targets.clear()
        target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                from PySide6.QtWidgets import QListWidgetItem
                name = os.path.basename(f)
                item = QListWidgetItem(name)
                item.setData(100, f)
                self.list_targets.addItem(item)
                
    def import_target_template(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        paths, _ = QFileDialog.getOpenFileNames(self, "Import Target CSV(s)", "", "CSV (*.csv *.txt)")
        if not paths: return
        target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
        os.makedirs(target_dir, exist_ok=True)
        imported = 0
        try:
            for path in paths:
                filename = os.path.basename(path)
                shutil.copy2(path, os.path.join(target_dir, filename))
                imported += 1
            QMessageBox.information(self, "Import Successful", f"Imported {imported} target curve(s) successfully.\nThey now appear in the Target dropdown.")
            self.reload_target_list()
            self.load_targets()
        except Exception as e:
            QMessageBox.critical(self, "Import Failed",
                "We couldn't import your target curve.\n\n"
                "Please check:\n"
                "• Is the file a valid CSV?\n"
                "• Does it have 'Frequency' and 'Magnitude' columns?\n\n"
                f"Technical detail: {e}")

    def export_target_template(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        item = self.list_targets.currentItem()
        if not item:
            QMessageBox.warning(self, "Nothing Selected", "Please select a target curve from the list first.")
            return
        src_path = item.data(100)
        filename = os.path.basename(src_path)
        dst_path, _ = QFileDialog.getSaveFileName(self, "Export Target", filename, "CSV (*.csv *.txt)")
        if not dst_path: return
        try:
            shutil.copy2(src_path, dst_path)
            QMessageBox.information(self, "Export Successful", "Target curve exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed",
                "We couldn't save the file.\n\n"
                "Please check:\n"
                "• Do you have write permissions for this folder?\n"
                "• Is there enough disk space?\n\n"
                f"Technical detail: {e}")

    def delete_target_template(self):
        from PySide6.QtWidgets import QMessageBox
        import os
        item = self.list_targets.currentItem()
        if not item:
            QMessageBox.warning(self, "Nothing Selected", "Please select a target curve from the list first.")
            return
        src_path = item.data(100)
        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{os.path.basename(src_path)}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(src_path)
                self.reload_target_list()
                self.load_targets()
            except Exception as e:
                QMessageBox.critical(self, "Couldn't Delete File",
                "We couldn't remove this target curve.\n\n"
                "Please check:\n"
                "• Is the file currently open in another program?\n"
                "• Do you have permission to delete it?\n\n"
                f"Technical detail: {e}")

    def backup_database(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import datetime
        import os
        
        default_name = f"inearsnitch_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.db"
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", default_name, "SQLite Database (*.db)")
        if not path: return
        
        try:
            shutil.copy2(self.db.db_path, path)
            QMessageBox.information(self, "Backup Saved", f"Database backed up to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed",
                "We couldn't create the database backup.\n\n"
                "Please check:\n"
                "• Do you have write permissions for the selected folder?\n"
                "• Is there enough free space on your drive?\n\n"
                f"Technical detail: {e}")

    def restore_database(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import shutil
        import os
        
        QMessageBox.warning(self, "Warning: This Will Overwrite Your Data",
            "Restoring a backup will OVERWRITE all current profiles and measurements.\n\n"
            "A safety copy of your current database will be created automatically before the restore.")
        
        path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database (*.db)")
        if not path: return
        
        try:
            # Create a safety backup of the current DB
            safety_path = self.db.db_path + ".safety.bak"
            if os.path.exists(self.db.db_path):
                shutil.copy2(self.db.db_path, safety_path)
                
            # Overwrite with the selected file
            shutil.copy2(path, self.db.db_path)
            
            QMessageBox.information(self, "Restore Successful", "Database restored successfully.\n\nInEar Snitch will now reload your profiles.")
            
            # Reload application state
            self.current_iem_id = None
            self.current_musician_name = None
            self.current_iem_name = None
            self.update_watermark()
            self.load_profiles_from_db()
            self.load_targets()
            
            self.active_card = None
            if self.profile_cards:
                self.force_profile_selection(self.profile_cards[0])
            
            if hasattr(self, 'page_hist') and hasattr(self.page_hist, 'table'):
                self.page_hist.table.setRowCount(0)
                
            self.switch_workspace_tab(0) # Go to profiles tab
            
        except Exception as e:
            QMessageBox.critical(self, "Restore Failed",
                "We couldn't restore your backup.\n\n"
                "Please check:\n"
                "• Is the selected file a valid InEar Snitch database (.db)?\n"
                "• Is the file corrupted?\n\n"
                f"Technical detail: {e}")

    def _run_level_calibration(self):
        """Auto-calibration: plays ascending test tones to find optimal output level."""
        if self.selected_in_idx is None or self.selected_out_idx is None:
            QMessageBox.warning(self, "Audio Not Set Up",
                "We don't know which devices to use yet.\n\n"
                "Please open Settings (top right) and select your Input and Output devices in the Routing tab before running Calibration.")
            return

        # Fully stop any running RTA/Depth — two sd.Stream() instances
        # on the same device cause a hang
        if getattr(self, 'live_worker', None) and self.live_worker.isRunning():
            self.btn_rta_raw.setChecked(False)
            self.btn_iec_guide.setChecked(False)
            self.toggle_live_seal(False)

        self.btn_auto_cal.setEnabled(False)
        self.btn_auto_cal.setText("Calibrating...")
        self.cal_results_lbl.show()
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        import numpy as np
        target_ch = "L" if self.get_current_channel() == "Left" else "R"
        
        # Ascending amplitude steps (safe range: 0.01 to 0.25)
        steps = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.25]
        results = []
        log_lines = []
        
        for amp in steps:
            try:
                # Play 200ms 1kHz tone at this amplitude
                n = int(0.2 * self.audio_engine.sample_rate)
                t = np.linspace(0, 0.2, n, False)
                tone = np.sin(2 * np.pi * 1000 * t) * amp
                # Fade
                fade = int(0.005 * self.audio_engine.sample_rate)
                tone[:fade] *= np.linspace(0, 1, fade)
                tone[-fade:] *= np.linspace(1, 0, fade)
                # Stereo routing
                tone_stereo = np.zeros((n, 2))
                if target_ch == 'L':
                    tone_stereo[:, 0] = tone
                else:
                    tone_stereo[:, 1] = tone
                
                import threading
                n_frames = len(tone_stereo)
                
                def run_stream(in_channels):
                    out_pos = 0
                    in_pos = 0
                    rec_buf = np.zeros((n_frames, in_channels))
                    event = threading.Event()

                    def callback(indata, outdata, frames, time, status):
                        nonlocal out_pos, in_pos
                        chunk = min(frames, n_frames - out_pos)
                        if chunk > 0:
                            outdata[:chunk] = tone_stereo[out_pos:out_pos+chunk]
                            out_pos += chunk
                        if chunk < frames:
                            outdata[chunk:] = 0.0
                            
                        r_chunk = min(frames, n_frames - in_pos)
                        if r_chunk > 0:
                            rec_buf[in_pos:in_pos+r_chunk] = indata[:r_chunk, :]
                            in_pos += r_chunk
                            
                        if out_pos >= n_frames and in_pos >= n_frames:
                            event.set()
                            raise sd.CallbackStop

                    with sd.Stream(device=(self.selected_in_idx, self.selected_out_idx),
                                   samplerate=self.audio_engine.sample_rate, channels=(in_channels, 2),
                                   callback=callback):
                        event.wait(timeout=1.0)
                    return rec_buf[:, 0:1]

                try:
                    rec = run_stream(1)
                except Exception:
                    in_chans = sd.query_devices(self.selected_in_idx)['max_input_channels']
                    rec = run_stream(in_chans)
                
                peak = np.max(np.abs(rec))
                peak_dbfs = 20 * np.log10(peak + 1e-12)
                results.append((amp, peak_dbfs))
                
                # Build VU bar
                bar_len = max(0, int((peak_dbfs + 60) / 60 * 20))
                bar = "█" * bar_len + "░" * (20 - bar_len)
                line = f"Amp {amp:.3f} ({20*np.log10(amp):.0f} dBFS) -> Rec: {peak_dbfs:+.1f} dBFS  {bar}"
                log_lines.append(line)
                self.cal_results_lbl.setText("\n".join(log_lines))
                QApplication.processEvents()
                
                # Safety stop: if recording is already near clipping, don't go louder
                if peak_dbfs > -4.0:
                    log_lines.append("-- Stopped: approaching clipping --")
                    self.cal_results_lbl.setText("\n".join(log_lines))
                    break
                    
            except Exception as e:
                log_lines.append(f"Amp {amp:.3f} -> ERROR: {e}")
                self.cal_results_lbl.setText("\n".join(log_lines))
                break
        
        # Find optimal amplitude: target recording peak at -15 dBFS
        if len(results) < 2:
            self.cal_status_lbl.setText("Calibration failed: not enough valid measurements.")
            self.cal_status_lbl.setStyleSheet("color: #ef4444; font-size: 11px; padding: 4px;")
            self.btn_auto_cal.setEnabled(True)
            self.btn_auto_cal.setText("Start Auto-Calibration")
            return
        
        # Interpolate to find amplitude that produces -15 dBFS recording
        amps = np.array([r[0] for r in results])
        peaks = np.array([r[1] for r in results])
        target_peak = -15.0
        
        if peaks[-1] < target_peak:
            # Even max amplitude doesn't reach target — use the loudest safe one
            optimal_amp = amps[-1]
            actual_peak = peaks[-1]
        elif peaks[0] > target_peak:
            # Even min amplitude is too loud — use the quietest one
            optimal_amp = amps[0]
            actual_peak = peaks[0]
        else:
            # Interpolate
            optimal_amp = float(np.interp(target_peak, peaks, amps))
            actual_peak = target_peak
        
        optimal_amp = min(optimal_amp, 0.25)  # Hard cap
        stress_amp = min(optimal_amp * 2.0, 0.25)  # +6 dB, capped
        rta_amp = min(optimal_amp * 1.5, 0.25)  # Pink noise slightly louder
        
        # Predict recording peaks
        stress_peak = actual_peak + 20 * np.log10(stress_amp / optimal_amp + 1e-12)
        
        # Save to audio engine
        self.audio_engine.calibrated_sweep_amp = optimal_amp
        self.audio_engine.calibrated_rta_amp = rta_amp
        self.audio_engine.calibrated_stress_amp = stress_amp
        self.audio_engine.calibration_rec_peak = actual_peak
        
        # Save to QSettings
        from PySide6.QtCore import QSettings
        s = QSettings("InEarSnitch", "InEarSnitchApp")
        s.setValue("audio/calibrated_sweep_amp", float(optimal_amp))
        s.setValue("audio/calibrated_rta_amp", float(rta_amp))
        s.setValue("audio/calibrated_stress_amp", float(stress_amp))
        s.setValue("audio/calibration_rec_peak", float(actual_peak))
        s.sync()
        
        # Update UI
        log_lines.append("")
        log_lines.append(f"--- RESULT ---")
        log_lines.append(f"Sweep Amplitude:  {optimal_amp:.4f} ({20*np.log10(optimal_amp):.1f} dBFS)")
        log_lines.append(f"RTA Amplitude:    {rta_amp:.4f} ({20*np.log10(rta_amp):.1f} dBFS)")
        log_lines.append(f"Stress Amplitude: {stress_amp:.4f} ({20*np.log10(stress_amp):.1f} dBFS)")
        log_lines.append(f"Expected Rec Peak: {actual_peak:.1f} dBFS")
        
        # Warn if recording level is too low for reliable measurements
        if actual_peak < -30.0:
            log_lines.append("")
            log_lines.append("⚠️ WARNING: Recording level is very low!")
            log_lines.append("   Increase your system output level and re-calibrate.")
            QMessageBox.warning(self, "Recording Level Too Low",
                f"The signal coming in from your microphone is very quiet ({actual_peak:.0f} dBFS).\n\n"
                "Your measurements may be noisy and unreliable.\n"
                "Please increase your interface's output level, then run Calibration again."
            )
        
        # Warn if stress test can't go louder than normal sweep
        if stress_amp <= optimal_amp * 1.1:
            log_lines.append("")
            log_lines.append("⚠️ WARNING: Stress Test is at the same level as normal sweep!")
            log_lines.append("   Rub & Buzz detection may be unreliable.")
            log_lines.append("   Increase system output level to enable proper stress testing.")
        
        self.cal_results_lbl.setText("\n".join(log_lines))
        
        self.cal_status_lbl.setText(
            f"Calibrated: Sweep={optimal_amp:.4f}, Stress={stress_amp:.4f}, "
            f"Rec Peak={actual_peak:.0f} dBFS"
        )
        self.cal_status_lbl.setStyleSheet("color: #22c55e; font-size: 11px; padding: 4px;")
        
        self.btn_auto_cal.setEnabled(True)
        self.btn_auto_cal.setText("Re-Calibrate")
        
        # Enable stress test button now that calibration exists
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_stress_test'):
            self.page_ana.btn_stress_test.setEnabled(True)
            self.page_ana.btn_stress_test.setToolTip(
                f"Run a high-level sweep ({stress_amp:.3f} amplitude) to detect Rub & Buzz."
            )

    def run_stress_test(self):
        """Run a high-amplitude sweep and extract HOHD for Rub & Buzz detection."""
        stress_amp = getattr(self.audio_engine, 'calibrated_stress_amp', None)
        if stress_amp is None:
            QMessageBox.warning(self, "Not Calibrated Yet",
                                "Please run Output Level Calibration first (in Settings → Calibration) before using the Stress Test.")
            return
        
        if self.is_measuring:
            return
        
        if self.selected_in_idx is None or self.selected_out_idx is None:
            QMessageBox.warning(self, "Audio Not Set Up",
                "We don't know which audio devices to use.\n\n"
                "Please open Settings (top right) and select your Input and Output devices before running the Stress Test.")
            return
        
        # Fully stop any running RTA/Depth to prevent audio stream conflicts
        if getattr(self, 'live_worker', None) and self.live_worker.isRunning():
            self.btn_rta_raw.setChecked(False)
            self.btn_iec_guide.setChecked(False)
            self.toggle_live_seal(False)

        # Confirmation
        reply = QMessageBox.question(
            self, "Run Rub & Buzz Test?",
            f"This plays a louder-than-normal sweep to detect driver defects (Rub & Buzz).\n\n"
            f"Make sure your IEM is seated in the coupler — do NOT wear it while measuring.\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        target_ch = "L" if self.get_current_channel() == "Left" else "R"
        
        # --- PREFLIGHT LEVEL CHECK (Stress Test) ---
        try:
            passed, peak_dbfs, pf_msg = self.audio_engine.preflight_check(
                self.selected_in_idx, self.selected_out_idx, target_ch
            )
            if not passed:
                reply = QMessageBox.warning(
                    self, "Level Check Failed",
                    f"{pf_msg}\n\nThe Stress Test uses a higher output level than normal sweeps.\n"
                    f"Running with incorrect levels will produce invalid results.\n\n"
                    f"Do you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
        except Exception as e:
            print(f"[PREFLIGHT] Skipped: {e}")
        
        # Warn if stress amp can't go louder than normal sweep
        cal_sweep = getattr(self.audio_engine, 'calibrated_sweep_amp', 0.1)
        if stress_amp <= cal_sweep:
            QMessageBox.warning(
                self, "Stress Test May Be Limited",
                "Your output level isn't high enough to push the IEM harder than a regular measurement.\n\n"
                "Rub & Buzz detection may be less reliable.\n\n"
                "To improve this, increase your interface's output level and run the Calibration again."
            )
        # --- END PREFLIGHT ---

        self.sub_lbl.setText("STRESS TEST running...")
        self.sub_lbl.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: bold;")
        self.page_ana.btn_stress_test.setEnabled(False)
        self.is_measuring = True
        self.stress_overlay.start(1) # 1 sweep
        self.stress_overlay.set_text("STRESS TEST")
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Run measurement in a thread
        class StressWorker(QThread):
            finished = Signal(object, object)
            error = Signal(str)
            sweep_progress = Signal(float, int)
            
            def __init__(self, engine, in_idx, out_idx, ch, amp):
                super().__init__()
                self.engine = engine
                self.in_idx = in_idx
                self.out_idx = out_idx
                self.ch = ch
                self.amp = amp
            
            def run(self):
                try:
                    f, m, p, ir, noise = self.engine.measure(
                        self.in_idx, self.out_idx, self.ch,
                        duration=3.0, f_start=20.0, f_end=20000.0,
                        amplitude=self.amp,
                        progress_callback=lambda t: self.sweep_progress.emit(t, 1))
                    hohd_f, hohd_db = self.engine.extract_hohd(ir, duration=3.0, noise_floor=noise)
                    self.finished.emit(hohd_f, hohd_db)
                except Exception as e:
                    self.error.emit(str(e))
        
        self._stress_worker = StressWorker(
            self.audio_engine, self.selected_in_idx, self.selected_out_idx,
            target_ch, stress_amp)
        self._stress_worker.finished.connect(self._on_stress_done)
        self._stress_worker.error.connect(self._on_stress_error)
        self._stress_worker.sweep_progress.connect(self.stress_overlay.update_anim_sync)
        self._stress_worker.start()

    def _on_stress_done(self, hohd_f, hohd_db):
        import numpy as np
        self.is_measuring = False
        self.page_ana.btn_stress_test.setEnabled(True)
        self.stress_overlay.stop()
        
        # Do NOT smooth the HOHD for display (sharp peaks are the signal)
        valid = (hohd_f > 20) & (hohd_f < 10000)
        if np.any(valid):
            f_centers = hohd_f[valid]
            hohd_raw = hohd_db[valid]
            
            # Map HOHD (dB) directly to THD (%) scale for accurate reading on the Y-axis
            # Formula: 10^(dB/20) * 100
            hohd_display = np.clip(10 ** (hohd_raw / 20) * 100, 0, 10)
            self.page_ana.hohd_line.setData(np.log10(f_centers), hohd_display)
            self.page_ana.hohd_line.show()
            
            if len(f_centers) == 0:
                self.sub_lbl.setText("Stress Test complete — no usable signal detected. Try reseating the IEM in the coupler.")
                return
                
            peak_idx = np.argmax(hohd_raw)
            peak_hohd = hohd_raw[peak_idx]
            peak_freq = f_centers[peak_idx]
            
            # Relaxed thresholds for live concert environments (ambient noise tolerant)
            if peak_hohd > -30:
                status = "FAIL"
                color = "#ef4444"
            elif peak_hohd > -40:
                status = "WARN"
                color = "#f59e0b"
            else:
                status = "PASS"
                color = "#22c55e"
            
            self.sub_lbl.setText(f"Stress Test: {status} (Peak: {peak_hohd:.0f} dB)")
            self.sub_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            
            # Create a Diagnostic Card for the right pane
            report_item = {
                'title': 'Stress Test (Rub & Buzz)',
                'status': status,
                'desc': f"Peak HOHD: {peak_hohd:.0f} dB at {peak_freq:.0f} Hz.",
                'band': (peak_freq * 0.8, peak_freq * 1.2),
                'category': 'THD'
            }
            
            # Filter out old stress test reports and prepend the new one
            if hasattr(self.page_ana, '_last_report'):
                self.page_ana._last_report = [r for r in self.page_ana._last_report if r['title'] != 'Stress Test (Rub & Buzz)']
                self.page_ana._last_report.insert(0, report_item)
            else:
                self.page_ana._last_report = [report_item]
                
            self.page_ana.render_diagnostics()
            
            # Auto-zoom the THD graph to the problem area
            self.page_ana.thd_widget.setXRange(np.log10(peak_freq * 0.5), np.log10(peak_freq * 2.0), padding=0.1)
            
        else:
            self.sub_lbl.setText("Stress Test complete — no usable signal detected. Try reseating the IEM in the coupler.")
    
    def _on_stress_error(self, msg):
        from PySide6.QtWidgets import QMessageBox
        self.is_measuring = False
        self.stress_overlay.stop()
        self.page_ana.btn_stress_test.setEnabled(True)
        self.sub_lbl.setText("Stress Test failed — check your audio interface connection and try again.")
        self.sub_lbl.setStyleSheet("color: #ef4444; font-size: 12px;")
        QMessageBox.critical(self, "Stress Test Stopped",
            "The Rub & Buzz test ran into an audio problem.\n\n"
            "Please check:\n"
            "• Is your IEM securely seated in the coupler?\n"
            "• Is your audio interface connected and turned on?\n"
            "• Are the correct devices selected in Settings → Routing?\n\n"
            f"Technical detail: {msg}")


    def save_settings(self):
        from PySide6.QtCore import QSettings
        self.selected_in_idx = self.in_combo.currentData()
        self.selected_out_idx = self.out_combo.currentData()

        s = QSettings("InEarSnitch", "InEarSnitchApp")
        s.setValue("audio/input_device_name",  self.in_combo.currentText())
        s.setValue("audio/output_device_name", self.out_combo.currentText())
        s.setValue("audio/auto_normalize", self.chk_normalize.isChecked())
        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")
        s.setValue("audio/spl_offset_db",      getattr(self, "spl_offset_db", 0.0))
        s.sync()

        # Close the slide-out panel automatically upon saving
        self.settings_panel.setVisible(False)
        if hasattr(self, 'settings_dimmer'):
            self.settings_dimmer.setVisible(False)
            
        self.settings_save_lbl.setText("Saved")
        QTimer.singleShot(2500, lambda: self.settings_save_lbl.setText(""))

    def _load_settings(self):
        """Restore persisted settings at startup."""
        from PySide6.QtCore import QSettings
        s = QSettings("InEarSnitch", "InEarSnitchApp")

        saved_in  = s.value("audio/input_device_name",  "")
        saved_out = s.value("audio/output_device_name", "")
        saved_norm = s.value("audio/auto_normalize", True, type=bool)
        self.chk_normalize.setChecked(saved_norm)
        saved_cal = s.value("audio/coupler_cal_path", None)
        saved_spl = float(s.value("audio/spl_offset_db", 0.0))

        # Restore input device
        if saved_in:
            idx = self.in_combo.findText(saved_in)
            if idx >= 0:
                self.in_combo.setCurrentIndex(idx)
                self.selected_in_idx = self.in_combo.itemData(idx)

        # Restore output device
        if saved_out:
            idx = self.out_combo.findText(saved_out)
            if idx >= 0:
                self.out_combo.setCurrentIndex(idx)
                self.selected_out_idx = self.out_combo.itemData(idx)

        # Restore coupler calibration
        if saved_cal is not None:
            self.reload_calibrations(select_path=saved_cal)
            self.update_cal_preview()

        # Restore SPL offset
        if abs(saved_spl) > 0.01:
            self.spl_offset_db = saved_spl
            self._on_spl_offset_changed(saved_spl)

        # Restore level calibration
        cal_sweep = s.value("audio/calibrated_sweep_amp", None)
        if cal_sweep is not None:
            cal_sweep = float(cal_sweep)
            cal_rta = float(s.value("audio/calibrated_rta_amp", cal_sweep * 1.5))
            cal_stress = float(s.value("audio/calibrated_stress_amp", cal_sweep * 2.0))
            cal_peak = float(s.value("audio/calibration_rec_peak", -15.0))
            self.audio_engine.calibrated_sweep_amp = cal_sweep
            self.audio_engine.calibrated_rta_amp = cal_rta
            self.audio_engine.calibrated_stress_amp = cal_stress
            self.audio_engine.calibration_rec_peak = cal_peak
            if hasattr(self, 'cal_status_lbl'):
                self.cal_status_lbl.setText(
                    f"Calibrated: Sweep={cal_sweep:.4f}, Stress={cal_stress:.4f}, "
                    f"Rec Peak={cal_peak:.0f} dBFS"
                )
                self.cal_status_lbl.setStyleSheet("color: #22c55e; font-size: 11px; padding: 4px;")
                self.btn_auto_cal.setText("Re-Calibrate")
            if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_stress_test'):
                self.page_ana.btn_stress_test.setEnabled(True)
                self.page_ana.btn_stress_test.setToolTip(
                    f"Run a high-level sweep ({cal_stress:.3f} amplitude) to detect Rub & Buzz."
                )

    def _on_spl_offset_changed(self, offset_db):
        """Receive new SPL offset and update graph axis label."""
        self.spl_offset_db = offset_db
        if abs(offset_db) > 0.1:
            self.plot_widget.setLabel('left', f'Level (dB SPL, cal: {offset_db:+.1f}dB)')
        else:
            self.plot_widget.setLabel('left', 'Level (dBFS, uncalibrated)')
        if self.temp_freqs is not None:
            self.redraw_graph()




    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QScrollBar:vertical { border: none; background: #111; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #444; border-radius: 4px; }
        """)

    def open_add_profile_dialog(self):
        dialog = AddProfileDialog(self.db, self)
        if dialog.exec():
            self.load_profiles_from_db()

    def load_profiles_from_db(self):
        # Clear existing cards
        while self.profile_list_layout.count():
            item = self.profile_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.profile_cards = []
        
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, band, profile_pic FROM Musicians ORDER BY id DESC")
        musicians = cursor.fetchall()
        
        for m_id, name, band, pic in musicians:
            cursor.execute("SELECT id, model_name, iem_pic, abbreviation, custom_name, color FROM IEM_Models WHERE musician_id = ?", (m_id,))
            iems = cursor.fetchall()
            if not iems:
                iems = [(-1, "Unknown IEM", "", "", "", "#2a2a2a")]
                
            card = MusicianCard(name or "Unknown", band or "", iems, profile_pic=pic)
            card.m_id = m_id
            self.profile_list_layout.addWidget(card)
            self.profile_cards.append(card)
            
            card.iem_changed.connect(lambda c=card: self.force_profile_selection(c))
            
            # Allow clicking the card itself to select it
            def make_click(c):
                def handler(event):
                    self.force_profile_selection(c)
                return handler
            card.mousePressEvent = make_click(card)
            
        self.profile_list_layout.addStretch()
        conn.close()

    def force_profile_selection(self, card):
        import theme
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            from PySide6.QtGui import QColor
            
            for c in self.profile_cards:
                is_sel = (c == card)
                if is_sel:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #e4e4e7; border-radius: 8px; border: 2px solid #0284c7; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #3f3f46; border-radius: 8px; border: 2px solid #00FFFF; outline: none; }")
                else:
                    if theme.CURRENT_MODE == "light":
                        c.setStyleSheet("#musicianCardObj { background-color: #ffffff; border-radius: 8px; border: none; outline: none; }")
                    else:
                        c.setStyleSheet("#musicianCardObj { background-color: #2d2d34; border-radius: 8px; border: none; outline: none; }")
                
                if is_sel:
                    shadow = QGraphicsDropShadowEffect(c)
                    if theme.CURRENT_MODE == "light":
                        shadow.setBlurRadius(20)
                        shadow.setColor(QColor(0, 0, 0, 70))
                        shadow.setOffset(0, 6)
                    else:

                        # Subtle cyan glow in dark mode for elegant 3D lift
                        shadow.setBlurRadius(30)
                        shadow.setColor(QColor(0, 255, 255, 40))
                        shadow.setOffset(0, 0)
                    c.setGraphicsEffect(shadow)
                else:
                    c.setGraphicsEffect(None)
                    
            self.on_profile_selected(card)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Couldn't Load Profile",
                "We couldn't switch to this profile. Please try clicking on it again.\n\n"
                "If this keeps happening, restart the app.\n\n"
                f"Technical detail: {str(e)}")



    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Dynamically adjust L/R button padding to prevent text clipping while keeping them large on big screens
        if hasattr(self, 'btn_l') and hasattr(self, 'btn_r'):
            if event.size().width() < 1000:
                self.btn_l.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-left-radius: 6px; border-bottom-left-radius: 6px; border-right: none; padding: 12px 10px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #16a34a; color: white; border-color: #16a34a; }")
                self.btn_r.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-right-radius: 6px; border-bottom-right-radius: 6px; padding: 12px 10px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #dc2626; color: white; border-color: #dc2626; }")
            else:
                self.btn_l.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-left-radius: 6px; border-bottom-left-radius: 6px; border-right: none; padding: 12px 28px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #16a34a; color: white; border-color: #16a34a; }")
                self.btn_r.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; border-top-right-radius: 6px; border-bottom-right-radius: 6px; padding: 12px 28px; font-weight: bold; font-size: 14px; } QPushButton:checked { background-color: #dc2626; color: white; border-color: #dc2626; }")

        if hasattr(self, 'settings_dimmer'):
            self.settings_dimmer.setGeometry(0, 0, self.width(), self.height())

            
        if hasattr(self, 'settings_panel') and self.settings_panel is not None:
            cw_width = self.centralWidget().width() if self.centralWidget() else self.width()
            cw_height = self.centralWidget().height() if self.centralWidget() else self.height()
            self.settings_panel.setGeometry(
                cw_width - self.settings_panel.width(),
                40, # top bar height approximation
                self.settings_panel.width(),
                cw_height - 40
            )


    def on_target_channel_changed(self):
        import pyqtgraph as pg
        import theme
        if hasattr(self, 'live_worker') and self.live_worker.running:
            self.live_worker.set_target_channel(self.get_current_channel())
            color = theme.get_color('curve_left') if self.get_current_channel() == "Left" else theme.get_color('curve_right')
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                self.live_rta_line.setPen(pg.mkPen(color, width=2))

    def get_current_channel(self):
        if hasattr(self, 'btn_grp_chan'):
            btn = self.btn_grp_chan.checkedButton()
            if btn:
                txt = btn.text().strip()
                if txt in ("L", "Left"): return "Left"
                if txt in ("R", "Right"): return "Right"
                return txt
        return "Left"
        
    def get_current_sweeps(self):
        if hasattr(self, 'btn_grp_sweeps'):
            btn = self.btn_grp_sweeps.checkedButton()
            return btn.text() if btn else "1x"
        return "1x"

    def update_watermark(self):
        if not hasattr(self, 'watermark_item'): return
        chan = self.get_current_channel()
        if hasattr(self, 'current_iem_name') and hasattr(self, 'current_musician_name'):
            name_text = f"{self.current_iem_name} - {self.current_musician_name}" if self.current_iem_name else self.current_musician_name
            if hasattr(self, 'lbl_active_profile'):
                self.lbl_active_profile.setText(f"Profile: {self.current_musician_name}  |  IEM: {self.current_iem_name}")
                self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold;")
            self.watermark_item.setHtml(f'<div style="color: {theme.get_color("watermark")}; font-size: 32px; font-weight: bold; line-height: 1.2;"><center>{name_text}<br>{chan}</center></div>')
        else:
            self.watermark_item.setHtml(f'<div style="color: {theme.get_color("watermark")}; font-size: 32px; font-weight: bold; line-height: 1.2;"><center>NO PROFILE<br>{chan}</center></div>')

    def apply_dynamic_theme_styles(self):
        bg = theme.get_color('pg_bg')
        fg = theme.get_color('pg_fg')
        
        plots = [self.plot_widget]
        if hasattr(self, 'page_ana'):
            plots.extend([self.page_ana.plot_widget, self.page_ana.thd_widget, self.page_ana.csd_widget])
            
        for p in plots:
            p.setBackground(bg)
            p.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
            ax_l = p.getAxis('left')
            ax_b = p.getAxis('bottom')
            if ax_l:
                ax_l.setPen(fg)
                ax_l.setTextPen(fg)
            if ax_b:
                ax_b.setPen(fg)
                ax_b.setTextPen(fg)
                
            if hasattr(p, 'titleLabel') and p.titleLabel.text:
                p.setTitle(p.titleLabel.text, color=fg, size="14pt")
        
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'update_theme'):
            self.page_ana.update_theme()
            
        panel_bg = theme.get_color('bg_panel')
        border = theme.get_color('border')
        if hasattr(self, 'control_panel'):
            self.control_panel.setStyleSheet(f"#ControlPanel {{ background-color: {panel_bg}; border: 1px solid {border}; border-radius: 4px; }}")
            
        if hasattr(self, 'active_tour') and self.active_tour is not None:
            self.active_tour.update_theme()

        # --- FULL REFRESH OF F-STRING STYLES ---
        if hasattr(self, 'page_set'):
            self.page_set.setStyleSheet(f"#SettingsPanel {{ background-color: {theme.get_color('bg_panel')}; border-left: 1px solid {theme.get_color('border')}; }}")
        if hasattr(self, 'manual_browser'):
            self.manual_browser.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; border: 1px solid {theme.get_color('border')}; border-radius: 4px; padding: 10px;")
        if hasattr(self, 'console_output'):
            self.console_output.setStyleSheet(f"background-color: {theme.get_color('bg_main')}; color: {theme.get_color('text_primary')}; font-family: 'Courier New', Courier, monospace; font-size: 11px; padding: 5px; border: 1px solid {theme.get_color('border')}; border-radius: 4px;")
        
        # Refresh main tabs
        if hasattr(self, 'workspace_stacked'):
            self.switch_workspace_tab(self.workspace_stacked.currentIndex())

    def on_theme_toggle(self):
        theme.toggle_theme(self)
        self.apply_dynamic_theme_styles()
        self.update_watermark()
        self.redraw_graph()
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        self.repaint()
        
        # Re-apply card inline styles for the new theme
        active_card = None
        for c in self.profile_cards:
            if c.property("selected") == "true":
                active_card = c
            # Update AvatarButtons for the new theme
            for b_id, b in getattr(c, 'avatar_btns', []):
                b.update_style(b.property("selected") == "true")
                
        if active_card:
            self.force_profile_selection(active_card)

    def on_profile_selected(self, card=None):
        if not card: return
        self.active_card = card
        
        # UI Hardening: silently block profile switches during an active sweep
        if getattr(self, 'is_measuring', False):
            self.sub_lbl.setText("Measurement in progress — please wait before switching profiles.")
            self.sub_lbl.setStyleSheet("color: #FF8C00; font-size: 12px; font-weight: bold;")
            return
            
        # Clear styling from ALL OTHER CARDS, and restore active card
        for c in self.profile_cards:
            if c != card:
                for b_id, b in getattr(c, 'avatar_btns', []):
                    b.update_style(False)
            else:
                for b_id, b in getattr(c, 'avatar_btns', []):
                    b.update_style(b_id == getattr(c, 'current_iem_id', -1))
                    
        if card:
            name = card.name
            iem = card.current_iem_name
            iem_id = card.current_iem_id
            
            self.current_iem_name = iem
            self.current_musician_name = name
            self.update_watermark()
            from datetime import datetime
            self.sub_lbl.setText("Status: Ready to measure.")
            self.current_iem_id = iem_id
            
            # ProKit: auto-suggest last used tip for current IEM
            self.suggest_tip_for_current_iem()
            
            # Enable buttons since a profile is selected
            self.btn_capture.setEnabled(True)
            if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
            self.btn_save_db.setEnabled(True)
            
            # Fetch extra data for header
            import sqlite3
            
            # --- AUTO-SELECT TARGET CURVE ---
            if iem:
                best_match_idx = -1
                for i in range(1, self.cb_meas_target.count()):
                    tgt_name = self.cb_meas_target.itemText(i).lower()
                    if iem.lower() in tgt_name or tgt_name in iem.lower():
                        best_match_idx = i
                        break
                if best_match_idx != -1:
                    self.cb_meas_target.setCurrentIndex(best_match_idx)
                else:
                    self.cb_meas_target.setCurrentIndex(0)
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute("SELECT notes, profile_pic, id FROM Musicians WHERE name = ?", (name,))
            row = c.fetchone()
            conn.close()
            
            m_id = None
            if row:
                notes, pic, m_id = row
                if notes:
                    self.notes_lbl.setText(f'"{notes}"')
                    self.notes_lbl.setVisible(True)
                else:
                    self.notes_lbl.setVisible(False)
                    
                if pic:
                    from PySide6.QtGui import QImageReader, QPixmap
                    from profile_ui import create_circular_pixmap
                    reader = QImageReader(pic)
                    reader.setAutoTransform(True)
                    circ = create_circular_pixmap(reader, 80)
                    if circ:
                        self.header_pic.setPixmap(circ)
                        self.header_pic.setStyleSheet("background-color: transparent;")
                    else:
                        self.header_pic.clear()
                        self.header_pic.setStyleSheet("background-color: #333; border-radius: 40px;")
                else:
                    self.header_pic.clear()
                    self.header_pic.setStyleSheet("background-color: #333; border-radius: 40px;")
            else:
                self.header_pic.clear()
                self.header_pic.setStyleSheet("background-color: #333; border-radius: 40px;")
            
            # Refresh active tab
            if self.workspace_stacked.currentIndex() == 0 and hasattr(self.page_prof, 'load_profile'):
                self.page_prof.load_profile(iem_id, m_id)
            elif self.workspace_stacked.currentIndex() == 3 and hasattr(self.page_hist, 'load_history'):
                self.page_hist.load_history(m_id)

    def delete_profile(self):
        if not self.current_iem_id:
            self.sub_lbl.setText("No profile selected. Click a profile in the sidebar first.")
            self.sub_lbl.setStyleSheet("color: red; font-size: 13px;")
            return
        # UI Hardening: prevent deletion while sweep is running
        if self.is_measuring:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Measurement Running",
                "A measurement is currently running.\n\n"
                "Please wait for it to finish before deleting a profile.")
            return
        # Simple inline deletion to avoid modal question box
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Measurements WHERE iem_id = ?", (self.current_iem_id,))
        cursor.execute("DELETE FROM IEM_Models WHERE id = ?", (self.current_iem_id,))
        conn.commit()
        conn.close()


    def edit_profile(self):
        if not self.current_iem_id:
            return
            
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT m.name, m.band, i.model_name, m.id, m.profile_pic, m.notes 
            FROM IEM_Models i 
            JOIN Musicians m ON i.musician_id = m.id 
            WHERE i.id = ?
        ''', (self.current_iem_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return
            
        old_name, old_band, old_model, mus_id, old_pic, old_notes = row
        
        from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QPushButton, QTextEdit, QFileDialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Profile")
        dlg.setStyleSheet("background-color: #222; color: white;")
        layout = QFormLayout(dlg)
        
        le_name = QLineEdit(old_name)
        le_band = QLineEdit(old_band)
        le_model = QLineEdit(old_model)
        for le in [le_name, le_band, le_model]:
            le.setStyleSheet("background: #111; border: 1px solid #444; padding: 4px;")
            
        te_notes = QTextEdit(old_notes if old_notes else "")
        te_notes.setStyleSheet("background: #111; border: 1px solid #444; padding: 4px;")
        te_notes.setFixedHeight(60)
            
        btn_pic = QPushButton("Select Image" if not old_pic else "Change Image")
        btn_pic.setToolTip("Select or change profile image")
        btn_pic.setStyleSheet("background-color: #333; padding: 5px;")
        selected_pic = [old_pic]
        
        def choose_pic():
            path, _ = QFileDialog.getOpenFileName(dlg, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
            if path:
                selected_pic[0] = path
                btn_pic.setText("Image Selected")
                btn_pic.setStyleSheet("background-color: #008800;")
                
        btn_pic.clicked.connect(choose_pic)
            
        layout.addRow("Musician Name:", le_name)
        layout.addRow("Band / Role:", le_band)
        layout.addRow("IEM Model:", le_model)
        layout.addRow("Profile Picture:", btn_pic)
        layout.addRow("Notes:", te_notes)
        
        bbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bbox.accepted.connect(dlg.accept)
        bbox.rejected.connect(dlg.reject)
        layout.addRow(bbox)
        
        if dlg.exec():
            new_name = le_name.text().strip()
            new_band = le_band.text().strip()
            new_model = le_model.text().strip()
            new_notes = te_notes.toPlainText().strip()
            new_pic = selected_pic[0]
            
            if new_name and new_model:
                c.execute("UPDATE Musicians SET name=?, band=?, notes=?, profile_pic=? WHERE id=?", (new_name, new_band, new_notes, new_pic, mus_id))
                c.execute("UPDATE IEM_Models SET model_name=? WHERE id=?", (new_model, self.current_iem_id))
                conn.commit()
                self.load_profiles_from_db()
                
        conn.close()
        self.load_profiles_from_db()
        self.plot_widget.clear()
        
        self.sub_lbl.setText("Profile deleted successfully.")
        self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 13px;")
        self.current_iem_id = None
        self.settings_panel = None

    def run_compare(self):
        if not self.current_iem_id:
            return
            
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('SELECT frequencies, magnitude_l, magnitude_r, gain_db FROM Measurements WHERE iem_id = ? ORDER BY timestamp DESC LIMIT 1', (self.current_iem_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            self.sub_lbl.setText("No previous measurements found for this IEM yet — run a measurement first!")
            self.sub_lbl.setStyleSheet("color: yellow; font-size: 13px;")
            return
            
        import numpy as np
        try:
            self.ref_freqs = np.frombuffer(row[0], dtype=np.float64)
            self.ref_mag_l = np.frombuffer(row[1], dtype=np.float64) if row[1] else None
            self.ref_mag_r = np.frombuffer(row[2], dtype=np.float64) if row[2] else None
            gain_db = row[3] if row[3] else "Unknown"
            
            self.redraw_graph()
            
            self.sub_lbl.setText(f"Compare trace loaded. (Ref Gain: {gain_db})")
            self.sub_lbl.setStyleSheet("color: #888; font-size: 12px;")
        except Exception as e:
            log_debug(f"Error parsing ref trace: {str(e)}")

    def reset_graph_view(self):
        import numpy as np
        self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0)
        self.plot_widget.setYRange(40, 120, padding=0)
        if hasattr(self, 'page_ana'):
            self.page_ana.reset_zoom()

    def clear_trace(self):
        self.plot_widget.clear()
        self.temp_freqs = None
        self.temp_mag_l = None
        self.temp_mag_r = None
        self.temp_phase_l = None
        self.temp_phase_r = None
        self.temp_ir_l = None
        self.temp_ir_r = None
        self.ref_freqs = None
        self.ref_mag_l = None
        self.ref_mag_r = None
        self.temp_thd_data = None
        self.temp_csd_data = None
        self.plot_target_curve()
        self.update_analysis_view()
        self.sub_lbl.setText("Trace cleared.")
        self.sub_lbl.setStyleSheet("color: #888; font-size: 12px;")

    def on_meas_target_changed(self, index=None):
        self.page_ana.cb_ana_target.blockSignals(True)
        self.page_ana.cb_ana_target.setCurrentIndex(self.cb_meas_target.currentIndex())
        self.page_ana.cb_ana_target.blockSignals(False)
        self._apply_target_selection(self.cb_meas_target.currentData())
        
    def on_ana_target_changed(self, index=None):
        self.cb_meas_target.blockSignals(True)
        self.cb_meas_target.setCurrentIndex(self.page_ana.cb_ana_target.currentIndex())
        self.cb_meas_target.blockSignals(False)
        self._apply_target_selection(self.page_ana.cb_ana_target.currentData())
        
    def _parse_csv_file(self, path):
        import numpy as np
        f_list, m_list = [], []
        try:
            with open(path, 'r', encoding='utf-8-sig') as file:
                for line in file:
                    parts = line.replace(';', ',').split(',')
                    if len(parts) >= 2:
                        try:
                            freq = float(parts[0].strip())
                            mag = float(parts[1].strip())
                            f_list.append(freq)
                            m_list.append(mag)
                        except ValueError:
                            pass
            if len(f_list) > 10:
                return np.array(f_list), np.array(m_list)
        except Exception as e:
            print(f"Error parsing file {path}: {e}")
        return None, None

    def _apply_target_selection(self, data):
        self.target_freqs = None
        self.target_mags = None
        if data:
            self.target_freqs, self.target_mags = self._parse_csv_file(data)
        self.plot_target_curve()
        self.update_analysis_view()

    def on_meas_history_changed(self, index=None):
        self.page_ana.cb_ana_history.blockSignals(True)
        self.page_ana.cb_ana_history.setCurrentIndex(self.cb_meas_history.currentIndex())
        self.page_ana.cb_ana_history.blockSignals(False)
        self._apply_history_selection(self.cb_meas_history.currentData())
        
    def on_ana_history_changed(self, index=None):
        self.cb_meas_history.blockSignals(True)
        self.cb_meas_history.setCurrentIndex(self.page_ana.cb_ana_history.currentIndex())
        self.cb_meas_history.blockSignals(False)
        self._apply_history_selection(self.page_ana.cb_ana_history.currentData())
        
    def _apply_history_selection(self, data):
        self.history_freqs = None
        self.history_mag_l = None
        self.history_mag_r = None
        if data:
            import numpy as np
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute('SELECT frequencies, magnitude_l, magnitude_r FROM Measurements WHERE id=?', (data,))
            row = c.fetchone()
            conn.close()
            if row:
                import json
                self.history_freqs = np.frombuffer(row[0], dtype=np.float64)
                if row[1]: self.history_mag_l = np.frombuffer(row[1], dtype=np.float64)
                if row[2]: self.history_mag_r = np.frombuffer(row[2], dtype=np.float64)
        self.plot_target_curve()
        self.update_analysis_view()
        
    def on_global_history_changed(self, index=None):
        data = self.cb_global_history.currentData()
        self.history_freqs = None
        self.history_mag_l = None
        self.history_mag_r = None
        if data:
            import numpy as np
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute('SELECT frequencies, magnitude_l, magnitude_r FROM Measurements WHERE id=?', (data,))
            row = c.fetchone()
            conn.close()
            if row:
                import json
                self.history_freqs = np.frombuffer(row[0], dtype=np.float64)
                if row[1]: self.history_mag_l = np.frombuffer(row[1], dtype=np.float64)
                if row[2]: self.history_mag_r = np.frombuffer(row[2], dtype=np.float64)
        self.plot_target_curve()
        self.update_analysis_view()

    def on_rta_helper_toggled(self):
        if not getattr(self, 'live_worker', None) or not self.live_worker.isRunning():
            return
        if self.btn_iec_guide.isChecked():
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                self.rta_target_region.show()
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                self.rta_peak_line.show()
            if hasattr(self, 'rta_big_lbl') and self.rta_big_lbl is not None:
                self.rta_big_lbl.show()
        else:
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                self.rta_target_region.hide()
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                self.rta_peak_line.hide()
            if hasattr(self, 'rta_big_lbl') and self.rta_big_lbl is not None:
                self.rta_big_lbl.hide()

    def on_rta_button_clicked(self):
        sender = self.sender()
        
        if sender == self.btn_rta_raw:
            if self.btn_rta_raw.isChecked():
                self.btn_iec_guide.setChecked(False)
        else:
            if self.btn_iec_guide.isChecked():
                self.btn_rta_raw.setChecked(False)
                
        is_active = self.btn_rta_raw.isChecked() or self.btn_iec_guide.isChecked()
        is_running = getattr(self, 'live_worker', None) and self.live_worker.isRunning()
        
        if is_active and not is_running:
            # Force jump to Workspace Freq Response tab so the live graph is visible
            self.switch_workspace_tab(2)
            if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'graph_tabs'):
                self.page_ana.graph_tabs.setCurrentIndex(0)
            self.toggle_live_seal(True)
        elif not is_active and is_running:
            self.toggle_live_seal(False)
        elif is_active and is_running:
            self.on_rta_helper_toggled()
            
    def toggle_live_seal(self, checked):
        from PySide6.QtWidgets import QMessageBox
        import pyqtgraph as pg
        if checked:
            if self.selected_in_idx is None or self.selected_out_idx is None:
                QMessageBox.warning(self, "Audio Not Set Up",
                "We can't hear anything!\n\n"
                "Please open Settings (top right) and select your Input and Output devices first.")
                self.btn_rta_raw.setChecked(False)
                self.btn_iec_guide.setChecked(False)
                return
            
            cal_f, cal_m = None, None
            cal_path = self.mic_cal_combo.currentData()
            if cal_path:
                cal_f, cal_m = self._parse_csv_file(cal_path)

            self.sub_lbl.setText("Status: LIVE SEAL CHECK (Pink Noise)")
            self.sub_lbl.setStyleSheet("color: #db2777; font-size: 13px; font-weight: bold;")
            self.btn_capture.setEnabled(False)
            
            target_plot = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    target_plot.removeItem(self.live_rta_line)
                except Exception:
                    pass
            color = theme.get_color('curve_left') if self.get_current_channel() == "Left" else theme.get_color('curve_right')
            self.live_rta_line = target_plot.plot(pen=pg.mkPen(color, width=2), name="Live Seal")
            self.live_rta_line.show()
            
            import numpy as np
            from PySide6.QtCore import Qt
            if not hasattr(self, 'rta_target_region') or self.rta_target_region is None:
                self.rta_target_region = pg.LinearRegionItem(
                    values=[np.log10(7000), np.log10(8600)], 
                    movable=False, 
                    brush=pg.mkBrush(16, 185, 129, 35),
                    pen=pg.mkPen('#10b981', width=1, style=Qt.DashLine)
                )
                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)
            
            if not self.btn_iec_guide.isChecked():
                self.rta_target_region.hide()
            
            if not hasattr(self, 'rta_peak_line') or self.rta_peak_line is None:
                self.rta_peak_line = pg.InfiniteLine(angle=90, movable=False)
                self.rta_peak_line.setZValue(20)
                target_plot.addItem(self.rta_peak_line)
            self.rta_peak_line.hide()
            self.switch_workspace_tab(2)
            if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'graph_tabs'):
                self.page_ana.graph_tabs.setCurrentIndex(0)
            target_plot.update()
            target_plot.repaint()
            
            # Reset all EMA state so curve doesn't drift from top
            for attr in ('_rta_shift', '_max_rta_mean', '_iec_smooth_mags',
                         '_iec_status_counter', '_iec_last_ok'):
                if hasattr(self, attr):
                    delattr(self, attr)
            self._rta_warmup = 0  # Suppress seal diagnostics for first 30 frames (~1s)
            
            self.live_worker = LiveSealWorker(self.selected_in_idx, self.selected_out_idx, cal_f, cal_m, target_channel=self.get_current_channel())
            # Pass calibrated amplitude so pink noise matches calibrated sweep level
            cal_amp = getattr(self.audio_engine, 'calibrated_sweep_amp', 0.15)
            self.live_worker._cal_amp = cal_amp
            self.live_worker.update_signal.connect(self.update_live_rta)
            self.live_worker.error.connect(self.on_measurement_error)
            self.live_worker.start()
        else:
            if hasattr(self, 'live_worker'):
                self.live_worker.stop()
                if not self.live_worker.wait(2000):  # 2s timeout
                    self.live_worker.terminate()
                    self.live_worker.wait(1000)
            if hasattr(self, 'rta_big_lbl'):
                self.rta_big_lbl.hide()
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.live_rta_line)
                except Exception:
                    pass
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_target_region)
                except Exception:
                    pass
                self.rta_target_region = None
                
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_peak_line)
                except Exception:
                    pass
                self.rta_peak_line = None
            self.sub_lbl.setText("Status: Ready to measure.")
            self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 13px;")
            self.btn_capture.setEnabled(True)

    def update_live_rta(self, freqs, mag_db):
        import numpy as np
        mask = (freqs >= 20) & (freqs <= 20000)
        
        mask_1k = (freqs >= 500) & (freqs <= 2000)
        current_mean = np.mean(mag_db[mask_1k])
        target_db = 85.0
        calculated_shift = target_db - current_mean
        
        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            # Fast adaptation (~0.5s convergence) so level settles quickly
            self._rta_shift = 0.92 * self._rta_shift + 0.08 * calculated_shift
            
        self.live_rta_line.setData(freqs[mask], mag_db[mask] + self._rta_shift)
        
        # --- Live IEC 711 Positioning Diagnostics ---
        # Skip diagnostics during warmup (~1 second) while EMA settles
        warmup = getattr(self, '_rta_warmup', 0)
        if warmup < 30:
            self._rta_warmup = warmup + 1
            return
        try:
            # Detect if IEM is pulled out (massive drop in volume from recent peak)
            if not hasattr(self, '_max_rta_mean'):
                self._max_rta_mean = current_mean
            
            # Slowly decay the peak tracking; cap upward jumps to 2 dB/frame
            # so single-frame transients (mic taps, cable bumps) can't spike it
            if current_mean > self._max_rta_mean:
                self._max_rta_mean = min(current_mean, self._max_rta_mean + 2.0)
            else:
                # Fast decay (~1 second recovery)
                self._max_rta_mean = 0.95 * self._max_rta_mean + 0.05 * current_mean

            if current_mean < self._max_rta_mean - 25.0:
                # Signal dropped by > 25dB compared to recent max → IEM removed
                seal_html = "<span style='color: #a8a29e; font-weight: bold;'>IEM Not Detected (Silence)</span>"
                depth_html = ""
                if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                    self.rta_peak_line.hide()
            else:
                # 1. Depth (8kHz peak) — EMA-smoothed spectrum to prevent flicker
                mask_treble = (freqs >= 6000) & (freqs <= 10000)
                if np.any(mask_treble):
                    treble_freqs = freqs[mask_treble]
                    treble_mags = mag_db[mask_treble]
                    
                    # Exponential moving average on the treble spectrum
                    alpha = 0.05  # Very smooth (~20 frame window)
                    if not hasattr(self, '_iec_smooth_mags') or len(self._iec_smooth_mags) != len(treble_mags):
                        self._iec_smooth_mags = treble_mags.copy()
                    else:
                        self._iec_smooth_mags = alpha * treble_mags + (1 - alpha) * self._iec_smooth_mags
                    
                    peak_freq = treble_freqs[np.argmax(self._iec_smooth_mags)]
                    
                    if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                        import pyqtgraph as pg
                        import numpy as np
                        self.rta_peak_line.setValue(np.log10(peak_freq))
                        if peak_freq < 7000 or peak_freq > 8600:
                            self.rta_peak_line.setPen(pg.mkPen('#eab308', width=4))
                        else:
                            self.rta_peak_line.setPen(pg.mkPen('#10b981', width=4))
                        if self.btn_iec_guide.isChecked():
                            self.rta_peak_line.show()
                        else:
                            self.rta_peak_line.hide()

                    # Hysteresis: status only changes after 8 consecutive frames outside range
                    is_ok = 7000 <= peak_freq <= 8600
                    if not hasattr(self, '_iec_status_counter'):
                        self._iec_status_counter = 0
                        self._iec_last_ok = is_ok
                    
                    if is_ok != self._iec_last_ok:
                        self._iec_status_counter += 1
                        if self._iec_status_counter >= 8:
                            self._iec_last_ok = is_ok
                            self._iec_status_counter = 0
                    else:
                        self._iec_status_counter = 0
                    
                    if self._iec_last_ok:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Depth OK ({:.1f}kHz)</span>".format(peak_freq/1000)
                    elif peak_freq < 7000:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Push Deeper (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Pull Out Slightly (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                else:
                    depth_html = ""
                    if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                        self.rta_peak_line.hide()
    
                # 2. Seal (40Hz vs 500Hz)
                mask_40 = (freqs >= 35) & (freqs <= 45)
                mask_500 = (freqs >= 450) & (freqs <= 550)
                if np.any(mask_40) and np.any(mask_500):
                    val_40 = np.mean(mag_db[mask_40])
                    val_500 = np.mean(mag_db[mask_500])
                    # Check for bass roll-off OR overall low signal variance (just noise floor)
                    if val_40 < val_500 - 12:
                        seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
                    else:
                        seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
                else:
                    seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")
            
            # Big on-screen text
            if not hasattr(self, 'rta_big_lbl'):
                import pyqtgraph as pg
                self.rta_big_lbl = pg.TextItem(html='', anchor=(0.5, 1.0))
                self.rta_big_lbl.setZValue(100)
                if hasattr(self, 'page_ana'):
                    self.rta_big_lbl.setParentItem(self.page_ana.plot_widget.getViewBox())
                else:
                    self.rta_big_lbl.setParentItem(self.plot_widget.getViewBox())
                    
            if hasattr(self, 'page_ana'):
                rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            else:
                rect = self.plot_widget.getViewBox().boundingRect()
                
            w = rect.width()
            if w < 600:
                font_size = 18
            elif w < 900:
                font_size = 22
            else:
                font_size = 28
                
            # Anchor is (0.5, 1.0) - bottom center
            self.rta_big_lbl.setPos(w/2, rect.height() - 20)
            divider = "<br>" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: {font_size}px; background-color: rgba(0,0,0,150); padding: 8px; border-radius: 8px;'><center>{seal_html}{divider}{depth_html}</center></div>")
            
            # Hide it if helper is off or if there is no text to show
            if not seal_html and not depth_html:
                self.rta_big_lbl.hide()
            elif not self.btn_iec_guide.isChecked():
                self.rta_big_lbl.hide()
            else:
                self.rta_big_lbl.show()
            
        except Exception as e:
            pass

    def run_measurement(self):
        from PySide6.QtWidgets import QMessageBox
        
        if not self.current_iem_id:
            QMessageBox.warning(self, "No Profile Selected",
                "You need to select a profile before measuring.\n\n"
                "Please select or create a Musician Profile from the sidebar on the left.")
            return
        
        # UI Hardening: block concurrent sweep attempts
        if self.is_measuring:
            QMessageBox.warning(self, "Measurement Running",
                "A measurement is already in progress.\n\n"
                "Please wait for it to complete before starting a new one.")
            return
            
        if self.selected_in_idx is None or self.selected_out_idx is None:
            QMessageBox.warning(self, "Audio Not Set Up",
                "We can't hear anything!\n\n"
                "Please open Settings (top right corner) and select your Input and Output devices first.")
            return
            
        target_ch = "L" if self.get_current_channel() == "Left" else "R"
        
        # Fully stop any running RTA/Depth to prevent audio stream conflicts
        if getattr(self, 'live_worker', None) and self.live_worker.isRunning():
            self.btn_rta_raw.setChecked(False)
            self.btn_iec_guide.setChecked(False)
            self.toggle_live_seal(False)
        
        # --- PREFLIGHT LEVEL CHECK ---
        # Compare current recording level against calibration reference.
        # Catches: user changed output level after calibration, AGC activated, etc.
        try:
            passed, peak_dbfs, pf_msg = self.audio_engine.preflight_check(
                self.selected_in_idx, self.selected_out_idx, target_ch
            )
            if not passed:
                reply = QMessageBox.warning(
                    self, "Level Check Failed",
                    f"{pf_msg}\n\nDo you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
        except Exception as e:
            print(f"[PREFLIGHT] Skipped: {e}")
        # --- END PREFLIGHT ---

        # Lock the profile ID for this sweep so a mid-sweep switch doesn't corrupt results
        self._sweep_locked_iem_id = self.current_iem_id
            
        self.sub_lbl.setText(f"Status: MEASURING {target_ch}...")
        self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold;")
        self.btn_capture.setEnabled(False)
        self.is_measuring = True
        
        # Force jump to Workspace Freq Response tab so the animation is visible
        self.switch_workspace_tab(2)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'graph_tabs'):
            self.page_ana.graph_tabs.setCurrentIndex(0)
        
        # Grab calibration data from Settings tab
        cal_f, cal_m = None, None
        cal_path = self.mic_cal_combo.currentData()
        if cal_path:
            cal_f, cal_m = self._parse_csv_file(cal_path)
        
        sweeps = int(self.get_current_sweeps().replace("x", ""))
        spl = getattr(self, 'spl_offset_db', 0.0)
        self.worker = MeasurementWorker(self.audio_engine, self.selected_in_idx, self.selected_out_idx, target_ch, cal_f, cal_m, sweeps, spl)
        
        self.worker.finished.connect(self.on_measurement_finished)
        self.worker.error.connect(self.on_measurement_error)
        self.meas_overlay.start(sweeps)
        
        self.worker.progress.connect(self._on_meas_progress)
        self.worker.sweep_progress.connect(self.meas_overlay.update_anim_sync)
        self.worker.start()

    def _on_meas_progress(self, txt):
        self.sub_lbl.setText(txt)
        if "Sweep" in txt:
            self.meas_overlay.lbl.setHtml(f'<div style="font-family: Arial; font-size: 64px; color: #00FFFF; font-weight: 900; letter-spacing: 5px; text-transform: uppercase;"><center>{txt.upper().replace("STATUS: ", "")}</center></div>')


    def update_analysis_view(self):
        # 1. Gather all potential data sources
        live_f = getattr(self, 'temp_freqs', None)
        live_ml = getattr(self, 'temp_mag_l', None)
        live_mr = getattr(self, 'temp_mag_r', None)
        
        hist_f = getattr(self, 'history_freqs', None)
        hist_ml = getattr(self, 'history_mag_l', None)
        hist_mr = getattr(self, 'history_mag_r', None)
        
        tgt_f = getattr(self, 'target_freqs', None)
        tgt_m = getattr(self, 'target_mags', None)
        
        thd_data = getattr(self, 'temp_thd_data', None)
        csd_data = getattr(self, 'temp_csd_data', None)
        ir_l = getattr(self, 'temp_ir_l', None)
        ir_r = getattr(self, 'temp_ir_r', None)

        # 2. Determine PRIMARY curve
        primary_f = None
        primary_ml = None
        primary_mr = None
        primary_source = None
        
        import numpy as np
        # Pass EVERYTHING independently so Analysis UI can render it.
        # If no live freqs, fallback to history freqs or target freqs as the x-axis base
        base_f = live_f if live_f is not None else (hist_f if hist_f is not None else tgt_f)
        
        if base_f is None:
            self.page_ana.update_analysis(None, None, None)
            return
            
        ref_mag_l = None
        ref_mag_r = None
        if hist_f is not None:
            if hist_ml is not None: ref_mag_l = np.interp(base_f, hist_f, hist_ml)
            if hist_mr is not None: ref_mag_r = np.interp(base_f, hist_f, hist_mr)
            
        out_tgt_f = tgt_f
        out_tgt_m = tgt_m

        pts = 240
        if hasattr(self, 'cb_smooth'):
            smooth_txt = self.cb_smooth.currentText()
            if smooth_txt == "1/24 Oct": pts = 240
            elif smooth_txt == "1/48 Oct": pts = 480
            elif smooth_txt == "1/12 Oct": pts = 120
            elif smooth_txt == "1/6 Oct": pts = 60
            elif smooth_txt == "Raw": pts = 0

        self.page_ana.update_analysis(
            base_f, 
            live_ml, 
            live_mr,
            ref_mag_l=ref_mag_l,
            ref_mag_r=ref_mag_r,
            tgt_freqs=out_tgt_f,
            tgt_mags=out_tgt_m,
            thd_data=thd_data,
            csd_data=csd_data,
            ir_l=ir_l,
            ir_r=ir_r,
            sweep_count=self.get_current_sweeps(),
            smoothing_pts=pts,
            noise_freqs=getattr(self, 'temp_noise_f_l', getattr(self, 'temp_noise_f_r', None)),
            noise_floor_db=getattr(self, 'temp_noise_m_l', getattr(self, 'temp_noise_m_r', None))
        )

    def on_measurement_finished(self, freqs, mag, phase, ir, channel, noise=None, noise_freqs=None, noise_mag_db=None):
        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_run_sweep'):
            self.page_ana.btn_run_sweep.setEnabled(True)
            self.page_ana.btn_run_sweep.setText("▶ MEASURE")
        if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
        
        import numpy as np
        # 1. Check raw volume
        idx_1k = (np.abs(freqs - 1000)).argmin()
        raw_val_1k = mag[idx_1k]
        low_vol_warning = False
        if raw_val_1k < -50.0:
            low_vol_warning = True
            
        # 2. Smart Post-Normalization
        if self.chk_normalize.isChecked() and np.isfinite(raw_val_1k):
            mag = mag + (80.0 - raw_val_1k)
        
        self.temp_freqs = freqs
        if channel == 'L':
            self.temp_mag_l = mag
            self.temp_phase_l = phase
            self.temp_ir_l = ir
            self.temp_noise_l = noise
            self.temp_noise_f_l = noise_freqs
            self.temp_noise_m_l = noise_mag_db
        else:
            self.temp_mag_r = mag
            self.temp_phase_r = phase
            self.temp_ir_r = ir
            self.temp_noise_r = noise
            self.temp_noise_f_r = noise_freqs
            self.temp_noise_m_r = noise_mag_db
            
        self.low_vol_warning = low_vol_warning
            
        self.plot_widget.clear()
        self.plot_target_curve()
        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            txt = "Measurement complete! Ready to save."
        else:
            other = "Right" if channel == "L" else "Left"
            txt = f"{channel} channel captured. Measure the {other} side, or Save to DB."
            
        if getattr(self, 'low_vol_warning', False):
            txt += " (⚠️ Signal was very quiet — please increase your interface's input gain.)"
            self.sub_lbl.setStyleSheet("color: #FFB300; font-size: 13px; font-weight: bold;")
        else:
            self.sub_lbl.setStyleSheet("color: #00FF00; font-size: 13px; font-weight: bold;")
        self.sub_lbl.setText(txt)
            
        self.redraw_graph()
        self.switch_workspace_tab(2)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'graph_tabs'):
            self.page_ana.graph_tabs.setCurrentIndex(0)
        ref_l = getattr(self, 'ref_mag_l', None)
        ref_r = getattr(self, 'ref_mag_r', None)
        tgt_f = getattr(self, 'target_freqs', None)
        tgt_m = getattr(self, 'target_mags', None)
        
        # Calculate Advanced Acoustic Metrics (THD and CSD)
        thd_data = None
        csd_data = None
        try:
            thd_l, thd_r, thd_freqs = None, None, None
            # Left THD
            if getattr(self, 'temp_ir_l', None) is not None:
                noise_l = getattr(self, 'temp_noise_l', None)
                noise_f_l = getattr(self, 'temp_noise_f_l', None)
                noise_m_l = getattr(self, 'temp_noise_m_l', None)
                thd_f_raw, thd_l_raw = self.audio_engine.extract_thd(self.temp_ir_l, 1.0, noise_floor=noise_l, noise_freqs=noise_f_l, noise_floor_db=noise_m_l)
                thd_freqs, thd_l, _ = self.audio_engine.smooth_spectrum(thd_f_raw, thd_l_raw, points=300)
            # Right THD
            if getattr(self, 'temp_ir_r', None) is not None:
                noise_r = getattr(self, 'temp_noise_r', None)
                noise_f_r = getattr(self, 'temp_noise_f_r', None)
                noise_m_r = getattr(self, 'temp_noise_m_r', None)
                thd_f_raw, thd_r_raw = self.audio_engine.extract_thd(self.temp_ir_r, 1.0, noise_floor=noise_r, noise_freqs=noise_f_r, noise_floor_db=noise_m_r)
                thd_freqs, thd_r, _ = self.audio_engine.smooth_spectrum(thd_f_raw, thd_r_raw, points=300)
                
            if thd_freqs is not None:
                thd_data = (thd_freqs, thd_l, thd_r)
                
            # CSD
            csd_data = {}
            if getattr(self, 'temp_ir_l', None) is not None:
                cf, ct, cm = self.audio_engine.calculate_csd(self.temp_ir_l)
                csd_data['L'] = (cf, ct, cm)
            if getattr(self, 'temp_ir_r', None) is not None:
                cf, ct, cm = self.audio_engine.calculate_csd(self.temp_ir_r)
                csd_data['R'] = (cf, ct, cm)
            if not csd_data:
                csd_data = None
        except Exception as e:
            print("Error computing DSP metrics:", e)

        self.temp_thd_data = thd_data
        self.temp_csd_data = csd_data
        self.update_analysis_view()
        
        # Run auto-diagnostics ONLY if both L and R are captured
        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            report_l = Analyzer.absolute_checks(freqs, self.temp_mag_l, self.temp_ir_l, "Left")
            report_r = Analyzer.absolute_checks(freqs, self.temp_mag_r, self.temp_ir_r, "Right")
            
            failures = [i['desc'] for i in report_l + report_r if i['status'] in ('FAIL', 'WARN')]
            
            if failures:
                self.sub_lbl.setText(f"Measurement issue: {failures[0]}")
                self.sub_lbl.setStyleSheet("color: #FF8C00; font-size: 13px; font-weight: bold;")
            else:
                self.sub_lbl.setText("Status: Capture Complete (L & R matched!). Ready to save.")
                self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")
        else:
            self.sub_lbl.setText(f"Status: {channel} channel captured. Measure the other side, or Save to DB.")
            self.sub_lbl.setStyleSheet("color: #888; font-size: 12px;")


    def save_as_target(self):
        if self.temp_freqs is None or self.temp_mag_l is None:
            return
            
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        import os
        import numpy as np
        
        name, ok = QInputDialog.getText(self, "Save Reference Target", "Enter the name of this Reference IEM (e.g. 'VE7 Pristine'):")
        if not ok or not name.strip():
            return
            
        filename = name.strip().replace(" ", "_") + ".csv"
        target_dir = "reference_targets/Pro_Live_IEMs"
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, filename)
        
        try:
            # Average L and R if both exist to create a central reference
            if self.temp_mag_r is not None:
                mag = (self.temp_mag_l + self.temp_mag_r) / 2.0
            else:
                mag = self.temp_mag_l
                
            data = np.column_stack((self.temp_freqs, mag))
            np.savetxt(path, data, delimiter=',', header="Frequency,Amplitude", comments='', fmt='%.2f')
            
            # Reload targets so it appears in the dropdown immediately
            self.load_targets()
            
            # Select it in the dropdown
            idx = self.cb_meas_target.findText(name.strip(), Qt.MatchContains)
            if idx >= 0:
                self.cb_meas_target.setCurrentIndex(idx)
                
            self.sub_lbl.setText(f"Saved as Reference: {name}")
            self.sub_lbl.setStyleSheet("color: #8b5cf6; font-weight: bold;")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed",
                "We couldn't save this as a reference target.\n\n"
                "Please check:\n"
                "• Do you have write permissions for the targets folder?\n"
                "• Is your hard drive full?\n\n"
                f"Technical detail: {e}")

    def export_csv(self):
        if self.temp_freqs is None or self.temp_mag_l is None:
            return
            
        from PySide6.QtWidgets import QFileDialog
        import numpy as np
        
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv *.txt)")
        if path:
            try:
                # We save Frequency, Mag L, and Mag R (if exists)
                if self.temp_mag_r is not None:
                    data = np.column_stack((self.temp_freqs, self.temp_mag_l, self.temp_mag_r))
                    header = "Frequency,Magnitude_L,Magnitude_R"
                else:
                    data = np.column_stack((self.temp_freqs, self.temp_mag_l))
                    header = "Frequency,Magnitude"
                    
                np.savetxt(path, data, delimiter=',', header=header, comments='', fmt='%.2f')
                self.sub_lbl.setText(f"Exported to {path}")
                self.sub_lbl.setStyleSheet("color: #00FF99;")
            except Exception as e:
                self.sub_lbl.setText("Export failed — please check the destination folder and try again.")
                self.sub_lbl.setStyleSheet("color: red;")

    def save_trace_to_db(self):
        if not self.current_iem_id: return
        if self.temp_freqs is None:
            self.sub_lbl.setText("Nothing to save yet — run a measurement first, then hit Save.")
            self.sub_lbl.setStyleSheet("color: red; font-size: 13px;")
            return
            
        gain = "Auto"
        notes = ""
        
        try:
            tip_id = 1
            if config.is_prokit_unlocked() and hasattr(self, 'combo_tip') and (self.combo_tip.isVisible() or (hasattr(self, 'tip_container') and not self.tip_container.isHidden())):
                val = self.combo_tip.currentData()
                if val is not None:
                    tip_id = int(val)

            self.db.save_measurement(
                self.current_iem_id, 
                self.temp_freqs, 
                self.temp_mag_l, 
                self.temp_mag_r, 
                self.temp_phase_l, 
                self.temp_phase_r,
                gain,
                notes,
                "",
                tip_id=tip_id
            )
            self.sub_lbl.setText("Status: Saved to Database.")
            self.sub_lbl.setStyleSheet("color: #00FF99; font-size: 12px;")
            
            # Button flash animation
            self.btn_save_db.setText("Saved")
            self.btn_save_db.setStyleSheet("QPushButton { background-color: #10b981; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #059669; }")
            
            # Using QTimer to restore (hardcoded to avoid closure state bugs if clicked multiple times rapidly)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_save_db.setText("Save"))
            QTimer.singleShot(1500, lambda: self.btn_save_db.setStyleSheet("QPushButton { background-color: #444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #555; } QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; } QPushButton:hover { background-color: #555; }"))
            
            # Immediately update the history tab so it reflects the new save
            if hasattr(self, 'active_card') and self.active_card:
                if hasattr(self.page_hist, 'load_history'):
                    self.page_hist.load_history(self.active_card.m_id)
            
            # Also update the history dropdowns so the user can select it for comparison immediately
            self.load_targets()
            
        except Exception as e:
            self.sub_lbl.setText("We couldn't save to the database — please try again.")
            self.sub_lbl.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
            print(f"DB Save Error: {e}")
        
        self.current_meas_photo = ""
        # UI cleanup: photo and notes are now handled at the profile level

    def on_measurement_error(self, err_msg):
        self.is_measuring = False   # UI Hardening: release lock on error
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
        self.sub_lbl.setText("Measurement failed — see the popup for details.")
        self.sub_lbl.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
        
        from PySide6.QtWidgets import QMessageBox
        # Force a UI update so the 'SCANNING' overlay disappears instantly BEFORE the dialog blocks the thread
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Measurement Failed")
        msg.setText("The measurement didn't complete successfully.")
        msg.setInformativeText(f"Please check that your IEM is seated correctly in the coupler and that your audio interface is connected.\n\nTechnical detail: {str(err_msg)}")
        msg.exec()

    def start_guided_tour(self):
        from tour_ui import TourManager
        if hasattr(self, 'active_tour') and self.active_tour is not None:
            return # Tour already running
            
        self.active_tour = TourManager(self)
        self.active_tour.finished.connect(self.on_tour_finished)
        self.active_tour.start_tour()
        
    def on_tour_finished(self):
        self.active_tour = None
        import os
        from config import get_data_dir
        flag_file = os.path.join(get_data_dir(), "tour_completed.flag")
        try:
            with open(flag_file, "w") as f:
                f.write("done")
        except:
            pass

    # ── ProKit Tip-Tracking Methods ───────────────────────────────────────────
    def prompt_prokit_unlock(self):
        """Prompt user for ProKit unlock code and activate features if valid."""
        code, ok = QInputDialog.getText(
            self,
            "ProKit Unlock",
            "Enter unlock code:"
        )
        if not ok:
            return False

        if config.unlock_prokit(code):
            QMessageBox.information(
                self,
                "Success",
                "ProKit unlocked successfully!"
            )
            self.update_prokit_ui_visibility()
            return True
        else:
            QMessageBox.warning(
                self,
                "Invalid code",
                "The entered unlock code is invalid."
            )
            return False

    # Aliases for unlock dialog
    open_prokit_unlock_dialog = prompt_prokit_unlock
    on_logo_triple_clicked = prompt_prokit_unlock

    def update_prokit_ui_visibility(self):
        """Update visibility of ProKit UI controls based on unlock state."""
        unlocked = config.is_prokit_unlocked()
        if hasattr(self, 'tip_container'):
            self.tip_container.setVisible(unlocked)
        if hasattr(self, 'combo_tip'):
            self.combo_tip.setVisible(unlocked)
            if unlocked:
                self.populate_tips()
                self.suggest_tip_for_current_iem()
        if hasattr(self, 'page_hist') and hasattr(self.page_hist, 'load_history'):
            try:
                m_id = None
                if hasattr(self, 'active_card') and self.active_card and hasattr(self.active_card, 'm_id'):
                    m_id = self.active_card.m_id
                if m_id is not None:
                    self.page_hist.load_history(m_id)
            except Exception:
                pass
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'render_diagnostics'):
            try:
                self.page_ana.render_diagnostics()
            except Exception:
                pass

    update_prokit_visibility = update_prokit_ui_visibility

    def populate_tips(self):
        """Populate the tip selection dropdown from the database catalog."""
        if not hasattr(self, 'combo_tip') or not hasattr(self, 'db'):
            return
        cur_id = self.combo_tip.currentData()
        self.combo_tip.blockSignals(True)
        self.combo_tip.clear()
        try:
            tips = self.db.get_all_tips(include_unknown=True) if hasattr(self.db, 'get_all_tips') else []
        except Exception:
            tips = []
        default_idx = -1
        for i, tip in enumerate(tips):
            icon = tip.get('icon_char', '')
            name = tip.get('name', '')
            display_text = f"{icon} {name}".strip()
            self.combo_tip.addItem(display_text, userData=tip['id'])
            if tip.get('is_default') in (1, True):
                default_idx = i

        if default_idx == -1:
            for i, tip in enumerate(tips):
                if tip.get('id') == 3:
                    default_idx = i
                    break
                
        if cur_id is not None and self.combo_tip.findData(cur_id) != -1:
            self.combo_tip.setCurrentIndex(self.combo_tip.findData(cur_id))
        elif default_idx != -1:
            self.combo_tip.setCurrentIndex(default_idx)
        elif self.combo_tip.count() > 0:
            self.combo_tip.setCurrentIndex(0)
        self.combo_tip.blockSignals(False)

    update_tip_selector = populate_tips

    def suggest_tip_for_current_iem(self):
        """Auto-suggest last used tip for current IEM, falling back to default."""
        if not hasattr(self, 'combo_tip') or not hasattr(self, 'db'):
            return
        
        last_tip_id = None
        if getattr(self, 'current_iem_id', None) and hasattr(self.db, 'get_last_used_tip'):
            try:
                last_tip_id = self.db.get_last_used_tip(self.current_iem_id)
            except Exception:
                last_tip_id = None
            
        if last_tip_id is not None:
            idx = self.combo_tip.findData(last_tip_id)
            if idx != -1:
                self.combo_tip.setCurrentIndex(idx)
                return
                
        # Fallback to default tip (is_default == 1, or fallback to id=3 "V26 Straight")
        def_id = None
        try:
            tips = self.db.get_all_tips(include_unknown=True) if hasattr(self.db, 'get_all_tips') else []
            for tip in tips:
                if tip.get('is_default') in (1, True):
                    def_id = tip.get('id')
                    break
        except Exception:
            def_id = None

        if def_id is None:
            def_id = 3

        def_idx = self.combo_tip.findData(def_id)
        if def_idx != -1:
            self.combo_tip.setCurrentIndex(def_idx)
        elif self.combo_tip.count() > 0:
            self.combo_tip.setCurrentIndex(0)

    on_iem_changed = suggest_tip_for_current_iem


# Module-level alias for test harness compatibility
InEarSnitchApp = MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    theme.init_theme('inearsnitch.db')
    window = MainWindow()
    window.showMaximized()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())
