# Project: InEarSnitch press_v2

## Architecture
Modular OpenSCAD architecture for next-generation rapid-clamping silicone mold press system.
- Shared Core (`shared_cavities.scad`): Pure functional & modular geometric library containing mathematically identical cavities (V27, V29, V30, V31), mold blocks, alignment pins, and tampers with explicit `$fn=100` and zero top-level geometry or unscoped global variables.
- Variant 1 (`press_v2_wedge.scad`): Dual-action self-locking tapered wedge-collet system (~7° taper, simultaneous Z-axial and X-lateral compression, ~73% material saving, ~2s closure).
- Variant 2 (`press_v2_cam.scad`): Over-center toggle/eccentric cam lever system with dual-lobe Y-yoke, 3.5mm stroke, anti-skew guided plunger, and 92° detent lock (~69% material saving, ~1.2s closure).
- Variant 3 (`press_v2_bayonet.scad`): Twist-lock conical bayonet with 60° 3-lug collar, 14° internal conical collet for 100% radial Rundum-Druck, and decoupled non-rotating floating thrust plate (~80% material saving, ~1.8s closure).
- Test & Verification (`verify_press_v2.py`): Automated Python test harness driving `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD` for CSG AST validation, preview rendering, and CLI assertions.
- Documentation (`CHANGELOG.md`): Full 5-field CAD Work Paper logging.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Shared Cavity Library | Mathematically identical V27, V29, V30, V31 cavities & tampers extracted from `MASTER_Silikon_Formen.scad` with explicit `$fn` | M1 | R2 / Survey 1 |
| 2 | Self-Contained Block Geometry | Standalone mold half & tamper modules without global variable scope leaks (resolves `use <...>` bug) | M1 | R2 / Survey 1 & 3 |
| 3 | Variant 1: Dual-Action Wedge Press | Sliding wedge driving axial downforce and lateral split-line clamp simultaneously (<3s closure) | M2 | R1, R3 / Survey 2 |
| 4 | Variant 2: Over-Center Cam Lever Press | Dual-lobe eccentric cam with anti-skew plunger and over-center lock (<1.5s closure) | M3 | R1, R3 / Survey 2 |
| 5 | Variant 3: Conical Bayonet Twist Press | 60° twist collar with conical collet (all-round radial clamp) & decoupled non-rotating thrust plate | M4 | R1, R3 / Survey 2 |
| 6 | Compact Material Efficiency | All 3 variants achieve 65%–80% volume reduction compared to legacy 158 cm³ block | M2, M3, M4 | R3 / Survey 1 & 2 |
| 7 | CLI Automated Verification Suite | Headless Python runner invoking OpenSCAD CLI to test syntax, CSG trees, and preview renders | M5 | R4 / Survey 3 |
| 8 | CAD Work Paper Logging | Comprehensive 5-field documentation in `CHANGELOG.md` per `cad_work_paper.md` rule | M6 | Mandatory Rules / Survey 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Shared Cavity Core Module | Create `press_v2/shared_cavities.scad` with V27, V29, V30, V31 & tampers | none | PLANNED |
| M2 | Variant 1: Wedge Clamp System | Implement `press_v2/press_v2_wedge.scad` | M1 | PLANNED |
| M3 | Variant 2: Cam Lever System | Implement `press_v2/press_v2_cam.scad` | M1 | PLANNED |
| M4 | Variant 3: Conical Bayonet System | Implement `press_v2/press_v2_bayonet.scad` | M1 | PLANNED |
| M5 | E2E CLI Render Test Suite | Implement `press_v2/verify_press_v2.py` & run CLI renders via OpenSCAD binary | M2, M3, M4 | PLANNED |
| M6 | CAD Work Paper & Final Audit | Update `CHANGELOG.md` with complete 5-field entries & forensic audit gate | M5 | PLANNED |

## Interface Contracts
### `shared_cavities.scad`
- Function signatures:
  - `function mold_size() = 34.0;`
  - `function mold_height() = 22.1;`
  - `function piston_lid_d() = 33.8;`
  - `function shaft_d() = 13.0;`
  - `function flange_d() = 20.0;`
- Module signatures:
  - `module cavity(tip_version="V27")` (supports "V27", "V29", "V30", "V31")
  - `module tamper(tip_version="V27")`
  - `module mold_half_left(tip_version="V27")`
  - `module mold_half_right(tip_version="V27")`
  - `module mold_assembled(tip_version="V27")`
- Error handling:
  - `assert(tip_version=="V27" || tip_version=="V29" || tip_version=="V30" || tip_version=="V31", "Invalid tip_version");`

### Variant Modules (`press_v2_wedge.scad`, `press_v2_cam.scad`, `press_v2_bayonet.scad`)
- Standard caller import: `use <shared_cavities.scad>;`
- Common parameter interface:
  - `tip_version = "V27";`
  - `mode = "assembly";` (options: "assembly", "print_plate", "sleeve", "clamp", "piston")
  - `tolerance = 0.25;`
- Render contract:
  - When opened in OpenSCAD GUI or `--preview`, display colored assembled mechanism.
  - When mode set to printable components or exported via CLI `-D mode="print_plate"`, render flat support-free printable parts.

## Code Layout
- `/Users/ben/Desktop/InEarSnitch/press_v2/shared_cavities.scad` — Isolated cavity & core geometry library
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_wedge.scad` — Variant 1 (Dual-Action Wedge Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_cam.scad` — Variant 2 (Over-Center Cam Lever Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/press_v2_bayonet.scad` — Variant 3 (Conical Bayonet Press)
- `/Users/ben/Desktop/InEarSnitch/press_v2/verify_press_v2.py` — Automated verification & render test script
- `/Users/ben/Desktop/InEarSnitch/CHANGELOG.md` — CAD Work Paper log
