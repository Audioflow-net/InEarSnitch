import re

with open("history_ui.py", "r") as f:
    content = f.read()

# 1. Add schema migration to load_history
migration_code = """        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} not found.")
            return

        try:
            import sqlite3
            import numpy as np
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure meas_name exists
            cursor.execute("PRAGMA table_info(Measurements)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'meas_name' not in columns:
                cursor.execute("ALTER TABLE Measurements ADD COLUMN meas_name TEXT")
                conn.commit()
"""
content = content.replace("""        if not os.path.exists(self.db_path):
            print(f"Database {self.db_path} not found.")
            return

        try:
            import sqlite3
            import numpy as np
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()""", migration_code)

# 2. Update SELECT query
content = content.replace(
    "SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name",
    "SELECT m.timestamp, m.notes, m.photo_path, m.frequencies, m.magnitude_l, m.magnitude_r, iem.model_name, iem.custom_name, m.meas_name"
)

# 3. Update row unpacking
content = content.replace(
    "timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name, custom_name = row\n                display_name = custom_name if custom_name else iem_name",
    "timestamp, notes, photo_path, freq_blob, mag_l_blob, mag_r_blob, iem_name, custom_name, meas_name = row\n                base_name = custom_name if custom_name else iem_name\n                display_name = meas_name if meas_name else base_name"
)

# 4. Update data_dict
content = content.replace(
    "'iem_name': display_name,",
    "'iem_name': display_name,\n                    'meas_name': meas_name if meas_name else '',\n                    'base_name': base_name,"
)

# 5. Add UI elements
ui_replacement = """        # Left Edit Pane (Matches graph width)
        left_edit = QFrame()
        left_edit_layout = QVBoxLayout(left_edit)
        left_edit_layout.setContentsMargins(15, 8, 15, 8)
        left_edit_layout.setSpacing(6)
        
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(10)
        
        self.edit_meas_name = QLineEdit()
        self.edit_meas_name.setPlaceholderText("Measurement Name (Leave blank for default IEM name)")
        self.edit_meas_name.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        
        self.edit_meas_date = QLineEdit()
        self.edit_meas_date.setPlaceholderText("Date/Time (YYYY-MM-DD HH:MM:SS)")
        self.edit_meas_date.setStyleSheet(f"background-color: {bg_hover}; color: {text_sec}; border: 1px solid {border}; padding: 4px 8px; border-radius: 4px; font-size: 11px;")
        self.edit_meas_date.setFixedWidth(160)
        
        meta_layout.addWidget(self.edit_meas_name, stretch=1)
        meta_layout.addWidget(self.edit_meas_date)
        
        from PySide6.QtWidgets import QPlainTextEdit
        self.txt_notes = QPlainTextEdit()
        self.txt_notes.setPlaceholderText("Measurement Notes...")
        self.txt_notes.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px 10px; border-radius: 6px; font-size: 12px;")
        
        self.notes_timer = QTimer(self)
        self.notes_timer.setSingleShot(True)
        self.notes_timer.setInterval(1000)
        self.notes_timer.timeout.connect(self.save_notes)
        
        self.txt_notes.textChanged.connect(self.notes_timer.start)
        self.edit_meas_name.textChanged.connect(self.notes_timer.start)
        self.edit_meas_date.textChanged.connect(self.notes_timer.start)
        
        left_edit_layout.addLayout(meta_layout)
        left_edit_layout.addWidget(self.txt_notes, stretch=1)"""

content = re.sub(r"# Left Edit Pane.*?left_edit_layout\.addWidget\(self\.txt_notes\)", ui_replacement, content, flags=re.DOTALL)

# 6. Update on_selection_changed
on_sel_rep = """    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        if not items:
            self.set_edit_controls_enabled(False)
            self.txt_notes.clear()
            self.edit_meas_name.clear()
            self.edit_meas_date.clear()
            return
            
        self.set_edit_controls_enabled(True)
        data = items[0].data(Qt.UserRole)
        
        self.txt_notes.blockSignals(True)
        self.edit_meas_name.blockSignals(True)
        self.edit_meas_date.blockSignals(True)
        
        self.txt_notes.setPlainText(data.get('notes', ''))
        self.edit_meas_name.setText(data.get('meas_name', ''))
        self.edit_meas_date.setText(data.get('timestamp', ''))
        
        self.txt_notes.blockSignals(False)
        self.edit_meas_name.blockSignals(False)
        self.edit_meas_date.blockSignals(False)"""
content = re.sub(r"    def on_selection_changed\(self\):.*?self\.txt_notes\.blockSignals\(False\)", on_sel_rep, content, flags=re.DOTALL)

# 7. Update set_edit_controls_enabled
set_edit_rep = """    def set_edit_controls_enabled(self, enabled):
        self.txt_notes.setEnabled(enabled)
        self.edit_meas_name.setEnabled(enabled)
        self.edit_meas_date.setEnabled(enabled)
        self.btn_export_history.setEnabled(enabled)
        self.btn_save_target.setEnabled(enabled)
        self.btn_delete_history.setEnabled(enabled)"""
content = re.sub(r"    def set_edit_controls_enabled\(self, enabled\):.*?self\.btn_delete_history\.setEnabled\(enabled\)", set_edit_rep, content, flags=re.DOTALL)

# 8. Update save_notes
save_notes_rep = """    def save_notes(self):
        items = self.list_widget.selectedItems()
        if not items: return
        
        data = items[0].data(Qt.UserRole)
        old_ts = data['timestamp']
        
        new_notes = self.txt_notes.toPlainText()
        new_name = self.edit_meas_name.text().strip()
        new_ts = self.edit_meas_date.text().strip()
        
        # fallback if empty
        if not new_ts: new_ts = old_ts
        
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # If timestamp changed, check if new one exists to prevent collision
            if new_ts != old_ts:
                cursor.execute("SELECT 1 FROM Measurements WHERE timestamp = ?", (new_ts,))
                if cursor.fetchone():
                    # Collision! Revert UI to old timestamp
                    self.edit_meas_date.blockSignals(True)
                    self.edit_meas_date.setText(old_ts)
                    self.edit_meas_date.blockSignals(False)
                    new_ts = old_ts
            
            cursor.execute('UPDATE Measurements SET notes = ?, meas_name = ?, timestamp = ? WHERE timestamp = ?', 
                           (new_notes, new_name, new_ts, old_ts))
            conn.commit()
            conn.close()
            
            # Update item data
            data['notes'] = new_notes
            data['meas_name'] = new_name
            data['timestamp'] = new_ts
            data['iem_name'] = new_name if new_name else data.get('base_name', '')
            items[0].setData(Qt.UserRole, data)
            
            # Update Card UI
            card = self.list_widget.itemWidget(items[0])
            if card:
                card.findChild(QLabel, "lbl_iem").setText(data['iem_name'])
                card.findChild(QLabel, "lbl_date").setText(data['timestamp'])
                
            # If timestamp changed, reload entirely so sort order is correct?
            if new_ts != old_ts:
                # We could reload entirely, but let's just let it be until next refresh
                pass
                
        except Exception as e:
            print(f"Error autosaving: {e}")"""
content = re.sub(r"    def save_notes\(self\):.*?conn\.close\(\)\n            data\['notes'\] = new_notes\n        except Exception as e:\n            print\(e\)", save_notes_rep, content, flags=re.DOTALL)

with open("history_ui.py", "w") as f:
    f.write(content)
