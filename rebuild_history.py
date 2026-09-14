import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Inject HistoryCardWidget at the top after imports
card_widget_code = """
class HistoryCardWidget(QWidget):
    def __init__(self, timestamp, iem_name, side, parent=None):
        super().__init__(parent)
        self.timestamp = timestamp
        self.iem_name = iem_name
        self.side = side
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        lbl_iem = QLabel(iem_name)
        lbl_iem.setStyleSheet("font-weight: bold; font-size: 13px; color: #fff;")
        
        lbl_date = QLabel(timestamp)
        lbl_date.setStyleSheet("font-size: 10px; color: #888;")
        
        info_layout.addWidget(lbl_iem)
        info_layout.addWidget(lbl_date)
        
        lbl_side = QLabel(side)
        if side.lower() == "left":
            lbl_side.setStyleSheet("background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        elif side.lower() == "right":
            lbl_side.setStyleSheet("background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
        else:
            lbl_side.setStyleSheet("background-color: #10b981; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;")
            
        layout.addLayout(info_layout)
        layout.addWidget(lbl_side)
        layout.addStretch()
        
        self.cb_graph = QCheckBox("Graph")
        self.cb_graph.setStyleSheet("QCheckBox { color: #888; font-size: 11px; font-weight: bold; }")
        layout.addWidget(self.cb_graph)
"""
code = code.replace("class HistoryWidget(QWidget):", card_widget_code + "\nclass HistoryWidget(QWidget):")

# 2. Rewrite __init__ layout
old_init_start = r'        self\.layout = QHBoxLayout\(self\)\n        self\.layout\.setContentsMargins\(0, 0, 0, 0\)\n.*?(?=self\.measurements = \[\])'

new_init = """        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        bg = theme.get_color("bg_sec")
        active = theme.get_color("bg_hover")
        border = theme.get_color("border")
        fg = theme.get_color("text_primary")
        text_sec = theme.get_color("text_secondary")
        
        # --- LEFT PANE ---
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)
        
        self.graph_tabs = QTabWidget()
        self.graph_tabs.setElideMode(Qt.ElideNone)
        self.graph_tabs.setUsesScrollButtons(True)
        self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        
        self.fr_container = QWidget()
        fr_layout = QVBoxLayout(self.fr_container)
        fr_layout.setContentsMargins(4, 4, 4, 4)
        fr_layout.setSpacing(4)
        
        # Corner Widget (Top Right)
        from PySide6.QtWidgets import QComboBox
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(15)
        corner_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        
        chan_vis_widget = QWidget()
        chan_vis_layout = QHBoxLayout(chan_vis_widget)
        chan_vis_layout.setContentsMargins(0,0,0,0)
        chan_vis_layout.setSpacing(0)
        
        self.btn_chan_l = QPushButton("Left")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet("QPushButton { background-color: #1a1a1a; color: #666; border: 1px solid #333; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #333; color: white; border-color: #555; }")
        
        self.btn_chan_r = QPushButton("Right")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet("QPushButton { background-color: #1a1a1a; color: #666; border: 1px solid #333; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #333; color: white; border-color: #555; }")
        
        chan_vis_layout.addWidget(self.btn_chan_l)
        chan_vis_layout.addWidget(self.btn_chan_r)
        
        self.btn_chan_l.clicked.connect(self.on_item_checked)
        self.btn_chan_r.clicked.connect(self.on_item_checked)
        corner_layout.addWidget(chan_vis_widget)
        
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)
        view_layout.setContentsMargins(0,0,0,0)
        view_layout.setSpacing(8)
        
        self.cb_smooth = QComboBox()
        self.cb_smooth.addItems(["1/24 Oct", "1/48 Oct", "1/12 Oct", "1/6 Oct", "Raw"])
        self.cb_smooth.setStyleSheet("QComboBox { background-color: #222; color: white; border: 1px solid #444; padding: 2px 10px; border-radius: 4px; font-size: 11px; font-weight: bold; min-height: 20px; }")
        self.cb_smooth.currentIndexChanged.connect(self.on_item_checked)
        view_layout.addWidget(self.cb_smooth)
        
        self.btn_reset_zoom = QPushButton("AUTOZOOM")
        self.btn_reset_zoom.setToolTip("Autozoom graph to fit curves")
        self.btn_reset_zoom.setMinimumWidth(90)
        self.btn_reset_zoom.setStyleSheet("QPushButton { background-color: #222; color: white; border: 1px solid #444; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:hover { background-color: #333; }")
        self.btn_reset_zoom.clicked.connect(self.reset_zoom)
        view_layout.addWidget(self.btn_reset_zoom)
        
        corner_layout.addWidget(view_widget)
        self.graph_tabs.setCornerWidget(corner_widget, Qt.TopRightCorner)

        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setClipToView(True)
        self.plot_widget.setDownsampling(auto=True, mode='peak')
        self.plot_widget.setBackground(theme.get_color("pg_bg"))
        self.plot_widget.setLabel('left', 'Magnitude', units='dB', color=theme.get_color("pg_fg"))
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz', color=theme.get_color("pg_fg"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLogMode(x=True, y=False)
        self.plot_widget.addLegend()
        self.reset_zoom()
        
        fr_layout.addWidget(self.plot_widget)
        self.graph_tabs.addTab(self.fr_container, "Measurement History")
        left_layout.addWidget(self.graph_tabs, stretch=1)
        
        # Edit Area (Under Graph)
        self.edit_container = QWidget()
        self.edit_container.setFixedHeight(70)
        self.edit_container.setStyleSheet(f"background-color: {bg}; border: 1px solid {border}; border-radius: 4px;")
        edit_layout = QHBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(15, 10, 15, 10)
        edit_layout.setSpacing(10)
        
        lbl_notes = QLabel("Notes:")
        lbl_notes.setStyleSheet(f"color: {text_sec}; font-weight: bold;")
        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText("Measurement Notes...")
        self.txt_notes.setStyleSheet(f"background-color: #1a1a1a; color: white; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
        self.txt_notes.editingFinished.connect(self.save_notes)
        
        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setProperty("class", "accent")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save as Target")
        self.btn_save_target.setProperty("class", "accent")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("Delete")
        self.btn_delete_history.setProperty("class", "danger")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        
        edit_layout.addWidget(lbl_notes)
        edit_layout.addWidget(self.txt_notes, stretch=1)
        edit_layout.addWidget(self.btn_export_history)
        edit_layout.addWidget(self.btn_save_target)
        edit_layout.addWidget(self.btn_delete_history)
        
        left_layout.addWidget(self.edit_container)
        self.edit_container.setEnabled(False) # Default disabled
        self.layout.addWidget(left_pane, stretch=1)
        
        # --- RIGHT PANE ---
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setFixedWidth(345)
        self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        
        target_tab = QWidget()
        target_layout = QVBoxLayout(target_tab)
        target_layout.setContentsMargins(8, 8, 8, 8)
        target_layout.setSpacing(10)
        
        # Search & Add Bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(6)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search history...")
        self.search_bar.setStyleSheet(f"background-color: #1a1a1a; color: white; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
        self.search_bar.textChanged.connect(self.filter_history)
        
        self.btn_import_history = QPushButton("+")
        self.btn_import_history.setToolTip("Import CSV")
        self.btn_import_history.setFixedSize(28, 28)
        self.btn_import_history.setStyleSheet("QPushButton { background-color: #06b6d4; color: white; border-radius: 4px; font-weight: bold; font-size: 16px; } QPushButton:hover { background-color: #0891b2; }")
        self.btn_import_history.clicked.connect(self.import_csv)
        
        search_layout.addWidget(self.search_bar, stretch=1)
        search_layout.addWidget(self.btn_import_history)
        target_layout.addLayout(search_layout)
        
        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"QListWidget {{ background-color: transparent; border: none; outline: none; }} QListWidget::item {{ padding: 2px; }} QListWidget::item:selected {{ background-color: #1a1a1a; border-radius: 6px; border: 1px solid {active}; }}")
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        target_layout.addWidget(self.list_widget, stretch=1)
        self.tools_tabs.addTab(target_tab, "Measurements")
        self.layout.addWidget(self.tools_tabs)
        
"""
code = re.sub(old_init_start, new_init, code, flags=re.DOTALL)

with open("history_ui.py", "w") as f:
    f.write(code)
