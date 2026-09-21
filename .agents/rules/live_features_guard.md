# InEar Snitch — Live-Features Guard

**PFLICHT FÜR ALLE AGENTEN:** Bevor du Seal- oder Depth-Detection planst,
prüfe ob diese bereits implementiert sind.

## Bereits implementierte Live-RTA Features (main.py)

| Feature | Implementierung | Code-Zeile |
|---------|----------------|------------|
| **Seal Check** | `40Hz vs 500Hz`, Δ > 12 dB = SEAL LEAK | ~L3466 |
| **Depth Check** | 8kHz-Peak (EMA-smoothed), 7000–8600 Hz = Depth OK | ~L3413 |
| **IEM-Erkennung** | Signal < max - 15 dB = IEM Not Detected | ~L3406 |

Diese Features laufen **nur im Live-RTA** (während der User den IEM manuell
einsteckt und den "Depth"-Button nutzt). Sie sind **NICHT** in gespeicherten
Messungen verfügbar — der Frequenzgang-BLOB enthält keinen Zeitstempel per Frame.

## Was das bedeutet

- Neue Features dürfen diese **NICHT duplizieren**, sondern müssen sie **erweitern**.
- Beispiel erlaubt: Historischer Seal-Verlauf über gespeicherte BLOB-Daten (40Hz vs 500Hz aus numpy-Array).
- Beispiel verboten: "Wir implementieren einen Seal-Score" — existiert bereits live.

## Depth-Mechanik (für DSP-Analysen)

Der IEC-711 Kuppler hat eine Helmholtz-Resonanz bei ~8 kHz.
- **7000–8600 Hz**: Einstecktiefe korrekt → "Depth OK"
- **< 7000 Hz**: IEM zu flach → "Push Deeper"
- **> 8600 Hz**: IEM zu tief → "Pull Out Slightly"

Verschiedene Tip-Typen inserieren systematisch bei verschiedenen Frequenzen
innerhalb dieser Zone (Tip-Signatur). Das ist ein legitimes neues Feature —
der Live-Check kennt nur die globale Zone, nicht den Tip-spezifischen Zielwert.
