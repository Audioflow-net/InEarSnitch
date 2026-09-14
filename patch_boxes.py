import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Close graph_tabs border
old_graph_style = 'self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }}'
new_graph_style = 'self.graph_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ left: 0px; alignment: left; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }}'
code = code.replace(old_graph_style, new_graph_style)

# 2. Add border to edit_container and use dynamic theme background
old_edit_style = 'self.edit_container.setStyleSheet("#EditContainer { background-color: #222; border-radius: 8px; }")'
new_edit_style = 'bg_panel = theme.get_color("bg_panel")\n        self.edit_container.setStyleSheet(f"#EditContainer {{ background-color: {bg_panel}; border: 1px solid {border}; border-radius: 4px; }}")'
code = code.replace(old_edit_style, new_edit_style)

with open("history_ui.py", "w") as f:
    f.write(code)
