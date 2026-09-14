import re

with open("test_iris_valve.scad", "r") as f:
    content = f.read()

# Make the file blazing fast for OpenSCAD preview
content = content.replace("$fn = 60;", "$fn = 30;")
content = content.replace("for(a=[0:3:359])", "for(a=[0:10:359])")
content = content.replace("sphere(d=thickness);", "cube(thickness, center=true);")

with open("test_iris_valve.scad", "w") as f:
    f.write(content)
