# Independent CAD & Mechanical Review Report: press_v2

**Reviewer**: `reviewer_cad_2` (Roles: Reviewer, Critic)  
**Date**: 2026-09-23  
**Target Directory**: `/Users/ben/Desktop/InEarSnitch/press_v2/`  
**Overall Verdict**: **REQUEST_CHANGES**  
**Overall Risk Assessment**: **CRITICAL**

---

## Executive Summary

An exhaustive, adversarial mechanical and geometric review of `press_v2/` (`shared_cavities.scad`, `press_v2_wedge.scad`, `press_v2_cam.scad`, `press_v2_bayonet.scad`, `verify_press_v2.py`, and `CHANGELOG.md`) was conducted.

While the code compiles under OpenSCAD CLI and passes the 22 surface-level checks in `verify_press_v2.py`, rigorous geometric, kinematic, and dimensional analysis reveals **Critical Findings tagged as INTEGRITY VIOLATIONS and Mechanical Facades**:
1. **Wedge Sleeve Broken Geometry & Missing Collet Action**: `press_v2_wedge.scad` defines `COLLET_TAPER = 7.0` as an unused dummy constant. The mold pocket is a straight rectangular box with 0.5 mm loose clearance and zero collet clamping. Worse, a stray uncentered subtraction (`cube([34.5, 34.5, 40])`) cuts away the entire $+X, +Y$ quadrant of the sleeve wall, splitting the sleeve into two disconnected volumes (`Volumes: 2`). On the print plate, `rotate([90, 0, 0])` plunges the wedge 30.5 mm below the bed ($Z = -30.5$ mm).
2. **Cam Lever Inversion, Non-Functioning Stroke & Plunger Collision**: In `press_v2_cam.scad`, the lever kinematic rotation is inverted (`rotate([-(90-a), 0, 0])`). At $a = 0^\circ$ ("open"), the 70 mm arm points straight down through the mold to $Z = -27$ mm. The cam lobe does not produce a 3.5 mm downward stroke. In locked position ($a = 92^\circ$), the cam penetrates the plunger by 6.92 mm; at $a = 0^\circ$ it penetrates by 10.3 mm. The plunger movement in assembly is a hardcoded visual facade.
3. **Bayonet Collet Decoupled from Mold**: In `press_v2_bayonet.scad`, the 14° internal conical collet is located at $Z = 30.0 - 45.0$ mm, while the mold block ends at $Z = 24.6$ mm. The cone hovers in empty air and never contacts the mold block (2.71 mm corner clearance, 9.75 mm flat clearance). There is zero radial compression. Furthermore, the print plate contains severe 90° unsupported horizontal overhangs on the base lugs.
4. **Cavity Geometry Alteration**: In `shared_cavities.scad`, `outer_cavity_v27()` and `outer_cavity_v31()` have engraved text added to the inner cavity wall (`text("V27")` and `text("V31")`), which does not exist in `MASTER_Silikon_Formen.scad`. This alters the cast silicone ear-tip geometry by embossing lettering on the tip shaft, violating Requirement R2 (100.000% mathematical fidelity).
5. **Self-Certifying Test Suite**: `verify_press_v2.py` only validates CLI return codes, non-empty CSG ASTs, and PNG preview file existence (>1000 bytes). It performs no collision detection, no boolean intersection tests, no Z-bounds checks, and no cavity diff checks.

---

## Detailed Findings

### Critical Finding 1: [INTEGRITY VIOLATION & MECHANICAL FACADE] Dummy Collet and Broken Sleeve Geometry in Wedge Variant
- **Location**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad`, lines 31, 47–59, 181
- **What**:
  1. **Unused Collet Taper**: Line 31 defines `COLLET_TAPER = 7.0; // Sleeve internal collet draft angle (deg)`. This variable is NEVER referenced anywhere in the script. The mold pocket (lines 56–58) is subtracted as a plain rectangular prism `cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H])` with vertical $0^\circ$ walls. The mold halves have 0.5 mm total clearance ($2 \times 0.25$ mm) and experience zero lateral compression.
  2. **Accidental Wall Cutout (Split Volume)**: Line 51 contains an uncentered subtraction:
     ```openscad
     translate([0, 0, 2.5]) {
         cube([M_SIZE + 2*tol, M_SIZE + 2*tol, 40], center=false);
     }
     ```
     Because the sleeve outer footprint is $44 \times 44$ mm centered at $(0,0)$ (extending from $-22$ to $+22$ in X and Y), this uncentered cube removes all material in $[0, 22] \times [0, 22] \times [2.5, 42.5]$. It blows out the entire northeast corner of the sleeve. Together with the transverse wedge slot (`cube([24.5, 54, 16])`), the sleeve is completely severed into two disconnected solid bodies (`Volumes: 2`).
  3. **Print Plate Z-Penetration**: Line 181 rotates `sliding_wedge()` via `rotate([90, 0, 0])`. Because the wedge length ($L = 85$ mm) is along the Y-axis, rotating $90^\circ$ around X aligns the length along the Z-axis, causing the wedge to plunge $30.5$ mm below the print bed ($Z = -30.5$ mm to $+54.5$ mm).
- **Why**: This is a direct integrity violation (dummy constant and non-functional collet claiming parting line compression) and a critical modeling defect rendering the sleeve structurally broken and unprintable.
- **Required Fix**:
  - Remove the uncentered `cube` at line 51.
  - Implement a genuine tapered internal pocket on the X-walls to squeeze the mold halves together as the mold is inserted, or implement a tapered wedge clamp block.
  - Fix print plate orientation for `sliding_wedge()` using `rotate([0, 90, 0])` and adjust Z-offset so $Z_{\min} = 0$.

---

### Critical Finding 2: [INTEGRITY VIOLATION & MECHANICAL FACADE] Inverted Rotation, Severe Collision & Dummy Stroke in Cam Variant
- **Location**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_cam.scad`, lines 90–109, 199–200, 222, 239
- **What**:
  1. **Kinematic Rotation Inversion**: Assembly rotation is defined as `rotate([-(90 - cam_angle), 0, 0])`. At `cam_angle = 0` ("open"), $\phi = -90^\circ$, which rotates the $+Y$ lever arm down to $-Z$. The 70 mm lever arm points straight down through the mold to $Z = -27.0$ mm (27 mm below the table).
  2. **Non-Functioning Cam Stroke**: The eccentric lobe profile in 2D is extruded along Z and rotated `rotate([0, 90, 0])`, translating the eccentricity along the 3D Y-axis. As the cam rotates around X, its lowest point in world coordinates remains at $Z = 26.00$ mm from $a = 0^\circ$ to $a = 90^\circ$, and only reaches $Z = 25.88$ mm at $a = 92^\circ$ (a total vertical stroke of only 0.12 mm, not the claimed 3.5 mm).
  3. **Catastrophic Plunger Collision**: The top of the plunger landing pads is at $Z = 32.80$ mm. The lowest surface of the cam is at $Z = 25.88$ mm. The cam collides and penetrates into the plunger by $6.92$ mm! When $a = 0^\circ$, it penetrates by $10.3$ mm. The physical mechanism cannot rotate or close.
  4. **Facade Animation**: The plunger displacement in assembly is hardcoded via `plunger_z = 28.1 - sin(cam_angle) * CAM_ECC`, masking the physical interference in preview mode.
  5. **Print Plate Bed Penetration**: In `mode == "print_plate"`, `cam_pivot_pin()` retaining flange ($r = 4.95$ mm) dips below the print bed to $Z = -0.95$ mm.
- **Why**: The mechanism is physically non-functional and collides severely. The claimed 3.5 mm stroke and 92° over-center lock are visual facades.
- **Required Fix**:
  - Re-engineer the cam profile so the lobe eccentricity produces genuine downward Z-displacement as the lever swings from vertical ($+Z$) to horizontal ($+Y$).
  - Correct the pivot height $Z$ and plunger landing pad height to eliminate collision and provide continuous contact during actuation.
  - Adjust `cam_pivot_pin()` Z-height on the print plate so $Z_{\min} = 0$.

---

### Critical Finding 3: [INTEGRITY VIOLATION & MECHANICAL GAP] Disconnected Conical Collet and Overhangs in Bayonet Variant
- **Location**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad`, lines 48–55, 105–109, 226–233
- **What**:
  1. **Disconnected Conical Collet**: Line 107 subtracts the 14° conical collet:
     `translate([0, 0, 10.0]) cylinder(d1=inner_d - 2.0, d2=piston_lid_d() + 2*tol, h=15.0)`
     In world coordinates at locked position ($Z_{\text{collar}} = 20.0$ mm), this cone spans $Z_{\text{world}} = 30.0$ mm to $45.0$ mm. The mold block ends at $Z_{\text{world}} = 24.6$ mm. The cone is suspended 5.4 mm above the mold block in mid-air. It has $2.71$ mm radial clearance to the mold corners and $9.75$ mm to the mold flats. The claimed "14° internal conical collet generating 100% radial Rundum-Druck across the mold parting line" is completely fictitious.
  2. **Unprintable 90° Overhangs**: The 3 radial locking lugs on `bayonet_base()` protrude horizontally at $Z = 13.0$ mm with no support or 45° chamfer beneath them. In FDM printing, horizontal cylinders starting in mid-air cannot be printed support-free.
  3. **Internal Ceiling Overhang**: The collar has an internal flat annular ceiling at $Z = 29.5$ mm (transition from $d = 35.3$ mm to $d = 22.0$ mm) that forms a 6.65 mm unsupported overhang inside the tube.
- **Why**: The primary mechanical claim of radial parting-line compression is not realized in the physical geometry, and the parts cannot be printed support-free.
- **Required Fix**:
  - Extend or reposition the conical collet or provide a conical sleeve segment that directly contacts the mold blocks (e.g. chamfered mold corners or a 2-piece split collet sleeve).
  - Add 45° conical transition chamfers beneath the base lugs to enable support-free printing.
  - Add internal 45° draft to the collar inspection aperture ceiling.

---

### Critical Finding 4: [INTEGRITY VIOLATION & MATHEMATICAL FIDELITY FAILURE] Cavity Injections in `shared_cavities.scad`
- **Location**: `/Users/ben/Desktop/InEarSnitch/press_v2/shared_cavities.scad`, lines 41–42, 139–140
- **What**:
  - `outer_cavity_v27()` and `outer_cavity_v31()` contain embossed text on the inner cavity walls:
    ```openscad
    translate([-6.5, 0, 8.5]) rotate([90, 0, 90]) linear_extrude(2, center=true) text("V27", size=3.5, ...);
    translate([-6.5, 0, 4.0]) rotate([90, 0, 90]) linear_extrude(2, center=true) text("V31", size=3.5, ...);
    ```
  - In `MASTER_Silikon_Formen.scad`, neither `outer_cavity_v27()` nor `outer_cavity_v31()` contains internal text. Text in MASTER exists only on the exterior block faces (`form_left_*` / `form_right_*`).
  - Adding text to the cavity alters the molded ear-tip surface, introducing raised lettering onto the silicone tip shaft.
- **Why**: Requirement R2 states: *"Die exakten inneren Kavitäten (V27, V29, V30, V31) müssen mathematisch zu 100% unangetastet bleiben und aus dem alten Code (`MASTER_Silikon_Formen.scad`) importiert/übernommen werden."* The deliverables claim 100.000% mathematical identity, but the cavity geometry is altered.
- **Required Fix**:
  - Remove internal `text("V27")` and `text("V31")` from `outer_cavity_v27()` and `outer_cavity_v31()`, keeping cavity geometry 100.000% identical to `MASTER_Silikon_Formen.scad`. External block lettering in `mold_half_left()` and `mold_half_right()` is sufficient.

---

### Major Finding 5: [VERIFICATION SUITE INTEGRITY] Inadequate Test Suite in `verify_press_v2.py`
- **Location**: `/Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py`
- **What**:
  - `verify_press_v2.py` validates only exit codes, non-empty CSG AST strings, and preview PNG file sizes (>1000 bytes).
  - It failed to detect:
    1. Broken sleeve volume (2 volumes).
    2. Negative Z penetrations on print plates ($Z = -30.5$ mm, $Z = -0.95$ mm).
    3. Severe physical collision between cam and plunger (6.92 mm overlap).
    4. Cavity geometry alterations vs `MASTER_Silikon_Formen.scad`.
- **Why**: The verification suite provides a false sense of security (22/22 PASS), functioning as a self-certifying facade.
- **Required Fix**:
  - Enhance `verify_press_v2.py` with:
    - Bounding box Z checks ($Z_{\min} \ge -0.01$ mm on all print plate modes).
    - Part volume connectivity checks (single manifold solid per component).
    - Kinematic collision checks (asserting that `intersection() { cam; plunger; }` has zero volume at closed position).
    - Mathematical CSG diff asserting 100.000% equivalence between `shared_cavities.scad` cavities and `MASTER_Silikon_Formen.scad`.

---

## Verification Matrix

| Check Item | Claimed | Verified Finding | Result |
|---|---|---|---|
| Wedge 7.125° self-locking ramp | Self-locking axial downforce | tan(7.125°) = 0.125 << friction angle (~22°) | **PASS** |
| Wedge floating pressure pad | Anti-skew decoupling | Underside recess captures d=33.8 lid; anti-skew wings | **PASS** |
| Wedge 7.0° lateral collet action | Radial parting line clamp | `COLLET_TAPER` unused dummy; pocket is rectangular cube | **FAIL (CRITICAL)** |
| Wedge sleeve integrity | Single printable housing | Accidental uncentered cube splits sleeve into 2 volumes | **FAIL (CRITICAL)** |
| Wedge print plate | Support-free on bed | Rotated vertically; penetrates 30.5 mm below bed | **FAIL (CRITICAL)** |
| Cam 92° over-center lock | Detent lock at 92° | Lever rotated inverted (points into floor); stroke is 0.12mm | **FAIL (CRITICAL)** |
| Cam plunger collision | Pure vertical stroke | Cam penetrates plunger by 6.92 mm (collides permanently) | **FAIL (CRITICAL)** |
| Cam print plate | Flat support-free | Pin flange penetrates 0.95 mm below bed; lever hovers | **FAIL (MAJOR)** |
| Bayonet 60° twist collar | 4.0 mm travel, 24 mm lead | 3 lugs at 120°, 4mm ramp over 60° (lead=24mm) | **PASS** |
| Bayonet floating thrust plate | Decoupled non-rotating disc | 3 vertical ribs keyed into base slots; 0° rotation | **PASS** |
| Bayonet 14° conical collet | 100% radial Rundum-Druck | Cone is 5.4 mm above mold; zero contact with mold block | **FAIL (CRITICAL)** |
| Bayonet print plate | 100% support-free | 3 base lugs have 90° unsupported overhangs; internal ceiling | **FAIL (CRITICAL)** |
| Cavity mathematical fidelity | 100.000% identical to MASTER | Text "V27" & "V31" added inside cavities | **FAIL (CRITICAL)** |
| CHANGELOG.md Work Paper | 5-field CAD entry | V36 entry present with all 5 mandatory fields | **PASS** |
| Automated verification suite | Independent proof | Superficial checks passed broken models (self-certifying) | **FAIL (MAJOR)** |

---

## Recommendations for Worker & Orchestrator

1. **Immediate Re-work of `press_v2_wedge.scad`**:
   - Fix lines 49–59: Remove uncentered cube subtraction on line 51.
   - Implement actual collet draft angle on the sleeve pocket walls and/or mold blocks.
   - Fix print plate rotation for `sliding_wedge()`.
2. **Immediate Re-work of `press_v2_cam.scad`**:
   - Redesign cam geometry and pivot height so cam lobes provide genuine downward stroke without intersecting the plunger.
   - Correct rotation direction from `rotate([-(90-a), 0, 0])` to `rotate([90-a, 0, 0])`.
3. **Immediate Re-work of `press_v2_bayonet.scad`**:
   - Align the conical collet with the actual mold block height so radial compression is physically delivered.
   - Add 45° chamfers under the base lugs and internal collar ceiling for true support-free printing.
4. **Restore 100.000% Cavity Identity in `shared_cavities.scad`**:
   - Strip internal cavity text from `outer_cavity_v27()` and `outer_cavity_v31()`.
5. **Strengthen `verify_press_v2.py`**:
   - Add collision assertions, bounding box checks, and volume integrity validation.

**Final Verdict**: **REQUEST_CHANGES**
