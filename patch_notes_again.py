import re

with open("history_ui.py", "r") as f:
    code = f.read()

import_timer = "from PySide6.QtCore import Qt"
if "from PySide6.QtCore import QTimer" not in code:
    code = code.replace(import_timer, "from PySide6.QtCore import Qt, QTimer")

# Find the edit container setup
start_marker = "        # Edit Area (Under Graph)"
end_marker = "        split_layout.addWidget(left_pane, stretch=1)"

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

new_edit_area = """        # Edit Area (Under Graph)
        self.edit_container = QFrame()
        self.edit_container.setFixedHeight(113)
        self.edit_container.setObjectName("EditContainer")
        self.edit_container.setStyleSheet("#EditContainer { background-color: #222; border-radius: 8px; }")
        
        edit_layout = QHBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(0)
        
        # Left Edit Pane (Matches graph width)
        left_edit = QFrame()
        left_edit_layout = QHBoxLayout(left_edit)
        left_edit_layout.setContentsMargins(15, 12, 15, 12)
        
        from PySide6.QtWidgets import QPlainTextEdit
        self.txt_notes = QPlainTextEdit()
        self.txt_notes.setPlaceholderText("Measurement Notes...")
        self.txt_notes.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 8px 12px; border-radius: 6px; font-size: 12px;")
        
        self.notes_timer = QTimer(self)
        self.notes_timer.setSingleShot(True)
        self.notes_timer.setInterval(1000)
        self.notes_timer.timeout.connect(self.save_notes)
        self.txt_notes.textChanged.connect(self.notes_timer.start)
        
        left_edit_layout.addWidget(self.txt_notes)
        
        # Right Edit Pane (Matches tools_tabs width)
        right_edit = QFrame()
        right_edit.setFixedWidth(345)
        right_edit_layout = QHBoxLayout(right_edit)
        right_edit_layout.setContentsMargins(15, 12, 15, 12)
        right_edit_layout.setSpacing(10)
        right_edit_layout.setAlignment(Qt.AlignCenter)
        
        self.btn_export_history = QPushButton("Export CSV")
        self.btn_export_history.setProperty("class", "accent")
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        
        self.btn_save_target = QPushButton("Save as Target")
        self.btn_save_target.setProperty("class", "accent")
        self.btn_save_target.clicked.connect(self.save_as_target)
        
        self.btn_delete_history = QPushButton("Delete")
        self.btn_delete_history.setProperty("class", "danger")
        self.btn_delete_history.clicked.connect(self.delete_selected)
        
        right_edit_layout.addStretch()
        right_edit_layout.addWidget(self.btn_export_history)
        right_edit_layout.addWidget(self.btn_save_target)
        right_edit_layout.addWidget(self.btn_delete_history)
        right_edit_layout.addStretch()
        
        edit_layout.addWidget(left_edit, stretch=1)
        edit_layout.addWidget(right_edit)
        
"""

code = code[:start_idx] + new_edit_area + code[end_idx:]

# Update save_notes and setText
code = code.replace("self.txt_notes.text()", "self.txt_notes.toPlainText()")
code = code.replace("self.txt_notes.setText(data.get('notes', ''))", "self.txt_notes.setPlainText(data.get('notes', ''))")

with open("history_ui.py", "w") as f:
    f.write(code)
