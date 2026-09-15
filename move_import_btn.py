import sys

with open('history_ui.py', 'r') as f:
    code = f.read()

# 1. Add the button to the bottom layout
old_bottom = """        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #0ea5e9; border-color: #0ea5e9; background-color: #111; }")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save Target")
        self.btn_save_target.setStyleSheet(btn_style_base + " QPushButton:hover { color: #10b981; border-color: #10b981; background-color: #111; }")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("🗑 Delete")
        self.btn_delete_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #ef4444; border-color: #ef4444; background-color: #111; }")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        
        right_edit_layout.addStretch()
        right_edit_layout.addWidget(self.btn_export_history)
        right_edit_layout.addWidget(self.btn_save_target)
        right_edit_layout.addWidget(self.btn_delete_history)
        right_edit_layout.addStretch()"""

new_bottom = """        self.btn_import_history = QPushButton("+ Import")
        self.btn_import_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #f59e0b; border-color: #f59e0b; background-color: #111; }")
        self.btn_import_history.clicked.connect(self.show_import_menu)

        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #0ea5e9; border-color: #0ea5e9; background-color: #111; }")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save Target")
        self.btn_save_target.setStyleSheet(btn_style_base + " QPushButton:hover { color: #10b981; border-color: #10b981; background-color: #111; }")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("🗑 Delete")
        self.btn_delete_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #ef4444; border-color: #ef4444; background-color: #111; }")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        
        right_edit_layout.addStretch()
        right_edit_layout.addWidget(self.btn_import_history)
        right_edit_layout.addWidget(self.btn_export_history)
        right_edit_layout.addWidget(self.btn_save_target)
        right_edit_layout.addWidget(self.btn_delete_history)
        right_edit_layout.addStretch()"""

if old_bottom in code:
    code = code.replace(old_bottom, new_bottom)
else:
    print("WARNING: old_bottom not found!")

# 2. Remove the old button from the top
old_top = """        self.search_bar.textChanged.connect(self.filter_history)
        
        self.btn_import_history = QPushButton("+ Import")
        self.btn_import_history.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_import_history.setToolTip("Import CSV")
        self.btn_import_history.setStyleSheet(f"QPushButton {{ background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; }} QPushButton:hover {{ background-color: {active}; color: white; }}")
        self.btn_import_history.setCursor(Qt.PointingHandCursor)
        self.btn_import_history.clicked.connect(self.show_import_menu)
        
        search_layout.addWidget(self.search_bar, stretch=1)
        search_layout.addWidget(self.btn_import_history)
        target_layout.addLayout(search_layout)"""

new_top = """        self.search_bar.textChanged.connect(self.filter_history)
        
        search_layout.addWidget(self.search_bar, stretch=1)
        target_layout.addLayout(search_layout)"""

if old_top in code:
    code = code.replace(old_top, new_top)
else:
    print("WARNING: old_top not found!")

with open('history_ui.py', 'w') as f:
    f.write(code)

print("SUCCESS")
