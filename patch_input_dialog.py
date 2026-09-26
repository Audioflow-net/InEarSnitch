import re

with open("history_ui.py", "r") as f:
    content = f.read()

old_logic = """        target_name, ok = QInputDialog.getText(self, "Save Target", "Target Name:", text=f"{iem} Target")
        if ok and target_name:"""

new_logic = """        dialog = QInputDialog(self)
        dialog.setWindowTitle("Save Target")
        dialog.setLabelText("Target Name:")
        dialog.setTextValue(f"{iem} Target")
        dialog.setMinimumWidth(400)
        dialog.resize(450, 150)
        
        import theme
        bg = theme.get_color('bg_panel')
        fg = theme.get_color('text_primary')
        border = theme.get_color('border')
        dialog.setStyleSheet(f"QInputDialog {{ background-color: {bg}; color: {fg}; }} QLineEdit {{ background-color: #111; color: white; border: 1px solid {border}; padding: 6px; border-radius: 4px; }} QLabel {{ color: {fg}; }} QPushButton {{ background-color: #333; color: white; border: 1px solid {border}; padding: 6px 12px; border-radius: 4px; }}")
        
        ok = dialog.exec()
        target_name = dialog.textValue()
        
        if ok and target_name:"""

content = content.replace(old_logic, new_logic)

with open("history_ui.py", "w") as f:
    f.write(content)
