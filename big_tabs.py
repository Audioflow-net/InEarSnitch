import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

old_nase = re.search(r'module halte_nase\(\) \{.*?\n\}', content, re.DOTALL).group(0)

new_nase = """module halte_nase() {
    // Massive, breite Halte-Lippe (Trapez-Form)
    hull() {
        // Basis an der Wand (breit für Stabilität)
        translate([0, -5, 0]) sphere(d=1.6, $fn=16);
        translate([0, 5, 0]) sphere(d=1.6, $fn=16);
        // Spitze (ragt 5mm über das Kabel!)
        translate([5, -2, 0]) sphere(d=1.6, $fn=16);
        translate([5, 2, 0]) sphere(d=1.6, $fn=16);
    }
}"""

content = content.replace(old_nase, new_nase)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
