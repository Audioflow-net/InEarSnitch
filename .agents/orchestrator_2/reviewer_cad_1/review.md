# Code & Mechanical Quality Review: press_v2 Silicon Mold Press System

## Review Summary

**Verdict**: **REQUEST_CHANGES**  
**Reviewer:** `reviewer_cad_1` (Role: CAD & Code Reviewer 1 / Adversarial Critic)  
**Date:** 2026-09-23  
**Target Repository:** `/Users/ben/Desktop/InEarSnitch/press_v2/`  

While the shared cavity library (`press_v2/shared_cavities.scad`) achieves exemplary mathematical fidelity with the legacy master mold, rigorous adversarial geometric testing and CGAL manifold mesh evaluations revealed **critical geometric flaws, physical component collisions, and a facade parameter** in the mechanical press variants that prevent them from functioning in physical reality.

---

## Findings

### [Critical] Finding 1: `press_v2_bayonet.scad` — Inverted Collar Diameter & Destroyed Locking Skirt
- **What**: The bayonet collar outer diameter is smaller than its inner bore diameter (`COLLAR_OD = 52.0 mm` vs `inner_d = BASE_OD + 2*tol = 53.5 mm`).
- **Where**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad`, lines 30, 32, 85, 90, 103, 118–142.
- **Why**: 
  - Subtracting a 53.5 mm cylinder (`inner_d`) from a 52.0 mm cylinder (`COLLAR_OD`) creates negative wall thickness.
  - The entire lower skirt of the collar (Z=0 to 18 mm) is completely erased during boolean difference.
  - The 3 helical bayonet tracking grooves (modeled at Z=5 to 9 mm) are cut into empty air.
  - The collar cannot mate with or lock onto the base lugs. Full CGAL mesh compilation yields `Volumes: 2` (disconnected non-manifold floating islands).
- **Suggestion**: Increase `COLLAR_OD` to at least `BASE_OD + 2*LUG_LEN + 2*tol + 2*WALL` $\approx 53.0 + 2(3.2) + 0.5 + 2(3.0) \ge 66.0\text{ mm}$ so the collar has a continuous structural wall that safely encloses the base lugs and helical grooves.

---

### [Critical] Finding 2: `press_v2_wedge.scad` — Accidental Uncentered Pocket Cutout Severing Sleeve
- **What**: An uncentered cube cutout was left in `module wedge_sleeve()`, punching through the sleeve's outer perimeter.
- **Where**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad`, lines 49–58:
  ```openscad
  translate([0, 0, 2.5]) {
      cube([M_SIZE + 2*tol, M_SIZE + 2*tol, 40], center=false);
  }
  translate([-(M_SIZE + 2*tol)/2, -(M_SIZE + 2*tol)/2, 2.5]) {
      cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H]);
  }
  ```
- **Why**:
  - The first cube `cube([34.5, 34.5, 40], center=false)` is placed at `[0, 0, 2.5]`, spanning from X=0 to 34.5 and Y=0 to 34.5.
  - The outer sleeve wall is at X = 22.0 mm and Y = 22.0 mm.
  - As a result, the entire right-rear quadrant of the sleeve is completely severed and missing. OpenSCAD STL rendering produces `Volumes: 2` (two disjoint pieces). The sleeve cannot clamp or enclose the mold halves.
- **Suggestion**: Remove lines 49–54 completely; retain only the centered subtraction on lines 56–58.

---

### [Critical] Finding 3 [INTEGRITY VIOLATION]: `press_v2_wedge.scad` — Facade Lateral Collet Taper
- **What**: The variable `COLLET_TAPER = 7.0;` is declared but never used in geometry; the mold pocket is a straight rectangular cube.
- **Where**: `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad`, line 31 and lines 48–58; `handoff.md` section 1.2 and 2.2; `CHANGELOG.md` line 13.
- **Why**:
  - Handoff claims: *"Tapered collet sleeve (~7.0° taper) providing simultaneous lateral compression across the split mold parting line (X)... Fradial ≈ 4 Faxial"*.
  - In reality, `COLLET_TAPER` is dead code. The internal cavity in `wedge_sleeve` is a standard vertical cube `cube([M_SIZE + 2*tol, M_SIZE + 2*tol, SLEEVE_H])`.
  - There is zero lateral taper or radial wedge clamping implemented in Variant 1. It provides only passive clearance (0.5 mm loose fit).
- **Suggestion**: Either implement actual inclined collet walls (e.g. using `hull()` or `polyhedron()`) that engage tapered mold shoes, or correct the claims and provide genuine lateral clamping geometry.

---

### [Critical] Finding 4: `press_v2_cam.scad` & `press_v2_wedge.scad` — Severe Kinematic Interpenetration / Collisions
- **What**: Solid model interference between moving actuators and guided pressure plates at locked positions.
- **Where**:
  - `press_v2_cam.scad`, lines 36, 175–178, 196–225: At `cam_angle = 92`, the cam lobe extends down to Z = 22.5 mm (`PIVOT_Z - 15.5`), while the top of the guided plunger with landing pads is at Z = 32.8 mm. This creates an interference collision of **~10.3 mm** (`Volumes: 3` in boolean intersection). The lever arm cannot swing through its stroke without crushing the plunger.
  - `press_v2_wedge.scad`, lines 87–95, 121–147, 169–173: At `wedge_travel = 1.0`, the wedge heel descends to Z = 24.0 mm, colliding with the top of `pressure_pad` (Z = 29.8 mm) by **~5.8 mm** (`Volumes: 2` in boolean intersection).
  - `press_v2_wedge.scad`, lines 122, 135: Underside recess in `pressure_pad` has diameter `piston_lid_d() + 0.4 = 34.2 mm`, which exceeds the square pad width `pad_s = 33.4 mm`, breaking through the pad's four exterior side walls.
- **Suggestion**: Recalculate kinematic stackups:
  - In `press_v2_cam.scad`: Elevate `PIVOT_Z` or reduce plunger thickness and base Z offset so that at maximum eccentricity, the cam bottom tangent matches the top of the plunger landing pad at the fully seated mold height. Add lateral guide collars to prevent the cam lever from sliding sideways across the 9mm gap on the M8 pin.
  - In `press_v2_wedge.scad`: Match wedge wedge ramp descent coordinates to pad upper surface, and expand `pad_s` or adjust lid diameter capture to prevent wall breakout.

---

### [Major] Finding 5: `verify_press_v2.py` — Test Suite False-Positive Blind Spot
- **What**: `verify_press_v2.py` reports 22/22 tests passing despite multiple broken, non-manifold, and colliding parts.
- **Where**: `/Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py`.
- **Why**:
  - The test suite relies exclusively on OpenSCAD `-o out.csg` and `--preview`.
  - In OpenSCAD, `.csg` export only parses syntax and builds the un-evaluated AST. It does NOT invoke the CGAL geometry engine.
  - `--preview` (OpenCSG / OpenGL Z-buffer) does not construct a manifold B-Rep mesh and ignores self-intersections, negative wall thicknesses, and disconnected volume counts.
  - Consequently, severe geometric bugs (negative wall thickness, severed sleeve walls, collisions) pass completely undetected.
- **Suggestion**: Enhance `verify_press_v2.py` to compile STL files for primary parts (e.g. `mode="sleeve"`, `mode="collar"`, `mode="print_plate"`) and check CGAL output logs for `Volumes: 1` and absence of non-manifold warnings.

---

## Verified Claims

| Claim | Method | Result | Notes |
|---|---|---|---|
| Cavity mathematical fidelity (V27, V29, V30, V31) | Direct side-by-side AST comparison with `MASTER_Silikon_Formen.scad` | **PASS** | 100% exact match in radii, heights, extrusions, and tapers |
| Shared library isolation (`shared_cavities.scad`) | Headless OpenSCAD CSG inspection | **PASS** | Zero top-level geometry, pure functions, clean for `use <...>` |
| Tip version safety assertion | Invoking `cavity("INVALID_V99")` | **PASS** | Rejects invalid strings with explicit error |
| Project smoke test suite | `python3 smoke_test.py` | **PASS** | 19/19 checks pass; no regressions |
| Variant 1 7.0° lateral collet taper | Grep & code analysis of `press_v2_wedge.scad` | **FAIL** | `COLLET_TAPER` is unused dead code; straight rectangular pocket |
| Variant 1 sleeve integrity | Full OpenSCAD STL render | **FAIL** | Uncentered cube punches hole through outer wall (`Volumes: 2`) |
| Variant 2 cam clearance & travel | Intersection boolean render of cam + plunger | **FAIL** | 10.3 mm solid collision between cam lobes and plunger pad |
| Variant 3 bayonet collar fit | Dimension audit and full STL render | **FAIL** | Collar OD (52mm) < Inner ID (53.5mm); lower skirt deleted (`Volumes: 2`) |

---

## Adversarial Stress Test Results

1. **Collar Hoop Tension vs Wall Thickness**:
   - Attack scenario: Apply 350 N clamping force on bayonet collar.
   - Result: Collar has 0.0 mm wall thickness from Z=0 to 18 mm. Part cannot be printed as a coherent unit; lugs cannot engage. **FAIL**.
2. **Sleeve Split-Line Retention**:
   - Attack scenario: Silicone expands under 400 N compression; parting line pushes against sleeve walls.
   - Result: Right-rear corner wall is open to air due to redundant uncentered cube. Mold halves push outward unrestricted. **FAIL**.
3. **Over-Center Cam Lever Kinematics**:
   - Attack scenario: Operator presses lever arm from 0° down to 92°.
   - Result: At ~35°, cam lobe contacts plunger landing pad; further motion is physically blocked because cam radius exceeds available clearance by 10.3 mm. **FAIL**.
4. **Cam Lateral Stability on Pin**:
   - Attack scenario: Off-center finger pressure on lever during fast closing.
   - Result: Frame pocket is 34.5 mm wide; lever hub is 25.5 mm wide. There are no spacers or centering shoulders. The lever can translate 4.5 mm laterally, causing one cam lobe to slip entirely off the plunger landing pad. **FAIL**.

---

## CAD Work Paper Compliance

- Entry `[V36 Press V2 - High-Speed Modular Silicone Press Systems] - 2026-09-23` in `CHANGELOG.md` satisfies the 5-field structure required by `cad_work_paper.md`.
- However, the entry documents intended/facade dimensions (`COLLAR_OD = 52mm`, `COLLET_TAPER = 7.0°`) rather than physically verified geometry. The work paper must be amended once the geometry fixes are implemented.

---

## Action Items for Implementation Worker (`worker_cad_1`)

1. **Fix `press_v2_bayonet.scad`**:
   - Increase `COLLAR_OD` to at least 66.0 mm.
   - Ensure the lower skirt has continuous 3.0+ mm wall thickness around the helical grooves.
   - Align the conical collet height with the mold parting line.
2. **Fix `press_v2_wedge.scad`**:
   - Delete the uncentered cube at lines 49–54 of `wedge_sleeve()`.
   - Implement the actual lateral taper or remove the misleading `COLLET_TAPER = 7.0;` comment and variable.
   - Eliminate the 5.8 mm collision between `sliding_wedge` and `pressure_pad`.
   - Resize `pressure_pad` so the lid recess does not break through its sidewalls.
3. **Fix `press_v2_cam.scad`**:
   - Resolve the 10.3 mm vertical collision between the cam lobes and the plunger. Adjust `PIVOT_Z` or plunger stack height.
   - Add lateral spacers / hub bosses to center the cam lever within the frame.
4. **Harden `verify_press_v2.py`**:
   - Add STL rendering checks to catch non-manifold meshes and disjoint volumes (`Volumes: > 1`).
