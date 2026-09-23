# Handoff Report: Independent Review of press_v2

**Agent:** `reviewer_cad_1`  
**Role:** CAD & Code Reviewer 1 / Adversarial Critic  
**Date:** 2026-09-23  
**Working Directory:** `/Users/ben/Desktop/InEarSnitch/.agents/orchestrator_2/reviewer_cad_1`  
**Verdict:** **REQUEST_CHANGES**  

---

## 1. Observation

1. **`press_v2_bayonet.scad` Inverted Diameter**:
   - Lines 30 & 32: `COLLAR_OD = 52.0;` and `BASE_OD = 53.0;`
   - Line 85: `inner_d = BASE_OD + 2*tol;` (evaluates to $53.0 + 2(0.25) = 53.5\text{ mm}$).
   - Line 103: `translate([0, 0, -1]) cylinder(d=inner_d, h=18.0, $fn=80);`
   - Rendering `bayonet_collar` to STL via `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad -D 'mode="collar"' -o /tmp/collar_test.stl` produced:
     ```
     CGAL Polyhedrons in cache: 8
     Total rendering time: 0:00:42.078
        Top level object is a 3D object:
        Simple: yes
        Volumes: 2
     ```
   - Inspection of `/tmp/collar_test.png` shows the entire lower collar skirt (Z=0 to 18 mm) is subtracted away because $53.5\text{ mm} > 52.0\text{ mm}$. The helical tracking grooves (Z=5 to 9 mm) are cut into empty space.

2. **`press_v2_wedge.scad` Severed Corner Wall**:
   - Lines 49–58:
     ```openscad
     translate([0, 0, 2.5]) {
         cube([M_SIZE + 2*tol, M_SIZE + 2*tol, 40], center=false);
     }
     translate([-(M_SIZE + 2*tol)/2, -(M_SIZE + 2*tol)/2, 2.5]) {
         cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H]);
     }
     ```
   - Rendering `mode="sleeve"` to STL via `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad -D 'mode="sleeve"' -o /tmp/sleeve_test.stl` produced:
     ```
     CGAL Polyhedrons in cache: 4
     Total rendering time: 0:00:04.620
        Top level object is a 3D object:
        Simple: yes
        Volumes: 2
     ```
   - Inspection of `/tmp/sleeve_test.png` reveals that the uncentered cube at `[0, 0, 2.5]` cuts through the positive XY quadrant, completely blowing open the outer perimeter wall and leaving the sleeve in two disjoint pieces.

3. **`press_v2_wedge.scad` Facade Collet Taper**:
   - Line 31 defines `COLLET_TAPER = 7.0;`.
   - Ripgrep query for `COLLET_TAPER` across `press_v2_wedge.scad` returned exactly 1 match (line 31 itself). It is never referenced or used in any geometric module.
   - The pocket is a vertical rectangular prism with straight $90^\circ$ walls (`cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H])`).

4. **Kinematic Interference & Collisions**:
   - In `press_v2_cam.scad`: At `cam_angle = 92`, the bottom of the cam lobe descends to $Z = 38.0 - 15.5 = 22.5\text{ mm}$. The top of the guided plunger with landing pads is at $Z = 24.6 + 7.0 + 1.2 = 32.8\text{ mm}$. Running an intersection boolean between `guided_plunger()` and `cam_lever()` in OpenSCAD produced:
     ```
     CGAL Polyhedrons in cache: 10
     Total rendering time: 0:00:21.518
        Top level object is a 3D object:
        Simple: yes
        Volumes: 3
     ```
     representing a ~10.3 mm solid collision.
   - In `press_v2_wedge.scad`: Running an intersection between `pressure_pad()` and `sliding_wedge()` at `wedge_travel = 1.0` produced `Volumes: 2`, indicating a ~5.8 mm interpenetration collision.

5. **`shared_cavities.scad` Exact Fidelity**:
   - Compared modules `outer_cavity_v27()`, `outer_cavity_v29()`, `outer_cavity_v30()`, `outer_cavity_v31()`, and tampers with lines 27–270 of `MASTER_Silikon_Formen.scad`. All radial, axial, and extrusion parameters match verbatim.
   - CSG AST check confirms zero top-level geometry.
   - Negative assertion test `cavity("INVALID_V99")` halts compilation with assertion error.

6. **Smoke Test & CLI Suite**:
   - `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` passes 19/19 checks.
   - `python3 /Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py` passes 22/22 tests in 7.31s because it tests only `.csg` syntax AST and `--preview` OpenGL buffers without running CGAL manifold volume evaluations.

---

## 2. Logic Chain

1. **Failure of Variant 3 (Bayonet)**:
   - Observation 1 demonstrates that `COLLAR_OD` (52.0 mm) is smaller than `inner_d` (53.5 mm).
   - In boolean CSG geometry, subtracting a larger concentric cylinder from a smaller one destroys the entire wall volume over the height of subtraction.
   - Therefore, the lower skirt of the collar does not exist physically (confirmed by `Volumes: 2` in CGAL), meaning the bayonet tracking grooves have no material and the collar cannot engage the base lugs.

2. **Failure of Variant 1 (Wedge)**:
   - Observation 2 demonstrates that an uncentered subtraction was left in `wedge_sleeve()`.
   - Because the sleeve wall thickness is 5 mm, subtracting a 34.5 mm cube from the origin pierces straight through the outer wall.
   - Therefore, the sleeve is structurally broken into two pieces (confirmed by `Volumes: 2`), failing Requirement R1 (starken Rundum-Druck) and printability.
   - Observation 3 shows that the claimed 7.0° lateral collet taper is dead code, constituting a facade implementation.
   - Observation 4 proves the wedge collides with the pressure pad by 5.8 mm.

3. **Failure of Variant 2 (Cam)**:
   - Observation 4 demonstrates that the cam lever cannot physically rotate into its locked position because it collides with the plunger by 10.3 mm (confirmed by `Volumes: 3` in intersection).
   - Furthermore, the lever has 9.0 mm of unrestricted lateral sliding play on the pivot pin, risking lobe derailment off the plunger landing pads.

4. **Conclusion on Test Suite**:
   - Observation 6 proves that `verify_press_v2.py` suffers from a false-positive blind spot because OpenSCAD `.csg` and `--preview` exports do not check manifold topology.

---

## 3. Caveats

- **No Caveats.** All source files, master reference geometry, CSG syntax trees, and 3D CGAL manifold evaluations were comprehensively tested and verified using the official OpenSCAD binary.

---

## 4. Conclusion

The deliverables cannot be approved in their current state.  
**Verdict: REQUEST_CHANGES.**  
The shared core library (`shared_cavities.scad`) is excellent and mathematically pristine. However, `press_v2_wedge.scad`, `press_v2_cam.scad`, and `press_v2_bayonet.scad` suffer from critical geometric defects, physical collisions, non-manifold broken meshes, and a facade parameter that must be rectified before the parts can be 3D printed or deployed.

---

## 5. Verification Method

To independently reproduce all findings and verify the invalidation:

1. **Verify Broken Bayonet Skirt (`Volumes: 2`)**:
   ```bash
   /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad -D 'mode="collar"' -o /tmp/collar_test.stl
   ```
   *Expected output:* CGAL outputs `Volumes: 2`. Inspection of `/tmp/collar_test.png` shows missing lower skirt.

2. **Verify Severed Wedge Sleeve Wall (`Volumes: 2`)**:
   ```bash
   /Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad -D 'mode="sleeve"' -o /tmp/sleeve_test.stl
   ```
   *Expected output:* CGAL outputs `Volumes: 2`. Inspection of `/tmp/sleeve_test.png` shows severed right-rear quadrant.

3. **Verify Cam Kinematic Collision (`Volumes: 3`)**:
   ```bash
   python3 -c '
   import subprocess
   with open("/tmp/test_cam_collision.scad", "w") as f:
       f.write("""
   use </Users/ben/Desktop/InEarSnitch/press_v2/press_v2_cam.scad>;
   intersection() {
       translate([0, 0, 24.6]) guided_plunger();
       translate([0, 0, 38.0]) rotate([-(90 - 92), 0, 0]) cam_lever();
   }
   """)
   res = subprocess.run(["/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD", "/tmp/test_cam_collision.scad", "-o", "/tmp/cam_col.stl"], capture_output=True, text=True)
   print(res.stderr)
   '
   ```
   *Expected output:* Output includes `Volumes: 3` (non-empty intersection indicating 10.3 mm collision).

4. **Verify Dead Code `COLLET_TAPER`**:
   ```bash
   grep -n "COLLET_TAPER" /Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad
   ```
   *Expected output:* Only line 31 appears.
