import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Add the Lego Lock holes into the CIEM Bay loop
old_loop = re.search(r'// CIEM / Bunker Bay\n\s*translate\(\[bay_x, bay_y, floor_h\]\).*?r=6\);', content, re.DOTALL).group(0)
new_loop = """// CIEM / Bunker Bay (Komplette Wanne für das TPU-Inlay)
            translate([bay_x, bay_y, floor_h]) rounded_pocket(iem_bay_w, iem_bay_d, base_h, r=6);
            
            // LEGO-LOCK LÖCHER (Einsenkungen für die Silica Tour Bunker!)
            // Gehen 1.2mm tief in den Boden, lassen aber 0.8mm Außenwand stehen (wasserdicht)
            translate([bay_x + 16.5, bay_y + 16.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 16.5, bay_y + 51.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);"""
content = content.replace(old_loop, new_loop)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
