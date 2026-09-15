from PySide6.QtWidgets import QApplication
from main import MainWindow
import sys
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

app = QApplication(sys.argv)
window = MainWindow()
window.resize(1280, 800)
window.show()

# Add dummy CSD data so the card renders
window.page_ana._last_report = [{'title': 'Left Treble Resonance (CSD)', 'status': 'WARN', 'desc': 'Slow treble decay... ' * 50, 'band': (2000, 7000), 'category': 'CSD'}]

step = 0
def take_screenshot():
    global step
    pixmap = window.grab()
    pixmap.save(f"screenshot_step{step}.png")
    print(f"Saved screenshot_step{step}.png")
    step += 1
    if step == 1:
        print("Switching to Waterfall tab...")
        window.page_ana.graph_tabs.setCurrentIndex(2)
        QTimer.singleShot(100, take_screenshot)
    elif step < 10:
        QTimer.singleShot(100, take_screenshot)
    else:
        app.quit()

QTimer.singleShot(500, take_screenshot)
app.exec()
