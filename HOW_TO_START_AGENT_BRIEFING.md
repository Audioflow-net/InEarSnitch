# InEar Snitch – How to Start: Info-Paket für den Tutorial-Agenten

> Dieses Dokument gibt dir als Agent **alles**, was du brauchst, um ein erstklassiges "How to Start"-Tutorial für den Endnutzer zu bauen. Lies es vollständig durch.

---

## 1. Wer ist der typische User?

Der typische InEar Snitch User ist ein **Tontechniker auf Tour** oder ein **Bandmitglied**, das für die In-Ear-Systeme zuständig ist. Er hat:
- Ein Audio-Interface (z.B. MOTU M2, Scarlett 2i2, oder ein billiges USB-Interface)
- Einen IEC-711 Referenz-Kuppler (oder eine günstigere Nachbau-Version)
- Ein Mess-Mikrofon (fest im Kuppler verbaut)
- Mehrere In-Ear-Monitore verschiedener Musiker, die regelmäßig gecheckt werden müssen

**Er ist KEIN Audio-Ingenieur.** Er kennt sich mit Frequenzgängen grundsätzlich aus, aber Begriffe wie "Deconvolution", "Tukey-Window" oder "Farina-Methode" sagen ihm nichts. Das Tutorial muss **praxisnah** und **in normaler Sprache** sein.

---

## 2. Der reale Ablauf (So benutzt man die App wirklich)

### Schritt 0: Erster Start → EULA
- Beim allerersten Start erscheint ein **Health & Safety Warning**.
- Der User MUSS "Accept" klicken, sonst schließt sich die App.
- Inhalt: Warnung vor Gehörschäden und Hardware-Schäden. Niemals IEMs im Ohr tragen während einer Messung!
- Kommt nur einmal. Danach nie wieder.

### Schritt 1: Hardware anschließen
**Was der User physisch tun muss:**
1. Audio-Interface an den Laptop anstecken (USB)
2. Mess-Mikrofon (im IEC-711 Kuppler) an den **Input** des Interfaces anstecken
3. IEM an den **Output** (Kopfhörer-Ausgang) des Interfaces anstecken
4. IEM in den Kuppler einsetzen (Silikonschlauch als Abdichtung!)
5. **WICHTIG:** Der IEM darf NICHT im Ohr stecken! Nur im Kuppler!

### Schritt 2: Settings → Routing Tab
**Wo in der App:** Zahnrad-Icon oben rechts → Settings-Panel öffnet sich → Tab "Routing"

Was eingestellt werden muss:
- **Input Device:** Das Mess-Mikrofon (z.B. "MOTU M2 Input 1")
- **Output Device:** Der Kopfhörer-Ausgang, an dem der IEM hängt (z.B. "MOTU M2 Headphone")
- **Auto-Normalize Checkbox:** Sollte aktiviert bleiben (normalisiert den Graphen auf 80 dB)

**Praxis-Tipp:** Viele User haben mehrere Audio-Geräte (Laptop-Mikrofon, Bluetooth-Kopfhörer etc.). Sie MÜSSEN das richtige Interface auswählen, sonst misst die App die eingebauten Laptop-Lautsprecher!

### Schritt 3: Settings → Calibration Tab
**Zwei Kalibrierungen existieren:**

**A) Coupler-Kalibrierung (Mikrofon-Profil):**
- Dropdown "Active Coupler Profile" → Eine `.txt` oder `.cal` Datei laden
- Das ist die Frequenzgang-Korrektur des Mess-Mikrofons im Kuppler
- Ohne Kalibrierung sind die Messwerte trotzdem brauchbar, aber nicht referenz-genau
- Für billige "Fake 711" Kuppler gibt es einen Generator in der App

**B) Output Level Calibration:**
- Button "Start Auto-Calibration" drücken
- **VORHER:** IEM muss im Kuppler sitzen und Interface muss angeschlossen sein!
- Die App spielt 10 aufsteigende Testtöne ab (0.01 → 0.25 Amplitude)
- Sie findet automatisch die perfekte Lautstärke, bei der das Mikrofon genug Signal bekommt, aber nicht clippt
- **Ziel:** Recording-Peak bei -15 dBFS
- Danach zeigt die App das Ergebnis an (Sweep-Amplitude, RTA-Amplitude, Stress-Amplitude)
- **Warnungen möglich:**
  - "Recording level is very low" → System-Output-Level am Interface hochdrehen und nochmal kalibrieren
  - "Stress Test is at the same level as normal sweep" → Rub & Buzz Test wird unzuverlässig

**TERMINOLOGIE-REGEL:**
- "Level" = die Ausgangslautstärke (Output-Regler am Interface oder in der Software)
- "Gain" = die Vorverstärkung am Mikrofon-Eingang (Input-Gain am Interface)
- Im Tutorial IMMER korrekt unterscheiden!

### Schritt 4: Profil anlegen
**Wo in der App:** Linke Sidebar → "+" Button

Was angelegt wird:
- **Musiker-Name** (z.B. "Ben Gitarre")
- **Band** (z.B. "The Audionauts")
- **Profilbild** (optional, Kamerabild oder Upload)
- **IEM-Modell** (z.B. "Shure SE846", mit Seriennummer, Kontaktperson, Bild)
- Ein Musiker kann **mehrere IEMs** haben

**Warum Profil zuerst?** Die App verweigert eine Messung, wenn kein Profil ausgewählt ist! Die Messung wird immer einem bestimmten IEM eines bestimmten Musikers zugeordnet.

### Schritt 5: Messen
**Der zentrale Moment!**

1. IEM in den Kuppler einsetzen (muss dicht sitzen!)
2. In der Sidebar den richtigen Musiker und IEM auswählen
3. Kanal wählen: Links oder Rechts (über die Segmented Buttons "L" / "R")
4. Anzahl Sweeps wählen: 1x, 2x, oder 3x (Mehrfach-Sweeps werden gemittelt = weniger Rauschen)
5. **"▶ MEASURE" drücken**

**Was dann passiert:**
- **Preflight Level Check:** Die App spielt einen kurzen 100ms Testton und prüft, ob der Pegel noch mit der Kalibrierung übereinstimmt. Bei >4 dB Abweichung kommt ein Pop-Up!
- **Sweep:** Ein 1-Sekunden Sinus-Sweep von 5 Hz bis 24 kHz wird abgespielt
- **Animation:** Während des Sweeps zeigt die App eine große Cyan-Animation
- **Ergebnis:** Der Frequenzgang erscheint sofort als Graph

6. Danach den anderen Kanal messen (R drücken → nochmal MEASURE)
7. Wenn beide Kanäle gemessen sind → "SAVE" drücken um in die Datenbank zu speichern

### Schritt 6: Diagnostik verstehen
**Wo in der App:** Wird automatisch nach der Messung angezeigt

Die App prüft automatisch auf:
- **Bass Roll-off:** Starker Pegelabfall unter 200 Hz → möglicher Seal-Verlust (undichter Sitz)
- **Phase Inversion:** Einer der Treiber ist verpolt
- **L/R Mismatch:** Linker und rechter Kanal weichen stark voneinander ab
- **THD (Verzerrungen):** Hohe harmonische Verzerrungen → Treiber defekt?
- **CSD (Resonanzen):** Nachklingverhalten → Treble-Resonanzen sichtbar

**Ergebnis-Karten:**
- 🟢 Grün = PASS (alles ok)
- 🟡 Gelb = WARN (Auffälligkeit, aber nicht kritisch)
- 🔴 Rot = FAIL (Problem erkannt)

### Schritt 7: History
**Wo in der App:** Tab "History" in der Workspace-Navigation

- Zeigt alle vergangenen Messungen eines IEMs chronologisch
- Man kann ältere Messungen anklicken und mit der aktuellen Messung überlagern
- Export als CSV möglich
- Messungen können gelöscht werden

---

## 3. Häufige Fehler die Anfänger machen

| Fehler | Was passiert | Wie die App reagiert |
|--------|-------------|---------------------|
| IEM nicht im Kuppler, sondern in der Hand | Kein Seal, Bass fehlt komplett | Bass Roll-off FAIL |
| Falsches Audio-Device ausgewählt | Laptop-Mikro misst Raum | Signal too quiet Error |
| Output Level zu hoch nach Kalibrierung | Clipping, flache Fake-Kurve | Preflight warnt "Level shifted by X dB" |
| macOS Voice Isolation aktiv | AGC komprimiert den Sweep | Flache Kurve, Flatness-Warning |
| Kein Profil ausgewählt | Messung nicht möglich | Pop-Up "No Profile Selected" |
| Direct Monitoring am Interface an | Misst die Soundkarte selbst | "Electrical Loopback Detected!" |

---

## 4. Die exakte UI-Struktur der App

### Hauptfenster-Layout:
```
┌─────────────────────────────────────────────────┐
│  [Logo]  InEar Snitch          [⚙ Settings]    │
├──────┬──────────────────────────────────────────┤
│      │   Navigation: [Profiles] [Work] [Hist]   │
│ Side │──────────────────────────────────────────│
│ bar  │                                          │
│      │   Workspace Area                         │
│ (Mu- │   (Profile Tab / Analysis Tab / History) │
│ siker│                                          │
│ Kar- │                                          │
│ ten) │──────────────────────────────────────────│
│      │   Control Panel:                         │
│      │   [L/R] [1x 2x 3x] [▶ MEASURE] [SAVE]  │
└──────┴──────────────────────────────────────────┘
```

### Settings-Panel (Overlay, rechts):
- **Tab "Routing":** Input/Output Device, Auto-Normalize Checkbox
- **Tab "Calibration":** Coupler-Profil Dropdown, CalibrationWidget, Output Level Calibration
- **Tab "Database":** DB-Pfad, Backup/Restore
- **Tab "Manual":** Eingebautes Handbuch (DE/EN/ES) mit Suchfunktion
- **Tab "Console":** Debug-Ausgabe

### Workspace Tabs:
- **Index 0:** Profile-Verwaltung (ProfileWidget)
- **Index 2:** Analysis/Workspace (AnalysisWidget mit Graphen, THD, CSD, Waterfall)
- **Index 3:** History (HistoryWidget)

---

## 5. Was das Tutorial NICHT erklären muss

- Wie man Python installiert (die App soll als fertige .app ausgeliefert werden)
- Wie man den IEC-711 Kuppler baut (dafür gibt's HARDWARE_BOM.md)
- DSP-Interna (Farina-Methode, Tukey-Windowing, FFT) – das ist Backend
- Die EQ/DSP Engine (das ist ein Power-User Feature)

---

## 6. Ton und Sprache des Tutorials

- **Duzen, nicht Siezen** (Musiker-Szene, kein Corporate-Tool)
- **Kurze Sätze, keine Fachprosa**
- Analogien benutzen: "Wie ein Stethoskop für deine InEars"
- Emojis sparsam einsetzen (🎧 🔊 ✅ ⚠️ sind ok)
- **Immer das WARUM erklären**, nicht nur das WAS
  - Falsch: "Drücke auf Auto-Calibration"
  - Richtig: "Drücke auf Auto-Calibration – damit findet die App heraus, wie laut sie den Testton spielen darf, ohne dass dein Mikrofon clippt"
