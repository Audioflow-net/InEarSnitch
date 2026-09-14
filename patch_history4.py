import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Modify the TOP splitter setup
old_wrap = r"""        wrap_layout\.addWidget\(self\.graph_tabs\)
        self\.splitter\.addWidget\(wrapper\)"""

# Wait, `self.graph_tabs` was just added to `wrap_layout`. I want to add an HBox for graph_tabs and tools_tabs.
# Actually, let's just make `wrap_layout` an HBox from the start.
old_wrapper_init = r"""        wrapper = QWidget\(\)
        wrap_layout = QVBoxLayout\(wrapper\)
        wrap_layout\.setContentsMargins\(4, 4, 4, 4\)
        wrap_layout\.setSpacing\(6\)"""

new_wrapper_init = """        wrapper = QWidget()
        wrap_layout = QHBoxLayout(wrapper)
        wrap_layout.setContentsMargins(4, 4, 4, 4)
        wrap_layout.setSpacing(6)"""
code = code.replace(old_wrapper_init, new_wrapper_init)

# Now, instead of just adding `self.graph_tabs` to `wrap_layout` and stopping, we add `tools_tabs` too.
old_graph_tabs_add = r"""        wrap_layout\.addWidget\(self\.graph_tabs\)
        self\.splitter\.addWidget\(wrapper\)"""

new_graph_tabs_add = """        wrap_layout.addWidget(self.graph_tabs, stretch=1)
        
        # Right pane: Tools Tabs (like Workspace)
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setFixedWidth(345)
        self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")
        
        target_tab = QWidget()
        target_layout = QVBoxLayout(target_tab)
        target_layout.setContentsMargins(15, 15, 15, 15)
        target_layout.setSpacing(10)
        
        lbl_targets_info = QLabel("Select a measurement below to manage it or save it as a Reference Target.")
        lbl_targets_info.setWordWrap(True)
        lbl_targets_info.setStyleSheet("color: #888; font-size: 12px; margin-bottom: 20px;")
        target_layout.addWidget(lbl_targets_info)
        
        # --- MOVE BUTTONS HERE ---
        self.btn_import_history = QPushButton("Import CSV")
        self.btn_import_history.setToolTip("Import a CSV measurement into the database for the current Musician")
        self.btn_import_history.setProperty("class", "accent")
        self.btn_import_history.clicked.connect(self.import_csv)
        target_layout.addWidget(self.btn_import_history)
        
        self.btn_save_target = QPushButton("Save as Target")
        self.btn_save_target.setToolTip("Saves the selected measurement to the Reference Targets folder (Squiglink targets)")
        self.btn_save_target.setProperty("class", "accent")
        self.btn_save_target.clicked.connect(self.save_as_target)
        target_layout.addWidget(self.btn_save_target)
        
        self.btn_export_history = QPushButton("Export Selected")
        self.btn_export_history.setToolTip("Export the selected measurement as a CSV file")
        self.btn_export_history.setProperty("class", "accent")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        target_layout.addWidget(self.btn_export_history)
        
        self.btn_delete_history = QPushButton("Delete Selected")
        self.btn_delete_history.setToolTip("Delete the selected measurement from the database")
        self.btn_delete_history.setProperty("class", "danger")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        target_layout.addWidget(self.btn_delete_history)
        
        target_layout.addStretch()
        
        self.tools_tabs.addTab(target_tab, "Targets")
        wrap_layout.addWidget(self.tools_tabs)
        
        self.splitter.addWidget(wrapper)"""
        
code = re.sub(old_graph_tabs_add, new_graph_tabs_add, code)

# 2. Remove the old button definitions from the bottom container
old_buttons = r"""        btn_row = QHBoxLayout\(\)
        
        self\.btn_import_history = QPushButton\("Import CSV"\)
        self\.btn_import_history\.setToolTip\("Import a CSV measurement into the database for the current Musician"\)
        self\.btn_import_history\.setProperty\("class", "accent"\)
        self\.btn_import_history\.clicked\.connect\(self\.import_csv\)
        btn_row\.addWidget\(self\.btn_import_history\)
        
        self\.btn_save_target = QPushButton\("Save as Target"\)
        self\.btn_save_target\.setToolTip\("Saves the selected measurement to the Reference Targets folder \(Squiglink targets\)"\)
        self\.btn_save_target\.setProperty\("class", "accent"\)
        self\.btn_save_target\.clicked\.connect\(self\.save_as_target\)
        btn_row\.addWidget\(self\.btn_save_target\)
        
        self\.btn_export_history = QPushButton\("Export Selected"\)
        self\.btn_export_history\.setToolTip\("Export the selected measurement as a CSV file"\)
        self\.btn_export_history\.setProperty\("class", "accent"\)
        self\.btn_export_history\.clicked\.connect\(self\.export_selected_csv\)
        btn_row\.addWidget\(self\.btn_export_history\)
        
        self\.btn_delete_history = QPushButton\("Delete Selected"\)
        self\.btn_delete_history\.setToolTip\("Delete the selected measurement from the database"\)
        self\.btn_delete_history\.setProperty\("class", "danger"\)
        self\.btn_delete_history\.clicked\.connect\(self\.delete_selected\)
        btn_row\.addWidget\(self\.btn_delete_history\)
        btn_row\.addStretch\(\)
        table_layout\.addLayout\(btn_row\)"""

code = re.sub(old_buttons, "", code)

with open("history_ui.py", "w") as f:
    f.write(code)
print("SUCCESS")
