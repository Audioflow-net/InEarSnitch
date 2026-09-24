import re

with open('/Users/ben/Desktop/InEarSnitch/CIEM_XL_Adapter_Molds.scad', 'r') as f:
    content = f.read()

new_code = """// ==========================================
// CIEM XL ADAPTER MOLDS - "STRAIGHT STRETCH TUBE"
// ==========================================
// Fokus: Ein absolut gerades, dünnwandiges Rohr, das extrem leicht zu gießen ist.
// Mechanik: Das Rohr hat durchgehend 13.0 mm Außendurchmesser (passt durch die Mutter).
//
// GANZ WICHTIG: Die Tiefe dieser Form ist jetzt EXAKT auf die Tiefe deiner V27-Tamper
// synchronisiert! Du musst für diese Form gar keinen neuen Tamper drucken, 
// sondern steckst einfach deinen bereits gedruckten V27-7 (oder V27-6 / V27-5) hinein!
// ==========================================

$fn = 100;
use <MASTER_Silikon_Formen.scad>;

// Die Variable aus dem MASTER importieren wir quasi mental: 
// (OpenSCAD übernimmt sie beim Rendern nicht direkt als globale, also definieren wir sie hier kurz gleich)
extra_v27_length = 3.0; 

// --- PARAMETER ---
tube_outer = 13.0; // Passt exakt in die IEC711 Mutter
ring_outer = 15.0; // Kleiner Anti-Tear Wulst ganz oben

module outer_cavity_straight() {
    // Z-Tiefe exakt mit dem V27 Tamper synchronisieren!
    z_tip = 9.6 - (7.61 + extra_v27_length) - 2.0; 
    
    // 1. Ankerloch bis zum Boden
    translate([0,0,-8.1]) cylinder(d=4.0, h=8.1 + z_tip, $fn=64);
    
    // 2. Der Anti-Tear Wulstring am tiefsten Punkt
    translate([0,0, z_tip + 1.5]) rotate_extrude($fn=64) translate([(ring_outer - 3.0)/2, 0, 0]) circle(d=3.0, $fn=32);
    translate([0,0, z_tip]) cylinder(d=ring_outer, h=3.0, $fn=64); 

    // 3. Das absolut gerade 13.0 mm Rohr (Z-Höhe exakt ausgerechnet)
    translate([0,0, z_tip + 3.0]) cylinder(d=tube_outer, h=9.6 - (z_tip + 3.0), $fn=64);
    
    // 4. IEC711 Flansch OBEN (Z=9.6 bis 14.11)
    translate([0,0,9.6]) cylinder(d=20.0, h=4.51, $fn=64);
}

// ==========================================
// RENDER MODULE
// ==========================================
module mold_half_left_ciem() {
    difference() {
        intersection() { mold_block(); translate([-17, -17, -10]) cube([17, 34, 40]); }
        outer_cavity_straight();
        translate([16.5, 0, 0]) rotate([90, 0, 90]) linear_extrude(2) text("TUBE", size=5, halign="center", valign="center", font="Arial:style=Bold");
        translate([-16.5, 0, 0]) rotate([90, 0, -90]) linear_extrude(2) text("TUBE", size=5, halign="center", valign="center", font="Arial:style=Bold");
        translate([0, 14, 6]) rotate([0, 90, 0]) cylinder(d=3.2, h=8, center=true, $fn=32);
        translate([0, -14, 6]) rotate([0, 90, 0]) cylinder(d=3.2, h=8, center=true, $fn=32);
    }
}

module mold_half_right_ciem() {
    union() {
        difference() {
            intersection() { mold_block(); translate([0, -17, -10]) cube([17, 34, 40]); }
            outer_cavity_straight();
            translate([16.5, 0, 0]) rotate([90, 0, 90]) linear_extrude(2) text("TUBE", size=5, halign="center", valign="center", font="Arial:style=Bold");
            translate([-16.5, 0, 0]) rotate([90, 0, -90]) linear_extrude(2) text("TUBE", size=5, halign="center", valign="center", font="Arial:style=Bold");
        }
        translate([0, 14, 6]) rotate([0, 90, 0]) cylinder(d1=1.5, d2=4.1, h=4, center=true, $fn=32);
        translate([0, -14, 6]) rotate([0, 90, 0]) cylinder(d1=1.5, d2=4.1, h=4, center=true, $fn=32);
    }
}

// --- LAYOUT ---
translate([-18, 0, 0]) color("DarkSlateGray") mold_half_left_ciem();
translate([ 18, 0, 0]) color("LightGray") mold_half_right_ciem();

// Du musst keinen neuen Tamper drucken! 
// Hier wird zur Visualisierung einfach dein V27 Tamper reingeschoben:
translate([  0, -35, 0]) color("Gold") piston_v27(hole_size=7.0, label="V27-7");
"""

with open('/Users/ben/Desktop/InEarSnitch/CIEM_XL_Adapter_Molds.scad', 'w') as f:
    f.write(new_code)

print("CIEM Synced with V27")
