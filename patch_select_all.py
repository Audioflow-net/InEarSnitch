import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''            line_edit = b\.lineEdit\(\)
            if line_edit:
                line_edit\.setStyleSheet\("background: transparent; color: white; border: none; padding: 2px;"\)'''

replacement = r'''            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                
                # Make text select all on focus/click so user doesn't have to delete it
                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.FocusIn:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        elif event.type() == QtCore.QEvent.MouseButtonPress:
                            QtCore.QTimer.singleShot(0, obj.selectAll)
                        return super().eventFilter(obj, event)
                
                # Attach to keep reference
                b._focus_filter = FocusSelectFilter(b)
                line_edit.installEventFilter(b._focus_filter)'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Select All patched.")
