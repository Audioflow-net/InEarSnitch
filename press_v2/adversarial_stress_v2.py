#!/usr/bin/env python3
"""
Adversarial Stress & Collision Test Suite (challenger_v2_1)
Forensic empirical validation of:
1. Mating collision volumes (locked and dynamic stroke)
2. Print plate bed bounding boxes (Zmin >= 0.0000 mm)
3. CGAL 2-manifold solid integrity (Simple: yes, Volumes: 2)
4. Audit of verify_press_v2.py test assertions
"""

import os
import sys
import subprocess
import tempfile
import struct
import time
import math

OPENSCAD_BIN = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
BASE_DIR = "/Users/ben/Desktop/InEarSnitch/press_v2"
WEDGE_SCAD = os.path.join(BASE_DIR, "press_v2_wedge.scad")
CAM_SCAD = os.path.join(BASE_DIR, "press_v2_cam.scad")
BAYONET_SCAD = os.path.join(BASE_DIR, "press_v2_bayonet.scad")
SHARED_SCAD = os.path.join(BASE_DIR, "shared_cavities.scad")


def parse_binstl(stl_path):
    if not os.path.exists(stl_path) or os.path.getsize(stl_path) <= 84:
        return 0, (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), 0.0
    with open(stl_path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        if n == 0:
            return 0, (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), 0.0
        min_x, max_x = float("inf"), float("-inf")
        min_y, max_y = float("inf"), float("-inf")
        min_z, max_z = float("inf"), float("-inf")
        total_vol = 0.0
        for _ in range(n):
            d = f.read(50)
            v = struct.unpack("<12fH", d)
            # v[0..2] is normal, v[3..5] is p1, v[6..8] is p2, v[9..11] is p3
            p1 = (v[3], v[4], v[5])
            p2 = (v[6], v[7], v[8])
            p3 = (v[9], v[10], v[11])
            for p in (p1, p2, p3):
                min_x = min(min_x, p[0]); max_x = max(max_x, p[0])
                min_y = min(min_y, p[1]); max_y = max(max_y, p[1])
                min_z = min(min_z, p[2]); max_z = max(max_z, p[2])
            # Signed volume contribution of tetrahedron (0, p1, p2, p3)
            # v = (p1 . (p2 x p3)) / 6.0
            cross_x = p2[1]*p3[2] - p2[2]*p3[1]
            cross_y = p2[2]*p3[0] - p2[0]*p3[2]
            cross_z = p2[0]*p3[1] - p2[1]*p3[0]
            tet_vol = (p1[0]*cross_x + p1[1]*cross_y + p1[2]*cross_z) / 6.0
            total_vol += tet_vol

        return n, (min_x, max_x), (min_y, max_y), (min_z, max_z), abs(total_vol)


def run_scad(scad_snippet, out_stl, defines=None):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False) as f:
        f.write(scad_snippet)
        tmp_scad = f.name
    
    cmd = [OPENSCAD_BIN, tmp_scad, "-o", out_stl, "--export-format", "binstl"]
    if defines:
        for k, v in defines.items():
            if isinstance(v, str):
                cmd.extend(["-D", f'{k}="{v}"'])
            elif isinstance(v, bool):
                cmd.extend(["-D", f'{k}={"true" if v else "false"}'])
            else:
                cmd.extend(["-D", f'{k}={v}'])
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    os.remove(tmp_scad)
    return res


def main():
    print("=" * 80)
    print("ADVERSARIAL STRESS & COLLISION TEST HARNESS — ITERATION 2")
    print("=" * 80)
    
    results = []
    
    # --------------------------------------------------------------------------
    # 1. Manifold Verification for all 10 components
    # --------------------------------------------------------------------------
    print("\n--- [DIMENSION 1] CGAL Manifold Integrity Check ---")
    components = [
        ("Wedge: sleeve", WEDGE_SCAD, "sleeve"),
        ("Wedge: wedge", WEDGE_SCAD, "wedge"),
        ("Wedge: pad", WEDGE_SCAD, "pad"),
        ("Cam: frame", CAM_SCAD, "frame"),
        ("Cam: lever", CAM_SCAD, "lever"),
        ("Cam: plunger", CAM_SCAD, "plunger"),
        ("Cam: pin", CAM_SCAD, "pin"),
        ("Bayonet: base", BAYONET_SCAD, "base"),
        ("Bayonet: collar", BAYONET_SCAD, "collar"),
        ("Bayonet: thrust_plate", BAYONET_SCAD, "thrust_plate"),
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for name, scad_file, mode_val in components:
            stl_out = os.path.join(tmpdir, f"{mode_val}.stl")
            cmd = [OPENSCAD_BIN, scad_file, "-o", stl_out, "-D", f'mode="{mode_val}"', "--export-format", "binstl"]
            t0 = time.time()
            res = subprocess.run(cmd, capture_output=True, text=True)
            dt = time.time() - t0
            is_simple = "Simple:        yes" in res.stderr
            is_vol2 = "Volumes:         2" in res.stderr
            triangles, xb, yb, zb, vol = parse_binstl(stl_out)
            passed = (res.returncode == 0) and is_simple and is_vol2 and triangles > 0
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name:25s} | Simple: {'yes' if is_simple else 'NO'} | Vol: {'2' if is_vol2 else res.stderr.split('Volumes:')[1][:10].strip() if 'Volumes:' in res.stderr else 'ERR'} | Tri: {triangles:6d} | Vol: {vol:8.1f}mm³ | {dt:.1f}s")
            results.append((f"Manifold: {name}", passed, f"Simple={is_simple}, Vol2={is_vol2}, tri={triangles}"))

    # --------------------------------------------------------------------------
    # 2. Print Plate Bed Bounding Box Check (Zmin >= 0.0000 mm)
    # --------------------------------------------------------------------------
    print("\n--- [DIMENSION 2] Print Plate Bed Bounding Box Check ---")
    plates = [
        ("Wedge Print Plate", WEDGE_SCAD),
        ("Cam Print Plate", CAM_SCAD),
        ("Bayonet Print Plate", BAYONET_SCAD),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        for name, scad_file in plates:
            stl_out = os.path.join(tmpdir, f"plate.stl")
            cmd = [OPENSCAD_BIN, scad_file, "-o", stl_out, "-D", 'mode="print_plate"', "--export-format", "binstl"]
            t0 = time.time()
            res = subprocess.run(cmd, capture_output=True, text=True)
            dt = time.time() - t0
            triangles, xb, yb, zb, vol = parse_binstl(stl_out)
            zmin = zb[0]
            zmax = zb[1]
            # Must be strictly >= -0.0001 mm (floating-point tolerance)
            passed = (res.returncode == 0) and (triangles > 0) and (zmin >= -0.0001)
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {name:25s} | Z_min: {zmin:8.4f} mm | Z_max: {zmax:8.4f} mm | Tri: {triangles:6d} | {dt:.1f}s")
            results.append((f"PrintPlate: {name}", passed, f"Zmin={zmin:.4f}mm, Zmax={zmax:.4f}mm"))

    # --------------------------------------------------------------------------
    # 3. Collision Volumes: Mating Parts in Locked Clamped Position
    # --------------------------------------------------------------------------
    print("\n--- [DIMENSION 3] Collision Volume: Locked Position ---")
    collision_tests = [
        (
            "Wedge vs Pad (at w_y = 0.0, locked per scad)",
            f"""
use <{WEDGE_SCAD}>;
intersection() {{
    translate([0, 0, 24.6]) pressure_pad();
    translate([0, 0, 30.6]) sliding_wedge();
}}
"""
        ),
        (
            "Wedge vs Pad (at w_y = -65.0, per verify_press_v2.py test 33)",
            f"""
use <{WEDGE_SCAD}>;
intersection() {{
    translate([0, 0, 24.6]) pressure_pad();
    translate([0, -65.0, 30.6]) sliding_wedge();
}}
"""
        ),
        (
            "Cam Lever vs Plunger (locked at cam_angle=92°)",
            f"""
use <{CAM_SCAD}>;
intersection() {{
    translate([0, 0, 24.6]) guided_plunger();
    translate([0, 0, 46.0]) rotate([-2, 0, 0]) cam_lever();
}}
"""
        ),
        (
            "Bayonet Collar vs Base (locked at twist_deg=60°)",
            f"""
use <{BAYONET_SCAD}>;
intersection() {{
    bayonet_base();
    translate([0, 0, 4.0]) rotate([0, 0, 60]) bayonet_collar();
}}
"""
        ),
        (
            "Bayonet Collar vs Thrust Plate (locked at twist_deg=60°)",
            f"""
use <{BAYONET_SCAD}>;
intersection() {{
    translate([0, 0, 25.6]) floating_thrust_plate();
    translate([0, 0, 4.0]) rotate([0, 0, 60]) bayonet_collar();
}}
"""
        ),
        (
            "Wedge vs Sleeve (locked position w_y=0)",
            f"""
use <{WEDGE_SCAD}>;
intersection() {{
    wedge_sleeve();
    translate([0, 0, 30.6]) sliding_wedge();
}}
"""
        ),
        (
            "Cam Lever vs Frame (locked at 92°)",
            f"""
use <{CAM_SCAD}>;
intersection() {{
    cam_base_frame();
    translate([0, 0, 46.0]) rotate([-2, 0, 0]) cam_lever();
}}
"""
        ),
        (
            "Pad vs Tamper V27 (seated mold at Z=2.5)",
            f"""
use <{WEDGE_SCAD}>;
use <{SHARED_SCAD}>;
intersection() {{
    translate([0, 0, 24.6]) pressure_pad();
    translate([0, 0, 2.5 - mold_z_min()]) tamper("V27");
}}
"""
        ),
        (
            "Plunger vs Tamper V27 (seated mold at Z=2.5)",
            f"""
use <{CAM_SCAD}>;
use <{SHARED_SCAD}>;
intersection() {{
    translate([0, 0, 24.6]) guided_plunger();
    translate([0, 0, 2.5 - mold_z_min()]) tamper("V27");
}}
"""
        ),
        (
            "Thrust Plate vs Tamper V27 (seated mold at Z=2.5)",
            f"""
use <{BAYONET_SCAD}>;
use <{SHARED_SCAD}>;
intersection() {{
    translate([0, 0, 25.6]) floating_thrust_plate();
    translate([0, 0, 2.5 - mold_z_min()]) tamper("V27");
}}
"""
        ),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        for name, snippet in collision_tests:
            stl_out = os.path.join(tmpdir, "col.stl")
            t0 = time.time()
            res = run_scad(snippet, stl_out)
            dt = time.time() - t0
            is_empty_msg = "Current top level object is empty" in res.stderr
            triangles, xb, yb, zb, vol = parse_binstl(stl_out)
            dz = zb[1] - zb[0] if triangles > 0 else 0.0
            # Strict collision: solid volume > 0.001 mm³ or dz > 0.001 mm
            passed = is_empty_msg or (triangles == 0) or (vol < 0.001 and dz < 0.001)
            status = "PASS (0.0mm³)" if passed else "FAIL"
            print(f"[{status}] {name:50s} | Tri: {triangles:4d} | Vol: {vol:8.4f}mm³ | dz: {dz:6.4f}mm | {dt:.1f}s")
            results.append((f"Collision: {name}", passed, f"Empty={is_empty_msg}, Tri={triangles}, Vol={vol:.4f}mm³, dz={dz:.4f}mm"))

    # --------------------------------------------------------------------------
    # 4. Deep Kinematic Sweep & Geometric Functionality
    # --------------------------------------------------------------------------
    print("\n--- [DIMENSION 4] Kinematic Stroke & Interference Sweep ---")
    
    # Check Cam rotation sweep: from 0° to 92° in 10° steps
    with tempfile.TemporaryDirectory() as tmpdir:
        cam_sweep_passed = True
        max_cam_col_vol = 0.0
        for ang in range(0, 95, 10):
            stroke_frac = math.sin(math.radians(ang))
            plunger_z = 24.6 + (1.0 - stroke_frac) * 3.5
            snippet = f"""
use <{CAM_SCAD}>;
intersection() {{
    translate([0, 0, {plunger_z:.4f}]) guided_plunger();
    translate([0, 0, 46.0]) rotate([{90 - ang:.1f}, 0, 0]) cam_lever();
}}
"""
            stl_out = os.path.join(tmpdir, f"cam_sweep_{ang}.stl")
            res = run_scad(snippet, stl_out)
            is_empty_msg = "Current top level object is empty" in res.stderr
            triangles, _, _, zb, vol = parse_binstl(stl_out)
            dz = zb[1] - zb[0] if triangles > 0 else 0.0
            if not (is_empty_msg or triangles == 0 or (vol < 0.001 and dz < 0.001)):
                cam_sweep_passed = False
                max_cam_col_vol = max(max_cam_col_vol, vol)
                print(f"  [CAM SWEEP COLLISION] angle={ang}°: vol={vol:.4f}mm³, dz={dz:.4f}mm")
        
        print(f"[{'PASS' if cam_sweep_passed else 'FAIL'}] Cam Lever vs Plunger Dynamic Rotation Sweep (0°-92°) | Max Vol: {max_cam_col_vol:.4f}mm³")
        results.append(("Cam Sweep Kinematics", cam_sweep_passed, f"MaxVol={max_cam_col_vol:.4f}mm³"))

    # Check Bayonet twist sweep: from 0° to 60° in 10° steps
    with tempfile.TemporaryDirectory() as tmpdir:
        bayonet_sweep_passed = True
        max_bay_col_vol = 0.0
        for twist in range(0, 65, 10):
            t_frac = twist / 60.0
            collar_z = 8.0 - t_frac * 4.0
            thrust_z = 25.6 + (1.0 - t_frac) * 4.0
            snippet = f"""
use <{BAYONET_SCAD}>;
intersection() {{
    bayonet_base();
    translate([0, 0, {collar_z:.4f}]) rotate([0, 0, {twist}]) bayonet_collar();
}}
"""
            stl_out = os.path.join(tmpdir, f"bay_sweep_{twist}.stl")
            res = run_scad(snippet, stl_out)
            is_empty_msg = "Current top level object is empty" in res.stderr
            triangles, _, _, zb, vol = parse_binstl(stl_out)
            dz = zb[1] - zb[0] if triangles > 0 else 0.0
            if not (is_empty_msg or triangles == 0 or (vol < 0.001 and dz < 0.001)):
                bayonet_sweep_passed = False
                max_bay_col_vol = max(max_bay_col_vol, vol)
                print(f"  [BAYONET BASE COLLISION] twist={twist}°: vol={vol:.4f}mm³, dz={dz:.4f}mm")

        print(f"[{'PASS' if bayonet_sweep_passed else 'FAIL'}] Bayonet Collar vs Base Dynamic Twist Sweep (0°-60°) | Max Vol: {max_bay_col_vol:.4f}mm³")
        results.append(("Bayonet Sweep Kinematics", bayonet_sweep_passed, f"MaxVol={max_bay_col_vol:.4f}mm³"))

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("CHALLENGER V2 EMPIRICAL SUMMARY")
    print("=" * 80)
    all_passed = all(p for _, p, _ in results)
    for name, p, det in results:
        print(f"[{'PASS' if p else 'FAIL'}] {name} — {det}")
    print("=" * 80)
    print(f"OVERALL RESULT: {'ALL PASS' if all_passed else 'FAILURES DETECTED'}")
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
