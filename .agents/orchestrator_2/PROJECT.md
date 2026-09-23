# Project: InEarSnitch press_v2

## Architecture
Modular OpenSCAD architecture for next-generation rapid-clamping silicone mold press system.
- Shared Core (`shared_cavities.scad`): Pure functional & modular geometric library containing mathematically identical cavities (V27, V29, V30, V31), mold blocks, alignment pins, and tampers with explicit `$fn=100` and zero top-level geometry or unscoped global variables.
- Variant 1 (`press_v2_wedge.scad`): Dual-action self-locking tapered wedge-collet system (~7.125° top wedge, 7.0° internal collet taper on X walls, simultaneous Z-axial and X-lateral compression, ~54 cm³ volume, ~73% material saving, ~2s closure). Single manifold body, 0.0 mm³ collision, flat print plate.
- Variant 2 (`press_v2_cam.scad`): Over-center toggle/eccentric cam lever system with dual-lobe Y-yoke, 56mm frame, 46mm pivot height, 3.5mm stroke, anti-skew guided plunger, and 92° detent lock (~62 cm³ volume, ~69% material saving, ~1.2s closure). Single manifold body, 0.0 mm³ collision, upright open rotation.
- Variant 3 (`press_v2_bayonet.scad`): Twist-lock conical bayonet with 60° 3-lug collar, 66mm OD, 14° internal conical collet directly clamping mold block corners at Z=20.1mm, 45° support chamfers, and decoupled non-rotating floating thrust plate (~39 cm³ volume, ~80% material saving, ~1.8s closure). Single manifold body, 0.0 mm³ collision.
- Test & Verification (`verify_press_v2.py`): Automated Python test harness driving `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD` for CSG AST validation, preview rendering, parameter checks, CGAL manifoldness (`Volumes: 2`), kinematic collision non-interference (0.0 mm³ volume), and bed bounding box ($Z_{\min} \ge 0.0000$ mm). 40/40 tests pass.
- Documentation (`CHANGELOG.md`): Full 5-field CAD Work Paper logging under [V36] and [V36.2].

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | Shared Cavity Library | Mathematically identical V27, V29, V30, V31 cavities & tampers extracted from `MASTER_Silikon_Formen.scad` with explicit `$fn` | M1 | R2 / Survey 1 | DONE (0 drift verified) |
| 2 | Self-Contained Block Geometry | Standalone mold half & tamper modules without global variable scope leaks (resolves `use <...>` bug) | M1 | R2 / Survey 1 & 3 | DONE |
| 3 | Variant 1: Dual-Action Wedge Press | Sliding wedge driving axial downforce and lateral split-line clamp simultaneously (<3s closure, 7° collet) | M2 | R1, R3 / Survey 2 | DONE (0.0mm³ collision) |
| 4 | Variant 2: Over-Center Cam Lever Press | Dual-lobe eccentric cam with anti-skew plunger and over-center lock (<1.5s closure, 3.5mm stroke) | M3 | R1, R3 / Survey 2 | DONE (0.0mm³ collision) |
| 5 | Variant 3: Conical Bayonet Twist Press | 60° twist collar with conical collet (all-round radial clamp) & decoupled non-rotating thrust plate | M4 | R1, R3 / Survey 2 | DONE (0.0mm³ collision) |
| 6 | Compact Material Efficiency | All 3 variants achieve 65%–80% volume reduction compared to legacy 158 cm³ block | M2, M3, M4 | R3 / Survey 1 & 2 | DONE (~39–62 cm³) |
| 7 | CLI Automated Verification Suite | Headless Python runner invoking OpenSCAD CLI to test syntax, CSG trees, manifoldness, and collisions | M5 | R4 / Survey 3 | DONE (40/40 pass) |
| 8 | CAD Work Paper Logging | Comprehensive 5-field documentation in `CHANGELOG.md` per `cad_work_paper.md` rule | M6 | Mandatory Rules / Survey 3 | DONE (V36 & V36.2) |

## Milestones
| # | Name | Scope | Dependencies | Status | Key Outputs |
|---|------|-------|-------------|--------|-------------|
| M1 | Shared Cavity Core Module | Create `press_v2/shared_cavities.scad` with V27, V29, V30, V31 & tampers | none | DONE | 100.000% mathematical fidelity, 0 drift |
| M2 | Variant 1: Wedge Clamp System | Implement `press_v2/press_v2_wedge.scad` | M1 | DONE | 7° collet taper, 0.0mm³ collision, single manifold |
| M3 | Variant 2: Cam Lever System | Implement `press_v2/press_v2_cam.scad` | M1 | DONE | 3.5mm stroke, 0.0mm³ collision, single manifold |
| M4 | Variant 3: Conical Bayonet System | Implement `press_v2/press_v2_bayonet.scad` | M1 | DONE | 66mm OD, 14° collet, 0.0mm³ collision, single manifold |
| M5 | E2E CLI Render Test Suite | Implement `press_v2/verify_press_v2.py` & run CLI renders via OpenSCAD binary | M2, M3, M4 | DONE | 40/40 tests pass in 367s |
| M6 | CAD Work Paper & Final Audit | Update `CHANGELOG.md` with complete 5-field entries & forensic audit gate | M5 | DONE | Forensic Audit: CLEAN |

## Code Layout
- `/Users/ben/Desktop/InEarSnitch/press_v2/shared_cavities.scad` — Isolated cavity & core geometry library
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad` — Variant 1 (Dual-Action Wedge Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_cam.scad` — Variant 2 (Over-Center Cam Lever Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad` — Variant 3 (Conical Bayonet Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py` — Automated verification & render test script (40/40 tests)
- `/Users/ben/Desktop/InEarSnitch/CHANGELOG.md` — CAD Work Paper log
