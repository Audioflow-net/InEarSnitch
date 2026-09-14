import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Update the button styling and action
old_btn = r'self\.btn_import_history = QPushButton\("\+"\)\n\s*self\.btn_import_history\.setToolTip\("Import CSV"\)\n\s*self\.btn_import_history\.setFixedSize\(28, 28\)\n\s*self\.btn_import_history\.setStyleSheet\(.*?\)\n\s*self\.btn_import_history\.clicked\.connect\(self\.import_csv\)'

new_btn = """self.btn_import_history = QPushButton("+")
        self.btn_import_history.setToolTip("Import CSV")
        self.btn_import_history.setFixedSize(28, 28)
        self.btn_import_history.setStyleSheet("QPushButton { background-color: transparent; color: #888; font-weight: bold; font-size: 24px; border: none; padding-bottom: 4px; } QPushButton:hover { color: white; }")
        self.btn_import_history.clicked.connect(self.show_import_menu)"""

code = re.sub(old_btn, new_btn, code, flags=re.DOTALL)


# 2. Replace import_csv with show_import_menu and do_import_csv
old_import_func = r'    def import_csv\(self\):.*?def reset_zoom\(self\):'

new_import_func = """    def show_import_menu(self):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QCursor
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #222; color: white; border: 1px solid #444; } QMenu::item { padding: 6px 24px; } QMenu::item:selected { background-color: #333; }")
        
        act_stereo = menu.addAction("Import as Stereo (L+R)")
        act_left = menu.addAction("Import as Left Channel")
        act_right = menu.addAction("Import as Right Channel")
        
        action = menu.exec(QCursor.pos())
        if action == act_stereo: self.do_import_csv("stereo")
        elif action == act_left: self.do_import_csv("left")
        elif action == act_right: self.do_import_csv("right")

    def do_import_csv(self, mode="stereo"):
        import __main__
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import numpy as np
        import sqlite3
        import os
        
        if not hasattr(__main__, 'window') or not getattr(__main__.window, 'current_iem_id', None):
            QMessageBox.warning(self, "Import CSV", "Please select a specific IEM from the Musician Profile in the sidebar first, so we know where to save the imported data.")
            return
            
        iem_id = __main__.window.current_iem_id
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV Files (*.csv *.txt)")
        if not path: return
        
        try:
            # First try parsing as comma separated, then fallback to tab/space if needed
            data = np.genfromtxt(path, delimiter=',', skip_header=0, invalid_raise=False)
            if np.isnan(data).all():
                # Try space/tab separated (common in REW/Squiglink exports)
                data = np.genfromtxt(path, skip_header=0, invalid_raise=False)
                
            # If the first row is strings (header), skip_header=0 makes them nan.
            # We filter out rows that are entirely nan
            data = data[~np.isnan(data).all(axis=1)]
            
            if data.ndim != 2 or data.shape[1] < 2:
                QMessageBox.critical(self, "Import Error", "CSV format must be at least two columns (Freq, Mag).")
                return
                
            freqs = data[:, 0]
            
            if mode == "left":
                mag_l = data[:, 1]
                mag_r = None
            elif mode == "right":
                mag_l = None
                mag_r = data[:, 1]
            else:
                # Stereo
                mag_l = data[:, 1]
                mag_r = data[:, 2] if data.shape[1] > 2 else data[:, 1] # fallback to mono if no 3rd column
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            filename = os.path.basename(path)
            notes = f"Imported: {filename}"
            
            ml = mag_l.tobytes() if mag_l is not None else b''
            mr = mag_r.tobytes() if mag_r is not None else b''
            pl = b''
            pr = b''
            fb = freqs.tobytes()
            
            c.execute(\"\"\"
                INSERT INTO Measurements 
                (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (iem_id, "Auto", fb, ml, mr, pl, pr, notes, ""))
            conn.commit()
            conn.close()
            
            self.load_history(iem_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import file:\\n{e}")

    def reset_zoom(self):"""

code = re.sub(old_import_func, new_import_func, code, flags=re.DOTALL)

with open("history_ui.py", "w") as f:
    f.write(code)
