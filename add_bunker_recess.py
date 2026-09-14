import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Add recess to Base Case
old_bay = re.search(r'// CIEM / Bunker Bay \(Komplett tief!\).*?rounded_pocket\(iem_bay_w, iem_bay_d, base_h, r=6\);', content, re.DOTALL).group(0)

new_bay = """// CIEM / Bunker Bay (Komplett tief!)
            translate([bay_x, bay_y, floor_h]) rounded_pocket(iem_bay_w, iem_bay_d, base_h, r=6);
            
            // Der Bunker-Sitz (0.5mm Vertiefung, damit die Kassette satt einrastet)
            translate([bay_x + 0.9, bay_y + 0.9, floor_h - 0.5]) rounded_pocket(33.2, 68.2, 0.6, r=3.1);"""
content = content.replace(old_bay, new_bay)

# 2. Update Z-Height in Assembly
old_assembly = """        // 1. Tour Bunker (Links im Fach)
        translate([bay_x + 1, bay_y + 1, floor_h]) tour_bunker();
        
        // 2. Bunker Deckel (Sitzt flach im Shelf des Bunkers!)
        translate([bay_x + 1.5, bay_y + 1.5, floor_h + 17.0 - 1.5]) bunker_lid();"""

new_assembly = """        // 1. Tour Bunker (Links im Fach) - Sitzt jetzt 0.5mm tiefer in der Vertiefung!
        translate([bay_x + 1, bay_y + 1, floor_h - 0.5]) tour_bunker();
        
        // 2. Bunker Deckel (Sitzt flach im Shelf des Bunkers!)
        translate([bay_x + 1.5, bay_y + 1.5, floor_h - 0.5 + 17.0 - 1.5]) bunker_lid();"""
content = content.replace(old_assembly, new_assembly)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
