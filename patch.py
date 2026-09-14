with open("collet_chuck_v2.scad", "r") as f:
    content = f.read()

# Ändere den Standardwert auf "reihe"
content = content.replace('part = "querschnitt";', 'part = "reihe";')

with open("collet_chuck_v2.scad", "w") as f:
    f.write(content)
