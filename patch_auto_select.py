import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace("self.cb_target.count()", "self.cb_meas_target.count()")
code = code.replace("self.cb_target.itemText(i)", "self.cb_meas_target.itemText(i)")
code = code.replace("self.cb_target.setCurrentIndex", "self.cb_meas_target.setCurrentIndex")

with open("main.py", "w") as f:
    f.write(code)

print("Auto select fixed.")
