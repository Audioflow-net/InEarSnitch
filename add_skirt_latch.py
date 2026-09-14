import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Remove notch & dimples, add Latch Groove
old_wanne = re.search(r'// Aussparung für die Airtight Pull-Tab Lasche.*?(?=\n\n        for \(c = \[0 : cols - 1\]\))', content, re.DOTALL).group(0)

new_wanne = """// Die Frontwand ist jetzt komplett MASIV (Luftdicht).
        
        // RUCKSACK-VERRIEGELUNG (Einrastmulde für den Skirt-Latch)
        // Eine saubere, 1mm tiefe Nut auf der Außenseite der Kiste.
        translate([box_w/2 - 16, -0.1, 25.0]) cube([32, 1.1, 2.0]);
        // Fase für leichteres Einschnappen
        hull() {
            translate([box_w/2 - 16, -0.1, 27.0]) cube([32, 1.1, 0.1]);
            translate([box_w/2 - 16, 1.0, 28.0]) cube([32, 0.1, 0.1]);
        }"""
content = content.replace(old_wanne, new_wanne)

# 2. Lid: Remove old Pull-Tab and old Bumps, add Skirt Latch
old_lid = re.search(r'// Airtight Overhang Pull-Tab.*?(?=\n    \}\n\}\n)', content, re.DOTALL).group(0)

new_lid = """// Die Scharnier-Pins (Standard Rund, d=2.8)
        translate([1.75, lid_d - 1.8 + 2.7, 1.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=1.9, center=true, $fn=16);
        translate([box_w - 1.75, lid_d - 1.8 + 2.7, 1.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=1.9, center=true, $fn=16);
            
        // RUCKSACK-VERRIEGELUNG (Der Skirt-Latch)
        // Ein 100% 3D-gedruckter flexibler Haken, der über die Frontwand greift.
        color("#A0A0A0") union() {
            // Massive Verbindung zum Deckel (Spaltüberbrückung)
            translate([box_w/2 - 15, -1.2, 0]) cube([30, 3.9, lid_h]);
            // Flexibler Hebelarm (1.2mm dick für perfekten PLA-Flex)
            translate([box_w/2 - 15, -1.2, -9.0]) cube([30, 1.2, 9.0]);
            // Einrast-Haken mit 45-Grad Support-freier Fase
            hull() {
                translate([box_w/2 - 15, -1.2, -9.0]) cube([30, 1.2, 1.0]);
                translate([box_w/2 - 15, 0, -7.5]) cube([30, 1.0, 0.1]);
            }
        }"""
content = content.replace(old_lid, new_lid)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
