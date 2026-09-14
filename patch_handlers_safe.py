import re

with open("main.py", "r") as f:
    lines = f.readlines()

out = []
in_target = False
for line in lines:
    if line.startswith("    def on_target_selected(self, index=None):"):
        in_target = True
        out.append("""    def on_global_target_changed(self, index=None):
        data = self.cb_global_target.currentData()
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
        
    def on_global_history_changed(self, index=None):
        data = self.cb_global_history.currentData()
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
""")
        continue
        
    if in_target:
        if line.startswith("    def "):
            in_target = False
        else:
            continue
            
    if not in_target:
        out.append(line)

with open("main.py", "w") as f:
    f.writelines(out)

print("Handlers replaced safely.")
