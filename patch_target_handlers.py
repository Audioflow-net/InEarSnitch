import re

with open("main.py", "r") as f:
    code = f.read()

# Replace on_target_selected with new handlers
old_handler = re.compile(r'    def on_target_selected\(self, index=None\):.*?            self\.redraw_graph\(\)\n', re.DOTALL)

new_handler = """    def on_global_target_changed(self, index=None):
        data = self.cb_global_target.currentData()
        self.target_freqs = None
        self.target_mags = None
        
        if data:
            import numpy as np
            try:
                csv_data = np.genfromtxt(data, delimiter=',', invalid_raise=False)
                if csv_data.ndim == 2 and csv_data.shape[1] >= 2:
                    self.target_freqs = csv_data[:, 0]
                    self.target_mags = csv_data[:, 1]
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
                
        self.plot_target_curve() # Update Measurement view (we can plot history here too if we want)
        self.update_analysis_view()

    # Stub to replace the old method body that was matched
    def redraw_graph(self):
"""

code = re.sub(old_handler, new_handler, code)

with open("main.py", "w") as f:
    f.write(code)

print("Handlers patched.")
