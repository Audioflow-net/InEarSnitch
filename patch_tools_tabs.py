import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

content = content.replace(
    "self.tools_tabs = QTabWidget()\n        self.tools_tabs.setElideMode(Qt.ElideNone)",
    "self.tools_tabs = QTabWidget()\n        self.tools_tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)\n        self.tools_tabs.setElideMode(Qt.ElideNone)"
)

with open("analysis_ui.py", "w") as f:
    f.write(content)
