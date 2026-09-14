import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Replace the massive Recess with a 2x2 Lego Hole Grid
old_bay = re.search(r'// CIEM / Bunker Bay \(Komplett tief!\).*?rounded_pocket\(33\.2, 68\.2, 0\.6, r=3\.1\);', content, re.DOTALL).group(0)

new_bay = """// CIEM / Bunker Bay (Komplett tief!)
            translate([bay_x, bay_y, floor_h]) rounded_pocket(iem_bay_w, iem_bay_d, base_h, r=6);
            
            // 4-WAY LEGO-LOCK (Vertiefungen für beliebige Rotation)
            translate([bay_x + 17.5, bay_y + 17.5, floor_h - 1.0]) cylinder(d=6.0, h=1.1, $fn=24);
            translate([bay_x + 17.5, bay_y + 52.5, floor_h - 1.0]) cylinder(d=6.0, h=1.1, $fn=24);
            translate([bay_x + 52.5, bay_y + 17.5, floor_h - 1.0]) cylinder(d=6.0, h=1.1, $fn=24);
            translate([bay_x + 52.5, bay_y + 52.5, floor_h - 1.0]) cylinder(d=6.0, h=1.1, $fn=24);"""
content = content.replace(old_bay, new_bay)

# 2. Assembly: Revert Bunker Z-height back to floor_h
old_assembly = """        // 1. Tour Bunker (Links im Fach) - Sitzt jetzt 0.5mm tiefer in der Vertiefung!
        translate([bay_x + 1, bay_y + 1, floor_h - 0.5]) tour_bunker();
        
        // 2. Bunker Deckel (Sitzt flach im Shelf des Bunkers!)
        translate([bay_x + 1.5, bay_y + 1.5, floor_h - 0.5 + 17.0 - 1.5]) bunker_lid();"""

new_assembly = """        // 1. Tour Bunker (Sitzt bündig auf dem Boden und klickt in die Lego-Löcher!)
        translate([bay_x + 1, bay_y + 1, floor_h]) tour_bunker();
        
        // 2. Bunker Deckel
        translate([bay_x + 1.5, bay_y + 1.5, floor_h + 17.0 - 1.5]) bunker_lid();"""
content = content.replace(old_assembly, new_assembly)

# 3. Bunker: Add the Lego Pegs to the bottom
old_bunker = re.search(r'// QUERSTROM-BELÜFTUNG \(Side-Flow Air Vents\).*?for \(y = \[42 : 4 : 62\]\) translate\(\[31, y, 3\]\) cube\(\[5, 1\.5, 10\]\);', content, re.DOTALL).group(0)

new_bunker = """// QUERSTROM-BELÜFTUNG (Side-Flow Air Vents)
        for (y = [10 : 4 : 30]) translate([31, y, 3]) cube([5, 1.5, 10]);
        for (y = [42 : 4 : 62]) translate([31, y, 3]) cube([5, 1.5, 10]);
    }
    
    // LEGO-LOCK PEGS (Die Nupsies, die im Boden einrasten!)
    color("#FF9800") {
        translate([16.5, 16.5, -1.0]) cylinder(d=5.7, h=1.0, $fn=24);
        translate([16.5, 51.5, -1.0]) cylinder(d=5.7, h=1.0, $fn=24);"""
content = content.replace(old_bunker, new_bunker)


with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
