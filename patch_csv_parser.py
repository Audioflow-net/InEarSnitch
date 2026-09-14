import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Add _parse_csv_file method
new_method = """    def _parse_csv_file(self, path):
        import numpy as np
        f_list, m_list = [], []
        try:
            with open(path, 'r', encoding='utf-8-sig') as file:
                for line in file:
                    parts = line.replace(';', ',').split(',')
                    if len(parts) >= 2:
                        try:
                            freq = float(parts[0].strip())
                            mag = float(parts[1].strip())
                            f_list.append(freq)
                            m_list.append(mag)
                        except ValueError:
                            pass
            if len(f_list) > 10:
                return np.array(f_list), np.array(m_list)
        except Exception as e:
            print(f"Error parsing file {path}: {e}")
        return None, None
"""
# Insert it after on_meas_target_changed
content = content.replace("    def _apply_target_selection(self, data):", new_method + "\n    def _apply_target_selection(self, data):")

# 2. Update _apply_target_selection
old_target = """        if data:
            import numpy as np
            try:
                # Robust manual parsing to avoid genfromtxt issues with headers/BOM/encodings
                f_list, m_list = [], []
                with open(data, 'r', encoding='utf-8-sig') as file:
                    for line in file:
                        parts = line.replace(';', ',').split(',')
                        if len(parts) >= 2:
                            try:
                                freq = float(parts[0].strip())
                                mag = float(parts[1].strip())
                                f_list.append(freq)
                                m_list.append(mag)
                            except ValueError:
                                pass # Skip headers or invalid rows
                if len(f_list) > 10:
                    self.target_freqs = np.array(f_list)
                    self.target_mags = np.array(m_list)
            except Exception as e:
                print("Error loading target CSV:", e)"""
new_target = """        if data:
            self.target_freqs, self.target_mags = self._parse_csv_file(data)"""
content = content.replace(old_target, new_target)

# 3. Update toggle_live_seal
old_rta_cal = """            cal_f, cal_m = None, None
            cal_path = self.mic_cal_combo.currentData()
            if cal_path:
                try:
                    import numpy as np
                    data = np.genfromtxt(cal_path, invalid_raise=False)
                    if data.ndim > 1 and data.shape[1] >= 2:
                        cal_f = data[:, 0]
                        cal_m = data[:, 1]
                except Exception:
                    pass"""
new_rta_cal = """            cal_f, cal_m = None, None
            cal_path = self.mic_cal_combo.currentData()
            if cal_path:
                cal_f, cal_m = self._parse_csv_file(cal_path)"""
content = content.replace(old_rta_cal, new_rta_cal)

# 4. Update run_measurement
old_meas_cal = """        cal_f, cal_m = None, None
        cal_path = self.mic_cal_combo.currentData()
        if cal_path:
            try:
                import numpy as np
                data = np.genfromtxt(cal_path, invalid_raise=False)
                if data.ndim > 1 and data.shape[1] >= 2:
                    cal_f = data[:, 0]
                    cal_m = data[:, 1]
            except Exception as e:
                log_debug(f"Error loading mic cal: {e}")"""
new_meas_cal = """        cal_f, cal_m = None, None
        cal_path = self.mic_cal_combo.currentData()
        if cal_path:
            cal_f, cal_m = self._parse_csv_file(cal_path)"""
content = content.replace(old_meas_cal, new_meas_cal)

with open('main.py', 'w') as f:
    f.write(content)
