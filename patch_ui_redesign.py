import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Replace the layout setup in __init__
old_layout = r"""        self\.splitter = QSplitter\(Qt\.Vertical\)
        self\.layout\.addWidget\(self\.splitter\)
        
        # --- Plots Area ---
        self\.plots_scroll = QScrollArea\(\)
.*
        self\.csd_layout\.addWidget\(self\.csd_widget\)
        
        self\.splitter\.addWidget\(self\.plots_scroll\)"""

new_layout = """        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # --- Left Pane: Graphs (QTabWidget) ---
        from PyQt5.QtWidgets import QTabWidget
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; border-radius: 4px; } QTabBar::tab { background: #222; color: #888; padding: 8px 16px; border: 1px solid #333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; } QTabBar::tab:selected { background: #333; color: white; font-weight: bold; }")
        
        # 1. FR Graph
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(0, 0, 0, 0)
        
        zoom_layout = QHBoxLayout()
        self.btn_chan_l = QPushButton("Left (L)")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet(theme.get_style('button_tab'))
        self.btn_chan_r = QPushButton("Right (R)")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet(theme.get_style('button_tab'))
        self.btn_reset_zoom = QPushButton("Reset Zoom")
        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)
        fr_layout.addLayout(zoom_layout)
        
        self.plot_widget = pg.PlotWidget()
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
        self.thd_widget = pg.PlotWidget()
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
        self.csd_widget = pg.PlotWidget()
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
        self.tools_tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; border-radius: 4px; } QTabBar::tab { background: #222; color: #888; padding: 8px 16px; border: 1px solid #333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; } QTabBar::tab:selected { background: #333; color: white; font-weight: bold; }")
        
        # 1. Diagnostics Tool
        self.diag_container = QWidget()
        diag_layout = QVBoxLayout(self.diag_container)
        diag_layout.setContentsMargins(10, 10, 10, 10)
        
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.report_container = QWidget()
        self.report_layout = QVBoxLayout(self.report_container)
        self.report_layout.setAlignment(Qt.AlignTop)
        self.report_scroll.setWidget(self.report_container)
        diag_layout.addWidget(self.report_scroll)
        self.tools_tabs.addTab(self.diag_container, "🩺 Diagnostics")
        
        # 2. Hardware DSP Tool
        self.dsp_container = QWidget()
        dsp_layout = QVBoxLayout(self.dsp_container)
        dsp_layout.setContentsMargins(10, 10, 10, 10)
        
        from PyQt5.QtWidgets import QCheckBox, QSlider, QDoubleSpinBox
        self.cb_dsp_enable = QCheckBox("Enable Hardware DSP (Live)")
        self.cb_dsp_enable.setStyleSheet("font-size: 14px; font-weight: bold; color: #00FF99;")
        dsp_layout.addWidget(self.cb_dsp_enable)
        
        dsp_info = QLabel("Applies Real-Time IIR filters to the output sweep/pink noise. Measure physical THD changes!")
        dsp_info.setWordWrap(True)
        dsp_info.setStyleSheet("color: #aaa; font-size: 11px; margin-bottom: 10px;")
        dsp_layout.addWidget(dsp_info)
        
        self.peq_bands = []
        for i in range(5):
            band_frame = QFrame()
            band_frame.setStyleSheet("background: #222; border-radius: 6px; padding: 4px;")
            bl = QVBoxLayout(band_frame)
            bl.setContentsMargins(5,5,5,5)
            
            row1 = QHBoxLayout()
            lbl = QLabel(f"Band {i+1}")
            lbl.setStyleSheet("font-weight: bold; color: #ddd;")
            cb_on = QCheckBox("On")
            cb_on.setChecked(True)
            row1.addWidget(lbl)
            row1.addStretch()
            row1.addWidget(cb_on)
            bl.addLayout(row1)
            
            row2 = QHBoxLayout()
            row2.addWidget(QLabel("Freq:"))
            sb_f = QDoubleSpinBox()
            sb_f.setRange(20, 20000)
            sb_f.setValue([60, 250, 1000, 4000, 8000][i])
            sb_f.setDecimals(0)
            row2.addWidget(sb_f)
            
            row2.addWidget(QLabel("Gain:"))
            sb_g = QDoubleSpinBox()
            sb_g.setRange(-24, 24)
            sb_g.setValue(0)
            row2.addWidget(sb_g)
            
            row2.addWidget(QLabel("Q:"))
            sb_q = QDoubleSpinBox()
            sb_q.setRange(0.1, 10)
            sb_q.setValue(1.41 if i > 0 and i < 4 else 0.7)
            row2.addWidget(sb_q)
            bl.addLayout(row2)
            
            dsp_layout.addWidget(band_frame)
            self.peq_bands.append({'on': cb_on, 'f': sb_f, 'g': sb_g, 'q': sb_q, 'type': 'peq' if i>0 and i<4 else ('lowshelf' if i==0 else 'highshelf')})
            
            def update_dsp(checked=False, idx=i):
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
                dsp_engine.set_master(self.cb_dsp_enable.isChecked())
                
            cb_on.toggled.connect(update_dsp)
            sb_f.valueChanged.connect(update_dsp)
            sb_g.valueChanged.connect(update_dsp)
            sb_q.valueChanged.connect(update_dsp)
            
        self.cb_dsp_enable.toggled.connect(update_dsp)
        dsp_layout.addStretch()
        self.tools_tabs.addTab(self.dsp_container, "🎛️ Hardware EQ")
        
        self.splitter.addWidget(self.tools_tabs)
        self.splitter.setSizes([700, 300])"""

content = re.sub(old_layout, new_layout, content, flags=re.DOTALL)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
