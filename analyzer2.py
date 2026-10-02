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
            methods = set([m.name for m in node.body if isinstance(m, ast.FunctionDef)])
            # Also catch class variables
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            methods.add(target.id)
            classes[node] = methods

    for cls, methods in classes.items():
        for node in ast.walk(cls):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'connect':
                    arg = node.args[0] if node.args else None
                    if isinstance(arg, ast.Attribute):
                        if isinstance(arg.value, ast.Name) and arg.value.id == 'self':
                            method_name = arg.attr
                            if method_name not in methods:
                                print(f"File {filepath}: Class {cls.name} connects to missing self.{method_name} (Line {node.lineno})")

