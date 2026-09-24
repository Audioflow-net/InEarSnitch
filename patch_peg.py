import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

old_peg = r'// Ecke Oben Links \(Neben dem Mikrofon-Schacht\)\s*translate\(\[11\.0, 77\.0, 0\]\) petg_alignment_peg\(15\.0, 6\.0, tol\);'
new_peg = """// Ecke Oben Links (Neben dem Mikrofon-Schacht)
            // GELÖSCHT: Der neue Logo-Turm bei X=15.65 übernimmt jetzt exakt diese Funktion 
            // und dient als massiver Anker-Stift für die obere linke Ecke!"""
content = re.sub(old_peg, new_peg, content)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
