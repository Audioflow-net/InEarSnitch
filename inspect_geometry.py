from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main import MainWindow
import sys

app = QApplication(sys.argv)
w = MainWindow()
w.resize(1200, 800)
w.show()

def inspect():
    print(f"Window: {w.width()}x{w.height()}")
    print(f"AnalysisWidget: {w.page_ana.width()}x{w.page_ana.height()}")
    print(f"Splitter: {w.page_ana.split_layout.width()}x{w.page_ana.split_layout.height()}")
    print(f"Left Pane: {w.page_ana.graph_tabs.parent().width()}x{w.page_ana.graph_tabs.parent().height()}")
    print(f"Graph Tabs: {w.page_ana.graph_tabs.width()}x{w.page_ana.graph_tabs.height()}")
    print(f"CSD Widget: {w.page_ana.csd_widget.width()}x{w.page_ana.csd_widget.height()}")
    print(f"Control Panel: {w.control_panel.width()}x{w.control_panel.height()}")
    print(f"Control Layout Right Group geometry: {w.control_panel.layout().itemAt(2).geometry()}")
    app.quit()

QTimer.singleShot(1000, inspect)
app.exec()
