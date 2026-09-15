import re

with open("history_ui.py", "r") as f:
    content = f.read()

content = content.replace(
    'lbl_iem.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {fg};")',
    'lbl_iem.setStyleSheet(f"background-color: transparent; font-weight: bold; font-size: 13px; color: {fg};")'
)

content = content.replace(
    'lbl_date.setStyleSheet(f"font-size: 10px; color: {text_sec};")',
    'lbl_date.setStyleSheet(f"background-color: transparent; font-size: 10px; color: {text_sec};")'
)

content = content.replace(
    'self.cb_graph.setStyleSheet(f"QCheckBox {{ color: {text_sec}; font-size: 11px; font-weight: bold; }}")',
    'self.cb_graph.setStyleSheet(f"QCheckBox {{ background-color: transparent; color: {text_sec}; font-size: 11px; font-weight: bold; }}")'
)

with open("history_ui.py", "w") as f:
    f.write(content)
