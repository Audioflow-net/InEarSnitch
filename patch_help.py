import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# 1. Inject the HelpHoverButton class at the top
class_injection = """from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSplitter, QTabWidget, QComboBox, QDial, QLineEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QObject

class HelpHoverButton(QPushButton):
    def __init__(self, text, target_widget, parent=None):
        super().__init__(text, parent)
        self.target_widget = target_widget
        self.setFixedSize(24, 24)
        self.setStyleSheet("QPushButton { border-radius: 12px; background: #3f3f46; color: white; font-weight: bold; font-size: 13px; border: none; } QPushButton:hover { background: #0ea5e9; }")
        self.setCursor(Qt.PointingHandCursor)
        
    def enterEvent(self, event):
        self.target_widget.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.target_widget.hide()
        super().leaveEvent(event)
"""

content = content.replace("from PySide6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSplitter, QTabWidget, QComboBox, QDial, QLineEdit, QSizePolicy\nfrom PySide6.QtCore import Qt, Signal, QTimer, QSize, QPropertyAnimation, QEasingCurve, QObject", class_injection)


# 2. Modify THD layout
thd_old = """        thd_layout.addWidget(self.thd_widget)
        
        # Stress test button bar
        stress_bar = QHBoxLayout()"""

thd_new = """        
        # THD Help
        self.thd_help_lbl = QLabel("<b>THD (Total Harmonic Distortion)</b> shows unwanted harmonics added by the driver.<br>"
                                  "Spikes indicate resonance or clipping issues in the acoustic path.<br>"
                                  "<b>L2 = 2nd order</b> (Warmth/Thickness) | <b>L3 = 3rd order</b> (Harshness/Metallic). Lower is better.")
        self.thd_help_lbl.setStyleSheet("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 6px; padding: 10px; font-size: 13px;")
        self.thd_help_lbl.setWordWrap(True)
        self.thd_help_lbl.hide()
        
        btn_thd_help = HelpHoverButton("?", self.thd_help_lbl)
        
        thd_top_bar = QHBoxLayout()
        thd_top_bar.addWidget(self.thd_help_lbl)
        thd_top_bar.addStretch()
        thd_top_bar.addWidget(btn_thd_help)
        thd_top_bar.setAlignment(btn_thd_help, Qt.AlignTop)
        
        thd_layout.addLayout(thd_top_bar)
        thd_layout.addWidget(self.thd_widget)
        
        # Stress test button bar
        stress_bar = QHBoxLayout()"""

content = content.replace(thd_old, thd_new)


# 3. Modify CSD Graph
csd_old = """        # 3. CSD Graph
        self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.csd_widget.setClipToView(True)
        self.csd_widget.setDownsampling(auto=True, mode='peak')
        self.csd_widget.setBackground('#18181b')
        self.csd_widget.setLogMode(x=True, y=False)
        self.csd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.csd_widget.getAxis('bottom').setHeight(25)
        self.csd_widget.setLabel('left', 'Magnitude (dB)')
        self.csd_widget.getAxis('left').setWidth(45)
        self.csd_widget.setXRange(np.log10(200), np.log10(20000))
        self.csd_widget.setYRange(-60, 20)
        self.csd_widget.getViewBox().disableAutoRange()
        self.graph_tabs.addTab(self.csd_widget, "Waterfall (CSD)")"""

csd_new = """        # 3. CSD Graph
        csd_container = QWidget()
        csd_layout = QVBoxLayout(csd_container)
        csd_layout.setContentsMargins(5, 5, 5, 5)
        
        self.csd_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.csd_widget.setClipToView(True)
        self.csd_widget.setDownsampling(auto=True, mode='peak')
        self.csd_widget.setBackground('#18181b')
        self.csd_widget.setLogMode(x=True, y=False)
        self.csd_widget.showGrid(x=True, y=True, alpha=0.3)
        self.csd_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.csd_widget.getAxis('bottom').setHeight(25)
        self.csd_widget.setLabel('left', 'Magnitude (dB)')
        self.csd_widget.getAxis('left').setWidth(45)
        self.csd_widget.setXRange(np.log10(200), np.log10(20000))
        self.csd_widget.setYRange(-60, 20)
        self.csd_widget.getViewBox().disableAutoRange()
        
        # CSD Help
        self.csd_help_lbl = QLabel("<b>CSD (Cumulative Spectral Decay / Waterfall)</b> shows how fast frequencies decay over time.<br>"
                                  "Ridges stretching forward indicate driver ringing or mechanical resonances.<br>"
                                  "A clean, fast drop-off means tight, precise sound reproduction. Less ringing is better.")
        self.csd_help_lbl.setStyleSheet("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 6px; padding: 10px; font-size: 13px;")
        self.csd_help_lbl.setWordWrap(True)
        self.csd_help_lbl.hide()
        
        btn_csd_help = HelpHoverButton("?", self.csd_help_lbl)
        
        csd_top_bar = QHBoxLayout()
        csd_top_bar.addWidget(self.csd_help_lbl)
        csd_top_bar.addStretch()
        csd_top_bar.addWidget(btn_csd_help)
        csd_top_bar.setAlignment(btn_csd_help, Qt.AlignTop)
        
        csd_layout.addLayout(csd_top_bar)
        csd_layout.addWidget(self.csd_widget)
        
        self.graph_tabs.addTab(csd_container, "Waterfall (CSD)")"""

content = content.replace(csd_old, csd_new)

with open("analysis_ui.py", "w") as f:
    f.write(content)
