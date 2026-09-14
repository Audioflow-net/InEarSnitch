import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Add Stapel-Rillen (Stacking Grooves) to the Lid
old_label = re.search(r'// Label auf der OBERSEITE.*?translate\(\[box_w/2 - 30, 15, lid_h - 0\.6\]\) cube\(\[60, 15, 0\.7\]\);', content, re.DOTALL).group(0)

new_label = """// STAPEL-RILLEN (Damit die Kisten im Rack ineinander klicken und Z-Höhe sparen!)
            translate([2.5, 2.5, lid_h - 1.0]) rounded_pocket(14, 120.6, 1.1, r=2);
            translate([box_w - 2.5, box_d - 2.5, lid_h - 1.0]) rotate([0, 0, 180]) rounded_pocket(14, 120.6, 1.1, r=2);
            
            // Label auf der OBERSEITE
            translate([box_w/2 - 30, 15, lid_h - 0.6]) cube([60, 15, 0.7]);"""

content = content.replace(old_label, new_label)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
