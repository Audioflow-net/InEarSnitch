import re

with open("collet_chuck_v3.scad", "r") as f:
    content = f.read()

# Ersetze die part-Definition
content = content.replace('part = "querschnitt"; // "querschnitt", "reihe", "komplett"', 
                          'part = "tpu_set"; // "tpu_set", "base", "nut", "washer", "querschnitt", "reihe"')

# Füge die Export-Blöcke unten hinzu
export_blocks = """
else if (part == "tpu_set") {
    // Alle 3 TPU Donuts auf einmal für den Slicer
    translate([-20, 0, 0]) TPU_Donut("S");
    translate([0, 0, 0]) TPU_Donut("M");
    translate([20, 0, 0]) TPU_Donut("L");
}
else if (part == "base") { Base(); }
else if (part == "nut") { Nut(0); }
else if (part == "washer") { Washer(); }
"""

content = content + export_blocks

with open("collet_chuck_v3.scad", "w") as f:
    f.write(content)
