# InEar Snitch - Entwickler-Katalog (Software-Architektur)

Dieses Dokument bietet einen Überblick über die Software-Architektur des InEar Snitch Projekts, die wichtigsten Dateien, deren Zuständigkeiten sowie die zentralen Klassen und deren Methoden/Signale.

---

## 1. Datei-Übersicht und Zuständigkeiten

- **`main.py`**: Der Haupteinstiegspunkt der Anwendung. Verwaltet das Hauptfenster (`MainWindow`), das Routing zwischen den verschiedenen Tabs (Profile, History, Calibration, Analysis) und orchestriert die Messabläufe mithilfe des `MeasurementWorker`.
- **`audio_engine.py`**: Enthält die Audio-Logik der Anwendung. Steuert die Audio-Geräte, generiert Sine-Sweeps, wendet Inverse-Filter an und berechnet akustische Metriken wie Glättung, THD (Total Harmonic Distortion) und CSD (Cumulative Spectral Decay).
- **`analysis.py`**: Die Logik-Komponente zur Auswertung von Messungen. Prüft Messdaten auf absolute Limits und wertet Metriken wie THD und CSD basierend auf vordefinierten Diagnoseregeln aus.
- **`database.py`**: Stellt die Schnittstelle zur SQLite-Datenbank (`inearsnitch.db`) bereit. Kümmert sich um die Initialisierung der Tabellen, das Speichern von Messwerten und das Laden von Referenzkurven.
- **`profile_ui.py`**: Die Benutzeroberfläche zur Verwaltung von Musiker-Profilen und deren In-Ear-Monitoren (IEMs). Erlaubt das Hinzufügen, Bearbeiten und Löschen von Profilen und Profilbildern.
- **`history_ui.py`**: Die Benutzeroberfläche für den Messverlauf. Lädt vergangene Messungen eines spezifischen IEMs, zeigt sie in einem Graphen an und bietet Export- (CSV) sowie Löschfunktionen.
- **`calibration_ui.py`**: Die Benutzeroberfläche für die System- bzw. Mikrofon-Kalibrierung. Erlaubt das Laden von Kalibrierungs-Dateien (z.B. txt), die Anzeige der Kalibrierungskurve und wendet diese auf das System an.
- **`analysis_ui.py`**: Die Benutzeroberfläche zur Visualisierung der Analyse- und Diagnose-Ergebnisse für durchgeführte Messungen.

---

## 2. Hauptklassen und ihre wichtigsten Methoden / Signale

### `main.py`
- **`MainWindow`**
  - *Zuständigkeit:* Hauptfenster, UI-Setup, Event-Handling.
  - *Methoden:* `setup_ui`, `run_measurement`, `on_measurement_finished`, `on_measurement_error`, `plot_target_curve`, `switch_workspace_tab`, `load_targets`, `export_csv`, `save_trace_to_db`
- **`MeasurementWorker`**
  - *Zuständigkeit:* Hintergrund-Thread zur asynchronen Durchführung der Audio-Messung, um ein Einfrieren der UI zu verhindern.
  - *Methoden:* `run`
  - *Signale:* `finished`, `error`, `progress`
- **`MusicianCard`**
  - *Zuständigkeit:* UI-Komponente (Karte) zur Darstellung eines Profils in der Seitenleiste/Übersicht.
  - *Signale:* `iem_changed`

### `audio_engine.py`
- **`AudioEngine`**
  - *Zuständigkeit:* Gekapselte Audio-Verarbeitung.
  - *Methoden:* `get_devices` (Hardware suchen), `generate_sweep` (Mess-Signal erzeugen), `get_inverse_filter` (Kompensation), `measure` (Durchführung), `smooth_spectrum` (Glättung), `extract_thd`, `calculate_csd`

### `analysis.py`
- **`Analyzer`**
  - *Zuständigkeit:* Diagnostik und Grenzüberprüfung der akustischen Messdaten.
  - *Methoden:* `run_full_diagnostics`, `absolute_checks`, `evaluate_thd`, `evaluate_csd`

### `database.py`
- **`DatabaseManager`**
  - *Zuständigkeit:* Persistenz der Messungen und Profile.
  - *Methoden:* `_init_db`, `save_measurement`, `load_reference_measurement`

### `profile_ui.py`
- **`ProfileWidget`**
  - *Zuständigkeit:* Verwaltung des gesamten Profil-Bereichs.
  - *Methoden:* `load_profile`, `update_pic_preview`, `add_another_iem`, `delete_musician`, `save_all`
  - *Signale:* `profile_updated`, `profile_deleted`
- **`IEMCardWidget`**
  - *Zuständigkeit:* Karte zur Darstellung eines spezifischen IEMs innerhalb eines Musikerprofils.
  - *Methoden:* `update_image`, `upload_pic`, `get_data`
  - *Signale:* `delete_requested`
- **`ProfilePicWidget`**
  - *Zuständigkeit:* Bild-UI für Profilfotos.
  - *Signale:* `clicked`

### `history_ui.py`
- **`HistoryWidget`**
  - *Zuständigkeit:* Tabellarische und grafische Ansicht älterer Messungen.
  - *Methoden:* `load_history` (lädt DB-Einträge), `on_item_selected`, `on_item_checked`, `export_selected_csv`, `delete_selected`, `get_checked_rows`

### `calibration_ui.py`
- **`CalibrationWidget`**
  - *Zuständigkeit:* Verwaltung der Mikrofon-Korrektur.
  - *Methoden:* `load_file`, `parse_file`, `plot_curve`, `generate_calibration`, `apply_calibration`
  - *Signale:* `calibration_applied`

### `analysis_ui.py`
- **`AnalysisWidget`**
  - *Zuständigkeit:* UI für die Darstellung der Diagnostik-Ergebnisse (z.B. Passed/Failed Metriken).
  - *Methoden:* `update_analysis`

*(Hinweis: Mehrere UI-Dateien verwenden zudem eine `FreqAxisItem` Klasse, die von `pg.AxisItem` erbt, um eine logarithmische oder formatierte Frequenzachse (`tickStrings`) für PyqtGraph bereitzustellen.)*

---

## 3. Acoustic DSP & Measurement Constraints (Critical Rules)

### Sweep Amplitude & ADC Clipping
- **Constraint:** The internal measurement sweep must ALWAYS be generated at `-20 dBFS` (Amplitude `0.1`), never at `1.0` (0 dBFS).
- **Reason:** In-Ear Monitors inside a sealed IEC711 coupler generate extreme Sound Pressure Levels (110-120+ dB SPL). Outputting a sweep at full digital scale causes the microphone ADC to severely clip (up to 30% of samples). Hard clipping destroys the relative amplitude differences between frequencies, resulting in a perfectly flat (but completely invalid) frequency response curve after deconvolution. 

### Auto-Gain Control (AGC) & OS Enhancements
- **Constraint:** All operating-system level microphone enhancements (e.g., macOS "Voice Isolation", Windows "Audio Enhancements", or hardware AGC) must be disabled during measurements.
- **Reason:** Dynamic range compressors and AGCs will aggressively normalize loud sweeps in real-time, effectively functioning as an inverse EQ. This artificially flattens the recorded sweep, creating a false Dirac-impulse after deconvolution. Pink Noise is immune to this specific flattening effect (as AGC reduces the broadband volume evenly), making Sweep vs. Pink Noise discrepancies a primary indicator of active AGC interference.
