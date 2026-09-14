import os

files = ["collet_chuck_v4_bigbore.scad", "collet_chuck_v5_godzilla.scad", "PRINT_ME_V4_PLA.scad", "PRINT_ME_V5_PLA.scad"]

for filename in files:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            content = f.read()
        
        # Reduziere die Auflösung der Gewinde drastisch, um CGAL zu entlasten
        content = content.replace("steps_per_turn = 72;", "steps_per_turn = 36;")
        
        with open(filename, "w") as f:
            f.write(content)
