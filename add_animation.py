import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Replace the static lid placement with an animated one
old_lid_placement = r'translate\(\[0, 0, 34\.0\]\) stage_lid\(\);'

new_lid_placement = """// ANIMATION: Nutze View -> Animate in OpenSCAD (FPS: 30, Steps: 100)
        // Phase 1: Slide-to-Unlock (Deckel schiebt sich 2.5mm nach hinten)
        anim_slide = ($t == 0) ? -2.5 : (($t < 0.2) ? -2.5 + ($t / 0.2) * 2.5 : 0);
        // Phase 2: Aufklappen (Deckel schwenkt 90 Grad hoch)
        anim_angle = ($t >= 0.2 && $t < 0.6) ? (($t - 0.2) / 0.4) * 90 : (($t >= 0.6) ? 90 : 0);
        // Phase 3: Drop-Down (Deckel gleitet im Schlitz nach unten)
        anim_drop  = ($t >= 0.6) ? -(($t - 0.6) / 0.4) * 30.5 : 0;

        translate([0, anim_slide, 34.0 + anim_drop])
            translate([0, 121.1, 1.5])
            rotate([-anim_angle, 0, 0])
            translate([0, -121.1, -1.5])
            stage_lid();"""

content = re.sub(old_lid_placement, new_lid_placement, content)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
