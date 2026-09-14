import re

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'r') as f:
    content = f.read()

# 1. Base Case: Replace simple vertical slots with Keyed Slots (Roof + Gap)
old_slots = re.search(r'// Einfache vertikale Scharnier-Schlitze.*?\n.*?\n.*?\}', content, re.DOTALL).group(0)
new_slots = """// KEYED HINGE: Vertikaler Schlitz mit Dach und 1.8mm Spalt!
        // Die Zylinderkammer geht nur bis Z=36.0 (darüber ist ein 1mm starkes Dach!)
        translate([3.2, pin_y, 5]) cylinder(d=3.2, h=31.0, $fn=16);
        translate([box_w - 3.2, pin_y, 5]) cylinder(d=3.2, h=31.0, $fn=16);
        
        // Der 1.8mm breite Spalt im Dach (hier passt der Pin nur hochkant durch)
        translate([3.2, pin_y, 36.5]) cube([10, 1.8, 2.0], center=true);
        translate([box_w - 3.2, pin_y, 36.5]) cube([10, 1.8, 2.0], center=true);
    }"""
content = content.replace(old_slots, new_slots)

# 2. Lid: Replace round pins with D-Pins (Keyed Pins)
old_pins = re.search(r'// Einfache Scharnier-Pins.*?\n.*?\n.*?\}', content, re.DOTALL).group(0)
new_pins = """// KEYED PINS (D-Form): Sind 2.8mm hoch, aber nur 1.6mm tief.
        // Horizontal (Geschlossen): Pin ist 2.8mm dick -> Blockiert unterm 1.8mm Dach!
        // Vertikal (Offen): Pin ist 1.6mm dick -> Rutscht durch den 1.8mm Spalt!
        intersection() {
            union() {
                translate([3.2, lid_d - 1.8 + 2.7, 0.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=2.5, center=true, $fn=16);
                translate([box_w - 3.2, lid_d - 1.8 + 2.7, 0.5]) rotate([0, 90, 0]) cylinder(d=2.8, h=2.5, center=true, $fn=16);
            }
            // Der Schnitt-Block, der die Pins in der Tiefe (Y) auf 1.6mm abflacht
            translate([box_w/2, lid_d - 1.8 + 2.7, 0.5]) cube([box_w + 10, 1.6, 2.8], center=true);
        }
    }"""
content = content.replace(old_pins, new_pins)

with open('/Users/ben/Desktop/InEarSnitch/iem_stage_box.scad', 'w') as f:
    f.write(content)
