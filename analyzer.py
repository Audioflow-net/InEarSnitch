import ast
import os

files = ['main.py', 'analysis_ui.py', 'profile_ui.py', 'history_ui.py']

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    tree = ast.parse(content)
    
    print(f"--- Analysis for {filepath} ---")
    
    class_methods = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            class_methods[node.name] = methods
            
    # Find connects
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'connect':
                # Looking for self.method
                arg = node.args[0] if node.args else None
                if isinstance(arg, ast.Attribute):
                    if isinstance(arg.value, ast.Name) and arg.value.id == 'self':
                        method_name = arg.attr
                        # Try to find which class this belongs to by looking at the parent... 
                        # Actually it's easier: just print it, and later we check if any class is missing it.
                        print(f"Connect call found: self.{method_name} at line {node.lineno}")

    # Find loops in functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            has_loop = False
            for child in ast.walk(node):
                if isinstance(child, (ast.For, ast.While)):
                    has_loop = True
                    break
            if has_loop:
                print(f"Loop found in function: {node.name} at line {node.lineno}")

print("Done.")
