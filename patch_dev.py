import re

with open("dev.py", "r") as f:
    content = f.read()

old_logic = """def get_mtimes():
    mtimes = {}
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '__pycache__' in root or 'venv' in root:
            continue
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                mtimes[path] = os.path.getmtime(path)
    return mtimes"""

new_logic = """def get_mtimes():
    mtimes = {}
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '__pycache__' in root or 'venv' in root:
            continue
        for f in files:
            if f.endswith('.py') and not f.startswith('.!'):
                path = os.path.join(root, f)
                try:
                    mtimes[path] = os.path.getmtime(path)
                except FileNotFoundError:
                    pass
    return mtimes"""

content = content.replace(old_logic, new_logic)

with open("dev.py", "w") as f:
    f.write(content)
