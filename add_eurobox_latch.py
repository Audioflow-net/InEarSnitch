import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Remove old Pull-Tab cutout, add Eurobox Catch and Notch
old_base_cutout = re.search(r'// Airtight Pull-Tab Cutout.*?translate\(\[box_w/2 - 16, -0\.1, 34\.0\]\) cube\(\[32, 2\.6, 3\.1\]\);', content, re.DOTALL).group(0)

new_base_cutout = """// EUROBOX LATCH: Der Ausschnitt in der Frontwand für den flachen Klipp
        // 1. Der Freiraum, damit der Klipp nach innen federn kann (Notch)
        translate([box_w/2, 1.5, 32.5]) cube([32.0, 3.0, 12.0], center=true);
        // 2. Die Halte-Kante (Catch Ledge), unter der der Haken einrastet
        translate([box_w/2, 1.2, 25.0]) cube([32.0, 2.4, 3.0], center=true);
        // 3. Freiraum unter der Kante für den Haken
        translate([box_w/2, 1.5, 23.5]) cube([32.0, 3.0, 4.0], center=true);"""
content = content.replace(old_base_cutout, new_base_cutout)

# 2. Lid: Remove old Pull-Tab, add Eurobox Skirt
old_lid_tab = re.search(r'// Airtight Overhang Pull-Tab.*?translate\(\[box_w/2, -0\.1, lid_h/2\]\) rounded_pocket\(30, 4, lid_h, r=1\.5\);', content, re.DOTALL).group(0)

new_lid_tab = """// EUROBOX LATCH: Der flexible Scharnier-Schnapper (Skirt)
        union() {
            // Die flexible Zunge (1.6mm dünn, 15.5mm lang), liegt bündig zur Außenwand
            translate([box_w/2, 0.8, -4.75]) cube([31.0, 1.6, 15.5], center=true);
            
            // Der Haken (zeigt nach innen), rastet exakt unter Z=23.5 (Base) ein
            translate([box_w/2, 1.7, -11.5]) cube([31.0, 1.8, 2.0], center=true);
            
            // Die Fingernagel-Rille (Griff-Lippe auf der Außenseite zum Hochziehen)
            translate([box_w/2, -0.3, -3.0]) cube([31.0, 0.6, 2.0], center=true);
        }"""
content = content.replace(old_lid_tab, new_lid_tab)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
