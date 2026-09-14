with open("/Users/ben/Desktop/InEarSnitch/SnitchCase_Sliding_V3.scad", "r") as f:
    code = f.read()

insert_idx = code.find("// Stopper-Kragen vorne")
if insert_idx != -1:
    tab_code = """
            // Hebe-Nase (Lifting Tab) zum Hochklappen
            // Ein prominenter Hebel ganz vorne am Cradle, damit man sofort sieht, wie man es anhebt!
            translate([8, C_Y - 6, 26]) cube([15, 12, 4]);
            
"""
    code = code[:insert_idx] + tab_code + code[insert_idx:]

with open("/Users/ben/Desktop/InEarSnitch/SnitchCase_Sliding_V3.scad", "w") as f:
    f.write(code)
