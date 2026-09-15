#!/usr/bin/env python3
"""
InEar Snitch - Smoke Test
Run this AFTER every code change to catch regressions.
Usage: python3 smoke_test.py
"""
import sys
import ast
import os

FAIL = 0
PASS = 0

def check(name, condition, detail=""):
    global FAIL, PASS
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name} — {detail}")
        FAIL += 1

def main():
    global FAIL, PASS
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n🔍 SMOKE TEST — InEar Snitch\n")
    
    # ---- 1. SYNTAX CHECK ----
    print("1️⃣  Syntax Check")
    for f in ["main.py", "analysis_ui.py", "audio_engine.py", "analysis.py"]:
        if os.path.exists(f):
            try:
                ast.parse(open(f).read())
                check(f"Syntax: {f}", True)
            except SyntaxError as e:
                check(f"Syntax: {f}", False, str(e))
        else:
            check(f"Exists: {f}", False, "FILE MISSING")
    
    # ---- 2. CRITICAL IMPORTS ----
    print("\n2️⃣  Critical Imports")
    try:
        main_src = open("main.py").read()
        ana_src = open("analysis_ui.py").read()
        check("main.py imports PySide6", "from PySide6" in main_src)
        check("analysis_ui.py imports pyqtgraph", "import pyqtgraph" in ana_src)
    except Exception:
        pass
    
    # ---- 3. CRITICAL WIDGET REFERENCES ----
    print("\n3️⃣  Critical Widget References (main.py)")
    critical_widgets = [
        "self.btn_capture", "self.btn_trace", "self.btn_save_db", 
        "self.btn_rta_raw", "self.btn_iec_guide", "self.cb_meas_target",
        "self.cb_meas_history", "self.plot_widget", "self.page_ana"
    ]
    for w in critical_widgets:
        assign_pattern = f"{w} ="
        check(f"Widget: {w}", assign_pattern in main_src, "NOT FOUND — widget deleted or renamed!")
    
    # ---- 4. DATA FLOW & ANTI-REGRESSION ----
    print("\n4️⃣  Data Flow & Anti-Regression")
    check("temp_mag_l used", "self.temp_mag_l" in main_src, "Missing temp_mag_l")
    check("target_freqs used", "self.target_freqs" in main_src, "Missing target_freqs")
    check("EQ knob anti-wrap", "_last_dial_val" in ana_src, "Knob wrap fix removed!")
    check("Card click transparency", "WA_TransparentForMouseEvents" in main_src, "Card click fix removed!")
    
    # ---- SUMMARY ----
    total = PASS + FAIL
    print(f"\n{'='*50}")
    if FAIL == 0:
        print(f"✅ ALL {total} CHECKS PASSED")
    else:
        print(f"❌ {FAIL}/{total} CHECKS FAILED")
    print(f"{'='*50}\n")
    
    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())

    # ---- 5. CHANNEL MAPPING ----
    print("\n5️⃣  Channel Mapping Guard")
    check("get_current_channel maps L->Left", 
          'if txt in ("L", "Left"): return "Left"' in main_src or 
          'return "Left"' in main_src.split("get_current_channel")[1].split("def ")[0],
          "get_current_channel might return 'L' instead of 'Left'!")
