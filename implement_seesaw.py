with open('/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad', 'r') as f:
    text = f.read()

old_scoop = """    // 3.5 Finger Pick-up Slot (KONTROLLIERTER TRICHTER - V2)
    // Eine saubere, pillenförmige Mulde, die tief genug ist, aber IMMER
    // einen soliden 3.5mm TPU-Rand zur Außenwand stehen lässt!
    hull() {
        // Obere, breite Öffnung (Z=25)
        // Center Y=77, Radius=11 -> Max Y = 88.0 (TPU Wand ist bei 91.69 -> 3.69mm Rand bleibt!)
        translate([65.0, 77.0, 25.0]) sphere(d=22);
        translate([80.0, 77.0, 25.0]) sphere(d=22);
        
        // Tiefer Greif-Punkt (Z=8), schiebt sich schräg unter das Mikrofon
        translate([70.0, 74.0, 8.0]) sphere(d=10);
        translate([75.0, 74.0, 8.0]) sphere(d=10);
    }"""

new_scoop = """    // 3.5 Push-to-Eject Wippe (Seesaw Cavity)
    // Höhlt den Bereich unter dem schmalen Schaft (Stem) komplett bis zum Boden aus.
    // Drehpunkt (Fulcrum) des Hebels entsteht automatisch bei ca. X=73. 
    // Drückt man links auf den Schaft, ploppt der dicke Adapter rechts mechanisch aus dem TPU!
    hull() {
        translate([15.0, chan_y, -eps]) cylinder(h=14.0, d=16.0);
        translate([65.0, chan_y, -eps]) cylinder(h=14.0, d=16.0);
    }"""

text = text.replace(old_scoop, new_scoop)

# Auch den Header-Kommentar updaten für Klarheit
text = text.replace("// 3-HORIZONTAL-BAND LAYOUT (Max Cable, 6 Tips, No IEM Pocket)", "// Push-to-Eject Seesaw Mechanism for IEC711 Coupler\n// 3-HORIZONTAL-BAND LAYOUT (Max Cable, 6 Tips, No IEM Pocket)")

with open('/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad', 'w') as f:
    f.write(text)

print("Seesaw mechanism implemented!")
