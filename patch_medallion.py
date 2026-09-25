import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

# 1. Add variables for logo position at the top
if 'logo_x =' not in content:
    content = content.replace('// --- 1. Design Parameters ---', '// --- 1. Design Parameters ---\nlogo_x = 12.0;\nlogo_y = 84.0;\n')

# 2. Update cutouts() - replace the whole section 5
old_cutouts_logo = r'// 5\. DAS INTEGRIERTE LOGO \(Top Left\).*?// C\) Der Ausschnitt im TPU für den massiven Wellen-Block!.*?waves_block\(\);\n'
new_cutouts_logo = """// 5. DAS INTEGRIERTE LOGO (Top Left) - NEUES MEDAILLON DESIGN!
    // Nur noch 2.0mm tief in die Oberfläche gestanzt. Kein Durchbruch mehr!
    translate([logo_x, logo_y, depth + flange_t - 2.0])
        linear_extrude(height=2.0 + 2*eps) {
            offset(r=0.2) custom_logo_2d();
            offset(r=0.2) waves_block();
        }\n"""
content = re.sub(old_cutouts_logo, new_cutouts_logo, content, flags=re.DOTALL)

# 3. Restore the peg in petg_support_blocks
old_peg = r'// Ecke Oben Links \(Neben dem Mikrofon-Schacht\)\s*// GELÖSCHT: Der neue Logo-Turm bei X=15\.65 übernimmt jetzt exakt diese Funktion \s*// und dient als massiver Anker-Stift für die obere linke Ecke!'
new_peg = """// Ecke Oben Links (Neben dem Mikrofon-Schacht)
            // WIEDER DA: Da das Logo jetzt nur noch ein flaches Medaillon ist, brauchen wir den Anker-Stift wieder!
            translate([11.0, 77.0, 0]) petg_alignment_peg(15.0, 6.0, tol);"""
content = re.sub(old_peg, new_peg, content)

# 4. Remove the tower and logo from petg_chassis, and add logo_medallion module
old_chassis_logo = r'// 3\. DIE LOGO-STELZEN & TURM \(Top Left Corner\).*?// C\) NEU: Der massive Block unter den Wellen.*?waves_block\(\);'
new_chassis_logo = """// 3. LOGO-TURM WURDE ENTFERNT (Jetzt separates Medaillon)"""
content = re.sub(old_chassis_logo, new_chassis_logo, content, flags=re.DOTALL)

# 5. Add the logo_medallion module and toggle
if 'module logo_medallion()' not in content:
    content += """
// ==========================================
// SEPARATES LOGO-MEDAILLON (2mm Flat Print)
// ==========================================
module logo_medallion() {
    color("darkturquoise")
    linear_extrude(height=2.0) {
        custom_logo_2d();
        waves_block();
    }
}
"""

# 6. Update rendering logic at bottom
old_render = r'if \(show_test_print\) \{.*?\} else if'
new_render = """if (show_test_print) {
    color("Gold", 1.0) test_print();
} else if"""
content = re.sub(old_render, new_render, content, flags=re.DOTALL)

# 7. Update test_print module
old_test = r'module test_print\(part="tpu"\) \{.*?\}'
new_test = """module test_print(part="tpu") {
    // Schneidet exakt die obersten 6mm der TPU-Ecke ab und legt sie flach aufs Bett
    translate([0, 0, -(23.62 + 1.5 - 6.0)]) {
        intersection() {
            tpu_insert_full();
            translate([-5.0, 60.0, 23.62 + 1.5 - 6.0])
                cube([45.0, 35.0, 6.0]);
        }
    }
}"""
content = re.sub(old_test, new_test, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
