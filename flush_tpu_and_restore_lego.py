import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Update Base Case TPU Holes to be Countersunk (Senkkopf)
old_tpu_holes = re.search(r'// Löcher für die TPU-Kufen.*?\n.*?\n.*?\n.*?\n.*?\$fn=30\);', content, re.DOTALL).group(0)
new_tpu_holes = """// Löcher für die TPU-Kufen (Jetzt mit SENKKOPF-Fase, damit das TPU plan mit dem Boden abschließt!)
        translate([11.0, 20.0, -0.1]) cylinder(d=8, h=3, $fn=30);
        translate([11.0, 20.0, 0.5]) cylinder(d1=8, d2=12, h=1.6, $fn=30);
        
        translate([11.0, 105.6, -0.1]) cylinder(d=8, h=3, $fn=30);
        translate([11.0, 105.6, 0.5]) cylinder(d1=8, d2=12, h=1.6, $fn=30);
        
        translate([box_w - 11.0, 20.0, -0.1]) cylinder(d=8, h=3, $fn=30);
        translate([box_w - 11.0, 20.0, 0.5]) cylinder(d1=8, d2=12, h=1.6, $fn=30);
        
        translate([box_w - 11.0, 105.6, -0.1]) cylinder(d=8, h=3, $fn=30);
        translate([box_w - 11.0, 105.6, 0.5]) cylinder(d1=8, d2=12, h=1.6, $fn=30);"""
content = content.replace(old_tpu_holes, new_tpu_holes)

# 2. Put the Universal Lego Holes BACK into the PLA Base Case
old_bays = re.search(r'// CIEM / Bunker Bay.*?\n\s*translate\(\[bay_x, bay_y, floor_h\]\).*?r=6\);', content, re.DOTALL).group(0)
new_bays = """// CIEM / Bunker Bay (Komplette Wanne für das TPU-Inlay)
            translate([bay_x, bay_y, floor_h]) rounded_pocket(iem_bay_w, iem_bay_d, base_h, r=6);
            
            // LEGO-LOCK MULDEN (Universal-Raster für Silica Tour Bunker direkt im harten PLA-Boden!)
            // 4-Loch Raster Links (Für Bunker auf der linken Seite)
            translate([bay_x + 9.5, bay_y + 24.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 23.5, bay_y + 24.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 9.5, bay_y + 43.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 23.5, bay_y + 43.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            
            // 4-Loch Raster Rechts (Falls TPU gespiegelt wird!)
            translate([bay_x + 46.5, bay_y + 24.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 60.5, bay_y + 24.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 46.5, bay_y + 43.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);
            translate([bay_x + 60.5, bay_y + 43.5, floor_h - 1.2]) cylinder(d=6.0, h=1.3, $fn=24);"""
content = content.replace(old_bays, new_bays)

# 3. Clean up TPU Tray (Remove the clever floor/swallow holes, go back to full cutout)
old_tpu_tray = re.search(r'// 1\. Bunker Cutout.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\$fn=30\);', content, re.DOTALL).group(0)
new_tpu_tray = """// 1. Bunker Cutout (Links) - Geht wieder komplett durch! Bunker steht direkt auf dem harten PLA.
            translate([0.5, 0.5, -0.1]) rounded_pocket(34, 69, 17.2, r=3.5);
            // Kabel-Tresor über dem Bunker
            translate([2, 2, 17]) rounded_pocket(31, 66, 15, r=3);"""
content = content.replace(old_tpu_tray, new_tpu_tray)

# 4. Update TPU Rail to have Flush Countersunk Heads (No more mushroom!)
old_tpu_rail = re.search(r'translate\(\[8\.5, 17\.5, 0\]\) cylinder\(d=8\.0, h=2\.4.*?\n.*?\n.*?\n.*?\$fn=30\);', content, re.DOTALL).group(0)
new_tpu_rail = """// Flush Countersunk Head (Senkkopf) - Schließt bündig mit Z=2.0 ab!
        translate([8.5, 17.5, 0]) cylinder(d=8.0, h=0.5, $fn=30);
        translate([8.5, 17.5, 0.5]) cylinder(d1=8.0, d2=11.75, h=1.5, $fn=30);
        translate([8.5, 103.1, 0]) cylinder(d=8.0, h=0.5, $fn=30);
        translate([8.5, 103.1, 0.5]) cylinder(d1=8.0, d2=11.75, h=1.5, $fn=30);"""
content = content.replace(old_tpu_rail, new_tpu_rail)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
