import re

with open('main.py', 'r') as f:
    content = f.read()

old_logic = """                        if hasattr(self, 'chk_rta_helper') and self.chk_rta_helper.isChecked():
                            self.rta_peak_line.show()"""

new_logic = """                        if hasattr(self, 'chk_rta_helper') and self.chk_rta_helper.isChecked():
                            self.rta_peak_line.show()
                        else:
                            self.rta_peak_line.hide()"""

content = content.replace(old_logic, new_logic)

with open('main.py', 'w') as f:
    f.write(content)
