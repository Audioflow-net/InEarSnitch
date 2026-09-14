import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''        for b in boxes_hist \+ boxes_tgt:
            b\.blockSignals\(False\)'''

replacement = r'''        for b in boxes_hist + boxes_tgt:
            b.blockSignals(False)
            # Make combobox searchable
            b.setEditable(True)
            from PyQt5.QtWidgets import QCompleter
            from PyQt5.QtCore import Qt
            b.setInsertPolicy(b.NoInsert)
            completer = b.completer()
            if completer:
                completer.setCompletionMode(QCompleter.PopupCompletion)
                completer.setFilterMode(Qt.MatchContains)
            
            # Styling the line edit inside the combobox
            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                # Update placeholder text manually if empty
                if b.count() > 0 and b.currentIndex() == -1:
                    line_edit.setText(b.itemText(0))'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Dropdowns patched.")
