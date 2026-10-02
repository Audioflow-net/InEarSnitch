class MeasurementWorker(QThread):
    meas_finished = Signal(object, object, object, object, str, object, object, object)
    error = Signal(str)
    progress = Signal(str)
    sweep_progress = Signal(float, int)

    def __init__(self, audio_engine, in_idx, out_idx, target_channel, cal_f=None, cal_m=None, sweeps=1, spl_offset_db=0.0, stress_test=False):
        super().__init__()
        self.audio_engine = audio_engine
        self.in_idx = in_idx
        self.out_idx = out_idx
        self.target_channel = target_channel
        self.cal_f = cal_f
        self.cal_m = cal_m
        self.sweeps = sweeps
        self.spl_offset_db = spl_offset_db
        self.stress_test = stress_test

    def run(self):
        try:
            import numpy as np
            import time
            mags, phases, irs, noises = [], [], [], []
            freqs = None
            
            # Use 0.25 (approx -12 dBFS) for stress test, otherwise default 0.15
            test_amplitude = 0.25 if self.stress_test else 0.15
            
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
                                                amplitude=test_amplitude,
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
            
            self.meas_finished.emit(freqs, avg_mag, avg_phase, avg_ir, self.target_channel, avg_noise, noise_f, noise_m)
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



class ProKitTipSelector(QPushButton):
    currentIndexChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cb_prokit_tip")
        self.setToolTip("Select ProKit Adapter Tip")
        self.setCursor(Qt.PointingHandCursor)
        self.items = []
        self._current_index = -1
        self._signals_blocked = False
        self.clicked.connect(self.show_popup)
        self.update_styling()
        
    def blockSignals(self, b):
        self._signals_blocked = b
        return super().blockSignals(b)
        
    def update_styling(self):
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        hover = theme.get_color('accent_edge')
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                font-weight: bold;
                font-size: 12px;
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                border: 1px solid {hover};
            }}
        """)
        
    def clear(self):
        self.items = []
        self._current_index = -1
        self.setText("Select Adapter...  ▼")
        
    def addItem(self, text, userData=None):
        self.items.append({'text': text, 'data': userData})
        if self._current_index == -1:
            self.setCurrentIndex(0)
            
    def count(self):
        return len(self.items)
        
    def currentData(self):
        if 0 <= self._current_index < len(self.items):
            return self.items[self._current_index]['data']
        return None
        
    def findData(self, data):
        for i, item in enumerate(self.items):
            if item['data'] == data:
                return i
        return -1
        
    def setCurrentIndex(self, idx):
        if 0 <= idx < len(self.items):
            self._current_index = idx
            self.setText(self.items[idx]['text'] + "  ▼")
            if not self._signals_blocked:
                self.currentIndexChanged.emit(idx)
                
    def show_popup(self):
        from PySide6.QtWidgets import QMenu, QWidgetAction, QGridLayout, QVBoxLayout, QWidget, QLabel
        from PySide6.QtGui import QPixmap, QAction
        from PySide6.QtCore import Qt
        import os, theme
        
        # Use QMenu as the base to get native perfectly-working "click outside to close" behavior
        menu = QMenu(self.window())
        menu.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        menu.setStyleSheet("QMenu { background: transparent; border: none; }")
        
        main_widget = QWidget()
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        hover = theme.get_color('bg_hover')
        
        main_widget.setStyleSheet(f"""
            QWidget#PopupMain {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                color: {fg};
            }}
            QPushButton:hover {{
                background-color: {hover};
                border: 1px solid {border};
            }}
        """)
        main_widget.setObjectName("PopupMain")
        
        grid = QGridLayout(main_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("Select Adapter Tip")
        title.setStyleSheet(f"font-weight: 900; font-size: 16px; color: {fg}; padding-bottom: 5px; border: none; background: transparent;")
        grid.addWidget(title, 0, 0, 1, 3)
        
        image_mapping = {
            "V27 Modular": "render_V27.png",
            "V29 Cone": "render_V29.png",
            "V30 Pro": "render_V30.png",
            "V31 XL Panzer": "render_V31.png",
            "Flare (6.0 mm)": "render_FLARE.png",
            "Flare (5.0 mm)": "render_FLARE_5.png",
            "Flare (Clamp C5)": "render_FLARE_C5.png"
        }
        
        row, col = 1, 0
        for i, item in enumerate(self.items):
            btn = QPushButton()
            btn.setFixedSize(140, 140)
            btn.setCursor(Qt.PointingHandCursor)
            
            parts = item['text'].split(' ', 1)
            name = parts[1] if len(parts) > 1 else item['text']
            
            btn_layout = QVBoxLayout(btn)
            btn_layout.setSpacing(4)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            
            img_name = image_mapping.get(name, None)
            img_path = os.path.join(os.path.dirname(__file__), "assets", "tips", img_name) if img_name else None
            
            if img_path and os.path.exists(img_path):
                lbl_icon = QLabel()
                lbl_icon.setAlignment(Qt.AlignCenter)
                lbl_icon.setStyleSheet("border: none; background: transparent;")
                pix = QPixmap(img_path)
                if not pix.isNull():
                    lbl_icon.setPixmap(pix.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    lbl_icon.setText("?")
            else:
                lbl_icon = QLabel(parts[0] if len(parts) > 1 else "?")
                lbl_icon.setAlignment(Qt.AlignCenter)
                lbl_icon.setStyleSheet("font-size: 48px; color: #0ea5e9; border: none; background: transparent;")
            
            lbl_name = QLabel(name)
            lbl_name.setAlignment(Qt.AlignCenter)
            lbl_name.setWordWrap(True)
            lbl_name.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {fg}; border: none; background: transparent;")
            
            btn_layout.addWidget(lbl_icon)
            btn_layout.addWidget(lbl_name)
            
            def make_handler(idx):
                def handler(checked):
                    self.setCurrentIndex(idx)
                    menu.close()
                return handler
            btn.clicked.connect(make_handler(i))
            
            if i == self._current_index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {theme.get_color('accent_glow')};
                        border: 1px solid {theme.get_color('accent_edge')};
                        border-radius: 8px;
                        color: {fg};
                    }}
                """)
            
            grid.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        action = QWidgetAction(menu)
        action.setDefaultWidget(main_widget)
        menu.addAction(action)
        
        # Calculate popup position to pop upwards
        main_widget.adjustSize()
        h = main_widget.sizeHint().height()
        pos = self.mapToGlobal(self.rect().topLeft())
        # Move up by height + 5px margin
        pos.setY(pos.y() - h - 5)
        
        menu.exec(pos)

class GlobalHelpButton(QPushButton):
    def __init__(self, tab_widget, parent=None):
        super().__init__("?", parent)
        self.tab_widget = tab_widget
        self.setFixedSize(24, 24)
        self.setCursor(Qt.PointingHandCursor)
        
        self.popup = QLabel(parent, Qt.ToolTip)
        self.popup.setWordWrap(True)
        self.popup.setMinimumWidth(550)
        self.popup.hide()
        self.update_styling()
        
    def update_styling(self):
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        accent = theme.get_color('accent')
        btn_bg = theme.get_color('bg_hover')
        
        self.setStyleSheet(f"QPushButton {{ border-radius: 12px; background: {btn_bg}; color: {fg}; font-weight: bold; font-size: 13px; border: 1px solid {border}; }} QPushButton:hover {{ background: {accent}; color: #000000; border: none; }}")
        self.popup.setStyleSheet(f"background-color: {bg}; color: {fg}; border: 1px solid {accent}; border-radius: 8px; padding: 12px; font-size: 13px;")
        
    def enterEvent(self, event):
        idx = self.tab_widget.currentIndex()
        if idx == 0:
            self.popup.setText("<b>Frequency Response</b> shows the overall tonal balance (the 'sound signature') of the In-Ear Monitor from Sub-Bass to Upper Treble.<br><br>"
                               "• <b>Sub-Bass (20 - 60 Hz):</b> Rumble and physical impact. High elevation here gives cinematic depth.<br>"
                               "• <b>Mid-Bass (60 - 250 Hz):</b> Punch, warmth, and body. Too much can make the sound 'muddy' or 'boomy'.<br>"
                               "• <b>Mids (250 - 2000 Hz):</b> Vocals and core instruments. A dip here creates a 'V-Shape', pushing vocals back.<br>"
                               "• <b>Treble (2kHz - 10kHz):</b> Clarity, attack, and presence. Sharp peaks here can cause sibilance or harshness.<br>"
                               "• <b>Air (10kHz+):</b> Sense of spaciousness and soundstage.<br><br>"
                               "<b>How to use:</b><br>"
                               "Select a Reference Target (e.g., IEF Neutral) from the dropdown below to see how your IEM deviates from a known baseline.")
        elif idx == 1:
            self.popup.setText("<b>Total Harmonic Distortion (THD)</b> measures how much the In-Ear Monitor alters the original audio signal by adding unwanted harmonic frequencies.<br><br>"
                               "• <b>L2 (2nd Harmonic):</b> Sounds warm and musical. A slight elevation here is often perceived as 'thick' or 'pleasant', but too much muddies the bass.<br>"
                               "• <b>L3 (3rd Harmonic):</b> Sounds harsh, metallic, and fatiguing. High L3 often points to mechanical issues, driver clipping, or acoustic blockages.<br><br>"
                               "<b>Stress Test (Rub & Buzz):</b><br>"
                               "Runs a high-level sweep to detect mechanical defects (like a rubbing voice coil). If the red HOHD (High Order) line spikes, the driver is likely physically damaged.<br><br>"
                               "<b>What to look for:</b><br>"
                               "A clean IEM should have THD well below 1%. Sharp, isolated spikes strongly indicate resonance issues or a failing driver.")
        elif idx == 2:
            self.popup.setText("<b>Cumulative Spectral Decay (CSD / Waterfall)</b> visualizes how quickly the In-Ear Monitor stops producing sound after the signal stops, adding the dimension of <i>Time</i> to the frequency response.<br><br>"
                               "• <b>Clean Decay:</b> The graph drops off sharply and smoothly. This means the driver is fast and well-controlled, leading to precise transients and clear separation.<br>"
                               "• <b>Ringing / Ridges:</b> Mountains stretching forward in time mean the driver or acoustic chamber continues to resonate. Severe ringing causes listening fatigue and smeared details.<br><br>"
                               "<b>What to look for:</b><br>"
                               "Focus on the lower treble (4kHz - 8kHz). A deep, fast drop-off here is the hallmark of a high-end, well-tuned IEM. Prolonged ridges indicate poor acoustic damping.")
        
        # Position diagonally left below the button
        self.popup.adjustSize()
        pos = self.mapToGlobal(self.rect().bottomLeft())
        pos.setX(pos.x() - self.popup.width() + 10)
        pos.setY(pos.y() + 5)
        self.popup.move(pos)
        self.popup.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.popup.hide()
        super().leaveEvent(event)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.setWindowTitle("")
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

    def closeEvent(self, event):
        if hasattr(self, 'live_worker') and self.live_worker and self.live_worker.isRunning():
            self.live_worker.stop()
            self.live_worker.wait()
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

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
        
        import os
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import Qt
        
        self.logo_img = QLabel()
        logo_img = self.logo_img
        logo_path = os.path.join(os.path.dirname(__file__), "Final Logo InEar Snitch.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            if not pix.isNull():
                # The top bar is 50px high, so 30px height fits perfectly
                logo_img.setPixmap(pix.scaledToHeight(46, Qt.SmoothTransformation))
        logo_img.setStyleSheet("margin-right: 2px; margin-top: 2px;")
        
        logo = QLabel("InEar SNITCH")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 20px; letter-spacing: 2px;")
        sublogo = QLabel("DIAGNOSTICS")
        sublogo.setStyleSheet("color: #666; font-size: 11px; font-weight: 600; letter-spacing: 1px; margin-left: 8px; margin-top: 3px;")
        
        top_layout.addWidget(logo_img)
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
        if hasattr(self, 'logo_img'):
            self.logo_img.installEventFilter(self.logo_triple_click_filter)
        
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
        self.profile_bar = QWidget()
        profile_bar = self.profile_bar
        profile_bar.setMinimumWidth(240)
        profile_bar.setMaximumWidth(340)
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
        
        self.lbl_prof = QLabel("MUSICIAN PROFILES")
        lbl_prof = self.lbl_prof
        lbl_prof.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        prof_layout.addWidget(lbl_prof)
        
        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        search_input = self.search_input
        search_input.setPlaceholderText("Search...")
        search_input.setStyleSheet("background-color: #111; color: white; border: 1px solid #333; padding: 5px; border-radius: 4px;")
        search_input.textChanged.connect(self.filter_profiles)
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
        
        self.cb_meas_target = SearchableComboBox()
        self.cb_meas_target.setToolTip("Select a target curve. Type to search.")
        self.cb_meas_target.setMinimumWidth(100)
        self.cb_meas_target.setMaximumWidth(340)
        self.cb_meas_target.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        
        self.cb_meas_history = SearchableComboBox()
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
        self.combo_tip = ProKitTipSelector(self)
        # Aliases
        self.cb_tip = self.combo_tip
        self.cb_prokit_tip = self.combo_tip
        
        # Wrap in container for visibility gating and bottom alignment
        self.tip_container = QWidget()
        self.tip_container.setObjectName("tip_container")
        tip_v = QVBoxLayout(self.tip_container)
        tip_v.setContentsMargins(8, 0, 0, 0)
        tip_v.setSpacing(0)
        tip_v.addStretch()
        tip_v.addWidget(self.combo_tip)
        
        self.populate_tips()
        self.tip_container.setVisible(config.is_prokit_unlocked())
        
        # --- MODULE 4: LIVE TOOLS (RTA / Depth) ---
        rta_widget = QWidget()
        rta_widget.setFixedWidth(95)
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
        run_layout = QHBoxLayout()
        run_layout.setSpacing(4)
        run_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_capture = QPushButton("RUN")
        self.btn_capture.setToolTip("Start measurement capture (Space)")
        self.btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_capture.setStyleSheet("QPushButton { background-color: #10b981; color: black; font-weight: bold; font-size: 24px; border-radius: 6px; padding: 12px 10px;} QPushButton:disabled { background-color: #333; color: #666; } QPushButton:hover { background-color: #34d399; }")
        self.btn_capture.clicked.connect(self.run_measurement)
        
        run_layout.addWidget(self.btn_capture)
        
        run_widget = QWidget()
        run_widget.setFixedWidth(220)
        run_widget.setLayout(run_layout)
        mod_capture.addWidget(run_widget, stretch=1)
        
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
        right_group.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        right_group.setSpacing(7) # Pushes RTA 8px to the right to align with the visual edge of the QTabWidget above
        # Tip selector aligned to bottom (next to Depth)
        right_group.addWidget(self.tip_container)
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
        self.page_ana.init_eq_db()
        self.page_ana.load_eq_presets()
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
        
        self.btn_global_help = GlobalHelpButton(self.page_ana.graph_tabs, self)
        view_layout.addWidget(self.btn_global_help)
        
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
            from PySide6.QtGui import QDesktopServices
            link = url.toString()
            if link.startswith("http://") or link.startswith("https://"):
                QDesktopServices.openUrl(url)
                return
            
            file_path = link.split("#")[0]
            if not file_path:
                file_path = "MANUAL.md"
                
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

        privacy_layout = QHBoxLayout()
        privacy_layout.setContentsMargins(0, 0, 0, 0)
        privacy_lbl = QLabel("Privacy: All data is stored exclusively on this device. No telemetry, no tracking.")
        privacy_lbl.setWordWrap(True)
        privacy_lbl.setStyleSheet("font-size: 11px; color: #888888;")
        privacy_layout.addWidget(privacy_lbl)
        
        btn_about = QPushButton("ℹ️ About / Health & Safety")
        btn_about.setStyleSheet("background: transparent; color: #888888; border: none; font-size: 11px; text-decoration: underline;")
        btn_about.setCursor(Qt.PointingHandCursor)
        btn_about.clicked.connect(self.show_about_dialog)
        privacy_layout.addWidget(btn_about)
        
        set_layout.addLayout(privacy_layout)

        self.reload_calibrations()
        self.update_cal_preview()

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
        
        flag_val = "0"
        if os.path.exists(flag_file):
            try:
                with open(flag_file, "r") as f:
                    flag_val = f.read().strip()
            except: pass
            
        if flag_val == "0":
            # First launch: Pulse the tour button and mark as launched once
            try:
                with open(flag_file, "w") as f:
                    f.write("1")
            except: pass
            self._start_tour_pulse()
        elif flag_val == "1":
            # Second launch: stop pulsing forever
            try:
                with open(flag_file, "w") as f:
                    f.write("done")
            except: pass

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
        
        # Save current selections to restore them after clearing
        saved_hist = self.cb_meas_history.currentText() if hasattr(self, 'cb_meas_history') and self.cb_meas_history.count() > 0 else None
        saved_tgt = self.cb_meas_target.currentText() if hasattr(self, 'cb_meas_target') and self.cb_meas_target.count() > 0 else None
        
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
                        date_str = dt.strftime("%d.%m. %H:%M:%S")
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
            b.setMaxVisibleItems(25)
            from PySide6.QtWidgets import QCompleter
            from PySide6.QtCore import Qt
            b.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            completer = b.completer()
            if completer:
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setFilterMode(Qt.MatchContains)
                if completer.popup():
                    completer.popup().setStyleSheet("background-color: #111; color: white; border: 1px solid #333;")
                    # Re-install event filter just in case the popup was recreated
                    completer.popup().removeEventFilter(b)
                    completer.popup().installEventFilter(b)
                completer.setMaxVisibleItems(25)
            
            # Styling the line edit inside the combobox
            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                # The SearchableComboBox class handles its own events now.
                    
        # Restore selections
        if saved_hist and saved_hist != "No History Selected":
            idx = self.cb_meas_history.findText(saved_hist)
            if idx >= 0:
                for b in boxes_hist:
                    b.setCurrentIndex(idx)
        if saved_tgt and saved_tgt != "No Target Selected":
            idx = self.cb_meas_target.findText(saved_tgt)
            if idx >= 0:
                for b in boxes_tgt:
                    b.setCurrentIndex(idx)

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
            if hasattr(self, "page_prof"): self.page_prof.current_musician_id = None
            if hasattr(self, "page_hist"): self.page_hist.last_m_id = None
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

        reply = QMessageBox.question(self, self.tr("Hearing Safety Warning"),
                                     self.tr("Calibration will play ascending tone bursts at potentially high volumes.\n\n"
                                             "Please ensure the In-Ear Monitor is NOT in your ear before continuing.\n\n"
                                             "Proceed with calibration?"),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

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
                silence_samples = int(0.3 * self.audio_engine.sample_rate)
                tone_stereo = np.zeros((silence_samples + n, 2))
                if target_ch == 'L':
                    tone_stereo[silence_samples:, 0] = tone
                else:
                    tone_stereo[silence_samples:, 1] = tone
                
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
                
                if len(rec) > silence_samples:
                    peak = np.max(np.abs(rec[silence_samples:]))
                else:
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
            log_lines.append("   Action: Push the volume up and recalibrate!")
            QMessageBox.warning(self, "Volume Too Low",
                "Volume Too Low!\n\n"
                "Push the volume up and recalibrate."
            )
            
        # Warn if recording level is too high even at minimum amplitude
        if optimal_amp <= 0.011:
            log_lines.append("")
            log_lines.append("⚠️ WARNING: Recording level is very high!")
            log_lines.append("   Action: Push the volume down and recalibrate!")
            QMessageBox.warning(self, "Volume Too High",
                "Volume Too High!\n\n"
                "Push the volume down and recalibrate."
            )
        
        # Warn if stress test can't go louder than normal sweep
        if stress_amp <= optimal_amp * 1.1:
            log_lines.append("")
            log_lines.append("⚠️ CRITICAL: No headroom for Stress Test")
            log_lines.append("   Action: Push the volume up and recalibrate!")
            
            QMessageBox.warning(self, "Volume Too Low",
                "Volume Too Low for Stress Test!\n\n"
                "Push the volume up and recalibrate."
            )
        
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
        
        if self.is_measuring:
            return

        # Confirmation
        reply = QMessageBox.question(
            self, self.tr("Run Rub & Buzz Test?"),
            self.tr("This plays a louder-than-normal sweep to detect driver defects (Rub & Buzz).\n\n"
            "Make sure your IEM is seated in the coupler — do NOT wear it while measuring.\n"
            "Continue?"),
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
            
            # --- AUTO-HEAL: If macOS changed device indices (hot-plug), re-populate and retry! ---
            if not passed and peak_dbfs == -9986.0:
                print("[AUTO-HEAL] PortAudio stream failed. Re-populating device list...")
                self.populate_audio_devices()
                # Retry preflight with potentially updated indices
                if self.selected_in_idx is not None and self.selected_out_idx is not None:
                    passed, peak_dbfs, pf_msg = self.audio_engine.preflight_check(
                        self.selected_in_idx, self.selected_out_idx, target_ch
                    )
            if not passed:
                from PySide6.QtCore import Qt
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Level Check Failed")
                
                info_append_html = "<br><br>The Stress Test uses a higher output level than normal sweeps.<br>Running with incorrect levels will produce invalid results."
                info_append_plain = "\n\nThe Stress Test uses a higher output level than normal sweeps.\nRunning with incorrect levels will produce invalid results.\n\nDo you want to continue anyway?"
                
                if "|TIP|" in pf_msg:
                    parts = pf_msg.split("|TIP|")
                    tech_details = parts[0].strip()
                    main_tip_lines = parts[1].strip().split('\n')
                    main_title = main_tip_lines[0]
                    main_expl = "<br>".join(main_tip_lines[1:])
                    
                    html = f"""
                    <div style='font-size: 15px; font-weight: bold; margin-bottom: 12px;'>
                        {main_title}
                    </div>
                    <div style='font-size: 13px; font-weight: normal; margin-bottom: 15px;'>
                        {main_expl}
                    </div>
                    <div style='font-size: 13px; font-weight: bold; margin-bottom: 15px; color: #eab308;'>
                        Do you want to continue anyway?
                    </div>
                    <div style='font-size: 11px; font-weight: normal; color: #9ca3af;'>
                        <b>Technical details:</b><br>{tech_details.replace(chr(10), '<br>')}{info_append_html}
                    </div>
                    """
                    msg_box.setText(html)
                    msg_box.setTextFormat(Qt.TextFormat.RichText)
                else:
                    msg_box.setText("Level Check Failed")
                    msg_box.setInformativeText(f"{pf_msg}{info_append_plain}")
                    
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.No)
                reply = msg_box.exec()
                
                if reply != QMessageBox.Yes:
                    return
        except Exception as e:
            QMessageBox.critical(self, "Preflight Error", f"An internal error occurred during preflight check:\n{e}")
            return
        
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
