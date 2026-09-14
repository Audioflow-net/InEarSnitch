import re

with open('main.py', 'r') as f:
    content = f.read()

perf_code = """pg.setConfigOption('background', '#18181b')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('antialias', True)  # Smoother curves
pg.setConfigOption('useOpenGL', False) # Disable OpenGL to prevent macOS crashes, software rendering is extremely fast in Qt6 anyway

# Global performance tweaks for pyqtgraph
pg.setConfigOption('useCupy', False)
pg.setConfigOption('useNumba', False)
"""

content = content.replace("pg.setConfigOption('background', '#18181b')", perf_code)

with open('main.py', 'w') as f:
    f.write(content)

# Now in analysis_ui.py, let's enable clipToView and autoDownsampling!
with open('analysis_ui.py', 'r') as f:
    content2 = f.read()

# Replace creation of PlotWidgets to include perf settings
content2 = content2.replace(
    "self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})",
    "self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})\n        self.plot_widget.setClipToView(True)\n        self.plot_widget.setDownsampling(auto=True, mode='peak')"
)
content2 = content2.replace(
    "self.thd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})",
    "self.thd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})\n        self.thd_widget.setClipToView(True)\n        self.thd_widget.setDownsampling(auto=True, mode='peak')"
)
content2 = content2.replace(
    "self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})",
    "self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})\n        self.csd_widget.setClipToView(True)\n        self.csd_widget.setDownsampling(auto=True, mode='peak')"
)

with open('analysis_ui.py', 'w') as f:
    f.write(content2)

print("SUCCESS")
