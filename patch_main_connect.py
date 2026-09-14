import sys

with open('main.py', 'r') as f:
    content = f.read()

old_code = """        self.page_ana = AnalysisWidget()
        self.workspace_stacked.addWidget(self.page_ana)"""

new_code = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_measurement)
        self.workspace_stacked.addWidget(self.page_ana)"""

content = content.replace(old_code, new_code)

with open('main.py', 'w') as f:
    f.write(content)
