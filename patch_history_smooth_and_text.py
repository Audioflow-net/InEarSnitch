import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Update text to just inherit the 64px font size!
code = code.replace(
    'self.set_text(f"SCANNING<br><span style=\\"font-size: 56px;\\">{sweep_num}/{self.sweeps}</span>")',
    'self.set_text(f"SCANNING<br>{sweep_num} / {self.sweeps}")'
)

# 2. Add smoothing to the history traces
pattern_history = r'''        if getattr\(self, 'history_freqs', None\) is not None:
            import pyqtgraph as pg
            if getattr\(self, 'history_mag_l', None\) is not None and self\.get_current_channel\(\) == "Left":
                self\.history_line_l = self\.plot_widget\.plot\(
                    self\.history_freqs,
                    self\.history_mag_l,
                    pen=pg\.mkPen\(theme\.get_color\('history_l'\), width=2, style=Qt\.DashLine\),
                    name="History L"
                \)
            if getattr\(self, 'history_mag_r', None\) is not None and self\.get_current_channel\(\) == "Right":
                self\.history_line_r = self\.plot_widget\.plot\(
                    self\.history_freqs,
                    self\.history_mag_r,
                    pen=pg\.mkPen\(theme\.get_color\('history_r'\), width=2, style=Qt\.DashLine\),
                    name="History R"
                \)'''

replacement_history = r'''        if getattr(self, 'history_freqs', None) is not None:
            import pyqtgraph as pg
            from audio_engine import AudioEngine
            
            smooth_txt = self.cb_smooth.currentText()
            if smooth_txt == "1/24 Oct": pts = 240
            elif smooth_txt == "1/48 Oct": pts = 480
            elif smooth_txt == "1/12 Oct": pts = 120
            elif smooth_txt == "1/6 Oct": pts = 60
            else: pts = 0
            
            if getattr(self, 'history_mag_l', None) is not None and self.get_current_channel() == "Left":
                f_h, m_h, _ = AudioEngine.smooth_spectrum(self.history_freqs, self.history_mag_l, points=pts)
                self.history_line_l = self.plot_widget.plot(
                    f_h, m_h,
                    pen=pg.mkPen(theme.get_color('history_l'), width=2, style=Qt.DashLine),
                    name="History L"
                )
            if getattr(self, 'history_mag_r', None) is not None and self.get_current_channel() == "Right":
                f_h, m_h, _ = AudioEngine.smooth_spectrum(self.history_freqs, self.history_mag_r, points=pts)
                self.history_line_r = self.plot_widget.plot(
                    f_h, m_h,
                    pen=pg.mkPen(theme.get_color('history_r'), width=2, style=Qt.DashLine),
                    name="History R"
                )'''

code = re.sub(pattern_history, replacement_history, code)

with open("main.py", "w") as f:
    f.write(code)

print("Text size and history smoothing patched.")
