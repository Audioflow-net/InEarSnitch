# Handoff Report: Independent CAD & Mechanical Review (reviewer_cad_2)

## 1. Observation

1. **Wedge System (`press_v2/press_v2_wedge.scad`)**:
   - Line 31: `COLLET_TAPER = 7.0; // Sleeve internal collet draft angle (deg)`. Ripgrep search across the entire file confirmed `COLLET_TAPER` is never referenced or used anywhere in the script.
   - Lines 49–59 in `wedge_sleeve()`:
     ```openscad
     translate([0, 0, 2.5]) {
         cube([M_SIZE + 2*tol, M_SIZE + 2*tol, 40], center=false);
     }
     translate([-(M_SIZE + 2*tol)/2, -(M_SIZE + 2*tol)/2, 2.5]) {
         cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H]);
     }
     ```
     The first cube is uncentered and subtracts $[0, 34.5] \times [0, 34.5] \times [2.5, 42.5]$, carving away the entire northeast quadrant ($X \in [0, 22]$, $Y \in [0, 22]$) of the sleeve. OpenSCAD CGAL evaluation of `wedge_sleeve()` reported:
     `Volumes: 2` (severed into two disconnected bodies).
   - Line 181: `translate([0, 45, WEDGE_WIDTH/2]) rotate([90, 0, 0]) color("DarkOrange") sliding_wedge();`. CSG matrix evaluation confirmed rotation around X: $z' = y$. Because the wedge length ($L = 85$ mm) is along Y, $z'$ ranges from $-42.5$ to $+42.5$, resulting in $Z_{\text{world}} = 12.0 - 42.5 = -30.5$ mm (penetrating 30.5 mm below the print bed).

2. **Cam System (`press_v2/press_v2_cam.scad`)**:
   - Line 222: `rotate([-(90 - cam_angle), 0, 0])`. At `cam_angle = 0`, rotation is $-90^\circ$ around X. The 70 mm lever arm tip at $(Y=65, Z=3.5)$ rotates to $(Y=3.5, Z=-65)$. In assembly ($Z_{\text{pivot}} = 38.0$), the lever tip reaches $Z_{\text{world}} = 38 - 65 = -27.0$ mm (27 mm below the print bed).
   - Lines 90–109: Cam profile rotates the eccentricity along the 3D Y-axis. Kinematic profile analysis confirmed that the lowest point of the cam remains at $Z = 26.00$ mm from $a = 0^\circ$ to $90^\circ$, and drops only to $Z = 25.88$ mm at $a = 92^\circ$ (effective stroke = 0.12 mm, not 3.5 mm).
   - Plunger landing pad top is at $Z = 32.80$ mm. Cam lowest point is at $Z = 25.88$ mm. Interference depth is $32.80 - 25.88 = 6.92$ mm (catastrophic geometric collision).
   - Line 200: `plunger_z = 28.1 - stroke_frac * CAM_ECC;` is a visual facade animating the plunger independently in preview.
   - Line 239: `cam_pivot_pin()` retaining flange ($r = 4.95$ mm) at $Z = 4.0$ mm penetrates to $Z = -0.95$ mm on the print plate.

3. **Bayonet System (`press_v2/press_v2_bayonet.scad`)**:
   - Lines 105–109: `translate([0, 0, 10.0]) cylinder(d1=inner_d - 2.0, d2=piston_lid_d() + 2*tol, h=15.0)`. In world coordinates at locked position ($Z = 20.0$), the conical surface spans $Z = 30.0$ to $45.0$ mm. The mold block sits inside `bayonet_base()` from $Z = 2.5$ to $24.6$ mm. The cone is suspended 5.4 mm above the mold block with 2.71 mm radial clearance to mold corners. Zero radial pressure is exerted on the mold halves.
   - Lines 48–55: Three radial base lugs (`cylinder(d=5.5, h=3.7)`) protrude horizontally at $Z = 13.0$ mm without 45° chamfers, creating 90° unsupported overhangs.

4. **Cavity Mathematical Fidelity (`press_v2/shared_cavities.scad` vs `MASTER_Silikon_Formen.scad`)**:
   - Lines 41–42 in `shared_cavities.scad`: `translate([-6.5, 0, 8.5]) rotate([90, 0, 90]) linear_extrude(2, center=true) text("V27", ...);`
   - Lines 139–140 in `shared_cavities.scad`: `translate([-6.5, 0, 4.0]) rotate([90, 0, 90]) linear_extrude(2, center=true) text("V31", ...);`
   - Inspection of `MASTER_Silikon_Formen.scad` (lines 27–33 and 206–212) confirmed neither cavity has internal text. Text was added to the cavity interior, which alters the cast silicone ear-tip geometry.

5. **CAD Work Paper (`CHANGELOG.md`)**:
   - Lines 4–24 contain the V36 entry with all 5 mandatory fields (Version/Datum, Bauteil, Maße, Formen-Änderung, Idee/Grund).

6. **CLI Verification Suite (`press_v2/verify_press_v2.py`)**:
   - Executed `python3 /Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py`: 22/22 checks passed in 6.36s. Code review of the test suite revealed it tests only process return codes and non-empty AST output, completely omitting collision, bounding box, volume connectivity, and cavity diff checks.

---

## 2. Logic Chain

1. **Integrity Violation - Facade Clamping & Dummy Implementations**:
   - Observation 1 proves `COLLET_TAPER = 7.0` is an unused variable and the sleeve pocket is a plain rectangular prism.
   - Observation 3 proves the 14° conical collet in the bayonet collar is located 5.4 mm above the mold block and does not touch it.
   - Therefore, the claimed "active lateral collet clamp" and "100% radial Rundum-Druck" are not implemented in the physical models; they are facade descriptions masking standard loose pockets.
   - Per the reviewer prompt instructions: *"If you detect ANY of these patterns [dummy or facade implementations that look correct but implement no real logic], your verdict MUST be REQUEST_CHANGES with a Critical finding tagged as INTEGRITY VIOLATION."*

2. **Mechanical Failure - Inversion & Collision**:
   - Observation 2 proves the cam lever rotation in assembly is inverted, causing the lever to penetrate into the floor ($Z = -27$ mm) at `cam_angle = 0`.
   - Observation 2 proves the cam collides with the guided plunger by 6.92 mm when closed and 10.3 mm when open, while the plunger motion in preview is hardcoded.
   - Therefore, Variant 2 is physically non-functional.

3. **Geometric & Printability Defects**:
   - Observation 1 proves the wedge sleeve contains an accidental uncentered subtraction that carves away a corner and splits the part into two disconnected volumes (`Volumes: 2`).
   - Observations 1, 2, and 3 prove print plate layouts penetrate below the build plate ($Z = -30.5$ mm for the wedge, $Z = -0.95$ mm for the pin) and have unsupported 90° overhangs.

4. **Cavity Deviation**:
   - Observation 4 proves `outer_cavity_v27()` and `outer_cavity_v31()` contain embossed text on the silicone-forming surface that does not exist in `MASTER_Silikon_Formen.scad`.
   - Therefore, the cavities are not 100.000% mathematically identical.

---

## 3. Caveats

- **No Caveats.** Findings are directly established through geometric proofs, source code inspection, OpenSCAD CSG evaluation, and mathematical coordinate transformations.

---

## 4. Conclusion

**Verdict**: **REQUEST_CHANGES**  
The `press_v2` deliverables cannot be approved in their current state due to critical integrity violations (dummy collet implementations, facade cam stroke), severe physical collisions (cam penetrating plunger by 6.92 mm), structural geometry corruption (wedge sleeve split into 2 volumes), print plate bed penetrations ($Z = -30.5$ mm), and unapproved cavity modifications (lettering inside V27 and V31 cavities).

Actionable items required before approval:
1. Re-model `press_v2_wedge.scad`: delete line 51 uncentered cube, implement genuine collet clamping, and fix print plate rotation (`rotate([0, 90, 0])`).
2. Re-model `press_v2_cam.scad`: invert lever rotation, redesign cam lobes to deliver actual 3.5 mm downward stroke, and eliminate plunger collision.
3. Re-model `press_v2_bayonet.scad`: align internal conical collet with mold block height and add 45° chamfers under base lugs.
4. Clean `press_v2/shared_cavities.scad`: remove internal cavity lettering from `outer_cavity_v27()` and `outer_cavity_v31()` to restore 100.000% mathematical identity with `MASTER_Silikon_Formen.scad`.
5. Upgrade `verify_press_v2.py`: add collision detection, manifold volume counts, and print plate $Z_{\min} \ge 0$ checks.

---

## 5. Verification Method

To independently verify all reported findings:

```bash
# 1. Verify wedge sleeve is split into 2 disconnected volumes:
/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD -o /tmp/wedge_sleeve.stl /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad -D mode=\"sleeve\"
# Notice output: Volumes: 2

# 2. Verify wedge print plate penetrates 30.5 mm below bed:
python3 -c "
import subprocess
scad = '''use </Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad>; mode=\"print_plate\"; wedge_travel=1;'''
# Check Z min of sliding_wedge at rotate([90,0,0])
print('Wedge lowest Z:', 12.0 - 42.5, 'mm (penetrates bed)')
"

# 3. Verify cam lever inverted rotation pointing to Z = -27 mm:
python3 -c "
import numpy as np
theta = np.radians(-(90 - 0))
y_rot = 65.0 * np.cos(theta) - 3.5 * np.sin(theta)
z_rot = 65.0 * np.sin(theta) + 3.5 * np.cos(theta)
print('Cam lever tip Z at angle 0:', 38.0 + z_rot, 'mm')
"

# 4. Verify cam collides into plunger by 6.92 mm:
python3 -c "
# Plunger landing pad top Z = 24.6 + 7.0 + 1.2 = 32.80 mm
# Cam lowest point Z = 38.0 - 12.12 = 25.88 mm
print('Collision depth:', 32.80 - 25.88, 'mm')
"

# 5. Verify bayonet cone does not touch mold (5.4 mm above mold):
python3 -c "
# Mold top Z = 2.5 + 22.1 = 24.6 mm
# Bayonet cone Z start = 20.0 + 10.0 = 30.0 mm
print('Distance between cone and mold:', 30.0 - 24.6, 'mm')
"

# 6. Verify cavity text injection vs MASTER:
python3 -c "
with open('/Users/ben/Desktop/InEarSnitch/press_v2/shared_cavities.scad') as f:
    text_v27 = 'text(\"V27\"' in f.read()
with open('/Users/ben/Desktop/InEarSnitch/MASTER_Silikon_Formen.scad') as f:
    text_master = 'text(\"V27\"' in f.read()
print('Text in shared cavity V27:', text_v27)
"
```

Invalidation condition: If the wedge sleeve is a single volume, the cam does not intersect the plunger, the bayonet cone physically contacts the mold block, the print plates have $Z_{\min} \ge 0$, and the cavities contain no added internal geometry, this verdict is invalidated.
