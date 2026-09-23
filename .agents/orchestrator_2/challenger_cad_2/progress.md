# Progress — challenger_cad_2

Last visited: 2026-09-23T11:08:30Z

## Current Status
- Discovered Major Bug in Variant 1 (Wedge Sleeve): Uncentered subtraction in lines 49-53 blows open the top-right corner wall of the sleeve.
- Discovered Collision in Variant 1: Wedge and pressure pad collide by 4.26mm; pressure pad and tamper lid collide by 1.5mm.
- Discovered Severe Collision in Variant 2: Cam lever penetrates guided plunger by 6.7mm; required stack height (25.2mm) exceeds available clearance (13.4mm) under pivot pin by 11.8mm.
- Discovered Kinematic Disconnection in Variant 3: Helical bayonet collar assembly position (collar_z=20.0) floats 16.0mm above base lugs (z=13.0); at locked position collar thrust shoulder stops 1.1mm above thrust plate, failing to seat piston.
- Running Printability and Overhang Analysis: Found Variant 1 print plate layout places wedge 30mm below print bed (Z_min = -30.06mm).

