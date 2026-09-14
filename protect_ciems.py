import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Update Tour Bunker Vents (Split into two clean zones)
old_bunker_vents = re.search(r'// QUERSTROM-BELÜFTUNG.*?(?=\n    \}\n\}\n)', content, re.DOTALL).group(0)

new_bunker_vents = """// QUERSTROM-BELÜFTUNG (Side-Flow Air Vents)
        // Vertikale Schlitze (1.5mm), exakt passend zu den beiden In-Ear Mulden
        for (y = [10 : 4 : 30]) translate([31, y, 3]) cube([5, 1.5, 10]);
        for (y = [42 : 4 : 62]) translate([31, y, 3]) cube([5, 1.5, 10]);"""
content = content.replace(old_bunker_vents, new_bunker_vents)

# 2. Update TPU Tray Windows to thick bumper bars
old_tpu_windows = re.search(r'// QUERSTROM-FENSTER \(Unten\).*?translate\(\[33, 40, 3\]\) cube\(\[5, 24, 10\]\);', content, re.DOTALL).group(0)

new_tpu_windows = """// QUERSTROM-GITTER (Unten) - BUMPER PROTECTION!
            // Statt offener Fenster schneiden wir auch hier Schlitze.
            // Die weichen TPU-Stege dazwischen verdecken das harte Plastik des Bunkers,
            // sodass die wertvollen In-Ears weich abgefedert werden!
            // Schlitze sind 2.0mm für Toleranz-Ausgleich beim Luftstrom.
            for (y = [10 : 4 : 30]) translate([33, y, 3]) cube([5, 2.0, 10]);
            for (y = [42 : 4 : 62]) translate([33, y, 3]) cube([5, 2.0, 10]);"""
content = content.replace(old_tpu_windows, new_tpu_windows)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
