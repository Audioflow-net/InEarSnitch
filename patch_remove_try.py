import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''    def update_anim_sync\(self, t_elapsed, sweep_num\):
        try:
            import math'''

replacement = r'''    def update_anim_sync(self, t_elapsed, sweep_num):
        import math'''

code = re.sub(pattern, replacement, code)

pattern2 = r'''            self\.region\.hide\(\)
        except Exception as e:
            print\("ANIM SYNC CRASH:", e\)
            import traceback
            traceback\.print_exc\(\)'''

replacement2 = r'''            self.region.hide()'''

code = re.sub(pattern2, replacement2, code)

with open("main.py", "w") as f:
    f.write(code)

print("Removed try-except.")
