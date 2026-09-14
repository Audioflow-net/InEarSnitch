import re

# 1. Patch main.py
with open("main.py", "r") as f:
    code = f.read()

# Fix grid alpha
code = code.replace(
    'self.plot_widget.showGrid(x=True, y=True, alpha=0.3)',
    'self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)'
)

# Remove the Prev1, 2, 3 logic!
# We will just remove that entire sqlite block in redraw_graph
pattern_prevs = r'''            try:
                import sqlite3
                conn = sqlite3\.connect\(self\.db\.db_path\)
                c = conn\.cursor\(\)
                c\.execute\(\'\'\'
                    SELECT frequencies, magnitude_l, magnitude_r
                    FROM Measurements
                    WHERE iem_id = \?
                    ORDER BY timestamp DESC
                    LIMIT 3
                \'\'\', \(self\.current_iem_id,\)\)
                rows = c\.fetchall\(\)
                conn\.close\(\)
                
                for idx, row in enumerate\(rows\):
                    f_blob, ml_blob, mr_blob = row
                    if f_blob:
                        freq = np\.frombuffer\(f_blob, dtype=np\.float64\)
                        alpha = max\(40, 120 - \(idx \* 30\)\) # Fade out older ones
                        
                        if ml_blob:
                            ml = np\.frombuffer\(ml_blob, dtype=np\.float64\)
                            f_h, m_h, _ = AudioEngine\.smooth_spectrum\(freq, ml, points=pts or 0\)
                            r, g, b = theme\.get_color\('curve_left_rgb'\)
                            self\.plot_widget\.plot\(f_h, m_h, pen=pg\.mkPen\(color=\(r, g, b, alpha\), width=1\), name=f"Prev\{idx\+1\} L"\)
                        if mr_blob:
                            mr = np\.frombuffer\(mr_blob, dtype=np\.float64\)
                            f_h, m_h, _ = AudioEngine\.smooth_spectrum\(freq, mr, points=pts or 0\)
                            r, g, b = theme\.get_color\('curve_right_rgb'\)
                            self\.plot_widget\.plot\(f_h, m_h, pen=pg\.mkPen\(color=\(r, g, b, alpha\), width=1, style=Qt\.DashLine\), name=f"Prev\{idx\+1\} R"\)
            except Exception as e:
                pass'''

code = re.sub(pattern_prevs, '', code)

with open("main.py", "w") as f:
    f.write(code)


# 2. Patch analysis_ui.py
with open("analysis_ui.py", "r") as f:
    code = f.read()

code = code.replace(
    'showGrid(x=True, y=True, alpha=0.3)',
    'showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)'
)

# make sure theme is imported in analysis_ui.py if not already. 
# It already is, since it uses theme.get_color.

with open("analysis_ui.py", "w") as f:
    f.write(code)

# 3. Patch history_ui.py
with open("history_ui.py", "r") as f:
    code = f.read()

code = code.replace(
    'showGrid(x=True, y=True, alpha=0.3)',
    'showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)'
)

with open("history_ui.py", "w") as f:
    f.write(code)

print("Grids and prevs patched.")
