import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# Add the parameter at the top
content = content.replace("layout_mode =  false;    // LAYOUT AN", "layout_mode =  false;    // LAYOUT AN\ncross_section = 1;       // 0=Aus, 1=Schnitt Front-Schnapper, 2=Schnitt Heck-Scharnier")

# Find the Animation / Assembly block
anim_start = content.find("if (!layout_mode) {")
anim_end = content.find("} else {") # End of the if block

anim_block = content[anim_start:anim_end]

# We need to wrap the contents of the if(!layout_mode) block in a module or just a difference.
new_anim_block = """module full_assembly() {
    base_case();

    // ANIMATION
    anim_angle = ($t < 0.5) ? ($t / 0.5) * 90 : 90;
    anim_drop  = ($t >= 0.5) ? -(($t - 0.5) / 0.5) * 30.5 : 0;

    translate([0, 0, 34.0 + anim_drop])
        translate([0, 121.1, 1.5])
        rotate([-anim_angle, 0, 0])
        translate([0, -121.1, -1.5])
        stage_lid();

    for (c = [0 : cols - 1]) {
        bay_x = wall + c * (iem_bay_w + wall);
        bay_y = 2.4; 
        translate([bay_x, bay_y, 0]) tour_bunker();
        translate([bay_x, bay_y, bunker_h]) bunker_lid();
        translate([bay_x, bay_y, 0]) tpu_iem_tray_v11();
    }
}

if (!layout_mode) {
    if (cross_section == 1) {
        // SCHNITT DURCH DEN FRONT-SCHNAPPER (X = Mitte)
        difference() {
            full_assembly();
            // Schneidet die rechte Hälfte weg
            translate([box_w/2, -10, -10]) cube([200, 200, 100]);
        }
    } else if (cross_section == 2) {
        // SCHNITT DURCH DAS SCHARNIER (X = 3.2)
        difference() {
            full_assembly();
            // Schneidet den Großteil weg, zeigt genau den Pin
            translate([3.2, -10, -10]) cube([200, 200, 100]);
        }
    } else {
        full_assembly();
    }
"""

content = content[:anim_start] + new_anim_block + content[anim_end:]

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
