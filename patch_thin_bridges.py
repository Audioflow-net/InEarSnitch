import re

with open('Peli1020_TPU_Insert_V31.scad', 'r') as f:
    content = f.read()

old_bridges = r'module logo_bridges_2d\(\) \{.*?\}'
new_bridges = """module logo_bridges_2d() {
    // KORREKTE Koordinaten für die Bridges, extrem DÜNN (r=0.15), 
    // damit das Auge nicht verdeckt wird!
    
    // Nase zu Hut (links) - Weiter links, weg vom Auge!
    hull() {
        translate([-4.8, -1.5]) circle(r=0.15, $fn=16);
        translate([-4.6, 1.0]) circle(r=0.15, $fn=16);
    }
    
    // Halstuch/Nacken zu Ohr (unten Mitte)
    hull() {
        translate([-1.5, -2.0]) circle(r=0.15, $fn=16);
        translate([0.0, -1.0]) circle(r=0.15, $fn=16);
    }
    
    // Ohr zu Funkwellen (rechts)
    hull() {
        translate([2.5, -1.5]) circle(r=0.15, $fn=16);
        translate([5.0, -1.5]) circle(r=0.15, $fn=16);
    }
}"""

content = re.sub(old_bridges, new_bridges, content, flags=re.DOTALL)

with open('Peli1020_TPU_Insert_V31.scad', 'w') as f:
    f.write(content)
