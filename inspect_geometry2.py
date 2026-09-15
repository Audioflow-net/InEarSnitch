from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from main import MainWindow
import sys

app = QApplication(sys.argv)
w = MainWindow()
w.resize(1200, 800)
w.show()

def inspect():
    w.page_ana.graph_tabs.setCurrentIndex(2)
    QApplication.processEvents()
    print(f"Graph Tabs: {w.page_ana.graph_tabs.width()}x{w.page_ana.graph_tabs.height()}")
    print(f"CSD Widget: {w.page_ana.csd_widget.width()}x{w.page_ana.csd_widget.height()}")
    app.quit()

QTimer.singleShot(1000, inspect)
app.exec()
