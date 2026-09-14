# InEar Snitch - Ultimate Agent Handoff & Project Brain Dump


> [!WARNING]
> **UPDATE (13.09.2026): UMBENENNUNG ABGESCHLOSSEN!**
> 1. Die App heißt ab sofort **InEar Snitch** (mit Leerzeichen in der UI).
> 2. Der Projektordner heißt nun **`/Users/ben/Desktop/InEarSnitch`** (ohne Bindestrich!). Alte Pfade wie `IE-SNITCH` führen ins Leere.
> 3. Die Datenbank heißt nun **`inearsnitch.db`**.
> 4. Das PyInstaller-Build Bundle heißt intern **`InEarSnitch`**.
> 5. Der Bug beim Erstellen einer frischen DB (fehlende Spalten `notes`, `photo_path` in `Measurements`) wurde gefixt.
> **Alle Skripte, Commands und Agents MÜSSEN den neuen Pfad `InEarSnitch` verwenden!**

**WICHTIG FÜR JEDEN NEUEN AGENTEN:** 
Lies dieses Dokument vollständig durch, bevor du auch nur eine einzige Zeile Code schreibst oder änderst. Dies ist die gesammelte Projekthistorie und das tiefgreifende Architekturwissen, das wir uns in unzähligen Iterationen hart erarbeitet haben.

---

## 1. Projektübersicht
- **Projektname:** **InEar Snitch** (früher InEar Snitch)
- **Ziel:** Eine professionelle, in Python (PySide6) geschriebene Desktop-Anwendung zur Messung, Diagnose und Katalogisierung von In-Ear-Monitoren (IEMs) mithilfe eines IEC-711 Referenz-Kupplers. 
- **Zielgruppe:** Bands, Tontechniker und Musiker, die den Gesundheitszustand ihrer IEMs (Phasendreher, verstopfte Filter, kaputte Treiber) schnell und automatisiert testen wollen.

---

## 2. Architektur & Wichtige Dokumente (Link-Katalog)
Du MUSST dich mit folgenden Dokumenten vertraut machen, je nachdem an welchem Teil der App du arbeitest:

- **Software-Architektur & Klassen:** [`DEVELOPER_CATALOG.md`](./DEVELOPER_CATALOG.md)
  - *Lies das, um zu verstehen, wie `main.py`, `audio_engine.py`, `analysis.py` und `database.py` zusammenspielen.*
- **Hardware-Teile & 3D-Druck:** [`HARDWARE_BOM.md`](./HARDWARE_BOM.md)
- **Lizenzen & Rechtliches:** [`NOTICES.txt`](./NOTICES.txt)
- **Regeln (Rules):** Die `.agents/rules/` Dateien (z.B. `cad_work_paper.md`, `terminal_paths.md`) gelten bedingungslos!

---

## 3. Akustische & DSP Core-Regeln (Hart Erlerntes Wissen!)
Wir haben extrem viel Zeit damit verschwendet, falsche Graphen zu debuggen. **Diese Regeln dürfen NIEMALS im Code aufgeweicht werden:**
1. **Sweep Amplitude MUSS -20 dBFS sein:** Ein In-Ear Hörer in einem abgedichteten IEC-711 Kuppler erzeugt absurde Schalldrücke (teilweise >120 dB SPL). Wenn wir den Sine-Sweep mit `1.0` (0 dBFS) feuern, clippt der Mikrofon-ADC komplett (bis zu 30% Hard-Clipping). Das zerstört die Amplitudendifferenzen und führt nach der Faltung (Deconvolution) zu völlig falschen, extrem flachen Graphen! Die Amplitude in `audio_engine.py` bleibt bei `0.1` (-20 dBFS).
2. **OS Audio-Enhancements:** macOS "Voice Isolation" oder Hardware-AGC flachen laute Sweeps künstlich ab, was die Messungen zerstört.
3. **Phasen-Ausrichtung:** Jeder gemessene Impuls (IR) wird via Numpy `np.roll` auf den Peak (t=0) zentriert, andernfalls wirft PyQtGraph völlig unbrauchbare Phasen-Plots aus.
4. **Pro-Audio Terminologie (STRENGE REGEL):**
   - **"Level"** = Ausgangslautstärke (Output zum IEM). Wird in unserer Software-Kalibrierung gesteuert.
   - **"Gain"** = Vorverstärkung am Mikrofon-Eingang (Input Preamp am Interface).
   - In allen UI-Texten, Warnungen und Fehlermeldungen MUSS korrekt zwischen Level und Gain unterschieden werden! Niemals "Gain" schreiben wenn "Level" gemeint ist.

---

## 3b. Preflight-Check & Level-Warnsystem (TODO – muss noch eingebaut werden!)
Es existiert bereits eine fertige `preflight_check()` Methode in `audio_engine.py` (Zeile 50-116), die:
1. Einen 100ms Probe-Ton bei 1kHz abspielt
2. Den aufgenommenen Peak misst
3. Ihn mit dem gespeicherten Kalibrierungs-Peak (`calibration_rec_peak`) vergleicht
4. Alarm schlägt wenn der Pegel um >4 dB abweicht

**STATUS: ✅ ERLEDIGT (commit d2fdeec)**
- `preflight_check()` wird jetzt in `run_measurement()` UND `run_stress_test()` aufgerufen.
- Bei Level-Drift > 4 dB kommt ein Pop-Up mit "Do you want to continue anyway?" (Yes/No).
- Die Kalibrierung warnt jetzt bei zu niedrigem Recording-Peak (< -30 dBFS).
- Die Kalibrierung warnt wenn `stress_amp ≈ optimal_amp` (Stress-Test kann nicht lauter).
- DSP-Sicherheitslücke geschlossen: `np.clip(sweep, -amplitude, amplitude)` wird NACH dem DSP-Processing angewendet.
- Disclaimer-Wording: "gain" → "output level" korrigiert.

---

## 4. Die macOS Standalone App (.app) & PyInstaller Historie
Der Versuch, die App über PyInstaller als doppelklickbare Mac-App zu verpacken, war ein gigantischer Kampf. Falls du hier weiterarbeiten musst, beachte:
- **Der Hyphen-Bug (Bindestrich):** Wenn der übergeordnete Ordner oder die App einen Bindestrich hat (z.B. `InEar Snitch`), stürzt das `pkg_resources` / `setuptools` Modul auf MacOS beim Start der fertigen App mit einem `InvalidVersion: '/Users/.../InEar Snitch'` Fehler ab! Deshalb heißt die verpackte App intern im Build-Skript `InEarSnitch` ohne Bindestrich. Zudem wurde `packaging==21.3` installiert, um den Bug abzufedern.
- **Entitlements:** Eine macOS `.app` DARF NICHT auf das Mikrofon zugreifen, es sei denn, die `Info.plist` hat den Schlüssel `NSMicrophoneUsageDescription`. Unser `build_mac.sh` fügt das via `plutil` ein.
- **Detritus & Signatur:** `.DS_Store`-Dateien brechen die Mac-Signierung (`codesign`). Das Build-Skript entfernt diese zwingend mit `find ... -delete` und `xattr -cr`, bevor es signiert.
- **Datenbank & Dateipfade in der .app:** Die App hat in der Sandbox Schreibschutz! Wir haben einen Workaround in `main.py` programmiert: Wenn die App als Frozen-App (`sys.frozen`) läuft, wechselt sie das Arbeitsverzeichnis (`os.chdir`) nach `~/Documents/InEarSnitch/`. Nur so kann sie die SQLite-Datenbank (`inearsnitch.db`) und `reference_targets/` sicher und updatesicher speichern!
- **Datenbank-Schema Crash:** Wenn die `.app` frisch startet und eine neue DB anlegt, MUSS `_init_db` in `database.py` alle Spalten (inkl. der neuen `profile_pic`, `notes`) generieren, da die App sonst beim ersten SQLite-Select crasht! (Wurde gerade erst gefixt).

---

## 5. UI & Theme
- Die App unterstützt ein globales **Dynamic Theme System (Dark / Light Mode)**. 
- Fast alle harten Inline-CSS Formatierungen (`setStyleSheet`) wurden aus den `.py` Dateien gelöscht. Stattdessen nutzt die App Eigenschaften (z.B. `widget.setProperty('class', 'danger')`), die zentral in `theme.py` abgewickelt werden.
- Warn-Karten (Diagnostics) in `analysis_ui.py` fragen `theme.is_light()` ab, um zur Laufzeit korrekte Farben zu berechnen. **Wenn du neue UI-Elemente baust, nutze immer `theme.py` und niemals hardcodierte `#FFFFFF` Farben!**

---

