# Adversarial Challenge Report: Mechanical Stress & Printability Analysis

**Agent:** `challenger_cad_2`  
**Role:** Mechanical Stress & Printability Challenger  
**Date:** 2026-09-23  
**Target:** `/Users/ben/Desktop/InEarSnitch/press_v2`  
**Explicit Verdict:** **REJECT (ALL 3 VARIANTS HAVE CRITICAL KINEMATIC & PRINTABILITY DEFECTS)**

---

## Executive Summary

A forensic empirical investigation of the Press V2 implementation (`press_v2_wedge.scad`, `press_v2_cam.scad`, `press_v2_bayonet.scad`, and `verify_press_v2.py`) was conducted using OpenSCAD CLI 2021.01, STL mesh analysis, CSG intersection evaluation, and kinematic stack-up calculations.

While `verify_press_v2.py` reports 22/22 passes, this test suite is an **illusory oracle** that only checks CSG syntax and preview PNG generation. In reality:
1. **Variant 1 (Wedge)**:
   - Suffers a catastrophic cutout blowout in the sleeve corner due to an uncentered subtraction.
   - The wedge collides vertically with the floating pressure pad by **4.26 mm** (`Z = 25.54` to `29.80 mm`).
   - The pressure pad collides with the tamper lid by **1.5 mm**.
   - The wedge cannot fully seat the piston at Z=14.1; it jams at only 27% travel, protruding 50.1 mm out of the housing.
   - In `mode="print_plate"`, the wedge is placed **30.06 mm below the build plate** ($Z_{\text{min}} = -30.06\text{ mm}$).
2. **Variant 2 (Cam)**:
   - Suffers an impossible vertical stack-up under the pivot pin: required height is **25.2 mm**, but available distance from pivot to mold shoulder is only **13.4 mm** (an **11.8 mm shortfall**).
   - In the assembly position, the cam lobe penetrates the guided plunger plate by **6.7 mm** (`Z = 26.1` to `32.8 mm`).
   - The cam cannot even be physically installed with the pivot pin in place.
   - In `mode="print_plate"`, the palm press pad floats 2.0 mm in mid-air as an unsupported cantilever, and the pivot pin extends below the print bed.
3. **Variant 3 (Bayonet)**:
   - The collar in the author's assembly position is floating **16.0 mm above the base lugs** (OpenSCAD intersection is completely empty).
   - At the true physical locked position, the collar thrust flange stops **1.1 mm above the thrust plate**, providing **zero axial downforce**.
   - In `mode="print_plate"`, the 3 radial base lugs ($d=5.5\text{ mm}$) are 100% unsupported horizontal cantilevers protruding at $Z = 13.0\text{ mm}$, which will collapse during FDM printing without supports.

---

## Detailed Findings by Challenge Dimension

### 1. Mechanical Kinematics, Stroke & Collision Verification

#### 1.1 Variant 1: Wedge Press (`press_v2_wedge.scad`)
- **Question**: Does the wedge travel fully seat the piston at Z=14.1?
- **Finding**: **NO (FAILED)**.
- **Root Cause & Mathematical Proof**:
  - Mold shoulder sits at $Z = 24.6\text{ mm}$ ($Z_{\text{min}} = -8.0$, translated $+10.5\text{ mm}$).
  - Fully seated tamper lid top is at $Z = 27.6\text{ mm}$.
  - Pressure pad recess ceiling sits on tamper lid top ($Z = 27.6\text{ mm}$). With $3.7\text{ mm}$ solid pad thickness above the recess, the pad contact surface is at $Z = 31.3\text{ mm}$.
  - The sleeve slot ceiling is at $Z = 39.5\text{ mm}$.
  - Maximum available vertical clearance: $39.5 - 31.3 = 8.2\text{ mm}$.
  - At the wedge over-travel stop lugs ($Y_{\text{wedge}} = 26.5\text{ mm}$), the wedge thickness is $12.21\text{ mm}$.
  - Wedge interference: $12.21 - 8.20 = 4.01\text{ mm}$.
  - Empirical verification via OpenSCAD CSG intersection:
    ```openscad
    intersection() {
        translate([0, 0, 24.6]) pressure_pad();
        translate([0, 0, 24.0]) sliding_wedge();
    }
    ```
    Generated `/tmp/test_wedge_pad_collision.stl`: Solid volume of 32 vertices, 18 facets, penetration bounds $X \in [-11.75, 11.75]$, $Y \in [-13.1, 16.7]$, $Z \in [25.54, 29.80]$ (**4.26 mm vertical collision**).
  - Physical consequence: The wedge jams at $Y_{\text{wedge}} = -23.6\text{ mm}$ (only $18.9\text{ mm}$ of travel, $< 27\%$ stroke). The wedge sticks out 50.1 mm from the housing. The piston is NEVER fully seated at Z=14.1.

#### 1.2 Variant 1 Sleeve Wall Blowout
- **Finding**: **CRITICAL GEOMETRIC DEFECT**.
- **Code**: `press_v2_wedge.scad`, lines 49-53:
  ```openscad
  translate([0, 0, 2.5]) {
      cube([M_SIZE + 2*tol, M_SIZE + 2*tol, 40], center=false);
      // Center the pocket
  }
  ```
- **Proof**: The uncentered cube from $(0,0,2.5)$ to $(34.5, 34.5, 42.5)$ was left in the `difference()` before the centered pocket was added. This completely destroys and blows open the outer corner of the sleeve ($X \in [17.25, 22.0]$, $Y \in [17.25, 22.0]$). Verified via `/tmp/wedge_sleeve.png` (missing corner wall) and OpenSCAD reporting `Volumes: 2`.

#### 1.3 Variant 2: Cam Lever Press (`press_v2_cam.scad`)
- **Question**: Does the cam 3.5mm stroke fully engage the tamper lid down to the mold shoulder?
- **Finding**: **NO (FAILED)**.
- **Root Cause & Mathematical Proof**:
  - Distance from pivot axle ($Z = 38.0$) to mold shoulder ($Z = 24.6$) is strictly $13.4\text{ mm}$.
  - Stack required between pivot and shoulder:
    - Tamper lid: $3.0\text{ mm}$
    - Guided plunger plate: $6.7\text{ mm}$
    - Cam lobe: $12.0\text{ mm}$ (open) / $15.5\text{ mm}$ (closed)
    - Total required height: $21.7\text{ mm}$ (open) / $25.2\text{ mm}$ (closed).
  - Clearance deficit: **11.8 mm closed**, **8.3 mm open**.
  - Empirical verification via OpenSCAD CSG intersection:
    ```openscad
    intersection() {
        translate([0, 0, 24.6]) guided_plunger();
        translate([0, 0, 38.0]) rotate([2, 0, 0]) cam_lever();
    }
    ```
    Generated `/tmp/test_cam_plunger_collision.stl`: Solid volume with 194 vertices, 101 facets, 3 separate volumes, collision bounds $Z \in [26.1, 32.8]$ (**6.7 mm solid penetration**).
  - Physical consequence: The cam lever cannot be assembled; the pivot pin cannot be inserted because the cam lobe crashes into the plunger by $> 6\text{ mm}$.

#### 1.4 Variant 3: Bayonet Press (`press_v2_bayonet.scad`)
- **Question**: Does the 60° twist draw down the floating thrust plate without rotating the piston?
- **Finding**: **PARTIAL (Anti-rotation works, Draw-down kinematics fails)**.
- **Root Cause & Mathematical Proof**:
  - Anti-rotation decoupling: 3 vertical ribs on `floating_thrust_plate` mate into 3 vertical channels in `bayonet_base`. Pure vertical travel without rotation is preserved.
  - Collar assembly error: Base lugs are at $Z = 13.0\text{ mm}$. Helical grooves on collar are at $h = 5.0\text{ mm}$ to $9.0\text{ mm}$. To engage, collar bottom must be at $Z = 8.0\text{ mm}$ (open) and $Z = 4.0\text{ mm}$ (closed).
  - The author hardcoded `collar_z = 24.0 - t_frac * 4.0;` ($Z = 24.0 \to 20.0$).
  - At $Z = 20.0$, the collar is **16.0 mm above the lugs**. Verified via OpenSCAD intersection: returned `Current top level object is empty`.
  - True physical locked state: Collar at $Z = 4.0\text{ mm}$. Internal thrust shoulder is at $Z = 4.0 + 29.5 = 33.5\text{ mm}$. Fully seated thrust plate top is at $Z = 32.4\text{ mm}$.
  - Clearance gap: $33.5 - 32.4 = 1.1\text{ mm}$.
  - Physical consequence: When locked into detent, the collar stops 1.1 mm above the thrust plate. The collar applies **0.0 N downward clamping force**; the piston is never driven down.

---

### 2. Printability and Overhang Stress Analysis

All 3 variants were exported to STL via `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD -D mode="print_plate"` and analyzed via Python STL normal extraction:

| Variant | Export Time | Total Facets | Bed Facets | Safe Overhangs ($\le 45^\circ$) | Steep Overhangs ($45^\circ - 85^\circ$) | Horizontal Ceilings ($\ge 85^\circ$) | Bounding Box ($X, Y, Z$ in mm) |
|---|---|---|---|---|---|---|---|
| **Variant 1 Wedge** | 24.92s | 8,684 | 166 | 938 | **890** | 164 | `[-22.0, 62.9] x [-52.0, 46.3] x [-30.06, 58.5]` |
| **Variant 2 Cam** | 36.55s | 13,964 | 166 | 1,582 | **1,161** | 131 | `[-58.0, 48.9] x [-64.0, 86.0] x [-0.95, 48.0]` |
| **Variant 3 Bayonet** | 57.26s | 7,864 | 307 | 1,150 | **507** | 128 | `[-61.5, 61.3] x [-27.1, 63.3] x [0.0, 34.0]` |

#### Printability Defects:
1. **Submerged Geometry ($Z < 0$)**:
   - **Variant 1**: $Z_{\text{min}} = -30.06\text{ mm}$! In `mode="print_plate"`, line 181 rotates the 85 mm wedge around X at $Y=45, Z=12$, submerging 30 mm of the part beneath the build plate. This completely breaks standard slicing software.
   - **Variant 2**: $Z_{\text{min}} = -0.95\text{ mm}$! The retaining flange of `cam_pivot_pin()` dips below the build plate.
2. **Steep Overhangs & Unsupported Cantilevers**:
   - **Variant 1**: Pull handle loop is oriented as a horizontal hollow cylinder with 360° circular overhangs.
   - **Variant 2**: 
     - Transverse 8.5 mm axle hole through frame columns creates circular overhangs.
     - Palm press pad on cam lever floats 2.0 mm in mid-air with zero support.
     - Pivot pin is printed horizontally with retaining flanges, creating line contact with the bed and severe sag.
   - **Variant 3**:
     - The 3 radial locking lugs on `bayonet_base` ($d = 5.5\text{ mm}$, length $3.7\text{ mm}$) protrude horizontally into empty air at $Z = 13.0\text{ mm}$. They are 100% unsupported overhangs and will collapse during FDM printing.

---

### 3. Verification Harness (`verify_press_v2.py`) Failure

The test harness `verify_press_v2.py` gives a false sense of security:
- It tests that OpenSCAD runs without syntax errors.
- It tests that CSG files are written.
- It tests that preview PNGs are produced.
- **It NEVER evaluates physical clearance, NEVER checks part collisions, NEVER tests STL export on print plates, and NEVER verifies that $Z_{\text{min}} \ge 0$.**
- Because OpenSCAD syntax passes even when solids intersect by 6 mm, the harness reported 22/22 PASS while the designs are mechanically non-functional.

---

## Final Verdict & Recommendations

### Verdict: **REJECT**

### Required Action Items for CAD Developer (`worker_cad_1`):
1. **Variant 1 (Wedge)**:
   - Delete lines 49-53 in `press_v2_wedge.scad` (uncentered pocket blowout).
   - Fix stack-up: Increase sleeve slot height or reduce wedge thickness from $12.2\text{ mm}$ to $\le 8.2\text{ mm}$ at lock so the wedge can push the pad down to $Z = 24.6$ without colliding.
   - Deepen pad underside recess to 3.0 mm (matching tamper lid thickness).
   - In `mode="print_plate"`, translate wedge properly so $Z_{\text{min}} = 0.0$.
2. **Variant 2 (Cam)**:
   - Redesign frame column height and pivot position: Increase `PIVOT_Z` from 38.0 to $\ge 49.8\text{ mm}$ (or reduce cam radius from 12 mm to an appropriate micro-cam radius) to accommodate the tamper (3mm) + plunger (6.7mm) + cam lobe (15.5mm).
   - Orient pivot pin vertically on print plate.
   - Add support chamfer under palm press pad or orient lever flat on the arm surface.
3. **Variant 3 (Bayonet)**:
   - Correct `collar_z` kinematics in assembly to $Z = 8.0 \to 4.0\text{ mm}$.
   - Adjust collar thrust shoulder height so that at $Z = 4.0\text{ mm}$, the shoulder makes contact with the thrust plate at $Z = 32.4\text{ mm}$ (no 1.1 mm gap).
   - Add $45^\circ$ support chamfers beneath the 3 base locking lugs so they can print without supports.
