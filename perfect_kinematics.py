import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Roof and L-Track
old_roof = re.search(r'// CONTINUOUS ROOF: Die "Struktur.*?\n.*?\n.*?cube\(\[box_w - 12\.0, 4\.0, 1\.0\]\);', content, re.DOTALL).group(0)
new_roof = """// CONTINUOUS ROOF: Die "Struktur drüber über die ganze Breite" (Z=36 bis 37)
        // Das Dach beginnt bei Y=119.0. Wenn der Deckel hinten ist (123.0), greift er 4mm unter das Dach.
        color("#D0D0D0") translate([6.0, 119.0, 36.0]) cube([box_w - 12.0, 4.2, 1.0]);"""
content = content.replace(old_roof, new_roof)

old_track = re.search(r'// L-TRACK FÜHRUNG.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?center=true\);', content, re.DOTALL).group(0)
new_track = """// L-TRACK FÜHRUNG (Horizontaler Slide & Vertikaler Drop)
        // Horizontale Spur: Y = 114.0 (Offen) bis 118.0 (Geschlossen)
        translate([3.5, 116.0, 35.5]) cube([5.0, 4.0, 3.2], center=true); 
        // Vertikaler Schacht: Bei Y = 114.0
        translate([3.5, 114.0, 29.5]) cube([5.0, 3.2, 12.0], center=true); 
        
        // Rechte Spur
        translate([box_w - 3.5, 116.0, 35.5]) cube([5.0, 4.0, 3.2], center=true);
        translate([box_w - 3.5, 114.0, 29.5]) cube([5.0, 3.2, 12.0], center=true);"""
content = content.replace(old_track, new_track)

# 2. Stage Lid: Flange and Pins
old_flange = re.search(r'// REAR FLANGE CUTOUT.*?\n.*?\n.*?\n.*?\n.*?cube\(\[tongue_w, 4\.0, 2\.0\]\);', content, re.DOTALL).group(0)
new_flange = """// REAR FLANGE CUTOUT (Macht den hinteren Rand nur 2mm dick, damit er unter das Roof passt!)
            // Der Absatz ist exakt 4mm tief (Y=116.3 bis 120.3 in lokalen Koordinaten)
            translate([6.2, 116.3, 2.0]) cube([tongue_w, 4.0, 2.0]);"""
content = content.replace(old_flange, new_flange)

old_pins = re.search(r'// STANDARD PINS \(Für L-Track Führung\).*?\n.*?\n.*?\n.*?\$fn=24\);', content, re.DOTALL).group(0)
new_pins = """// STANDARD PINS (Für L-Track Führung)
        // Die Pins sitzen VOR der Flansch im 3mm dicken Material (Lokales Y = 115.3)
        // Im geschlossenen Zustand landen sie global auf Y = 118.0 (Hinten im L-Track)
        translate([6.2, 115.3, 1.5]) rotate([0, -90, 0]) cylinder(d=3.0, h=3.0, $fn=24);
        translate([box_w - 6.2, 115.3, 1.5]) rotate([0, 90, 0]) cylinder(d=3.0, h=3.0, $fn=24);"""
content = content.replace(old_pins, new_pins)

# 3. Animation Block (Update Hinge Point)
old_anim = re.search(r'translate\(\[0, 121\.1, 1\.5\]\)\n\s*rotate\(\[-anim_angle, 0, 0\]\)\n\s*translate\(\[0, -121\.1, -1\.5\]\)', content, re.DOTALL).group(0)
new_anim = """// Hinge Point in der Animation auf Y=114.0 aktualisiert
        translate([0, 114.0, 1.5])
        rotate([-anim_angle, 0, 0])
        translate([0, -114.0, -1.5])"""
content = content.replace(old_anim, new_anim)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
