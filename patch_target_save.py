import re

with open("history_ui.py", "r") as f:
    content = f.read()

old_logic = """                os.makedirs("Reference Targets", exist_ok=True)
                target_path = os.path.join("Reference Targets", f"{target_name.replace('/', '_')}.csv")"""

new_logic = """                target_dir = os.path.join("reference_targets", "Pro_Live_IEMs")
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, f"{target_name.replace('/', '_')}.csv")"""

content = content.replace(old_logic, new_logic)

with open("history_ui.py", "w") as f:
    f.write(content)
