sed -i '' '/base_case();/,/lid_dock();/c\
base_case();\
\
for (c = [0 : cols - 1]) {\
    bay_x = wall + c * (70.0 + wall);\
    bay_y = wall;\
    translate([bay_x + 3, bay_y + 3, floor_h + silica_vault_h - 1.6])\
        silica_grid_cover();\
    translate([bay_x, bay_y, floor_h + silica_vault_h])\
        tpu_iem_tray_v9();\
}\
\
translate([0, 0, base_h])\
    rotate([lid_angle, 0, 0])\
    translate([0, 0, -lid_h])\
    lid_dock();\
' /Users/ben/Desktop/InEarSnitch/iem_stage_box.scad
