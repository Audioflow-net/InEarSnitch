import sys

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    code = f.read()

# 1. Update Gap
old_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Wieder im perfekten Schwerpunkt zentriert (X=92)!
    // Clearance präzise auf 0.8mm reduziert für Bambu Lab A1 Mini TPU
    difference() {
        translate([92, 67.65, 20.12]) 
            rotate([0, 90, 0]) 
                cylinder(h=11.6, d=30.8, center=true);
                
        // MASSIVER SCHUTZ ZUM TOWER: Wir löschen den Freiraum in der vorderen Hälfte!
        // Alles was Y < 64 ist, bleibt zu 100% massives TPU. 
        // Der Tower endet bei Y=53.65. Wir haben also >10mm Gummi-Wand zwischen Lasche und Tower!
        translate([92, 32.0, 20.0]) 
            cube([20, 64.0, 50.0], center=true); // Schneidet das Gap von Y=0 bis Y=64 weg
            
        // Obere Hälfte abschneiden (Schutz der Kanten)
        // eps Hinzugefügt um Coplanar Face mit dem Zylinder-Ursprung zu verhindern
        translate([92, 67.0, 45.12 - eps]) 
            cube([20, 50.0, 50.0], center=true); // Z=20.12 bis Z=70.12
    }
            
    // Freischnitt für den hinteren Zug-Tab der Lasche
    translate([92, 82.0, 30.0])
        cube([11.6, 6.0, 60], center=true);"""

new_gap = """    // 3. TPU STRAP GAP (Längs-Hängematte / Longitudinal Hammock)
    // Wir ersetzen den kurzen Gurt durch eine massive Hängematte unter dem Mikrofon!
    
    // A) Langer, flacher Schacht unter dem Mikrofon (X=68 bis X=98)
    translate([68, 62.15, 2.0])
        cube([30, 11.0, 10.0]); // Bietet Platz für den langen Hebel-Gurt
        
    // B) Freiraum für die hintere Kurve (wie vorher, aber optimiert)
    difference() {
        translate([92, 67.65, 20.12]) 
            rotate([0, 90, 0]) 
                cylinder(h=11.6, d=30.8, center=true);
                
        // MASSIVER SCHUTZ ZUM TOWER (Y < 64 bleibt unangetastet!)
        translate([92, 32.0, 20.0]) 
            cube([20, 64.0, 50.0], center=true); 
            
        // Obere Hälfte abschneiden (Z > 20.12)
        translate([92, 67.0, 45.12 - eps]) 
            cube([20, 50.0, 50.0], center=true);
    }
            
    // C) Freischnitt für den hinteren vertikalen Zug-Tab
    translate([92, 82.0, 30.0])
        cube([11.6, 6.0, 60], center=true);"""

if old_gap in code:
    code = code.replace(old_gap, new_gap)
else:
    print("WARNING: Could not find old_gap")

# 2. Update Strap
old_strap = """module tpu_strap() {
    // 1. Ein Viertelkreis-Gurt vom Boden bis zur Rückwand
    // Wieder perfekt im Schwerpunkt (X=92) zentriert.
    difference() {
        translate([92, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=10, d=29.2, center=true); // r_außen = 14.6
        translate([92, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=12, d=26.0, center=true); // r_innen = 13.0
            
        // Obere Hälfte abschneiden (Z > 20.12)
        translate([92, 67.65, 20.12 + 10 - eps]) 
            cube([12, 40, 20], center=true);
            
        // Vordere Hälfte abschneiden (Y < 67.65)
        translate([92, 67.65 - 15 - eps, 20.12])
            cube([12, 30, 40], center=true);
    }
    
    // 2. Unterer Anker (Y = 67.65)
    // Verbindet den tiefsten Punkt des Gurts fest mit dem TPU-Boden (Z=2)
    // Geht extra tief bis Z=1, damit der Radikal-Schnitt bei Z=2 keine Coplanar Face Warning erzeugt!
    translate([87, 65.65, 1.0])
        cube([10, 2.0, 7.0]); // Fester Pfeiler ins Fundament
        
    // 3. Hinterer Zug-Tab (Y = 67.65 + 13.0 = 80.65)
    translate([87, 80.65, 15.0]) {
        cube([10, 2.4, 25.0]); // Lasche auf 2.4mm verdickt (6 Perimeters), gegen "Wet Noodle" Effekt beim Druck!
        translate([0, -2, 23]) cube([10, 4.4, 2.0]); // Griff-Knubbel (wandert mit nach oben)
    }
}"""

new_strap = """module tpu_strap() {
    // === LONGITUDINAL HAMMOCK STRAP ===
    // Verlängert den Gurt massiv nach links (X-Achse), um einen riesigen Hubweg zu erzeugen!
    
    // 1. Der neue Anker bei X=70 (weit weg unterm Schaft)
    translate([69, 62.65, 1.0])
        cube([4, 10, 7.0]); // Massiv im Boden verankert
        
    // 2. Das flache Zugband (X=73 bis X=87)
    // Es liegt schwebend im Schacht (Z=3.12 bis 5.52)
    translate([73, 62.65, 3.12])
        cube([14, 10, 2.4]); // 2.4mm starkes, ultra-flexibles Band
        
    // 3. Die 90-Grad Kurve hinten am Schwerpunkt (X=92)
    difference() {
        translate([92, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=10, d=29.2, center=true); // r_außen = 14.6
        translate([92, 67.65, 20.12]) rotate([0, 90, 0]) 
            cylinder(h=12, d=24.4, center=true); // r_innen = 12.2 (damit Dicke exakt 2.4mm ist!)
            
        // Obere Hälfte abschneiden (Z > 20.12)
        translate([92, 67.65, 20.12 + 10 - eps]) 
            cube([12, 40, 20], center=true);
            
        // Vordere Hälfte abschneiden (Y < 67.65)
        translate([92, 67.65 - 15 - eps, 20.12])
            cube([12, 30, 40], center=true);
    }
    
    // 4. Hinterer vertikaler Zug-Tab (Y = 80.65)
    translate([87, 80.65, 15.0]) {
        cube([10, 2.4, 25.0]); // 2.4mm dick gegen Wet-Noodle
        translate([0, -2, 23]) cube([10, 4.4, 2.0]); // Griff-Knubbel
    }
}"""

if old_strap in code:
    code = code.replace(old_strap, new_strap)
else:
    print("WARNING: Could not find old_strap")

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(code)

print("SUCCESS")
