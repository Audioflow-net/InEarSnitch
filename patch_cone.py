import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# 1. Mache den Trichter in der blauen Basis unten breiter (d1=15)
content = content.replace('cylinder(d1=10, d2=24, h=5.1);', 'cylinder(d1=15, d2=26, h=5.1); // Breiterer Trichter unten')

# 2. Passe die TPU Donuts an (d1=15), damit sie nicht abgeschnitten werden!
content = content.replace('cylinder(d1=11, d2=22.5, h=4); // Konisch', 'cylinder(d1=15, d2=23.8, h=4); // Breiterer Fuß, damit die Lippe nicht abreißt')

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
