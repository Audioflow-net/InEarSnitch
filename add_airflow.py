import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Add Vents to tour_bunker
old_bunker = re.search(r'module tour_bunker\(\) \{.*?(?=\nmodule bunker_lid\(\))', content, re.DOTALL).group(0)

new_bunker = """module tour_bunker() {
    color("#FF9800") difference() {
        // Hauptkörper
        rounded_pocket(33, 68, 17.0, r=3);
        
        // Tiefer Hohlraum für Silica
        translate([1.5, 1.5, 1.5]) rounded_pocket(30, 65, 16, r=2);
        
        // Deckel-Shelf
        translate([0.4, 0.4, 17.0 - 1.6]) rounded_pocket(32.2, 67.2, 2.0, r=2.5);
        
        // QUERSTROM-BELÜFTUNG (Side-Flow Air Vents)
        // Vertikale Schlitze in der rechten Wand. Nur 1.5mm breit, damit keine Perlen rausfallen!
        for (y = [10 : 4 : 58]) {
            translate([31, y, 3]) cube([5, 1.5, 10]);
        }
    }
}
"""
content = content.replace(old_bunker, new_bunker)


# 2. Add Windows to TPU Tray
old_tpu = re.search(r'// Kabel-Durchführungen.*?translate\(\[30, 50, 17\]\) cube\(\[10, 6, 15\]\);', content, re.DOTALL).group(0)

new_tpu = """// Kabel-Durchführungen (Oben)
            translate([30, 16, 17]) cube([10, 6, 15]);
            translate([30, 50, 17]) cube([10, 6, 15]);
            
            // QUERSTROM-FENSTER (Unten)
            // Massive Durchbrüche zur rechten Bunker-Wand für maximalen Luftaustausch!
            translate([33, 6, 3]) cube([5, 24, 10]);
            translate([33, 40, 3]) cube([5, 24, 10]);"""
content = content.replace(old_tpu, new_tpu)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
