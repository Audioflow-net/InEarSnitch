import sys

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    code = f.read()

# 1. Update TPU Cutouts for the Anchor (Verankerung)
old_shaft = """    // 3. PETG ELEVATOR SHAFT (Führungstunnel für den Fahrstuhl)
    // a) Die Hub-Kammer (Reisebereich für die dicke Bodenplatte: Z=0 bis Z=12)
    translate([92 - 0.5, 55 - 0.5, -eps])
        rounded_rect(26 + 1.0, 33 + 1.0, 12.0 + eps, 3.0); // X: 92..118, Y: 55..88
        
    // b) Der vertikale Schacht für die Mic-Wiege (Z=12 bis open)
    translate([95 - 0.5, 56 - 0.5, 12])
        rounded_rect(20 + 1.0, 23 + 1.0, z_center, 2.0); // X: 95..115, Y: 56..79
        
    // c) Der Schacht für den HINTEREN vertikalen Griff (Y=82)
    translate([98 - 0.5, 82 - 0.5, 12])
        rounded_rect(14 + 1.0, 4 + 1.0, 50.0, 1.0);"""

new_shaft = """    // 3. PETG ELEVATOR SHAFT (Führungstunnel für den Fahrstuhl)
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

if old_shaft in code:
    code = code.replace(old_shaft, new_shaft)
else:
    print("WARNING: Could not find old_shaft")

# 2. Add Springs to petg_elevator()
old_elevator = """        // 3. Der HINTERE Zug-Griff (Pull-Tab)
        // Platziert hinter dem Mikrofon (Y=82), fernab von Tip und Tower!
        translate([98, 82, 2]) {
            // Vertikaler Schaft (Breite 14mm, Tiefe 4mm)
            rounded_rect(14, 4, 28.0, 1.0);
            
            // T-Bar (Dicker Zylinder oben, der quer liegt!)
            // Querachse ist X, also rotieren wir um Y
            translate([0, 2, 28])
                rotate([0, 90, 0])
                    cylinder(h=14, d=9.0, $fn=30);
        }
    }
}"""

new_elevator = """        // 3. Der HINTERE Zug-Griff (Pull-Tab)
        // Platziert hinter dem Mikrofon (Y=82), fernab von Tip und Tower!
        translate([98, 82, 2]) {
            // Vertikaler Schaft (Breite 14mm, Tiefe 4mm)
            rounded_rect(14, 4, 28.0, 1.0);
            
            // T-Bar (Dicker Zylinder oben, der quer liegt!)
            translate([0, 2, 28])
                rotate([0, 90, 0])
                    cylinder(h=14, d=9.0, $fn=30);
        }
        
        // 4. Auto-Return Blattfedern (Print-In-Place PETG Springs)
        // Drücken permanent gegen die TPU-Decke bei Z=12. 
        // Lässt man den Griff los, federt der Fahrstuhl sanft nach unten.
        for (y_pos = [57, 75]) {
            translate([94, y_pos, 2]) {
                // Feder ragt im 30-Grad Winkel von der Basis bis Z=11.5 hoch
                hull() {
                    cube([2, 5, eps]);
                    translate([10, 0, 9.5]) cube([2, 5, eps]);
                }
            }
        }
    }
}"""

if old_elevator in code:
    code = code.replace(old_elevator, new_elevator)
else:
    print("WARNING: Could not find old_elevator")

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(code)

print("SUCCESS")
