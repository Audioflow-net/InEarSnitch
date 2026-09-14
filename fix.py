import re

with open('/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad', 'r') as f:
    content = f.read()

# We need to find module peli_body() and replace it cleanly.
start_idx = content.find('module peli_body() {')
end_idx = content.find('// --- 3. Internal Cutouts Module ---')

new_peli_body = """module peli_body() {
    union() {
        // 1. MAIN BODY (Drafted shape inside the case)
        hull() {
            translate([base_dx, base_dx, 0])
                rounded_rect(base_x, base_y, eps, base_r);
            translate([0, 0, depth])
                rounded_rect(rim_x, rim_y, eps, fillet_r);
        }
        
        // 2. FLANSCH UND EINHAK-LIPPE (U-Channel über den Kistenrand)
        // Nach exaktem PDF-Querschnitt: Der Flansch geht flach nach außen und hat
        // an der äußersten Kante eine nach UNTEN zeigende Lippe, die über den Plastikrand greift.
        translate([-flange_w, -flange_w, depth]) {
            // Flacher Flansch (oben, 1.5mm dick)
            rounded_rect(rim_x + 2*flange_w, rim_y + 2*flange_w, flange_t, fillet_r + flange_w);
            
            // Nach unten zeigende Einhak-Lippe (am äußersten Rand)
            // lip_w = 1.0 (Dicke der Lippe), lip_drop = 2.5 (Wie weit sie nach unten greift)
            translate([0, 0, -2.5])
            difference() {
                rounded_rect(rim_x + 2*flange_w, rim_y + 2*flange_w, 2.5, fillet_r + flange_w);
                translate([1.0, 1.0, -eps])
                    rounded_rect(rim_x + 2*flange_w - 2.0, rim_y + 2*flange_w - 2.0, 2.5 + 2*eps, fillet_r + flange_w - 1.0);
            }
        }
    }
}

"""

if start_idx != -1 and end_idx != -1:
    with open('/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad', 'w') as f:
        f.write(content[:start_idx] + new_peli_body + content[end_idx:])
    print("Fixed peli_body!")
else:
    print("Could not find bounds!")
