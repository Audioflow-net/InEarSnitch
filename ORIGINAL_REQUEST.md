# Original User Request

## Initial Request — 2026-09-22T08:07:27+02:00

Implement a "ProKit Tip-Tracking" feature for the PySide6 desktop app "InEar Snitch" — an IEM measurement tool that uses an IEC-711 reference coupler. The feature tracks which Ear Tip (coupler adapter) was used for each measurement, stores it in the database, displays it in history, and provides statistical analysis. The entire feature is hidden behind an offline SHA256 unlock-code system ("ProKit gate"). This is production code for a real audio measurement app with ~3950 lines in main.py.

Working directory: /Users/ben/Desktop/InEarSnitch
Integrity mode: development

**CRITICAL: Before any code change, run `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py`. If it fails → immediate `git checkout -- .`. No exceptions.**

**CRITICAL: Before starting work, read `/Users/ben/Desktop/InEarSnitch/HANDOFF_IN_EAR_SNITCH.md` and ALL files in `/Users/ben/Desktop/InEarSnitch/.agents/rules/` — they contain hard constraints.**

**CRITICAL: Git backup before every change: `git add -A && git commit -m "backup: vor [Feature]"`**

## Design Decisions (LOCKED — do not change)

These were decided by the user and verified by a DeepInvestigator feasibility analysis:

1. **Freitext is FORBIDDEN** — Tips are always from the `TipProfiles` catalog table. Freetext would break grouping for reproducibility scores.
2. **L and R ALWAYS separate** — All scores, badges, and analyses must be computed separately for `magnitude_l` and `magnitude_r`. Never combine into a single value.
3. **Legacy measurements (tip_id = NULL)** → automatically assigned to "Unbekannt" tip (id=1, always first seed entry). After migration: `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL`.
4. **Depth-Drift-Detection during sweep is IMPOSSIBLE** — A log-sine-sweep excites 8 kHz only for milliseconds at one exact time point. No drift tracking is physically possible from saved frequency response BLOBs. Do NOT implement this.
5. **Reproducibility Score must be band-limited to 20 Hz – 8 kHz** — Above 8 kHz, coupler resonances dominate and tiny insertion depth changes cause huge variance. A full-band score would always look terrible and mislead the user.
6. **Reproducibility Score requires ≥ 5 measurements** — Below that, return None / show "Not enough data". Below 10, show a warning that the score is preliminary.

## Requirements

### R1. Offline Unlock-Code System (config.py)

Add three functions to `config.py`: `is_prokit_unlocked()`, `unlock_prokit(code)`, `revoke_prokit()`. The system uses SHA256 hashes of codes in format `SNITCH-PROKIT-2024-001` through `-050`. The unlock state is persisted as a file `.prokit_unlocked` in `get_data_dir()`. No internet required.

The 50 SHA256 hashes to hardcode (from pre-generated codes):
```python
VALID_CODE_HASHES = {
    "1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2",
    "28c967ffdb947142ba96b211ac9b7a82d73e705ae4938b0048357842160ccca5",
    "467080d8304ae74587a8871d277301d6962350cc8d0adbdeacf164992306749e",
    "3340498b45cedd29a0f3e4bd16bc218e6642b2617966ac0bb992a4db2f643577",
    "752ec0de4e8783a1a9b6cea3727a875fce76fdc815c0188b53c42e090b6a6d49",
    "2d4daa3506a61e12f3e6bdcf812d381923313ce48c4c3261fe9eea85b48f8478",
    "fa19fa327ec49524a82509d8ece545cf599d41cbcedd120d94fa2fbe4ae67cf7",
    "2bd13e963d452a752e565da583a8e68055d2a98f106d1dd258a3ad795c177d0b",
    "9adb031d8be54cbf43003cc488add1f8f855e0dff40f6d4d02728107467c9bf7",
    "8329c956d34a3065c16c9fce051d318f48f59e3a168514ec118e784b2afd8aad",
    "bc688e2817772af9de241f6ccc18610c8ef7fb8804c27dd57ac360630dac498a",
    "a66191e82cd3095c357aaf3425269ca732e3f08e5fda033cc60a0af2a9b1cdf5",
    "766545bc887e483e9c41b204fbcf985763398ede9d7f731d6c17926cc094472c",
    "5903d43d01d796973d727dcf4914f654607428045aa0c4dddf44f8bc36ccc143",
    "25510b6e524bc19381508ebadde8a40e142dfd2db4f77b09170b92f87f724d2a",
    "0caec3efc96458f024248206516790cf9fd52aabb29cb4a5c9263d1bdaec0deb",
    "24bd2789b55de96bbf6a312680f6a1e282555eeb200b91b6d97d9290b548590c",
    "7d7f06121b54cdc34163f9c520f1a86d802c992580f515355a89a4e0bad75e42",
    "12fd82d9bfef2250bc8eca14a5578abf7db236a90fe779a495b4da8ad8bade28",
    "c433deca515974a48aa7d353482c57e5726e0f8830a0b5cd8401fc24ecef05bc",
    "f7180a263f1ca78f52bb304194a41d43ca9592591dfd9913f660a62c945b37e7",
    "ee7bd1d3904f1980bb93a778146265675321266cf12b34f213d111aa95b324e1",
    "7ea57abff314366f97a88d26cd1fe211432b463cc1b3bab5086e7c9d38a57584",
    "77f89e8a6ccad0efb0a93af8c55deba0b6bb8143e443c434086b5588a5d4c392",
    "02fdbd04dfa0b206c050030c0fde369c13b63826609b57629bc11eebc1b07953",
    "fb7bc08e304bc9f285deb479e7f2809f7878ed699571864663cd42a585712088",
    "5db52172b22bc0bb2839f3b6152db1ee40330259b061a97af317daef71f74cab",
    "c447ab57a79b5a0585c7fdea5bf960e6cad82504fc7d3779974c0ef6eff97cb8",
    "4f542e2e655cd4c549086585f1b35e4791a642dc48928b6678dbc61545daa06c",
    "9c5a61b5d71129cd60ad54432cf05bb51e197bcab379dfe3580298da4ac8405d",
    "b078f28b7df0f1309b46ff7f60f07dbf556de84e2f94d401f4cb76e735250ce1",
    "fe2fbfabd552d26935d42bab0363afea0fcf836e37cd5bf443fac45dcec2b301",
    "7ecb10814cce4353c5755321e58eaee1c7903517ec47ee1b7e885c74cbbb1eeb",
    "574ad449c2b3d44a819541c04f949b7da88726c88cdea706f3861c28c26eed75",
    "137648325202aa6877ef61d5a3676be21f6984d76825c228cd54cbeccbd1515a",
    "ee2cdd6fdac8c38e2407464045ae904bd3226744535961dfb62769f3644e5f2c",
    "144fb12c8c3153380ded932b955b1faf0eb630a0f92a5c9ad2b856ae128b7285",
    "b75abc7d948c7988501b6956ec5c73b2f3a7ba4331ff4625324056a12e8f827c",
    "f158ff3e0ffbb5cb70ec6ff3b5a9eeaf1c313aee6d74a0ad3c901db5becd96e0",
    "ff443743ef2e6039023ae4dc835a86a580287565c2d49f02734024cc9afee42b",
    "ad0e8d419b1647e5966034565f2494b646e4f1a36e1cbb807e9621ccf4249c7e",
    "4ed91365b766ec8fcd7a5cb4b34455255be226619a331b43062a78f704cb844b",
    "dbbb84b2101da22a25153e7fc97ceaa08592b28cfd32803c9068f85893633172",
    "07a30ae449aaec190e5307da93ddb1dc6d1c6c649e7f677e4f6be995f5a98a44",
    "8ca06be4b4c080a7343aafb358406adafe205581f7e4fd80680c78ef513ccba8",
    "3f43ab77a551d55e2d852c581d77fd1c6601ea961e747ced419027506a96d656",
    "49aff215aa8ed742bec2ebb5bdd7fe8d0b2ed4457e86f0be0c2c77209a3efe31",
    "f02975c34add7e5b646fda9731643b7af58216660cebf4d1e649f13d4f471e7b",
    "4d58450d5e89ab7d28ccd55a62d026034c8f1e10efa2b89347e1d2bd76237faa",
    "beb4fa70979bc164202352ec89574193cbdba08a5f2c6c5ff74088acd7600e7a",
}
```

### R2. Database Schema Migration (database.py)

Create `TipProfiles` table and add `tip_id` column to `Measurements`. Use the existing migration pattern (try/except `ALTER TABLE`). Seed data must insert "Unbekannt" FIRST (gets id=1), then "Kein Aufsatz", "Standard Foam", "ProKit V1", "ProKit V2". After migration, run `UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL` to assign all legacy measurements.

New methods needed: `get_all_tips()`, `get_last_used_tip(iem_id)` (must exclude id=1), `get_reproducibility_scores(iem_id, tip_id)` (20–8kHz only, L/R separate, returns None if < 5 measurements), `get_seal_history(iem_id, tip_id)` (40Hz vs 500Hz from BLOBs, L/R separate), `save_measurement()` extended with `tip_id` parameter (default=1).

### R3. Tip Selector UI in Bottom-Bar (main.py)

Add a tip ComboBox in the bottom bar near the RUN button. Only visible when `is_prokit_unlocked()` returns True. Must populate from `TipProfiles` catalog (no freetext). Must suggest last-used tip for current IEM when switching profiles. `save_trace_to_db()` must pass selected `tip_id` to `save_measurement()`.

Add unlock dialog accessible via triple-click on the app logo / title text — invisible to normal users.

### R4. Tip Badge in History Cards (history_ui.py)

Each `HistoryCardWidget` shows a small colored icon badge (using `icon_char` and `color_hex` from `TipProfiles`). The `load_history()` SQL must LEFT JOIN with `TipProfiles`. "Unbekannt" tips show a subtle grey "?" badge. L and R seal status from stored BLOBs shown separately if ProKit is unlocked.

### R5. Tip Analysis Card in Diagnostics (analysis_ui.py)

Add an optional analysis card in `render_diagnostics()` — only when ProKit is unlocked. Shows:
- Tip-specific 8kHz target value (extracted from stored frequency BLOB: find peak in 6–10 kHz range)
- Reproducibility score (std dev of magnitude, 20–8000 Hz only, L and R separate)
- Seal history trend (40Hz vs 500Hz delta over time, L and R separate)
- Minimum 5 measurements required; below 10 show "preliminary" warning

## Acceptance Criteria

### Smoke Test
- [ ] `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` passes (19/19) after ALL changes

### Unlock System
- [ ] `unlock_prokit("SNITCH-PROKIT-2024-001")` returns True and creates `.prokit_unlocked` file
- [ ] `unlock_prokit("WRONG-CODE")` returns False and creates no file
- [ ] `is_prokit_unlocked()` returns True after unlock, False after `revoke_prokit()`
- [ ] All ProKit UI elements are invisible when `is_prokit_unlocked()` returns False

### Database
- [ ] App starts without error on existing database (no tip_id column yet) — migration adds it
- [ ] "Unbekannt" is always id=1 in TipProfiles
- [ ] All pre-existing measurements have tip_id=1 after migration
- [ ] `save_measurement()` with tip_id parameter works and stores correctly

### UI
- [ ] Tip ComboBox appears in bottom bar only when unlocked
- [ ] Tip ComboBox is populated from TipProfiles catalog (no freetext input possible)
- [ ] Last-used tip is pre-selected when switching to an IEM that has previous measurements
- [ ] History cards show colored tip badge with correct icon
- [ ] Triple-click on app title opens unlock dialog

### Analysis
- [ ] Reproducibility score computed only for 20–8000 Hz range
- [ ] L and R scores are always separate — never combined
- [ ] Returns None / shows "Not enough data" when < 5 measurements for a tip
- [ ] Shows "preliminary" warning when 5–9 measurements

### No Regressions
- [ ] Existing UI elements (graphs, dropdowns, targets) are not broken
- [ ] `btn_toggle_tools` sidebar toggle still works
- [ ] Profile sidebar is not squeezed when switching tabs
- [ ] No new imports break on systems without ProKit data

## 2026-09-22T07:51:39Z

URGENT CORRECTION — Seed data in TipProfiles must use the REAL tip catalog, not generic placeholders.

The user has a visual catalog of actual designed tips at `/Users/ben/.gemini/antigravity/brain/dc2b2fbc-d180-476f-aea9-bae3683b5971/visual_catalog.html`. The current seed data ("ProKit V1", "ProKit V2", "Standard Foam") is WRONG.

Replace the seed data in `database.py` with these REAL tip models:

```python
default_tips = [
    # id=1 MUST be "Unbekannt" (legacy fallback) — DO NOT CHANGE
    ("Unbekannt", "Legacy-Messung ohne Tip-Information", "", "#444444", "?", 0),
    ("Kein Aufsatz", "Direkt ohne Tip gemessen", "", "#555555", "○", 0),
    ("V26 Straight", "Bester Allrounder — gerade 90°-Kante", "Silicone", "#22c55e", "▮", 1),
    ("V27 Rounded", "Komfort-Update — 2mm Abrundung an der Spitze", "Silicone", "#3b82f6", "▮", 0),
    ("V29-C Cone", "Konisch zulaufend — extremer Seal durch tiefes Einpressen", "Silicone", "#f97316", "◆", 0),
    ("V30-C Pro", "9mm Torus-Lippe, 4mm Loch — Stabilitäts-Upgrade", "Silicone", "#3b82f6", "◉", 0),
    ("V31-XL Panzer", "10mm Lippe, 6mm Loch — für fette Custom In-Ears", "Silicone", "#f97316", "◉", 0),
]
```

Notes:
- V28 Universal is EXCLUDED (verworfen/deprecated — "Choke-Tube Akustik" problem)
- V26 Straight is `is_default=1` (marked as "Bester Allrounder" in the catalog)
- All tips are Silicone material (these are silicone adapters with matching tamper/stamps)
- Each tip has a matching "Tamper" (stamp for the silicone mold) — not relevant for the DB but good context

Please update `database.py` seed data and re-run smoke tests. This is a data-only change, no structural modification needed.

## 2026-09-23T10:44:09Z

# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Entwurf und Implementierung von 3 neuen, hocheffizienten CAD-Varianten für ein Silikonform-Presssystem. Die neuen Designs müssen ein extrem schnelles Zusammenfügen/Spannen ermöglichen (bevor das Silikon aushärtet), Druck von allen Seiten aufbauen, praktikabel sein und Filament-Verschwendung minimieren. Die Agenten ermitteln selbstständig die drei mathematisch und praktisch besten Varianten.

Working directory: ~/Desktop/InEarSnitch/press_v2
Integrity mode: development

## Requirements

### R1. 3 Schnelle Press-Varianten
Entwicklung von 3 komplett unterschiedlichen mechanischen Gehäusen/Press-Konzepten (z.B. Klappe, Keil, Gewinde, etc.), die ein fast sofortiges Schließen und starken, gleichmäßigen Rundum-Druck ermöglichen.

### R2. Geometrische Integrität
Die exakten inneren Kavitäten (V27, V29, V30, V31) müssen mathematisch zu 100% unangetastet bleiben und aus dem alten Code (`MASTER_Silikon_Formen.scad`) importiert/übernommen werden. Lediglich der äußere Block und Schließmechanismus wird ersetzt.

### R3. Material-Effizienz
Das Design muss so kompakt wie möglich sein, um signifikant Filament und Druckzeit gegenüber dem bisherigen massiven Block zu sparen.

### R4. CLI Test-Umgebung
Da der `openscad` Befehl auf diesem Mac oft nicht direkt im `$PATH` liegt, muss das Team den absoluten Pfad zur App (z.B. `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD`) nutzen, um Test-Renders durchzuführen.

## Acceptance Criteria

### Verifikation & Testing
- [ ] Es existieren 3 separate OpenSCAD-Dateien im Ordner `press_v2`.
- [ ] Das Team hat per Kommandozeile erfolgreich verifiziert, dass alle 3 Varianten syntaktisch korrekt sind und sich ohne Fehler rendern lassen.
- [ ] Jede Variante umschließt die originalen Kavitäten, weist aber ein völlig neues, schnelleres äußeres Schließkonzept auf.
