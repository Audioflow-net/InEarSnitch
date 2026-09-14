import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Add the massive block to the main body union
old_body = "rounded_pocket(box_w, box_d, base_h, r=4);"
new_body = """union() {
            rounded_pocket(box_w, box_d, base_h, r=4);
            // Massiver Block (4.8mm dick) für den Eurobox-Verschluss an der Front!
            translate([box_w/2, 2.4, base_h/2]) cube([34, 4.8, base_h], center=true);
        }"""
content = content.replace(old_body, new_body)

# 2. Redesign the Latch Cuts in the Base Case
old_latch_cuts = re.search(r'// EUROBOX LATCH: Der Ausschnitt.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?center=true\);', content, re.DOTALL).group(0)
new_latch_cuts = """// EUROBOX LATCH: Der Ausschnitt in der massiven 4.8mm Frontwand
        // 1. Oberer Freiraum (Notch), tief genug (Y=4.0), damit Skirt und Daumen Platz haben
        translate([box_w/2, 2.0, 32.5]) cube([32.0, 4.0, 12.0], center=true);
        
        // 2. Die Halte-Kante (Catch Ledge). Wir schneiden nur Y=0 bis 1.7 weg. 
        // Es bleibt ein gewaltiger, 3.1mm dicker PLA-Balken als Kante stehen!
        translate([box_w/2, 0.85, 25.0]) cube([32.0, 1.7, 3.0], center=true);
        
        // 3. Unterer Freiraum für den Haken. Höhlt den Bereich unterm Balken aus.
        translate([box_w/2, 2.0, 20.0]) cube([32.0, 4.0, 7.0], center=true);"""
content = content.replace(old_latch_cuts, new_latch_cuts)

# 3. Fine-tune the Lid Hook to match the massive 1.7mm Ledge
old_skirt = re.search(r'// EUROBOX LATCH: Der flexible Scharnier-Schnapper.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\}', content, re.DOTALL).group(0)
new_skirt = """// EUROBOX LATCH: Der flexible Scharnier-Schnapper (Skirt)
        union() {
            // Die flexible Zunge (1.6mm dünn, 15.5mm lang), liegt bündig zur Außenwand (Y=0.8)
            translate([box_w/2, 0.8, -4.75]) cube([31.0, 1.6, 15.5], center=true);
            
            // Der Haken (massiv, geht bis Y=3.2 -> satter 1.5mm Interference-Klick unterm Balken!)
            translate([box_w/2, 2.0, -11.5]) cube([31.0, 2.4, 2.0], center=true);
            
            // Die Fingernagel-Rille (Griff-Lippe auf der Außenseite zum Hochziehen)
            translate([box_w/2, -0.3, -3.0]) cube([31.0, 0.6, 2.0], center=true);
        }"""
content = content.replace(old_skirt, new_skirt)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
