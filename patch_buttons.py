import re

with open("history_ui.py", "r") as f:
    code = f.read()

old_buttons = """        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setProperty("class", "accent")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save as Target")
        self.btn_save_target.setProperty("class", "accent")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("Delete")
        self.btn_delete_history.setProperty("class", "danger")
        self.btn_delete_history.clicked.connect(self.delete_selected)"""

new_buttons = """        btn_style_base = "QPushButton { background-color: #222; color: #888; font-weight: bold; padding: 6px 12px; border-radius: 4px; border: 1px solid #444; font-size: 11px;} QPushButton:disabled { color: #555; border-color: #333; }"
        
        self.btn_export_history = QPushButton("⎘ EXPORT CSV")
        self.btn_export_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #0ea5e9; border-color: #0ea5e9; background-color: #111; }")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("⤓ SAVE TARGET")
        self.btn_save_target.setStyleSheet(btn_style_base + " QPushButton:hover { color: #10b981; border-color: #10b981; background-color: #111; }")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("🗑 DELETE")
        self.btn_delete_history.setStyleSheet(btn_style_base + " QPushButton:hover { color: #ef4444; border-color: #ef4444; background-color: #111; }")
        self.btn_delete_history.clicked.connect(self.delete_selected)"""

code = code.replace(old_buttons, new_buttons)

with open("history_ui.py", "w") as f:
    f.write(code)
