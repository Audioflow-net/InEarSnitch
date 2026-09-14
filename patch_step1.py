import sys
import re

with open('main.py', 'r') as f:
    content = f.read()

# 1. Remove page_meas creation and references in setup_ui
page_meas_block = """        page_meas = QWidget()
        meas_layout = QVBoxLayout(page_meas)
        meas_layout.setContentsMargins(15, 15, 15, 15)
        meas_layout.setSpacing(15)
        
        # --- GRAPH (Top) ---
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': FreqAxisItem(orientation='bottom')})
        self.plot_widget.setBackground(theme.get_color('pg_bg'))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15 if theme.is_light() else 0.3)
        self.plot_widget.setLabel('left', 'Magnitude dB SPL')
        self.plot_widget.setLabel('bottom', 'Frequency Hz')
        self.plot_widget.setLogMode(x=True, y=False)
        self.meas_overlay = MeasurementAnimator(self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget)
        
        self.plot_widget.addLegend(offset=(20, 20))
        self.plot_widget.setYRange(40, 120)
        import numpy as np
        # Lock graph ranges so user can't zoom into meaningless areas
        self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0)
        self.plot_widget.setLimits(xMin=np.log10(20), xMax=np.log10(20000))
        self.plot_widget.getViewBox().disableAutoRange(axis=pg.ViewBox.XAxis)
        self.plot_widget.getViewBox().disableAutoRange(axis=pg.ViewBox.YAxis)
        self.plot_widget.setLimits(yMin=20, yMax=140)
        meas_layout.addWidget(self.plot_widget, stretch=1)
        
        # Add dynamic watermark
        self.watermark_item = pg.TextItem("", anchor=(1, 0), color=(80, 80, 80, 150))
        font = QFont("Arial", 28, QFont.Bold)
        self.watermark_item.setFont(font)
        self.watermark_item.setParentItem(self.plot_widget.getViewBox())
        
        def update_wm_pos():
            rect = self.plot_widget.getViewBox().boundingRect()
            self.watermark_item.setPos(rect.right() - 20, rect.top() + 20)
            
        self.plot_widget.getViewBox().sigResized.connect(update_wm_pos)"""

# Instead of removing plot_widget (which is heavily referenced), we'll keep it but NOT add it to the stack.
# Actually, the user wants "rest of the measurement app muss weg". 
# The simplest approach that doesn't break plot_widget references is to just not add it to the stack.
content = content.replace("self.workspace_stacked.addWidget(page_meas)", "")

# 2. Update navigation sidebar
nav_old = """        self.btn_nav_prof = QPushButton("PROFILE")
        self.btn_nav_prof.setToolTip("Navigate to Profile view")
        self.btn_nav_meas = QPushButton("MEASUREMENT")
        self.btn_nav_meas.hide()
        self.btn_nav_meas.setToolTip("Navigate to Measurement view")
        self.btn_nav_ana = QPushButton("WORKSPACE")
        self.btn_nav_ana.setToolTip("Navigate to Analysis view")
        self.btn_nav_hist = QPushButton("HISTORY")
        self.btn_nav_hist.setToolTip("Navigate to History view")
        
        self.style_tab(self.btn_nav_prof, False)
        self.style_tab(self.btn_nav_meas, True)
        self.style_tab(self.btn_nav_ana, False)
        self.style_tab(self.btn_nav_hist, False)
        
        nav_layout.addWidget(self.btn_nav_meas)
        nav_layout.addWidget(self.btn_nav_ana)
        nav_layout.addWidget(self.btn_nav_hist)
        nav_layout.addWidget(self.btn_nav_prof)"""

nav_new = """        self.btn_nav_prof = QPushButton("PROFILE")
        self.btn_nav_prof.setToolTip("Navigate to Profile view")
        self.btn_nav_ana = QPushButton("WORKSPACE")
        self.btn_nav_ana.setToolTip("Navigate to Analysis view")
        self.btn_nav_hist = QPushButton("HISTORY")
        self.btn_nav_hist.setToolTip("Navigate to History view")
        
        self.style_tab(self.btn_nav_prof, False)
        self.style_tab(self.btn_nav_ana, True)
        self.style_tab(self.btn_nav_hist, False)
        
        nav_layout.addWidget(self.btn_nav_ana)
        nav_layout.addWidget(self.btn_nav_hist)
        nav_layout.addWidget(self.btn_nav_prof)"""
content = content.replace(nav_old, nav_new)

# 3. Fix switch_workspace_tab mapping and shortcuts
# Old indices: 0=Prof, 1=Meas, 2=Ana, 3=Hist
# New indices: 0=Prof, 1=Ana, 2=Hist
# Wait! Instead of changing the stack indices globally (which might break other references), 
# the easiest way to remove page_meas from the stack is to just NOT add it.
# Then Ana becomes index 1, Hist becomes index 2.
# Let's see:
# `self.workspace_stacked.addWidget(self.page_prof)` -> index 0
# `self.workspace_stacked.addWidget(self.page_ana)` -> index 1
# `self.workspace_stacked.addWidget(self.page_hist)` -> index 2

content = content.replace("self.workspace_stacked.setCurrentIndex(1)", "self.workspace_stacked.setCurrentIndex(1) # Workspace")
content = content.replace("self.workspace_stacked.setCurrentIndex(2)", "self.workspace_stacked.setCurrentIndex(1)")

# Update switch mapping
old_switch = """    def switch_workspace_tab(self, idx):
        self.workspace_stacked.setCurrentIndex(idx)
        self.style_tab(self.btn_nav_prof, idx == 0)
        self.style_tab(self.btn_nav_meas, idx == 1)
        self.style_tab(self.btn_nav_ana, idx == 2)
        self.style_tab(self.btn_nav_hist, idx == 3)"""
        
new_switch = """    def switch_workspace_tab(self, idx):
        self.workspace_stacked.setCurrentIndex(idx)
        self.style_tab(self.btn_nav_prof, idx == 0)
        self.style_tab(self.btn_nav_ana, idx == 1)
        self.style_tab(self.btn_nav_hist, idx == 2)"""
content = content.replace(old_switch, new_switch)

# Fix click connections
content = content.replace("self.btn_nav_prof.clicked.connect(lambda: self.switch_workspace_tab(0))", "self.btn_nav_prof.clicked.connect(lambda: self.switch_workspace_tab(0))")
content = content.replace("self.btn_nav_meas.clicked.connect(lambda: self.switch_workspace_tab(1))", "")
content = content.replace("self.btn_nav_ana.clicked.connect(lambda: self.switch_workspace_tab(2))", "self.btn_nav_ana.clicked.connect(lambda: self.switch_workspace_tab(1))")
content = content.replace("self.btn_nav_hist.clicked.connect(lambda: self.switch_workspace_tab(3))", "self.btn_nav_hist.clicked.connect(lambda: self.switch_workspace_tab(2))")

# Fix Shortcuts
content = content.replace('QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.switch_workspace_tab(0))', 'QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.switch_workspace_tab(0))')
content = content.replace('QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.switch_workspace_tab(2))', 'QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.switch_workspace_tab(1))')
content = content.replace('QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.switch_workspace_tab(2))', '')
content = content.replace('QShortcut(QKeySequence("Ctrl+4"), self).activated.connect(lambda: self.switch_workspace_tab(3))', 'QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.switch_workspace_tab(2))')

# Any other switch_workspace_tab(2) to 1, and 3 to 2
content = content.replace("self.switch_workspace_tab(2)", "self.switch_workspace_tab(1)")
content = content.replace("self.switch_workspace_tab(3)", "self.switch_workspace_tab(2)")

with open('main.py', 'w') as f:
    f.write(content)
