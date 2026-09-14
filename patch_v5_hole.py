import os

files = ["collet_chuck_v5_godzilla.scad", "PRINT_ME_V5_PLA.scad", "PRINT_ME_V5_TPU.scad"]

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
        
        # Washer Loch von 34 auf 38mm vergrößern
        content = content.replace('translate([0, 0, -1]) cylinder(d=34, h=3); // 34mm Loch!!', 'translate([0, 0, -1]) cylinder(d=38, h=3); // 38mm MAXIMALES Loch!!')
        
        # Nut Loch von 34 auf 38mm vergrößern
        content = content.replace('translate([0, 0, 12.5]) cylinder(d=34, h=5);', 'translate([0, 0, 12.5]) cylinder(d=38, h=5);')
        
        with open(filename, "w") as f:
            f.write(content)
