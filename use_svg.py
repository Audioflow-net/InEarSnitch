with open("main.py", "r") as f:
    content = f.read()

content = content.replace('"Final Logo InEar Snitch_Transparent.png"', '"Final_Logo_Spy_Cleaned.svg"')

with open("main.py", "w") as f:
    f.write(content)
