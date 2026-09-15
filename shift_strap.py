import sys

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    code = f.read()

# 1. Update TPU STRAP GAP
old_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Wir schneiden einen Spalt (12mm breit) unter das Mikrofon (Y=67.65)
    // Radius der Trommel = 16.0 (Clearance zur Lasche = 1.4mm)
    translate([101, 67.65, 20.12])
        rotate([0, 90, 0])
            cylinder(h=12, d=32.0, center=true);
            
    // Freischnitt für den hinteren Zug-Tab der Lasche (Y=80 bis 84)
    // Extra hoch (50mm), damit die längere Lasche nirgends festbackt!
    translate([101, 82.0, 30.0])
        cube([12, 6.0, 60], center=true);"""

new_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Verschoben auf X=89 (Sichere Distanz zum Tower-Loch!)
    translate([89, 67.65, 20.12])
        rotate([0, 90, 0])
            cylinder(h=12, d=32.0, center=true);
            
    // Freischnitt für den hinteren Zug-Tab der Lasche (Y=80 bis 84)
    translate([89, 82.0, 30.0])
        cube([12, 6.0, 60], center=true);"""

if old_gap in code:
    code = code.replace(old_gap, new_gap)
else:
    print("WARNING: Could not find old_gap")

# 2. Update tpu_strap()
old_strap = """module tpu_strap() {
    // 1. Ein Viertelkreis-Gurt vom Boden bis zur Rückwand
    difference() {
        translate([101, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=10, d=29.2, center=true); // r_außen = 14.6
        translate([101, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=12, d=26.0, center=true); // r_innen = 13.0
            
        // Obere Hälfte abschneiden (Z > 20.12)
        translate([101, 67.65, 20.12 + 10]) 
            cube([12, 40, 20], center=true);
            
        // Vordere Hälfte abschneiden (Y < 67.65)
        translate([101, 67.65 - 15, 20.12])
            cube([12, 30, 40], center=true);
    }
    
    // 2. Unterer Anker (Y = 67.65)
    // Verbindet den tiefsten Punkt des Gurts fest mit dem TPU-Boden (Z=2)
    translate([96, 66.65, 2.0])
        cube([10, 2.0, 6.0]); // Fester Pfeiler ins Fundament
        
    // 3. Hinterer Zug-Tab (Y = 67.65 + 13.0 = 80.65)
    translate([96, 80.65, 15.0]) {
        cube([10, 1.6, 25.0]); // Lasche, deutlich verlängert bis Z=40
        translate([0, -2, 23]) cube([10, 3.6, 2.0]); // Griff-Knubbel (wandert mit nach oben)
    }
}"""

new_strap = """module tpu_strap() {
    // 1. Ein Viertelkreis-Gurt vom Boden bis zur Rückwand
    difference() {
        translate([89, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=10, d=29.2, center=true); // r_außen = 14.6
        translate([89, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=12, d=26.0, center=true); // r_innen = 13.0
            
        // Obere Hälfte abschneiden (Z > 20.12)
        translate([89, 67.65, 20.12 + 10]) 
            cube([12, 40, 20], center=true);
            
        // Vordere Hälfte abschneiden (Y < 67.65)
        translate([89, 67.65 - 15, 20.12])
            cube([12, 30, 40], center=true);
    }
    
    // 2. Unterer Anker (Y = 67.65)
    // Verbindet den tiefsten Punkt des Gurts fest mit dem TPU-Boden (Z=2)
    translate([84, 66.65, 2.0])
        cube([10, 2.0, 6.0]); // Fester Pfeiler ins Fundament
        
    // 3. Hinterer Zug-Tab (Y = 67.65 + 13.0 = 80.65)
    translate([84, 80.65, 15.0]) {
        cube([10, 1.6, 25.0]); // Lasche, deutlich verlängert bis Z=40
        translate([0, -2, 23]) cube([10, 3.6, 2.0]); // Griff-Knubbel (wandert mit nach oben)
    }
}"""

if old_strap in code:
    code = code.replace(old_strap, new_strap)
else:
    print("WARNING: Could not find old_strap")

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(code)

print("SUCCESS")
