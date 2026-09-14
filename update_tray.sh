sed -i '' '/module tpu_iem_tray() {/,/^}$/c\
module tpu_iem_tray() {\
    color("#4DB8FF")\
    union() {\
        difference() {\
            rounded_pocket(iem_bay_w - 2*tol, iem_bay_d - 2*tol, iem_bay_h - 2, r=5);\
            translate([35, 3, 2]) rounded_pocket(32, 74, iem_bay_h, r=3);\
            translate([3, 3, 2]) rounded_pocket(29, 35, iem_bay_h, r=3);\
            translate([3, 42, 2]) rounded_pocket(29, 35, iem_bay_h, r=3);\
            translate([28, 18, 2]) cube([12, 6, iem_bay_h]);\
            translate([28, 57, 2]) cube([12, 6, iem_bay_h]);\
            translate([11, 12, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([25, 12, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([11, 28, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([25, 28, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([11, 52, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([25, 52, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([11, 68, -1]) cylinder(d=8, h=10, $fn=20);\
            translate([25, 68, -1]) cylinder(d=8, h=10, $fn=20);\
            for (y = [12, 26, 40, 54, 68]) {\
                translate([43, y, -1]) cylinder(d=8, h=10, $fn=20);\
                translate([59, y, -1]) cylinder(d=8, h=10, $fn=20);\
            }\
        }\
        translate([35, 10, 32]) rotate([0, 90, 0]) halte_nase();\
        translate([35, 35, 32]) rotate([0, 90, 0]) halte_nase();\
        translate([35, 60, 32]) rotate([0, 90, 0]) halte_nase();\
        translate([67, 10, 32]) mirror([1, 0, 0]) halte_nase();\
        translate([67, 35, 32]) mirror([1, 0, 0]) halte_nase();\
        translate([67, 60, 32]) mirror([1, 0, 0]) halte_nase();\
    }\
}\
\
module halte_nase() {\
    hull() {\
        cylinder(d=5, h=5, $fn=20);\
        translate([0, 12, 0]) cylinder(d=5, h=5, $fn=20);\
    }\
}
' /Users/ben/Desktop/InEarSnitch/iem_stage_box.scad
