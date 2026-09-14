import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''            elif self\.workspace_stacked\.currentIndex\(\) == 3 and hasattr\(self\.page_hist, 'load_history'\):
                self\.page_hist\.load_history\(iem_id\)'''

replacement = r'''            elif self.workspace_stacked.currentIndex() == 3 and hasattr(self.page_hist, 'load_history'):
                self.page_hist.load_history(m_id)'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("ID patched.")
