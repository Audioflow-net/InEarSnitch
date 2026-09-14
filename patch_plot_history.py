import re

with open("main.py", "r") as f:
    code = f.read()

# Add removal logic for history lines to plot_target_curve
insert_start = r'''    def plot_target_curve\(self\):
        if hasattr\(self, 'target_line'\) and self.target_line is not None:
            self.plot_widget.removeItem\(self.target_line\)
            self.target_line = None'''

new_start = '''    def plot_target_curve(self):
        if hasattr(self, 'target_line') and self.target_line is not None:
            self.plot_widget.removeItem(self.target_line)
            self.target_line = None
        if hasattr(self, 'history_line_l') and self.history_line_l is not None:
            self.plot_widget.removeItem(self.history_line_l)
            self.history_line_l = None
        if hasattr(self, 'history_line_r') and self.history_line_r is not None:
            self.plot_widget.removeItem(self.history_line_r)
            self.history_line_r = None'''
            
code = re.sub(insert_start, new_start, code)

# Add plotting logic for history lines at the end of plot_target_curve
# We'll replace `        self.target_line = self.plot_widget.plot(` and everything up to the end of the method
insert_end = r'''            self\.target_line = self\.plot_widget\.plot\(
                tgt_f, 
                aligned_mags, 
                pen=pg\.mkPen\(theme\.get_color\('curve_target'\), width=2, style=Qt\.DashLine\), 
                name=f"Target \(aligned @\{anchor//1000 if anchor>=1000 else anchor\}\{'kHz' if anchor>=1000 else 'Hz'\}\)" if anchor else "Target"
            \)'''

new_end = '''            self.target_line = self.plot_widget.plot(
                tgt_f, 
                aligned_mags, 
                pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), 
                name=f"Target (aligned @{anchor//1000 if anchor>=1000 else anchor}{'kHz' if anchor>=1000 else 'Hz'})" if anchor else "Target"
            )

        if getattr(self, 'history_freqs', None) is not None:
            import pyqtgraph as pg
            if getattr(self, 'history_mag_l', None) is not None and self.get_current_channel() == "Left":
                self.history_line_l = self.plot_widget.plot(
                    self.history_freqs,
                    self.history_mag_l,
                    pen=pg.mkPen(theme.get_color('history_l'), width=2, style=Qt.DashLine),
                    name="History L"
                )
            if getattr(self, 'history_mag_r', None) is not None and self.get_current_channel() == "Right":
                self.history_line_r = self.plot_widget.plot(
                    self.history_freqs,
                    self.history_mag_r,
                    pen=pg.mkPen(theme.get_color('history_r'), width=2, style=Qt.DashLine),
                    name="History R"
                )'''
                
code = re.sub(insert_end, new_end, code)

with open("main.py", "w") as f:
    f.write(code)

print("Plot history injected.")
