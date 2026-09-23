# Dead Ends — press_v2

| Iteration | Approach Tried | Why It Failed | Files Touched |
|-----------|---------------|---------------|---------------|
| 1 | Straight sleeve pocket with dead `COLLET_TAPER` declaration in Wedge press | Pocket had 90° straight walls; failed to produce lateral clamping force on mold parting line; uncentered cube cutout severed outer wall into 2 bodies | `press_v2_wedge.scad` |
| 1 | Inverted cam lever rotation formula and uncalibrated vertical stack height | At angle 0 lever swung down into the mold bed ($Z=-27$mm); 6.7mm solid collision with plunger plate | `press_v2_cam.scad` |
| 1 | Collar inner bore (53.5mm) larger than outer diameter (52.0mm) in Bayonet press | Negative wall thickness severed collar skirt into 2 pieces; conical collet hovered 5.4mm in mid-air above mold | `press_v2_bayonet.scad` |
| 1 | Test runner checking only OpenSCAD exit code and AST generation | Failed to detect physical solid collisions, severed walls, or mid-air floating parts | `verify_press_v2.py` |
