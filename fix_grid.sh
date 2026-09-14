sed -i '' '/module silica_grid_cover() {/,/^}$/c\
module silica_grid_cover() {\
    grid_w = iem_bay_w - 6;\
    grid_d = iem_bay_d - 6;\
    \
    color("#FF9800")\
    difference() {\
        union() {\
            difference() {\
                rounded_pocket(grid_w - 0.2, grid_d - 0.2, 1.6, r=3);\
                for (gx = [4 : 3.5 : grid_w - 6]) {\
                    translate([gx, 4, -1])\
                        rounded_pocket(1.5, grid_d - 8, 4, r=0.75);\
                }\
            }\
            translate([grid_w/2, grid_d/2, 0])\
                cylinder(d=22, h=1.6, $fn=30);\
        }\
        translate([grid_w/2, grid_d/2, -1])\
            cylinder(d=14, h=4, $fn=30);\
    }\
}
' /Users/ben/Desktop/InEarSnitch/iem_stage_box.scad
