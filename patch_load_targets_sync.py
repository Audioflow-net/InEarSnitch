import re

with open("main.py", "r") as f:
    code = f.read()

# Replace the current load_targets logic
old_load_targets = re.compile(r'    def load_targets\(self\):.*?        self\.cb_global_target\.blockSignals\(False\)', re.DOTALL)

new_load_targets = """    def load_targets(self):
        # We populate the four combo boxes (2 in Meas, 2 in Ana)
        boxes_hist = [self.cb_meas_history, self.page_ana.cb_ana_history]
        boxes_tgt = [self.cb_meas_target, self.page_ana.cb_ana_target]
        
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(True)
            b.clear()
            
        for b in boxes_hist:
            b.addItem("No History Selected", None)
            
        for b in boxes_tgt:
            b.addItem("No Target Selected", None)
            
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
                for b in boxes_hist:
                    b.addItem(display, meas_id)
                
        # 2. Load CSV Files into Target
        import os
        import glob
        target_dir = "reference_targets/Pro_Live_IEMs"
        if os.path.exists(target_dir):
            files = glob.glob(os.path.join(target_dir, "*.csv"))
            for f in sorted(files):
                name = os.path.basename(f).replace('.csv', '')
                for b in boxes_tgt:
                    b.addItem(name, f)
                
        for b in boxes_hist + boxes_tgt:
            b.blockSignals(False)"""

code = re.sub(old_load_targets, new_load_targets, code)

# And now we need to fix the signal handlers!
# Replace on_global_target_changed with on_meas_target_changed / on_ana_target_changed
# We can just write one handler that syncs them!
old_handlers = re.compile(r'    def on_global_target_changed\(self, index=None\):.*?        self\.update_analysis_view\(\)\n', re.DOTALL)

new_handlers = """    def on_meas_target_changed(self, index=None):
        self.page_ana.cb_ana_target.blockSignals(True)
        self.page_ana.cb_ana_target.setCurrentIndex(self.cb_meas_target.currentIndex())
        self.page_ana.cb_ana_target.blockSignals(False)
        self._apply_target_selection(self.cb_meas_target.currentData())
        
    def on_ana_target_changed(self, index=None):
        self.cb_meas_target.blockSignals(True)
        self.cb_meas_target.setCurrentIndex(self.page_ana.cb_ana_target.currentIndex())
        self.cb_meas_target.blockSignals(False)
        self._apply_target_selection(self.page_ana.cb_ana_target.currentData())
        
    def _apply_target_selection(self, data):
        self.target_freqs = None
        self.target_mags = None
        if data:
            import numpy as np
            try:
                csv_data = np.genfromtxt(data, delimiter=',', invalid_raise=False)
                if csv_data.ndim == 1 or csv_data.shape[1] < 2:
                    csv_data = np.genfromtxt(data, invalid_raise=False)
                if csv_data.ndim > 1 and csv_data.shape[1] >= 2:
                    valid_rows = ~np.isnan(csv_data[:, 0]) & ~np.isnan(csv_data[:, 1])
                    self.target_freqs = csv_data[valid_rows, 0]
                    self.target_mags = csv_data[valid_rows, 1]
            except Exception as e:
                print("Error loading target CSV:", e)
        self.plot_target_curve()
        self.update_analysis_view()

    def on_meas_history_changed(self, index=None):
        self.page_ana.cb_ana_history.blockSignals(True)
        self.page_ana.cb_ana_history.setCurrentIndex(self.cb_meas_history.currentIndex())
        self.page_ana.cb_ana_history.blockSignals(False)
        self._apply_history_selection(self.cb_meas_history.currentData())
        
    def on_ana_history_changed(self, index=None):
        self.cb_meas_history.blockSignals(True)
        self.cb_meas_history.setCurrentIndex(self.page_ana.cb_ana_history.currentIndex())
        self.cb_meas_history.blockSignals(False)
        self._apply_history_selection(self.page_ana.cb_ana_history.currentData())
        
    def _apply_history_selection(self, data):
        self.history_freqs = None
        self.history_mag_l = None
        self.history_mag_r = None
        if data:
            import numpy as np
            import sqlite3
            conn = sqlite3.connect(self.db.db_path)
            c = conn.cursor()
            c.execute('SELECT freqs, mag_l, mag_r FROM Measurements WHERE id=?', (data,))
            row = c.fetchone()
            conn.close()
            if row:
                import json
                self.history_freqs = np.array(json.loads(row[0]))
                if row[1]: self.history_mag_l = np.array(json.loads(row[1]))
                if row[2]: self.history_mag_r = np.array(json.loads(row[2]))
        self.plot_target_curve()
        self.update_analysis_view()
"""

code = re.sub(old_handlers, new_handlers, code)

with open("main.py", "w") as f:
    f.write(code)

print("Load targets and sync handlers patched.")
