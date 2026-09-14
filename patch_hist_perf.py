with open('history_ui.py', 'r') as f:
    content = f.read()

content = content.replace(
    "self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})",
    "self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})\n        self.plot_widget.setClipToView(True)\n        self.plot_widget.setDownsampling(auto=True, mode='peak')"
)

with open('history_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
