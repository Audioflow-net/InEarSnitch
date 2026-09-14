import re

with open("main.py", "r") as f:
    code = f.read()

old_load_targets = """    def load_targets(self):
        self.cb_target.clear()
        self.cb_target.addItem("Select Reference/Target...", None)
        
        # 1. Load DB Measurements
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT m.id, mus.name, iem.model_name, m.timestamp 
            FROM Measurements m
            JOIN IEM_Models iem ON m.iem_id = iem.id
            JOIN Musicians mus ON iem.musician_id = mus.id
            ORDER BY m.timestamp DESC
        ''')
        db_rows = c.fetchall()
        conn.close()
        
        if db_rows:
            # We can't easily add unselectable separators in QComboBox without a custom model, so just add them
            for meas_id, m_name, i_model, ts in db_rows:
                date_str = ts.split(' ')[0] if ts else 'Unknown' # just the date part
                display = f"[DB] {m_name} - {i_model} ({date_str})"
                self.cb_target.addItem(display, ("db", meas_id))
                
        # 2. Load CSV Files
        import os
        import glob
        target_dir = "reference_targets/Pro_Live_IEMs"
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                name = os.path.basename(f).replace('.csv', '')
                self.cb_target.addItem(name, ("file", f))"""

new_load_targets = """    def load_targets(self):
        # We populate the new global combo boxes
        self.cb_global_history.blockSignals(True)
        self.cb_global_history.clear()
        self.cb_global_history.addItem("No History Selected", None)
        
        self.cb_global_target.blockSignals(True)
        self.cb_global_target.clear()
        self.cb_global_target.addItem("No Target Selected", None)
        
        # 1. Load DB Measurements into History
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT m.id, mus.name, iem.model_name, m.timestamp 
            FROM Measurements m
            JOIN IEM_Models iem ON m.iem_id = iem.id
            JOIN Musicians mus ON iem.musician_id = mus.id
            ORDER BY m.timestamp DESC
        ''')
        db_rows = c.fetchall()
        conn.close()
        
        if db_rows:
            for meas_id, m_name, i_model, ts in db_rows:
                date_str = ts.split(' ')[0] if ts else 'Unknown'
                display = f"{m_name} - {i_model} ({date_str})"
                self.cb_global_history.addItem(display, meas_id)
                
        # 2. Load CSV Files into Target
        import os
        import glob
        target_dir = "reference_targets/Pro_Live_IEMs"
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                name = os.path.basename(f).replace('.csv', '')
                self.cb_global_target.addItem(name, f)
                
        self.cb_global_history.blockSignals(False)
        self.cb_global_target.blockSignals(False)"""

code = code.replace(old_load_targets, new_load_targets)

with open("main.py", "w") as f:
    f.write(code)

print("load_targets patched.")
