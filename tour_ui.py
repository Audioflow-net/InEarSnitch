from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPoint, QRect, QRectF, Signal, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor

class TourManager(QWidget):
    finished = Signal()
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        # We need to receive mouse events to block them
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setGeometry(main_window.rect())
        main_window.installEventFilter(self)
        
        self.current_step = 0
        self.target_rect = QRect()
        
        # Coach mark UI
        self.coach_mark = QFrame(self)
        self.coach_mark.setObjectName("CoachMark")
        self.coach_mark.setFixedSize(560, 370)
        self.coach_mark.hide() # hide until layout resolves to prevent (0,0) flicker
        # Add Drop Shadow for modern look
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.coach_mark.setGraphicsEffect(shadow)

        self.update_theme()
        
    def update_theme(self):
        import theme
        bg_panel = theme.get_color("bg_panel")
        text_primary = theme.get_color("text_primary")
        text_secondary = theme.get_color("text_secondary")
        border = theme.get_color("border")
        bg_hover = theme.get_color("bg_hover")
        accent = theme.get_color("accent")
        danger = theme.get_color("danger")

        self.coach_mark.setStyleSheet(f"""
            #CoachMark {{
                background-color: {bg_panel};
                border: 1px solid {border};
                border-radius: 14px;
                font-family: "Inter", "Helvetica Neue", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            QLabel#StepLabel {{
                color: {accent};
                font-size: 13px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            QLabel#TitleLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {text_primary};
            }}
            QLabel#BodyLabel {{
                color: {text_secondary};
                font-size: 16px;
            }}
            QLabel#Dot {{
                color: {border};
                font-size: 24px;
            }}
            QLabel#Dot[active="true"] {{
                color: {accent};
            }}
            QPushButton {{
                font-size: 15px;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton#SkipButton {{
                background: transparent;
                color: {text_secondary};
                border: none;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton#SkipButton:hover {{
                color: {text_primary};
            }}
            QPushButton#BackButton {{
                background: transparent;
                color: {text_primary};
                border: 1px solid {border};
            }}
            QPushButton#BackButton:hover {{
                background: {bg_hover};
            }}
            QPushButton#NextButton {{
                background-color: #10b981;
                color: #ffffff;
                border: none;
                padding: 10px 28px;
            }}
            QPushButton#NextButton:hover {{
                background-color: #059669;
            }}
        """)
        
        cm_layout = QVBoxLayout(self.coach_mark)
        cm_layout.setContentsMargins(30, 30, 30, 30)
        cm_layout.setSpacing(0)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        self.lbl_step = QLabel()
        self.lbl_step.setObjectName("StepLabel")
        
        self.btn_skip = QPushButton("Skip Tour")
        self.btn_skip.setObjectName("SkipButton")
        self.btn_skip.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(self.lbl_step)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_skip)
        
        cm_layout.addLayout(header_layout)
        cm_layout.addSpacing(15)
        
        # --- CONTENT ---
        self.lbl_title = QLabel()
        self.lbl_title.setObjectName("TitleLabel")
        
        self.lbl_text = QLabel()
        self.lbl_text.setObjectName("BodyLabel")
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setFixedWidth(500)
        self.lbl_text.setTextFormat(Qt.RichText)
        self.lbl_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        cm_layout.addWidget(self.lbl_title)
        cm_layout.addSpacing(10)
        cm_layout.addWidget(self.lbl_text, 1) # stretch factor 1 pushes footer down
        
        # --- FOOTER ---
        footer_layout = QHBoxLayout()
        
        # Dots
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(6)
        self.dots = []
        for i in range(9): # 9 steps
            dot = QLabel("●")
            dot.setObjectName("Dot")
            dot.setProperty("active", False)
            self.dots.append(dot)
            self.dots_layout.addWidget(dot)
            
        footer_layout.addLayout(self.dots_layout)
        footer_layout.addStretch()
        
        self.btn_back = QPushButton("Back")
        self.btn_back.setObjectName("BackButton")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        
        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("NextButton")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        
        footer_layout.addWidget(self.btn_back)
        footer_layout.addWidget(self.btn_next)
        
        cm_layout.addLayout(footer_layout)
        
        # Connections
        self.btn_skip.clicked.connect(self.end_tour)
        self.btn_back.clicked.connect(self.prev_step)
        self.btn_next.clicked.connect(self.next_step)
        
        # Pulse animation timer
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.update)
        
        self.steps = [
            {
                "title": "Hardware Setup",
                "text": "Before clicking anything, set up your physical measurement rig:<br><br>1. Connect your Audio Interface to the laptop.<br>2. Plug the measurement microphone into the <b>Input</b>.<br>3. Plug the IEM into the <b>Output</b> (headphone jack).<br>4. Insert the IEM tightly into the coupler.<br><br><span style='color:#ef4444;'><b>CRITICAL:</b> NEVER wear the IEM in your ear during measurements!</span>",
                "get_target": lambda: None, # Center of screen
                "setup": lambda: self._close_settings_and_go(1)
            },
            {
                "title": "Audio Routing & Filters",
                "text": "Select your measurement microphone (Input) and headphone amplifier (Output) here.<br><br><span style='color:#ef4444;'><b>CRITICAL:</b> Disable macOS <i>Voice Isolation</i> and Windows <i>Audio Enhancements</i>. These OS filters will compress the loud sweep and ruin your trace.</span>",
                "get_target": lambda: self.main_window.settings_panel if self.main_window.settings_panel.isVisible() else self.main_window.btn_top_settings,
                "setup": lambda: self._open_settings_and_tab(0)
            },
            {
                "title": "Coupler Calibration",
                "text": "Load a <b>.txt</b> calibration file to mathematically correct the frequency response of your measurement microphone.<br><br>Got a budget fake 711 coupler? Use the <b>Auto-Generate</b> tool to create a custom calibration file from a reference target.",
                "get_target": lambda: self.main_window.cal_widget if hasattr(self.main_window, 'cal_widget') and self.main_window.settings_panel.isVisible() else self.main_window.btn_top_settings,
                "setup": lambda: self._open_settings_and_tab(1)
            },
            {
                "title": "Output Level Calibration",
                "text": "Before you measure, the engine needs to know how loud to play the test tone to avoid clipping.<br><br>Insert an IEM into the coupler and click <b>Start Auto-Calibration</b>. The app will play ascending sweeps to find the optimal measurement volume.",
                "get_target": lambda: self.main_window.btn_auto_cal if hasattr(self.main_window, 'btn_auto_cal') and self.main_window.settings_panel.isVisible() else self.main_window.btn_top_settings,
                "setup": lambda: self._open_settings_and_tab(1)
            },
            {
                "title": "Musician Profiles",
                "text": "You cannot measure without an active profile. Manage your musicians and their In-Ear Monitors here.<br><br>Every sweep is saved to a specific IEM, allowing you to track driver degradation and wear-and-tear over years.",
                "get_target": lambda: self.main_window.btn_nav_prof,
                "setup": lambda: self._close_settings_and_go(0)
            },
            {
                "title": "IEC Insertion Depth",
                "text": "Before you capture a sweep, you must set the physical insertion depth!<br><br>Turn on the <b>Depth</b> guide (RTA). Carefully push the IEM into the coupler until the resonance peak lands accurately in the green target zone (<b>7,000 Hz - 8,600 Hz</b>).",
                "get_target": lambda: self.main_window.btn_iec_guide if hasattr(self.main_window, 'btn_iec_guide') else self.main_window.btn_capture,
                "setup": lambda: self._close_settings_and_go(1)
            },
            {
                "title": "The Measurement Sweep",
                "text": "Insert the IEM into the coupler tightly (you need a tight seal!).<br><br>Select Left or Right channel, choose the amount of sweeps (multiple sweeps average out background noise), and hit <b>RUN</b>.",
                "get_target": lambda: self.main_window.btn_capture,
                "setup": lambda: self._close_settings_and_go(1)
            },
            {
                "title": "Automated Diagnostics",
                "text": "After measuring both sides, the engine automatically checks for hardware issues:<br><br>• <b>Phase Inversion:</b> Reversed wiring.<br>• <b>Bass Drop:</b> Massive air leak or broken dynamic driver.<br>• <b>Highs Drop:</b> Wax-clogged acoustic filter.",
                "get_target": lambda: getattr(self.main_window, 'page_ana', self.main_window).diag_container if hasattr(getattr(self.main_window, 'page_ana', self.main_window), 'diag_container') else self.main_window.btn_capture,
                "setup": lambda: self._setup_diagnostics_step()
            },
            {
                "title": "History Vault",
                "text": "Compare today's sweep with older measurements of the exact same IEM.<br><br>This is your ultimate tool to prove if a driver has actually degraded over a long tour, or if it's just the musician's ears getting tired.",
                "get_target": lambda: self.main_window.btn_nav_hist if hasattr(self.main_window, 'btn_nav_hist') else self.main_window.btn_capture,
                "setup": lambda: self._close_settings_and_go(2)
            }
        ]
        
    def eventFilter(self, obj, event):
        if obj == self.main_window and event.type() == event.Type.Resize:
            self.setGeometry(self.main_window.rect())
            self.update_coach_mark_position()
        return False
        
    def _open_settings_and_tab(self, tab_index):
        if not self.main_window.settings_panel.isVisible():
            self.main_window.btn_top_settings.click()
        if hasattr(self.main_window, 'settings_tabs'):
            self.main_window.settings_tabs.setCurrentIndex(tab_index)
            
    def _close_settings_and_go(self, tab_idx):
        if self.main_window.settings_panel.isVisible():
            self.main_window.btn_top_settings.click()
            
        if tab_idx == 0:
            self.main_window.btn_nav_prof.click()
        elif tab_idx == 1:
            self.main_window.btn_nav_ana.click()
        elif tab_idx == 2 and hasattr(self.main_window, 'btn_nav_hist'):
            self.main_window.btn_nav_hist.click()
            
    def _setup_diagnostics_step(self):
        self._close_settings_and_go(1)
        if hasattr(self.main_window, 'page_ana') and hasattr(self.main_window.page_ana, 'tools_tabs'):
            self.main_window.page_ana.tools_tabs.setCurrentIndex(0)

    def start_tour(self):
        self.show()
        self.raise_()
        self.pulse_timer.start(33)
        self.current_step = 0
        self.show_step()
        
    def end_tour(self):
        self.pulse_timer.stop()
        
        # Reset UI back to Main Workspace
        self._close_settings_and_go(1)
        
        self.hide()
        self.finished.emit()
        self.deleteLater()
        
    def next_step(self):
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.end_tour()
        else:
            self.show_step()
            
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
            
    def show_step(self):
        if self.current_step == len(self.steps) - 1:
            self.btn_next.setText("Finish")
        else:
            self.btn_next.setText("Next")
            
        self.btn_back.setVisible(self.current_step > 0)
            
        # Update dots
        for i, dot in enumerate(self.dots):
            dot.setProperty("active", i == self.current_step)
            dot.style().unpolish(dot)
            dot.style().polish(dot)
            
        step = self.steps[self.current_step]
        self.lbl_step.setText(f"STEP {self.current_step + 1} OF {len(self.steps)}")
        self.lbl_title.setText(step["title"])
        self.lbl_text.setText(step["text"])
        
        step["setup"]()
        
        # We don't need a singleShot timer anymore, the pulse timer will track the animating UI
        self._update_target_rect()
        self.update_coach_mark_position()
        self.coach_mark.show()
    def _update_target_rect(self):
        step = self.steps[self.current_step]
        target = step["get_target"]()
        if target and target.isVisible():
            pt = target.mapTo(self.main_window, QPoint(0, 0))
            self.target_rect = QRect(pt, target.size())
            
            # Hack to include the explanation text above the Auto-Cal button
            if target == getattr(self.main_window, 'btn_auto_cal', None):
                self.target_rect.setTop(self.target_rect.top() - 110)
        else:
            self.target_rect = QRect(self.width()//2, self.height()//2, 0, 0)
            
    def update_coach_mark_position(self):
        # Lock to a single static position: 
        # Slightly left-of-center (35% mark) so it never overlaps the right-side Settings panel
        cm_x = int((self.width() - self.coach_mark.width()) * 0.35)
        cm_x = max(20, cm_x) # ensure it doesn't go off-screen
        
        cm_y = (self.height() - self.coach_mark.height()) // 2
            
        self.coach_mark.move(cm_x, cm_y)
        self.coach_mark.show() # safe to show now, won't flicker at 0,0
        self.update() # trigger paintEvent

    def paintEvent(self, event):
        self._update_target_rect()
        
        from PySide6.QtGui import QPen
        import time
        import math
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRect(QRectF(self.rect()))
        
        if self.target_rect.isValid() and not self.target_rect.isEmpty():
            hole = QPainterPath()
            r = QRectF(self.target_rect).adjusted(-6, -6, 6, 6)
            hole.addRoundedRect(r, 8, 8)
            path = path.subtracted(hole)
            
            painter.fillPath(path, QColor(0, 0, 0, 120))
            
            # Draw pulsing highlight ring
            pulse = (math.sin(time.time() * 5) + 1) / 2 # 0.0 to 1.0
            
            import theme
            is_light = theme.is_light() if hasattr(theme, 'is_light') else False
            glow_color = QColor(2, 132, 199) if is_light else QColor(0, 255, 255)
            glow_color.setAlpha(int(pulse * 180 + 40)) # Base alpha + pulse
            
            pen = QPen(glow_color)
            pen.setWidthF(2.0 + pulse * 4.0)
            painter.setPen(pen)
            painter.drawRoundedRect(r, 8, 8)
            
        else:
            painter.fillPath(path, QColor(0, 0, 0, 120))
        
    def mousePressEvent(self, event):
        # Block clicks outside the coach mark to force user to use Next/Close
        event.accept()
