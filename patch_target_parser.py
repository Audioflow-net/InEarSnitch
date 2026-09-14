import sys

with open('main.py', 'r') as f:
    content = f.read()

old_parser = """            import numpy as np
            try:
                csv_data = np.genfromtxt(data, delimiter=',', invalid_raise=False)
                if csv_data.ndim == 1 or csv_data.shape[1] < 2:
                    csv_data = np.genfromtxt(data, invalid_raise=False)
                if csv_data.ndim > 1 and csv_data.shape[1] >= 2:
                    valid_rows = ~np.isnan(csv_data[:, 0]) & ~np.isnan(csv_data[:, 1])
                    self.target_freqs = csv_data[valid_rows, 0]
                    self.target_mags = csv_data[valid_rows, 1]
            except Exception as e:
                print("Error loading target CSV:", e)"""

new_parser = """            import numpy as np
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

content = content.replace(old_parser, new_parser)

with open('main.py', 'w') as f:
    f.write(content)
