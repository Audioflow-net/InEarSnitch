#!/usr/bin/env python3
"""
==============================================================================
InEarSnitch press_v2 - Adversarial Mathematical & Cavity Integrity Test Harness
==============================================================================
Empirical Challenger: challenger_cad_1

Rigorous verification of geometric identity between:
- MASTER_Silikon_Formen.scad (Legacy Single-Source-of-Truth)
- press_v2/shared_cavities.scad (Modular Core Library)
and parameter boundary stress testing of all press_v2 mechanisms.
==============================================================================
"""

import os
import sys
import struct
import subprocess
import tempfile
import time

OPENSCAD_BIN = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
WORKSPACE = "/Users/ben/Desktop/InEarSnitch"
PRESS_V2_DIR = os.path.join(WORKSPACE, "press_v2")
MASTER_SCAD = os.path.join(WORKSPACE, "MASTER_Silikon_Formen.scad")
SHARED_SCAD = os.path.join(PRESS_V2_DIR, "shared_cavities.scad")
WEDGE_SCAD = os.path.join(PRESS_V2_DIR, "press_v2_wedge.scad")
CAM_SCAD = os.path.join(PRESS_V2_DIR, "press_v2_cam.scad")
BAYONET_SCAD = os.path.join(PRESS_V2_DIR, "press_v2_bayonet.scad")


def run_cmd(cmd, timeout=120):
    t0 = time.time()
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dt = time.time() - t0
        return res.returncode, res.stdout, res.stderr, dt
    except subprocess.TimeoutExpired as e:
        return -1, "", f"TIMEOUT after {timeout}s: {e}", timeout


def parse_stl(filepath):
    """
    Parse STL (ASCII or binary) and return:
    (facet_count, volume_mm3, (min_x, min_y, min_z, max_x, max_y, max_z))
    """
    if not os.path.isfile(filepath):
        return 0, 0.0, None

    file_size = os.path.getsize(filepath)
    if file_size == 0:
        return 0, 0.0, None

    # Check if binary or ascii
    with open(filepath, "rb") as f:
        header = f.read(80)
        count_bytes = f.read(4)

    is_binary = False
    if len(count_bytes) == 4:
        expected_facets = struct.unpack("<I", count_bytes)[0]
        if file_size == 84 + expected_facets * 50:
            is_binary = True

    if is_binary:
        with open(filepath, "rb") as f:
            f.seek(84)
            facets = []
            min_v = [float("inf")] * 3
            max_v = [float("-inf")] * 3
            total_vol_6 = 0.0

            for _ in range(expected_facets):
                data = f.read(50)
                if len(data) < 50:
                    break
                floats = struct.unpack("<12fH", data)
                # floats[0:3] = normal, floats[3:6]=v1, floats[6:9]=v2, floats[9:12]=v3
                v1 = floats[3:6]
                v2 = floats[6:9]
                v3 = floats[9:12]

                for v in (v1, v2, v3):
                    for d in range(3):
                        if v[d] < min_v[d]:
                            min_v[d] = v[d]
                        if v[d] > max_v[d]:
                            max_v[d] = v[d]

                # Signed tetrahedron volume: v1 . (v2 x v3)
                # cross(v2, v3)
                cx = v2[1] * v3[2] - v2[2] * v3[1]
                cy = v2[2] * v3[0] - v2[0] * v3[2]
                cz = v2[0] * v3[1] - v2[1] * v3[0]
                dot = v1[0] * cx + v1[1] * cy + v1[2] * cz
                total_vol_6 += dot

            vol = abs(total_vol_6) / 6.0
            bbox = (*min_v, *max_v) if expected_facets > 0 else None
            return expected_facets, vol, bbox
    else:
        # ASCII STL
        facets_count = 0
        min_v = [float("inf")] * 3
        max_v = [float("-inf")] * 3
        total_vol_6 = 0.0
        current_vertices = []

        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("vertex"):
                    parts = line.split()
                    v = (float(parts[1]), float(parts[2]), float(parts[3]))
                    current_vertices.append(v)
                    for d in range(3):
                        if v[d] < min_v[d]:
                            min_v[d] = v[d]
                        if v[d] > max_v[d]:
                            max_v[d] = v[d]
                elif line.startswith("endfacet"):
                    if len(current_vertices) == 3:
                        facets_count += 1
                        v1, v2, v3 = current_vertices
                        cx = v2[1] * v3[2] - v2[2] * v3[1]
                        cy = v2[2] * v3[0] - v2[0] * v3[2]
                        cz = v2[0] * v3[1] - v2[1] * v3[0]
                        dot = v1[0] * cx + v1[1] * cy + v1[2] * cz
                        total_vol_6 += dot
                    current_vertices = []

        vol = abs(total_vol_6) / 6.0
        bbox = (*min_v, *max_v) if facets_count > 0 else None
        return facets_count, vol, bbox


def run_boolean_difference_test(test_id, name, orig_call, new_call, tmpdir):
    """
    Renders both difference(A, B) and difference(B, A) to STL via OpenSCAD CGAL.
    """
    # Wrapper SCAD that brings both in cleanly
    scad_content_fwd = f"""
$fn = 100;
mold_size = 34;
use <{MASTER_SCAD}>;
use <{SHARED_SCAD}>;

// Forward difference: Original MINUS New
difference() {{
    {orig_call};
    {new_call};
}}
"""
    scad_content_rev = f"""
$fn = 100;
mold_size = 34;
use <{MASTER_SCAD}>;
use <{SHARED_SCAD}>;

// Reverse difference: New MINUS Original
difference() {{
    {new_call};
    {orig_call};
}}
"""
    fwd_scad = os.path.join(tmpdir, f"{test_id}_fwd.scad")
    fwd_stl = os.path.join(tmpdir, f"{test_id}_fwd.stl")
    rev_scad = os.path.join(tmpdir, f"{test_id}_rev.scad")
    rev_stl = os.path.join(tmpdir, f"{test_id}_rev.stl")

    with open(fwd_scad, "w") as f:
        f.write(scad_content_fwd)
    with open(rev_scad, "w") as f:
        f.write(scad_content_rev)

    # Run Forward Render
    cmd_fwd = [OPENSCAD_BIN, fwd_scad, "-o", fwd_stl, "--export-format", "binstl"]
    rc_fwd, out_fwd, err_fwd, dt_fwd = run_cmd(cmd_fwd)
    facets_fwd, vol_fwd, bbox_fwd = parse_stl(fwd_stl)
    empty_fwd = (
        ("Current top level object is empty." in err_fwd)
        or ("No top level geometry to render" in err_fwd)
        or (facets_fwd == 0)
    )

    # Run Reverse Render
    cmd_rev = [OPENSCAD_BIN, rev_scad, "-o", rev_stl, "--export-format", "binstl"]
    rc_rev, out_rev, err_rev, dt_rev = run_cmd(cmd_rev)
    facets_rev, vol_rev, bbox_rev = parse_stl(rev_stl)
    empty_rev = (
        ("Current top level object is empty." in err_rev)
        or ("No top level geometry to render" in err_rev)
        or (facets_rev == 0)
    )

    fwd_clean = empty_fwd and (vol_fwd < 1e-4)
    rev_clean = empty_rev and (vol_rev < 1e-4)

    return {
        "test_id": test_id,
        "name": name,
        "fwd_clean": fwd_clean,
        "rev_clean": rev_clean,
        "fwd_facets": facets_fwd,
        "fwd_vol": vol_fwd,
        "fwd_bbox": bbox_fwd,
        "rev_facets": facets_rev,
        "rev_vol": vol_rev,
        "rev_bbox": bbox_rev,
        "dt": dt_fwd + dt_rev,
        "err_fwd": err_fwd.strip(),
        "err_rev": err_rev.strip(),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", type=str, default="all", choices=["1", "2", "3", "all"], help="Section to run (1, 2, 3, or all)")
    args = parser.parse_args()

    print("=" * 80)
    print(" InEarSnitch press_v2 - Adversarial Cavity & Mechanism Integrity Test")
    print(" Challenger: challenger_cad_1 (Empirical Challenger)")
    print("=" * 80)

    if not os.path.isfile(OPENSCAD_BIN):
        print(f"[CRITICAL FAIL] OpenSCAD binary not found at {OPENSCAD_BIN}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Working in sandbox: {tmpdir}\n")

        # ======================================================================
        # SECTION 1: CAVITY MATHEMATICAL FIDELITY (BOOLEAN DIFFERENCE)
        # ======================================================================
        if args.section in ("1", "all"):
            print("-" * 80)
            print("SECTION 1: BOOLEAN DIFFERENCE TESTS (CAVITIES & TAMPERS)")
            print("-" * 80)

        cavity_tests = [
            ("CAV-V27", "Cavity V27 Classic", "outer_cavity_v27()", 'cavity("V27")'),
            ("CAV-V29", "Cavity V29 Cone", "outer_cavity_v29()", 'cavity("V29")'),
            ("CAV-V30", "Cavity V30 Pro Cone", "outer_cavity_v30()", 'cavity("V30")'),
            ("CAV-V31", "Cavity V31 Panzer Cone", "outer_cavity_v31()", 'cavity("V31")'),
            ("TMP-V27-6", "Tamper V27 (hole=6.0)", "piston_v27(hole_size=6.0, label=\"V27-6\")", 'tamper("V27", hole_size=6.0, label="V27-6")'),
            ("TMP-V27-5", "Tamper V27 (hole=5.0)", "piston_v27(hole_size=5.0, label=\"V27-5\")", 'tamper("V27", hole_size=5.0, label="V27-5")'),
            ("TMP-V29", "Tamper V29 Cone", "piston_v29()", 'tamper("V29", hole_size=4.0, label="V29-C")'),
            ("TMP-V30-4", "Tamper V30 (hole=4.0)", "piston_v30(hole_size=4.0, label=\"V30-4\")", 'tamper("V30", hole_size=4.0, label="V30-4")'),
            ("TMP-V30-6", "Tamper V30 (hole=6.0)", "piston_v30(hole_size=6.0, label=\"V30-6\")", 'tamper("V30", hole_size=6.0, label="V30-6")'),
            ("TMP-V31-6", "Tamper V31 (hole=6.0)", "piston_v31(hole_size=6.0, label=\"V31-6\")", 'tamper("V31", hole_size=6.0, label="V31-6")'),
            ("TMP-V31-4", "Tamper V31 (hole=4.0)", "piston_v31(hole_size=4.0, label=\"V31-4\")", 'tamper("V31", hole_size=4.0, label="V31-4")'),
            ("MOLD-L-V27", "Mold Half Left V27", "form_left_v27()", 'mold_half_left("V27")'),
            ("MOLD-R-V27", "Mold Half Right V27", "form_right_v27()", 'mold_half_right("V27")'),
            ("MOLD-L-V31", "Mold Half Left V31", "form_left_v31()", 'mold_half_left("V31")'),
            ("MOLD-R-V31", "Mold Half Right V31", "form_right_v31()", 'mold_half_right("V31")'),
        ]

        diff_results = []
        for tid, tname, orig_c, new_c in cavity_tests:
            print(f"Running {tid:12} [{tname}] ...", end="", flush=True)
            res = run_boolean_difference_test(tid, tname, orig_c, new_c, tmpdir)
            diff_results.append(res)
            
            fwd_status = "0 DRIFT (EMPTY)" if res["fwd_clean"] else f"FAIL: {res['fwd_facets']} facets, vol={res['fwd_vol']:.4f}mm³"
            rev_status = "0 DRIFT (EMPTY)" if res["rev_clean"] else f"FAIL: {res['rev_facets']} facets, vol={res['rev_vol']:.4f}mm³"
            
            if res["fwd_clean"] and res["rev_clean"]:
                print(f" [PASS] ({res['dt']:.1f}s) - Forward: {fwd_status} | Reverse: {rev_status}")
            else:
                print(f" [DIFF] ({res['dt']:.1f}s)")
                print(f"    Orig - New: {fwd_status}")
                if res['fwd_bbox']:
                    print(f"      BBox: {res['fwd_bbox']}")
                print(f"    New - Orig: {rev_status}")
                if res['rev_bbox']:
                    print(f"      BBox: {res['rev_bbox']}")
                if res["err_fwd"]:
                    print(f"      Stderr Fwd: {res['err_fwd']}")
                if res["err_rev"]:
                    print(f"      Stderr Rev: {res['err_rev']}")

        # ======================================================================
        # SECTION 2: STRESS-TEST PARAMETER BOUNDARIES & INVALID INPUTS
        # ======================================================================
        if args.section in ("2", "all"):
            print("\n" + "-" * 80)
            print("SECTION 2: PARAMETER BOUNDARY & ASSERTION STRESS TESTING")
            print("-" * 80)

        stress_tests = [
            # shared_cavities.scad assertions
            {
                "id": "STRESS-SCAD-1",
                "desc": "shared_cavities cavity('V99') invalid version",
                "scad": f'use <{SHARED_SCAD}>;\ncavity("V99");',
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'V99'",
            },
            {
                "id": "STRESS-SCAD-2",
                "desc": "shared_cavities tamper('FOO') invalid version",
                "scad": f'use <{SHARED_SCAD}>;\ntamper("FOO");',
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'FOO'",
            },
            {
                "id": "STRESS-SCAD-3",
                "desc": "shared_cavities mold_half_left('UNKNOWN')",
                "scad": f'use <{SHARED_SCAD}>;\nmold_half_left("UNKNOWN");',
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'UNKNOWN'",
            },
            {
                "id": "STRESS-SCAD-4",
                "desc": "shared_cavities cavity('v27') lowercase auto-normalization",
                "scad": f'use <{SHARED_SCAD}>;\ncavity("v27");',
                "expect_error": False,
            },
            {
                "id": "STRESS-SCAD-5",
                "desc": "shared_cavities cavity(31) integer auto-normalization",
                "scad": f'use <{SHARED_SCAD}>;\ncavity(31);',
                "expect_error": False,
            },
            # press_v2_wedge.scad parameters
            {
                "id": "STRESS-WEDGE-1",
                "desc": "press_v2_wedge tip_version='INVALID' via CLI -D",
                "target_file": WEDGE_SCAD,
                "defines": {"tip_version": "INVALID"},
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'INVALID'",
            },
            {
                "id": "STRESS-WEDGE-2",
                "desc": "press_v2_wedge mode='print_plate' invalid mode handling",
                "scad": f'mode="nonexistent_mode";\ninclude <{WEDGE_SCAD}>;',
                "expect_error": False,  # check what it does
            },
            {
                "id": "STRESS-WEDGE-3",
                "desc": "press_v2_wedge extreme wedge_travel = -2.5 (over-retracted)",
                "target_file": WEDGE_SCAD,
                "defines": {"wedge_travel": -2.5},
                "expect_error": False,
            },
            {
                "id": "STRESS-WEDGE-4",
                "desc": "press_v2_wedge extreme tolerance = -1.0 (inverted geometry stress)",
                "target_file": WEDGE_SCAD,
                "defines": {"tolerance": -1.0},
                "expect_error": False,
            },
            # press_v2_cam.scad parameters
            {
                "id": "STRESS-CAM-1",
                "desc": "press_v2_cam tip_version='BAD_TIP' via CLI -D",
                "target_file": CAM_SCAD,
                "defines": {"tip_version": "BAD_TIP"},
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'BAD_TIP'",
            },
            {
                "id": "STRESS-CAM-2",
                "desc": "press_v2_cam cam_angle = 180 (full rotation beyond detent)",
                "target_file": CAM_SCAD,
                "defines": {"cam_angle": 180},
                "expect_error": False,
            },
            {
                "id": "STRESS-CAM-3",
                "desc": "press_v2_cam cam_angle = -45 (negative angle stress)",
                "target_file": CAM_SCAD,
                "defines": {"cam_angle": -45},
                "expect_error": False,
            },
            # press_v2_bayonet.scad parameters
            {
                "id": "STRESS-BAYO-1",
                "desc": "press_v2_bayonet tip_version='NON_EXISTENT' via CLI -D",
                "target_file": BAYONET_SCAD,
                "defines": {"tip_version": "NON_EXISTENT"},
                "expect_error": True,
                "expected_msg": "Invalid tip_version 'NON_EXISTENT'",
            },
            {
                "id": "STRESS-BAYO-2",
                "desc": "press_v2_bayonet twist_deg = 180 (over-twisted bayonet collar)",
                "target_file": BAYONET_SCAD,
                "defines": {"twist_deg": 180},
                "expect_error": False,
            },
            {
                "id": "STRESS-BAYO-3",
                "desc": "press_v2_bayonet twist_deg = -30 (reverse twist beyond stop)",
                "target_file": BAYONET_SCAD,
                "defines": {"twist_deg": -30},
                "expect_error": False,
            },
        ]

        stress_results = []
        for st in stress_tests:
            print(f"Running {st['id']:15} [{st['desc']}] ...", end="", flush=True)
            out_csg = os.path.join(tmpdir, f"{st['id']}.csg")
            
            if "target_file" in st:
                scad_path = st["target_file"]
            else:
                scad_path = os.path.join(tmpdir, f"{st['id']}.scad")
                with open(scad_path, "w") as f:
                    f.write(st["scad"])

            cmd = [OPENSCAD_BIN, scad_path, "-o", out_csg, "--check-parameters", "true"]
            if "defines" in st:
                for k, v in st["defines"].items():
                    if isinstance(v, str):
                        cmd.extend(["-D", f'{k}="{v}"'])
                    else:
                        cmd.extend(["-D", f'{k}={v}'])

            rc, out, err, dt = run_cmd(cmd)

            has_error = (rc != 0) or ("ERROR:" in err)
            expected_msg_found = False
            if st.get("expected_msg"):
                expected_msg_found = st["expected_msg"] in err

            if st["expect_error"]:
                if has_error and (expected_msg_found or not st.get("expected_msg")):
                    status = "PASS (CLEAN ASSERTION FAIL)"
                    passed = True
                else:
                    status = f"FAIL (Expected clean assertion, got rc={rc}, err={err.strip()})"
                    passed = False
            else:
                if not has_error:
                    status = "PASS (RENDERED CLEANLY)"
                    passed = True
                else:
                    status = f"FAIL (Unexpected error: {err.strip()})"
                    passed = False

            print(f" [{passed and 'PASS' or 'FAIL'}] ({dt:.1f}s) - {status}")
            stress_results.append({
                **st,
                "passed": passed,
                "rc": rc,
                "err": err.strip(),
                "dt": dt,
            })

        # ======================================================================
        # SECTION 3: FULL VARIANT RENDERS (PNG PREVIEW & STL PRINT_PLATE)
        # ======================================================================
        if args.section in ("3", "all"):
            print("\n" + "-" * 80)
            print("SECTION 3: FULL VARIANT RENDERS (PNG & STL EXPORT)")
            print("-" * 80)

        variant_renders = [
            ("RENDER-WEDGE-ASM", WEDGE_SCAD, "assembly", "V27", "png"),
            ("RENDER-WEDGE-PLT", WEDGE_SCAD, "print_plate", "V27", "stl"),
            ("RENDER-CAM-ASM", CAM_SCAD, "assembly", "V30", "png"),
            ("RENDER-CAM-PLT", CAM_SCAD, "print_plate", "V30", "stl"),
            ("RENDER-BAYO-ASM", BAYONET_SCAD, "assembly", "V31", "png"),
            ("RENDER-BAYO-PLT", BAYONET_SCAD, "print_plate", "V31", "stl"),
        ]

        render_results = []
        for rid, scad_f, mode, tip_v, out_ext in variant_renders:
            print(f"Running {rid:18} [{os.path.basename(scad_f)} mode={mode} tip={tip_v}] ...", end="", flush=True)
            out_file = os.path.join(tmpdir, f"{rid}.{out_ext}")
            cmd = [
                OPENSCAD_BIN,
                scad_f,
                "-o", out_file,
                "-D", f'mode="{mode}"',
                "-D", f'tip_version="{tip_v}"',
            ]
            if out_ext == "png":
                cmd.extend(["--preview", "--imgsize=800,600", "--autocenter", "--viewall"])

            rc, out, err, dt = run_cmd(cmd, timeout=90)
            file_ok = os.path.isfile(out_file) and os.path.getsize(out_file) > 0
            passed = (rc == 0) and file_ok and ("ERROR:" not in err)

            status = f"PASS (size={os.path.getsize(out_file):,}B, time={dt:.1f}s)" if passed else f"FAIL (rc={rc}, err={err.strip()})"
            print(f" [{passed and 'PASS' or 'FAIL'}] - {status}")
            render_results.append({
                "id": rid,
                "passed": passed,
                "size": os.path.getsize(out_file) if file_ok else 0,
                "dt": dt,
                "err": err.strip(),
            })

    print("\n" + "=" * 80)
    print(" ADVERSARIAL TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
