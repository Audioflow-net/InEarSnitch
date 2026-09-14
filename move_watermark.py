import sys

with open('main.py', 'r') as f:
    content = f.read()

# Make the watermark attach to the analysis page
old_wm = """        import pyqtgraph as pg
        # Use HTML to ensure text is right-aligned and natively rendered by OpenGL to avoid white-box bugs on macOS
        self.watermark_item = pg.TextItem(html=f'<div style="color: {theme.get_color("watermark")}; font-size: 32px; font-weight: bold; line-height: 1.2;"><center>NO PROFILE<br>Left</center></div>', anchor=(1, 0))
        # Add directly to ViewBox so it ignores data coordinate scaling but sticks to the view
        self.watermark_item.setParentItem(self.plot_widget.getViewBox())
        
        def update_wm_pos(vb):
            rect = vb.boundingRect()
            self.watermark_item.setPos(rect.right() - 20, rect.top() + 20)
            
        self.plot_widget.getViewBox().sigResized.connect(update_wm_pos)"""

new_wm = """        import pyqtgraph as pg
        self.watermark_item = pg.TextItem(html=f'<div style="color: {theme.get_color("watermark")}; font-size: 32px; font-weight: bold; line-height: 1.2;"><center>NO PROFILE<br>Left</center></div>', anchor=(1, 0))
        # Wait, self.page_ana isn't created yet here! We will move this assignment below page_ana creation."""
content = content.replace(old_wm, new_wm)

# Now inject the assignment AFTER self.page_ana is created (line ~975)
old_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_sweep)
        self.workspace_stacked.addWidget(page_meas)
        self.workspace_stacked.addWidget(self.page_ana)"""

new_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_sweep)
        self.workspace_stacked.addWidget(page_meas)
        self.workspace_stacked.addWidget(self.page_ana)
        
        # Attach watermark to analysis widget
        self.watermark_item.setParentItem(self.page_ana.plot_widget.getViewBox())
        def update_wm_pos(vb=None):
            rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            self.watermark_item.setPos(rect.right() - 20, rect.top() + 20)
        self.page_ana.plot_widget.getViewBox().sigResized.connect(update_wm_pos)
        update_wm_pos()"""
content = content.replace(old_ana, new_ana)

with open('main.py', 'w') as f:
    f.write(content)
