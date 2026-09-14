import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# Füge "pla_set" zu den Kommentaren hinzu
content = content.replace('part = "tpu_set"; // "tpu_set", "base", "nut", "washer", "querschnitt", "reihe"', 
                          'part = "pla_set"; // "pla_set", "tpu_set", "base", "nut", "washer", "querschnitt"')

# Füge den Block unten hinzu
old_export = 'else if (part == "base") { Base(); }'
new_export = """else if (part == "pla_set") {
    // Alle 3 PLA Teile auf einmal!
    translate([-25, 0, 0]) Base();
    translate([0, -30, 0]) Washer();
    translate([25, 0, 0]) Nut(0);
}
else if (part == "base") { Base(); }"""

content = content.replace(old_export, new_export)

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
