import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''    def update_anim_sync\(self, t_elapsed, sweep_num\):
        import math'''

replacement = r'''    def update_anim_sync(self, t_elapsed, sweep_num):
        try:
            import math'''

code = re.sub(pattern, replacement, code)

pattern2 = r'''        else:
            self\.sweep_line\.hide\(\)
            self\.region\.hide\(\)'''

replacement2 = r'''        else:
            self.sweep_line.hide()
            self.region.hide()
        except Exception as e:
            print("ANIM SYNC CRASH:", e)
            import traceback
            traceback.print_exc()'''

code = re.sub(pattern2, replacement2, code)

with open("main.py", "w") as f:
    f.write(code)

print("Patched with try-except.")
