with open("/Users/ben/Desktop/InEarSnitch/SnitchCase_Sliding_V3.scad", "r") as f:
    code = f.read()

code = code.replace("translate([8, C_Y - 6, 26]) cube([15, 12, 4]);", "translate([10, C_Y - 6, wall+1+16]) cube([15, 12, 4]);")

with open("/Users/ben/Desktop/InEarSnitch/SnitchCase_Sliding_V3.scad", "w") as f:
    f.write(code)
