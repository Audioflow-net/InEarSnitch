import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Update cutouts()
old_cutouts = r'// 5\. DAS INTEGRIERTE LOGO \(Top Left\) - NEUES MEDAILLON DESIGN!.*?waves_block\(\);\n\s*\}'
new_cutouts = """// 5. DAS INTEGRIERTE LOGO (Top Left) - TIEFES MEDAILLON MIT TRÄGERPLATTE!
    // 4.0mm tiefe, exakte Ausstanzung für das Logo (Sichtbarer Bereich)
    translate([logo_x, logo_y, depth + flange_t - 4.0])
        linear_extrude(height=4.0 + 2*eps) {
            offset(r=0.2) custom_logo_2d();
            offset(r=0.2) waves_block();
        }
    // 0.6mm tiefe, ovale Aussparung GANZ UNTEN für die verbindende Trägerplatte.
    // Das TPU wird beim Drucken über diese winzige 0.6mm Lücke "bridgen". 
    // Es wird minimal durchhängen, fängt sich aber sofort am massiven Boden darunter auf!
    translate([logo_x, logo_y, depth + flange_t - 4.6])
        linear_extrude(height=0.6 + eps) {
            offset(r=0.2) logo_tower_2d();
        }"""
content = re.sub(old_cutouts, new_cutouts, content, flags=re.DOTALL)

# 2. Update logo_medallion()
old_medallion = r'module logo_medallion\(\) \{.*?\}'
new_medallion = """module logo_medallion() {
    color("darkturquoise")
    union() {
        // 0.4mm dicke ovale Bodenplatte (Druckt als allererstes, verbindet alle losen Teile!)
        linear_extrude(height=0.4)
            logo_tower_2d();
            
        // 4.0mm dicke Logo-Elemente darauf
        translate([0, 0, 0.4 - eps])
        linear_extrude(height=4.0 + eps) {
            custom_logo_2d();
            waves_block();
        }
    }
}"""
content = re.sub(old_medallion, new_medallion, content, flags=re.DOTALL)

# 3. Update test_print()
old_test = r'module test_print\(part="tpu"\) \{.*?\}'
new_test = """module test_print(part="tpu") {
    // Schneidet exakt die obersten 7mm der TPU-Ecke ab und legt sie flach aufs Bett
    translate([0, 0, -(23.62 + 1.5 - 7.0)]) {
        intersection() {
            tpu_insert_full();
            translate([-5.0, 60.0, 23.62 + 1.5 - 7.0])
                cube([45.0, 35.0, 7.0]);
        }
    }
}"""
content = re.sub(old_test, new_test, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
