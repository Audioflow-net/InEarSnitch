import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# Ändere das 7.5mm Schall-Loch im TPU-Boden auf 5.0mm (Passend zum Coupler-Loch)
old_hole = 'translate([0, 0, -1]) cylinder(d=7.5, h=6);'
new_hole = 'translate([0, 0, -1]) cylinder(d=5.0, h=6); // Exakt 5mm wie die Coupler-Grube'

content = content.replace(old_hole, new_hole)

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
