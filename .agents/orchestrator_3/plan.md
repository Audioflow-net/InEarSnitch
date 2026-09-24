# Audit Plan: InEar Snitch Final Pre-Release Audit

## Overview
Perform a deep, non-modifying audit of the InEar Snitch application codebase according to the requirements in ORIGINAL_REQUEST.md (2026-09-24T15:34:28Z).

## Requirements & Scope
- **R1: Deep QA (Logic & Math)**
  - Scope: `audio_engine.py`, `eq_math.py` (and related audio/math workers/threads).
  - Targets: `NoneType` dereferences, division by zero, unhandled exceptions in background threads, NaN/Inf propagations, edge cases (empty arrays, silent audio, buffer underruns/overruns).
- **R2: UI Completeness Check**
  - Scope: `main.py`, `analysis_ui.py`.
  - Targets: Every `QPushButton`, `QComboBox`, `QAction`, menu item, and interactive widget. Ensure every signal is connected to a functional handler, no dead links, no `NotImplementedError`, no no-op stubs that fail silently or produce unhandled exceptions.
- **R3: Legal & Safety Audit**
  - Scope: Entire UI and audio pipeline (`main.py`, `analysis_ui.py`, `audio_engine.py`, etc.).
  - Targets: Health & safety disclaimers for hearing protection, particularly high-SPL (+15dB) "Stress Test", sine sweep output warnings, confirmation modals before high volume playback.

## Deliverables
- Comprehensive audit report in Markdown format at `/Users/ben/Desktop/InEarSnitch/AUDIT_REPORT.md` (and copied/mirrored in orchestrator working directory).
- Each finding must list:
  1. Category / Requirement (R1, R2, or R3)
  2. Severity (Critical, High, Medium, Low)
  3. File path and exact line number(s)
  4. Code snippet
  5. Detailed explanation of vulnerability/defect
  6. Potential impact
- CRITICAL CONSTRAINT: Zero source code changes. Strictly observation and reporting.

## Phases
1. **Phase 1: Decomposition & Parallel Exploration**
   - Dispatch Explorer 1: Target R1 (`audio_engine.py`, `eq_math.py`).
   - Dispatch Explorer 2: Target R2 (`main.py`, `analysis_ui.py`).
   - Dispatch Explorer 3: Target R3 (Legal & Safety, Stress Test +15dB, sine sweeps across all files).
2. **Phase 2: Review & Cross-Verification**
   - Dispatch Reviewer / Auditor to independently verify and challenge line numbers, edge cases, and ensure no false positives.
3. **Phase 3: Synthesis & Report Generation**
   - Collate all verified findings into `/Users/ben/Desktop/InEarSnitch/AUDIT_REPORT.md`.
   - Update state files and report completion to parent.
