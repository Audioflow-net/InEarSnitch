import re

with open("history_ui.py", "r") as f:
    code = f.read()

pattern_buttons = r'''        self\.btn_export_history = QPushButton\("Export Selected to CSV"\)
        self\.btn_export_history\.setToolTip\("Export selected history to CSV format"\)
        self\.btn_export_history\.setProperty\("class", "accent"\)
        self\.btn_export_history\.clicked\.connect\(self\.export_selected_csv\)
        btn_row\.addWidget\(self\.btn_export_history\)
        
        self\.btn_delete_history = QPushButton\("Delete Selected"\)
        self\.btn_delete_history\.setToolTip\("Delete selected history entries"\)
        self\.btn_delete_history\.setProperty\("class", "danger"\)
        self\.btn_delete_history\.clicked\.connect\(self\.delete_selected\)
        btn_row\.addWidget\(self\.btn_delete_history\)'''

btn_style = """
            QPushButton { background-color: #2a2a2d; color: white; border: 1px solid #3f3f46; border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #3f3f46; }
"""
btn_danger_style = """
            QPushButton { background-color: #7f1d1d; color: white; border: 1px solid #991b1b; border-radius: 4px; padding: 6px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #991b1b; }
"""

replacement_buttons = f'''        btn_style = """{btn_style}"""
        btn_danger_style = """{btn_danger_style}"""
        
        self.btn_import_history = QPushButton("Import CSV")
        self.btn_import_history.setStyleSheet(btn_style)
        self.btn_import_history.clicked.connect(self.import_csv)
        btn_row.addWidget(self.btn_import_history)
        
        self.btn_export_history = QPushButton("Export Selected")
        self.btn_export_history.setStyleSheet(btn_style)
        self.btn_export_history.clicked.connect(self.export_selected_csv)
        btn_row.addWidget(self.btn_export_history)
        
        self.btn_delete_history = QPushButton("Delete Selected")
        self.btn_delete_history.setStyleSheet(btn_danger_style)
        self.btn_delete_history.clicked.connect(self.delete_selected)
        btn_row.addWidget(self.btn_delete_history)'''

code = re.sub(pattern_buttons, replacement_buttons, code)

# Inject import_csv method
injection_import = r'''    def import_csv(self):
        import __main__
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import numpy as np
        import sqlite3
        import datetime
        
        if not hasattr(__main__, 'window') or not getattr(__main__.window, 'current_iem_id', None):
            QMessageBox.warning(self, "Import CSV", "Please select a specific IEM from the Musician Profile in the sidebar first, so we know where to save the imported data.")
            return
            
        iem_id = __main__.window.current_iem_id
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            data = np.genfromtxt(path, delimiter=',', skip_header=1, invalid_raise=False)
            if data.ndim != 2 or data.shape[1] < 2:
                QMessageBox.critical(self, "Import Error", "CSV format must be at least two columns (Freq, Mag_L).")
                return
                
            freqs = data[:, 0]
            mag_l = data[:, 1]
            mag_r = data[:, 2] if data.shape[1] > 2 else None
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            import os
            filename = os.path.basename(path)
            notes = f"Imported: {filename}"
            
            ml = mag_l.tobytes() if mag_l is not None else b''
            mr = mag_r.tobytes() if mag_r is not None else b''
            pl = b''
            pr = b''
            fb = freqs.tobytes()
            
            c.execute("""
                INSERT INTO Measurements 
                (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (iem_id, "Auto", fb, ml, mr, pl, pr, notes, ""))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Import Success", "CSV successfully imported!")
            
            # Reload
            if hasattr(self, 'last_m_id'):
                self.load_history(self.last_m_id)
            __main__.window.load_targets() # Update dropdowns
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")

    def load_history(self, m_id):'''

code = code.replace('    def load_history(self, m_id):', injection_import)

# We need to save last_m_id in load_history so we can reload
code = code.replace('    def load_history(self, m_id):', '    def load_history(self, m_id):\n        self.last_m_id = m_id')

with open("history_ui.py", "w") as f:
    f.write(code)

print("Buttons and Import patched.")
