import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Left tab: remove text and hide tab bar
code = code.replace('self.graph_tabs.addTab(self.fr_container, "Measurement History")', 
                    'self.graph_tabs.addTab(self.fr_container, "")\n        self.graph_tabs.tabBar().hide()')

# 2. Right tab: change "Measurements" to "ARCHIVE"
code = code.replace('self.tools_tabs.addTab(target_tab, "Measurements")', 
                    'self.tools_tabs.addTab(target_tab, "ARCHIVE")')

with open("history_ui.py", "w") as f:
    f.write(code)
