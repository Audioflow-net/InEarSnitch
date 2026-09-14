with open('main.py', 'r') as f:
    content = f.read()

old_code = """        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Measurement Failed")
        msg.setText("The audio engine encountered a critical error.")
        msg.setInformativeText(str(err_msg) + "\\n\\nCheck Settings or your macOS Microphone permissions.")
        msg.exec()"""

new_code = """        from PySide6.QtWidgets import QMessageBox
        # Force a UI update so the 'SCANNING' overlay disappears instantly BEFORE the dialog blocks the thread
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        msg = QMessageBox(self)  # FIXED: Passing self as parent keeps it on top!
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Measurement Failed")
        msg.setText("The audio engine encountered a critical error.")
        msg.setInformativeText(str(err_msg) + "\\n\\nCheck Settings or your macOS Microphone permissions.")
        msg.exec()"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('main.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
