with open('calibration_ui.py', 'r') as f:
    content = f.read()

content = content.replace(
    'self.plot_widget = pg.PlotWidget(title="Calibration Curve")',
    'self.plot_widget = pg.PlotWidget(title="Calibration Curve")\n        self.plot_widget.setClipToView(True)\n        self.plot_widget.setDownsampling(auto=True, mode="peak")'
)

with open('calibration_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
