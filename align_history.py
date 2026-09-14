with open("/Users/ben/Desktop/InEarSnitch/history_ui.py", "r") as f:
    text = f.read()

target = """        # TOP of splitter: Graph
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setTitle("Measurement History", color=theme.get_color("pg_fg"), size="14pt")
        self.plot_widget.setBackground(theme.get_color("pg_bg"))
        self.plot_widget.setLabel('left', 'Magnitude', units='dB', color=theme.get_color("pg_fg"))
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz', color=theme.get_color("pg_fg"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.addLegend()
        self.splitter.addWidget(self.plot_widget)"""

replacement = """        # TOP of splitter: Graph
        wrapper = QWidget()
        wrap_layout = QVBoxLayout(wrapper)
        wrap_layout.setContentsMargins(4, 4, 4, 4)
        wrap_layout.setSpacing(6)
        
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setElideMode(Qt.ElideNone)
        self.graph_tabs.setUsesScrollButtons(True)
        
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(4, 4, 4, 4)
        fr_layout.setSpacing(4)
        
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(6)
        
        lbl_dummy = QLabel(" ")
        lbl_dummy.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        zoom_layout.addWidget(lbl_dummy)
        
        zoom_layout.addStretch()
        self.btn_reset_zoom = QPushButton("🔍 Autozoom")
        self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
        self.btn_reset_zoom.clicked.connect(lambda: self.plot_widget.autoRange())
        zoom_layout.addWidget(self.btn_reset_zoom)
        
        fr_layout.addLayout(zoom_layout)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setBackground(theme.get_color("pg_bg"))
        self.plot_widget.setLabel('left', 'Magnitude', units='dB', color=theme.get_color("pg_fg"))
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz', color=theme.get_color("pg_fg"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.addLegend()
        
        fr_layout.addWidget(self.plot_widget)
        self.graph_tabs.addTab(self.fr_container, "Measurement History")
        
        wrap_layout.addWidget(self.graph_tabs)
        self.splitter.addWidget(wrapper)"""

if target in text:
    text = text.replace(target, replacement)
    with open("/Users/ben/Desktop/InEarSnitch/history_ui.py", "w") as f:
        f.write(text)
    print("Graph aligned")
else:
    print("Target not found")
