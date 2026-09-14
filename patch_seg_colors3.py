with open("main.py", "r") as f:
    code = f.read()

code = code.replace("f\\'\\'\\'", "f'''")
code = code.replace("\\'\\'\\')", "''')")

with open("main.py", "w") as f:
    f.write(code)

print("Syntax error fixed.")
