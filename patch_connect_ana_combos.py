import re

with open("main.py", "r") as f:
    code = f.read()

insert_point = r'(        self\.load_targets\(\))'

new_code = r"""        self.page_ana.cb_ana_target.currentIndexChanged.connect(self.on_ana_target_changed)
        self.page_ana.cb_ana_history.currentIndexChanged.connect(self.on_ana_history_changed)
\1"""

code = re.sub(insert_point, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Ana combos connected.")
