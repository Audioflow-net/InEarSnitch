# Dispatch Log

## 2026-09-22T06:08:35Z
You are the Project Orchestrator for the InEarSnitch codebase.
Your working directory is: /Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1

Read the authoritative original user request at:
/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md

Workspace directory: /Users/ben/Desktop/InEarSnitch

CRITICAL REQUIREMENTS & CONSTRAINTS:
1. Start-Protokoll: If this is a new session reading user rules, ensure compliance (eisteepfirsich rule).
2. CRITICAL: Before any code change, run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`. If it fails → immediate `git checkout -- .`. No exceptions.
3. CRITICAL: Before starting work, read `/Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md` and ALL files in `/Users/ben/Desktop/InEarSnitch/.agents/rules/` — they contain hard constraints.
4. CRITICAL: Git backup before every change: `git add -A && git commit -m "backup: vor [Feature]"`
5. All design decisions locked in ORIGINAL_REQUEST.md (Freitext forbidden, L and R always separate, tip_id=1 for Unbekannt, Reproducibility Score band-limited to 20Hz-8kHz, ≥5 measurements required, etc.).
6. All 5 requirements (R1 config.py, R2 database.py, R3 main.py, R4 history_ui.py, R5 analysis_ui.py) and acceptance criteria.
7. Maintain your `BRIEFING.md` and `progress.md` in your working directory `/Users/ben/Desktop/InEarSnitch/.agents/orchestrator_1`.
8. When all requirements and acceptance criteria are implemented and verified via `smoke_test.py` and targeted tests, report completion back to the sentinel.
