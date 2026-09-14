import sys

with open('main.py', 'r') as f:
    content = f.read()

old_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_measurement)
        
        self.watermark_item.setParentItem(self.page_ana.plot_widget.getViewBox())"""

new_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_measurement)
        
        # Re-attach the measurement overlay to the visible Analysis graph!
        self.meas_overlay = MeasurementAnimator(self.page_ana.plot_widget)
        
        self.watermark_item.setParentItem(self.page_ana.plot_widget.getViewBox())"""

content = content.replace(old_ana, new_ana)

with open('main.py', 'w') as f:
    f.write(content)
