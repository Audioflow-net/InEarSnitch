import os
filepath = '/Users/ben/Desktop/InEarSnitch/Peli1020_TPU_Insert_V30.scad'
with open(filepath, 'r') as f:
    text = f.read()

text = text.replace('rounded_pocket(15.0, 27.0, cable_well_depth + eps, 7.5, 6, 2.0);', 
                    'rounded_pocket(15.0, 34.5, cable_well_depth + eps, 7.5, 6, 2.0);')
with open(filepath, 'w') as f:
    f.write(text)
