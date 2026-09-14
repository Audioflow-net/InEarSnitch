with open("main.py", "r") as f:
    code = f.read()

old_load = """        saved_norm = s.value("audio/auto_normalize", type=bool)
        if saved_norm is None: saved_norm = True # Default True"""
new_load = """        saved_norm = s.value("audio/auto_normalize", True, type=bool)"""
code = code.replace(old_load, new_load)

with open("main.py", "w") as f:
    f.write(code)
print("Bool default patched.")
