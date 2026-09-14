import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Fix tools_tabs style to have a bottom border
tools_tabs_style_old = r'self\.tools_tabs\.setStyleSheet\(f"QTabWidget::tab-bar \{\{ alignment: center; \}\} QTabWidget::pane \{\{ border: 1px solid \{border\}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; \}\} QTabBar::tab \{\{ background: \{bg\}; color: \{text_sec\}; padding: 4px 10px; min-width: 80px; border: 1px solid \{border\}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; \}\} QTabBar::tab:selected \{\{ background: \{active\}; color: \{fg\}; \}\}"\)'

tools_tabs_style_new = 'self.tools_tabs.setStyleSheet(f"QTabWidget::tab-bar {{ alignment: center; }} QTabWidget::pane {{ border: 1px solid {border}; border-radius: 4px; }} QTabBar::tab {{ background: {bg}; color: {text_sec}; padding: 4px 10px; min-width: 80px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; font-size: 11px; }} QTabBar::tab:selected {{ background: {active}; color: {fg}; }}")'

code = re.sub(tools_tabs_style_old, tools_tabs_style_new, code)

# 2. Remove lbl_notes and increase txt_notes height
# lbl_notes = QLabel("Notes:")
# lbl_notes.setStyleSheet(f"color: {text_sec}; font-weight: bold;")
# self.txt_notes = QLineEdit()
# self.txt_notes.setPlaceholderText("Measurement Notes...")
# self.txt_notes.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
# ...
# edit_layout.addWidget(lbl_notes)

notes_creation_old = r'lbl_notes = QLabel\("Notes:"\)\n\s*lbl_notes\.setStyleSheet\(f"color: \{text_sec\}; font-weight: bold;"\)\n\s*self\.txt_notes = QLineEdit\(\)\n\s*self\.txt_notes\.setPlaceholderText\("Measurement Notes\.\.\."\)\n\s*self\.txt_notes\.setStyleSheet\(f"background-color: \{bg_hover\}; color: \{fg\}; border: 1px solid \{border\}; padding: 6px; border-radius: 4px;"\)'

notes_creation_new = 'self.txt_notes = QLineEdit()\n        self.txt_notes.setFixedHeight(36)\n        self.txt_notes.setPlaceholderText("Measurement Notes...")\n        self.txt_notes.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 8px 12px; border-radius: 6px; font-size: 12px;")'

code = re.sub(notes_creation_old, notes_creation_new, code)
code = code.replace("edit_layout.addWidget(lbl_notes)\n", "")
code = code.replace("edit_layout.addWidget(lbl_notes)", "")

with open("history_ui.py", "w") as f:
    f.write(code)
