import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_code = r"""        # Filter based on toggle independently!"""

new_code = """        if freqs is None:
            self.plot_widget.clear()
            self.thd_widget.clear()
            self.csd_widget.clear()
            for i in reversed(range(self.report_layout.count())): 
                w = self.report_layout.itemAt(i).widget()
                if w: w.deleteLater()
            return
            
        # Filter based on toggle independently!"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('analysis_ui.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
