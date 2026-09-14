with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# Erhöhe den Abstand von 20 auf 40!
content = content.replace('translate([-20, 0, 0]) TPU_Donut("S");', 'translate([-40, 0, 0]) TPU_Donut("S");')
content = content.replace('translate([20, 0, 0]) TPU_Donut("L");', 'translate([40, 0, 0]) TPU_Donut("L");')

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
