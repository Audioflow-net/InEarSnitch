import ast
import os

files = ['main.py', 'analysis_ui.py', 'profile_ui.py', 'history_ui.py']
for filepath in files:
    if not os.path.exists(filepath): continue
    with open(filepath, 'r') as f:
        content = f.read()
    tree = ast.parse(content)
    
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes[node] = filepath

    for cls, fp in classes.items():
        buttons = set()
        connects = set()
        
        # Find all self.btn_something assignments
        for node in ast.walk(cls):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                        if target.attr.startswith('btn_') or 'button' in target.attr.lower():
                            buttons.add(target.attr)
                            
        # Find all connects
        for node in ast.walk(cls):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'connect':
                # The caller is usually something like self.btn_xyz.clicked
                val = node.func.value
                if isinstance(val, ast.Attribute) and val.attr in ['clicked', 'toggled', 'pressed', 'released']:
                    caller = val.value
                    if isinstance(caller, ast.Attribute) and isinstance(caller.value, ast.Name) and caller.value.id == 'self':
                        connects.add(caller.attr)
                        
        dead_buttons = buttons - connects
        if dead_buttons:
            print(f"File {fp}, Class {cls.name} has potentially dead buttons: {dead_buttons}")

