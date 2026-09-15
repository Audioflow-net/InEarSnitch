# InEar Snitch - Ultimate Agent Handoff & Project Brain Dump

> [!CAUTION]
> **JEDER NEUE AGENT MUSS DIESES DOKUMENT VOLLSTÄNDIG LESEN, BEVOR ER AUCH NUR EINE ZEILE CODE ÄNDERT!**
> Wer das nicht tut, wird mit 100% Wahrscheinlichkeit etwas kaputt machen.

> [!WARNING]
> **UPDATE (15.09.2026): KRITISCHE AUDIO-ENGINE MIGRATION**
> 1. `measure()` in `audio_engine.py` wurde von `sd.playrec()` auf `sd.Stream()` umgebaut (Commit `f17c4b4`).
> 2. `preflight_check()` nutzt ebenfalls `sd.Stream()` (seit dem WASAPI-Fix).
> 3. `_run_level_calibration()` in `main.py` nutzt ebenfalls `sd.Stream()`.
> 4. **ES DARF NIRGENDS MEHR `sd.playrec()` VERWENDET WERDEN!** Es verursacht auf macOS mit separaten In/Out-Devices einen Electrical Loopback.
> 5. L/R Button Regression wurde gefixt: `get_current_channel()` mapped jetzt "L"→"Left", "R"→"Right" (Commit `5572de7`).

---

## 1. Projektübersicht
- **Projektname:** **InEar Snitch**
- **Pfad:** `/Users/ben/Desktop/InEarSnitch` (KEIN Bindestrich, KEIN Leerzeichen!)
- **Datenbank:** `inearsnitch.db`
- **Ziel:** Professionelle Desktop-App (PySide6) zur Messung, Diagnose und Katalogisierung von In-Ear-Monitoren (IEMs) via IEC-711 Referenz-Kuppler.
- **Zielgruppe:** Bands, Tontechniker, Musiker.
- **Plattformen:** macOS (primär), Windows (sekundär)

---

## 2. Architektur & Wichtige Dokumente

- **Software-Architektur & Klassen:** [`DEVELOPER_CATALOG.md`](./DEVELOPER_CATALOG.md)
- **Hardware-Teile & 3D-Druck:** [`HARDWARE_BOM.md`](./HARDWARE_BOM.md)
- **Lizenzen & Rechtliches:** [`NOTICES.txt`](./NOTICES.txt)
- **Hardware-Constraints (3D-Druck):** [`HARDWARE_CONSTRAINTS.md`](./HARDWARE_CONSTRAINTS.md)

---

## 3. ANTI-REGRESSION SYSTEM (PFLICHT!)

### Smoke-Test
Es existiert ein `smoke_test.py` im Projektroot. **Jeder Agent MUSS diesen VOR und NACH jeder Code-Änderung ausführen:**
```bash
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```
Der Test prüft:
- Syntax aller .py Dateien
- Kritische Imports (PySide6, pyqtgraph)
- Existenz aller UI-Widgets (btn_capture, plot_widget, page_ana, etc.)
- Datenfluss-Integrität (temp_mag_l, target_freqs, EQ-Knob Anti-Wrap)
- Channel-Mapping Guard (get_current_channel muss "Left"/"Right" zurückgeben)

**Wenn der Smoke-Test fehlschlägt → SOFORT `git checkout -- .` und von vorne!**

### Bekannte Regressions-Muster
Frühere Agenten haben folgende Fehler verursacht:
1. **L/R Button Text:** Buttons von "Left"/"Right" zu "L"/"R" umbenannt → `get_current_channel()` gab "L" statt "Left" zurück → App maß immer nur rechts.
2. **sqlite3 Import gelöscht:** Agent entfernte `import sqlite3` aus `profile_ui.py` → Profil-Auswahl crashte.
3. **Signal-Connections gelöscht:** Agent entfernte `.connect()` Aufrufe beim UI-Refactoring.
4. **sd.playrec() Error-Handler gebrochen:** Blanker try/except statt spezifischer Error-Codes → macOS Loopback.

---

## 4. Audio-Engine Architektur (KRITISCH!)

### sd.Stream() ÜBERALL (KEIN sd.playrec()!)

| Funktion | Datei | Methode | Status |
|----------|-------|---------|--------|
| RTA (Pink Noise Live) | `main.py` L537 | `LiveSealWorker` → `sd.Stream()` | ✅ |
| Sweep-Messung | `audio_engine.py` L212 | `measure()` → `sd.Stream()` | ✅ (Fix 15.09) |
| Preflight-Check | `audio_engine.py` L93 | `preflight_check()` → `sd.Stream()` | ✅ |
| Level-Kalibrierung | `main.py` L2173 | `_run_level_calibration()` → `sd.Stream()` | ✅ |

**WARUM?** `sd.playrec()` erzeugt auf macOS bei separaten Input/Output-Devices (z.B. MacBook Kopfhörerausgang + USB-Mic) ein Aggregate Device, das den Output direkt zum Input routet (Electrical Loopback). `sd.Stream()` mit Callback funktioniert korrekt mit separaten Devices auf ALLEN Plattformen.

### Das sd.Stream() Callback-Pattern:
```python
def run_stream(in_channels):
    out_pos = [0]
    in_pos = [0]
    rec_buf = np.zeros((n_frames, in_channels))
    done_event = threading.Event()

    def callback(indata, outdata, frames, time_info, status):
        chunk = min(frames, n_frames - out_pos[0])
        if chunk > 0:
            outdata[:chunk] = stimulus[out_pos[0]:out_pos[0]+chunk]
            out_pos[0] += chunk
        if chunk < frames:
            outdata[chunk:] = 0.0
        r_chunk = min(frames, n_frames - in_pos[0])
        if r_chunk > 0:
            rec_buf[in_pos[0]:in_pos[0]+r_chunk] = indata[:r_chunk, :]
            in_pos[0] += r_chunk
        if out_pos[0] >= n_frames and in_pos[0] >= n_frames:
            done_event.set()
            raise sd.CallbackStop

    with sd.Stream(device=(in_idx, out_idx),
                   samplerate=sr, channels=(in_channels, 2),
                   callback=callback):
        done_event.wait(timeout=duration + 2.0)
    return rec_buf[:, 0]

# Immer mit Fallback für Windows WASAPI:
try:
    rec = run_stream(1)
except sd.PortAudioError:
    in_chans = sd.query_devices(in_idx)['max_input_channels']
    rec = run_stream(in_chans)
```

### Windows WASAPI Kompatibilität
- Windows crasht HART (Segfault ohne Fehlermeldung) wenn Input und Output unterschiedliche Sample-Rates haben.
- Vor jeder Messung: `sys.platform == "win32"` → Sample-Rates vergleichen → User-Warnung wenn ungleich.
- Der `channels=1` Aufruf schlägt auf manchen Windows-WASAPI-Interfaces fehl → Fallback auf `max_input_channels`.

### User-Setup (macOS)
Der User (Ben) misst mit:
- **Output:** MacBook Built-in Kopfhörerausgang → IEM im Kuppler
- **Input:** Separates USB-Interface → Messmikrofon im IEC711 Kuppler
- **Das ist ein valides Setup!** Separate Devices funktionieren mit `sd.Stream()`.

---

## 5. Akustische & DSP Core-Regeln

1. **Sweep Amplitude = -20 dBFS (0.1):** IEM im geschlossenen Kuppler erzeugt >120 dB SPL. Bei 0 dBFS clippt der ADC.
2. **OS Audio-Enhancements MÜSSEN aus sein:** macOS "Voice Isolation", Hardware-AGC zerstören Messungen.
3. **Phasen-Ausrichtung:** IR wird via `np.roll` auf Peak (t=0) zentriert.
4. **Preflight-Drift-Toleranz:** 6 dB (von 4 dB hochgesetzt, da Noise-Varianz bei niedrigen Pegeln).
5. **HF-Padding:** `measure()` fügt 0.5s Silence ans Ende des Sweeps an, damit HF-Frequenzen das Mic noch erreichen (USB-Latenz).
6. **Pro-Audio Terminologie:**
   - **"Level"** = Ausgangslautstärke (Output zum IEM)
   - **"Gain"** = Vorverstärkung am Mic-Input
   - **NIEMALS verwechseln in UI-Texten!**

---

## 6. UI-Architektur

### Haupt-Tabs (workspace_stacked)
- Index 0: **Profile** (`page_prof`, `profile_ui.py`)
- Index 1: **Workspace** (Legacy-Plot + Controls)
- Index 2: **Analysis** (`page_ana`, `analysis_ui.py`) – FR, THD, CSD Graphen + Diagnostics
- Index 3: **History** (`page_hist`, `history_ui.py`)

### Wichtige UI-Elemente (NICHT LÖSCHEN/UMBENENNEN!)
- `self.btn_l`, `self.btn_r` – L/R Channel Buttons (Text "L"/"R", aber `get_current_channel()` gibt "Left"/"Right" zurück!)
- `self.btn_capture` / `self.btn_rta_raw` / `self.btn_iec_guide` – Bottom Bar
- `self.cb_smooth` – Smoothing Dropdown
- `self.cb_meas_target` / `self.cb_meas_history` – Target/History Dropdowns
- `self.page_ana` – AnalysisWidget Instanz
- `self.plot_widget` – Legacy PyQtGraph Workspace Plot
- `self.profile_cards` – Liste aller MusicianCard Widgets
- `self.btn_grp_chan` – QButtonGroup für L/R

### Theme System
- `theme.py` verwaltet Dark/Light Mode
- Neue UI-Elemente MÜSSEN `theme.get_color()` und `theme.is_light()` nutzen
- KEINE hardcodierten Farben!

---

## 7. Bekannte offene Bugs / TODOs

### Audio & DSP
- [ ] **Smoothing Dropdown:** `cb_smooth.currentIndexChanged` ist mit `redraw_graph()` verbunden, sollte aber `update_analysis_view()` aufrufen
- [ ] **CSD Waterfall:** 50 Slices mit solidem Fill sehen aus wie ein roter Block. Reduzieren auf ~16 Slices, semi-transparenter Fill

### UI
- [ ] **Crosshair/Cursor:** Snapping InfiniteLine + TextItem auf Freq Response Graph fehlt
- [ ] **UX Error Messages:** Technische Fehlermeldungen müssen in laienverständliche Texte umgeschrieben werden

### Distribution
- [ ] **macOS .app Bundle:** PyInstaller Build funktioniert, aber Signing/Notarization fehlt
- [ ] **Windows EXE:** Baut via GitHub Actions, aber kein Code Signing (SmartScreen-Warnung)
- [ ] **Troubleshooting Guide:** Soll in manuals (DE/EN/ES) eingebaut werden
- [ ] **What to Buy Guide:** Hardware-Einkaufsführer in 3 Preisklassen (manuals)

---

## 8. macOS .app & PyInstaller
- **Hyphen-Bug:** Kein Bindestrich im App-Namen (intern `InEarSnitch`)
- **Entitlements:** `Info.plist` braucht `NSMicrophoneUsageDescription`
- **Datenbank-Pfad:** Bei Frozen-App → `os.chdir(~/Documents/InEarSnitch/)`
- **Signierung:** `.DS_Store` Dateien brechen `codesign` → Build-Skript räumt auf

---

## 9. Datei-Übersicht

| Datei | Zweck |
|-------|-------|
| `main.py` (~3850 Zeilen) | Hauptfenster, MeasurementWorker, LiveSealWorker, UI-Setup |
| `audio_engine.py` (~610 Zeilen) | Sweep-Generierung, measure(), preflight, THD, CSD |
| `analysis.py` | Diagnostik-Logik (Schwellenwerte, Checks) |
| `analysis_ui.py` (~1020 Zeilen) | AnalysisWidget: FR/THD/CSD Graphen, Diagnostics Cards, EQ |
| `profile_ui.py` | Profil-Verwaltung, IEM-Cards |
| `history_ui.py` | Messverlauf, Export |
| `calibration_ui.py` | Mic-Kalibrierung UI |
| `database.py` | SQLite ORM (inearsnitch.db) |
| `theme.py` | Dark/Light Mode System |
| `eq_math.py` | DSP Engine für Hardware-EQ |
| `smoke_test.py` | Anti-Regression Test (PFLICHT!) |
| `config.py` | get_data_dir() Helper |
