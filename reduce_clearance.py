import sys

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    code = f.read()

old_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Verschoben auf X=89 (Sichere Distanz zum Tower-Loch!)
    translate([89, 67.65, 20.12])
        rotate([0, 90, 0])
            cylinder(h=12, d=32.0, center=true);
            
    // Freischnitt für den hinteren Zug-Tab der Lasche (Y=80 bis 84)
    translate([89, 82.0, 30.0])
        cube([12, 6.0, 60], center=true);"""

new_gap = """    // 3. TPU STRAP GAP (Freiraum für die Print-In-Place Lasche)
    // Verschoben auf X=89 (Sichere Distanz zum Tower-Loch!)
    // Clearance präzise auf 0.8mm reduziert für Bambu Lab A1 Mini TPU
    translate([89, 67.65, 20.12])
        rotate([0, 90, 0])
            cylinder(h=11.6, d=30.8, center=true);
            
    // Freischnitt für den hinteren Zug-Tab der Lasche
    translate([89, 82.0, 30.0])
        cube([11.6, 6.0, 60], center=true);"""

if old_gap in code:
    code = code.replace(old_gap, new_gap)
else:
    print("WARNING: Could not find old_gap")

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(code)

print("SUCCESS")
