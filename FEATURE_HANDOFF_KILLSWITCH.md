# FEATURE HANDOFF: Emergency Kill-Switch (InEar Protection)

## Kontext
Es wurde ein "Emergency Kill-Switch" in die InEar Snitch App implementiert, um In-Ear Monitore (insbesondere empfindliche BA-Treiber/Tweeter) vor thermischer Zerstörung zu schützen. Dieser Fall tritt ein, wenn der User den "Live RTA / Depth"-Modus startet und der physische Kopfhörerverstärker versehentlich auf 100 % steht.

## Implementierungs-Details
**Zielort:** `main.py` -> Klasse `LiveSealWorker` -> Methode `run()` -> `callback()`

1. **Top-Level Check:** Die Überprüfung findet ganz oben im Audio-Callback statt, noch bevor das `outdata`-Array mit dem kalibrierten Pink Noise befüllt wird.
2. **Frequency-Masking (> 1 kHz):** Um Fehlalarme durch niederfrequenten Körperschall (Handling Noise beim Einsetzen der In-Ears) zu vermeiden, wertet der Algorithmus per rFFT ausschließlich Frequenzen > 1000 Hz aus.
3. **Schwellenwert:** Sobald die ermittelte Energie im Hochtonbereich den Wert von **-10.0 dBFS** überschreitet, greift der Not-Stopp.
4. **Not-Stopp-Ablauf:**
   - Ein Warnsignal wird an die GUI gesendet: `self.error.emit("EMERGENCY STOP: Signal zu laut! In-Ear in Gefahr. Bitte Interface leiser drehen.")`
   - Um einen lauten Audio-Pop (Impuls) beim Stream-Abbruch zu verhindern, wird der uninitialisierte Buffer genullt: `outdata.fill(0.0)`.
   - Der Stream wird in derselben Millisekunde per `raise sd.CallbackStop` terminiert.

## Performance & Stabilität (Zero-Allocation)
Da wir uns im kritischen Realtime-Audio-Callback befinden, wurde die Logik auf minimale Objekterzeugung (Zero-Allocation) getrimmt:
- `kill_window` und `kill_high_mask` werden dynamisch gecacht.
- `kill_sig` wird mit `np.empty` alloziiert und via `np.multiply(..., out=kill_sig)` in-place beschrieben.
- Die Leistung (Energie) wird ohne Zwischen-Arrays direkt mittels C-nativer `np.vdot(high_bins, high_bins).real` berechnet.
- Das Exception-Handling wurde angepasst (`except sd.CallbackStop: raise`), damit das `CallbackStop`-Event nicht fälschlicherweise vom allgemeinen `Exception`-Block verschluckt und die GUI-Meldung überschrieben wird.

## Aufgabe für den Master Agent
Bitte überprüfe diese Implementierung aus der Vogelperspektive:
- **UI & Lifecycle:** Integriert sich das abgefangene `sd.CallbackStop` und das resultierende `self.error.emit` sauber in das Fehler-Handling der `main.py` GUI (insb. `on_measurement_error`)?
- **Thread State:** Wenn der Stream stirbt, bleibt `self.running` des QThreads auf `True`. Die Architektur von `LiveSealWorker` scheint darauf ausgelegt zu sein (der Thread wartet in `sd.sleep(100)`, bis die GUI ihn via `.stop()` beendet). Ist das im Kontext der Gesamt-App sicher?
- **Audio Engine Freeze:** Es wurde bestätigt, dass die `audio_engine.py` (gemäß CODE FREEZE) unangetastet blieb.

**Smoke-Test:** Alle Checks bestehen (Exit 0).
