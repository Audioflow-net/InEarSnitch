import os
import re

filepath = '/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad'
with open(filepath, 'r') as f:
    text = f.read()

# 1. Lower PETG Block B to allow deeper ramp
old_block_b = "translate([20, 55, 0]) support_free_block(60, 18, 5.0, tol);"
new_block_b = "translate([20, 55, 0]) support_free_block(60, 18, 2.0, tol);"
if old_block_b in text:
    text = text.replace(old_block_b, new_block_b)

# 2. Maximize the ramp
old_seesaw = """    // 3. PUSH-TO-EJECT SEESAW CAVITY (RAMPE)
    // Breite = 10.0mm (Das Mic hat 15mm, liegt also auf massiven TPU-Schultern auf für extremen Grip!)
    // Anstatt eines geraden Lochs ist es nun eine elegante Rampe!
    // Die Rampe endet nun bei exakt X=75.65 (Das ist exakt 12mm VOR dem dicken Korpus bei X=87.65).
    // Dadurch hat der Mic-Schaft einen massiven 12mm TPU-Block als perfekten Hebel-Punkt!
    translate([15.0, chan_y + 1.65 - 5.0, 0])
        ramp_pocket(l=60.65, w=10.0, h_top=depth + flange_t + 1.0, z_deep=6.0, z_shallow=14.12, r=4.0, br=4.0, chamfer=2.0);"""

new_seesaw = """    // 3. PUSH-TO-EJECT SEESAW CAVITY (RAMPE - MAX LIFT)
    // Breite = 10.0mm (Das Mic hat 15mm, liegt also auf massiven TPU-Schultern auf für extremen Grip!)
    // Der 12mm harte TPU-Hebelblock vor dem dicken Korpus bleibt exakt erhalten (endet bei X=75.65).
    // ABER: Die Rampe startet jetzt ganz links an der äußersten Spitze (X=9.65) und taucht
    // extrem tief bis auf Z=2.0 ab (früher Z=6.0). Dadurch gibt es massiv mehr Hub!
    translate([9.65, chan_y + 1.65 - 5.0, 0])
        ramp_pocket(l=66.0, w=10.0, h_top=depth + flange_t + 1.0, z_deep=2.0, z_shallow=14.12, r=4.0, br=4.0, chamfer=2.0);"""

if old_seesaw in text:
    text = text.replace(old_seesaw, new_seesaw)
    with open(filepath, 'w') as f:
        f.write(text)
    print("Ramp maximized successfully!")
else:
    print("Could not find the old seesaw code to replace.")

