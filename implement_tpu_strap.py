import sys

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    code = f.read()

# 1. Update variables at the top
code = code.replace("show_petg_elevator = true;", "show_petg_elevator = false; // DELETED")
code = code.replace("show_petg_elevator = false;", "show_petg_elevator = false; // DELETED")

# 2. Update cutouts() - replace the Elevator Shaft with the Strap Gap
old_shaft = """    // 3. PETG ELEVATOR SHAFT (Führungstunnel für den Fahrstuhl)
    // a) Die Einrast-Lippe (Verankerung: Z=0 bis Z=1)
    // Die Öffnung (25x32) ist 1mm KLEINER als die PETG-Bodenplatte (26x33).
    // Das PETG-Teil wird hier durchgepresst und rastet danach unlösbar ein!
    translate([92.5, 55.5, -eps])
        rounded_rect(25, 32, 1.0 + eps, 2.0);
        
    // b) Die Hub-Kammer (Reisebereich für die dicke Bodenplatte: Z=1 bis Z=12)
    // Hier hat die Platte (26x33) exakt 0.5mm Spiel rundum zum Gleiten.
    translate([92 - 0.5, 55 - 0.5, 1.0])
        rounded_rect(26 + 1.0, 33 + 1.0, 11.0, 3.0);
        
    // c) Der vertikale Schacht für die Mic-Wiege (Z=12 bis open)
    translate([95 - 0.5, 56 - 0.5, 12])
        rounded_rect(20 + 1.0, 23 + 1.0, z_center, 2.0);
        
    // d) Der Schacht für den HINTEREN vertikalen Griff (Y=82)
    translate([98 - 0.5, 82 - 0.5, 12])
        rounded_rect(14 + 1.0, 4 + 1.0, 50.0, 1.0);"""

new_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Wir schneiden einen Spalt (12mm breit) unter das Mikrofon (Y=67.65)
    // Radius der Trommel = 16.0 (Clearance zur Lasche = 1.4mm)
    translate([101, 67.65, 20.12])
        rotate([0, 90, 0])
            cylinder(h=12, d=32.0, center=true);
            
    // Freischnitt für den hinteren Zug-Tab der Lasche (Y=80 bis 84)
    translate([101, 82.0, 20.12])
        cube([12, 6.0, 30], center=true);"""

if old_shaft in code:
    code = code.replace(old_shaft, new_gap)
else:
    print("WARNING: Could not find old_shaft")

# 3. Add tpu_strap() module
strap_module = """
// ==========================================
// V32: PRINT-IN-PLACE TPU PULL STRAP
// ==========================================
module tpu_strap() {
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
        cube([10, 1.6, 15.0]); // Lasche, reicht bis Z=30
        translate([0, -2, 13]) cube([10, 3.6, 2.0]); // Griff-Knubbel
    }
}
"""

if "module tpu_strap()" not in code:
    code = code.replace("module tpu_insert_full() {", strap_module + "\nmodule tpu_insert_full() {")

# 4. Modify tpu_insert_full to include the strap
old_insert = """module tpu_insert_full() {
    difference() {
        // Original TPU logic
        difference() {
            peli_body();
            cutouts();
            tpu_chassis_cutout(); // Loch für das PETG Chassis
            tpu_weight_relief();  // Massive Gewölbe an der Unterseite
        }
        
        // RADIKAL-SCHNITT: Wir schneiden die untersten 2.0 mm komplett weg!"""

new_insert = """module tpu_insert_full() {
    difference() {
        union() {
            // Original TPU logic
            difference() {
                peli_body();
                cutouts();
                tpu_chassis_cutout(); // Loch für das PETG Chassis
                tpu_weight_relief();  // Massive Gewölbe an der Unterseite
            }
            // Add the Print-In-Place Strap inside the cut gap!
            tpu_strap();
        }
        
        // RADIKAL-SCHNITT: Wir schneiden die untersten 2.0 mm komplett weg!"""

if old_insert in code:
    code = code.replace(old_insert, new_insert)
else:
    print("WARNING: Could not find old_insert")
    
# 5. Remove petg_elevator rendering
if "if (show_petg_elevator) {" in code:
    code = code.replace("""    if (show_petg_elevator) {
        petg_elevator();
    }""", "")

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(code)

print("SUCCESS")
