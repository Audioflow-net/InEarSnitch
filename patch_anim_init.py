import re

with open("main.py", "r") as f:
    code = f.read()

old_init = """        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.sweeps = 1
        self.start_time = 0"""

new_init = """        self.sweeps = 1"""

code = code.replace(old_init, new_init)

with open("main.py", "w") as f:
    f.write(code)

print("MeasurementAnimator init patched.")
