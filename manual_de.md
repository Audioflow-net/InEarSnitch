# InEar Snitch: Benutzerhandbuch (Hilfedatei)

Willkommen bei InEar Snitch, der professionellen Software für das Messen, Analysieren und Diagnostizieren von In-Ear Monitoren (IEMs).

Dieses Handbuch erklärt die grundlegenden Funktionen und hilft Ihnen, genaue Messungen durchzuführen.

👉 **Neu hier?** Lies zuerst den [Was du brauchst – Hardware Guide](#hardware-guide), um dein Audio-Setup richtig einzurichten!

## Keyboard Shortcuts (Tastaturkürzel)

Die folgenden Tastenkombinationen beschleunigen Ihren Workflow:
- `Space`: Run Sweep (Messung starten)
- `Ctrl+S` / `Cmd+S`: Trace speichern (Save Trace)
- `Backspace` / `Delete`: Trace löschen (Clear Trace)
- `Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`: Zwischen den Tabs wechseln (Profile, Measurement, Analysis, History)

<a name="hardware-guide"></a>
## Was du brauchst – Hardware Guide

Bevor du mit dem Messen beginnen kannst, benötigst du die richtige Hardware. InEar Snitch erfasst akustische Signale, daher ist ein korrektes Setup der "Messkette" essenziell.

### 1. Die Messkette erklärt

Die Messkette beschreibt den Weg des Audiosignals von der Software bis zum IEM und wieder zurück in den Computer.

```text
[Computer] ──OUTPUT──▶ [IEM] ──▶ [IEC711 Kuppler] ◀── [Messmikrofon] ──INPUT──▶ [Computer]
```

**Wie es funktioniert:**
- Es gibt einen **OUTPUT-Pfad** (Ton zum IEM) und einen **INPUT-Pfad** (Mikrofon zurück zum Computer).
- Beides muss **GLEICHZEITIG** funktionieren (Full-Duplex).
- InEar Snitch unterstützt **SEPARATE** Geräte für Input und Output (z.B. MacBook-Ausgang + USB-Mic-Interface).

### 2. Voraussetzungen an das Audio-System

**Was dein Audio-Setup können MUSS:**
- Gleichzeitig abspielen UND aufnehmen (Full-Duplex).
- In InEar Snitch als separates Input UND Output Device erscheinen.
- Stabile Treiber (Core Audio auf macOS, WASAPI auf Windows).

**💡 macOS Besonderheit:**
- Input und Output **DÜRFEN** verschiedene Geräte sein!
- Beispiel: MacBook Kopfhörerausgang (Output) + USB Audio Interface (Input) → funktioniert!
- Die App nutzt intern `sd.Stream()` statt `sd.playrec()`, was separate Devices problemlos unterstützt.

**⚠️ Windows Besonderheit:**
- Input und Output **MÜSSEN** auf exakt der gleichen Sample Rate stehen (z.B. beide 48000 Hz).
- Prüfe das unter: Systemsteuerung → Sound → Aufnahme/Wiedergabe → Eigenschaften → Erweitert.
- Wenn die Sample Rates nicht übereinstimmen, crasht die App beim Messen!

### 3. Drei Setup-Varianten (Preisklassen)

#### 💰 Budget Setup (~50-80€) – "Ich hab schon einen Mac/PC"

**Was du brauchst:**
- **IEC711 Kuppler mit eingebautem Mikrofon** (ca. 30€)
  - Suche auf AliExpress: "IEC711 coupler microphone ear simulator"
  - Kaufe "Typ 4" (ohne individuelle Kalibrierung) – die App hat eine generische IEC711-Korrekturdatei eingebaut.
- **USB Audio Interface** (ca. 35-45€)
  - Behringer UM2 (ca. 35€) oder Behringer UMC22 (ca. 45€)
  - Hat eigenen Kopfhörerausgang (Output) + Klinke/XLR-Eingang (Input).

**ODER noch günstiger:**
- **Der 3€ Geheimtipp:** Winzige USB-C Soundkarten (z.B. auf AliExpress) funktionieren wunderbar! 
  - **WICHTIG:** Der Dongle **MUSS ZWEI getrennte Buchsen** haben (eine für Kopfhörer, eine für das Mikrofon).
- **IEC711 Kuppler:** AliExpress Typ 4 (ca. 30€).
- **In InEar Snitch:** Settings → Routing → Input = USB-Soundkarte, Output = USB-Soundkarte (oder "Built-in Output" am Mac).
- **Gesamtkosten: ab ca. 35€!**

#### 💰💰 Empfohlenes Setup (~100-200€)

- **IEC711 Kuppler** mit individuellem Kalibrierungsfile (ca. 60€)
- **USB Audio Interface:** Focusrite Scarlett Solo (ca. 100€) oder MOTU M2 (ca. 180€)
  - Bessere Preamps = weniger Rauschen = sauberere Messungen.
  - Stabile, gut getestete Treiber für macOS und Windows.
- Wenn du SCHON ein Audio-Interface hast (egal welche Marke: Focusrite, MOTU, RME, Universal Audio, PreSonus, Steinberg, Audient, Behringer...): Nur den Kuppler kaufen!

#### 💰💰💰 Pro/Labor Setup (~400€+)

- **GRAS RA0045** oder **Brüel & Kjær** Kuppler (ca. 300-500€)
- **RME Babyface Pro FS** (ca. 500€) oder **MOTU M2** (ca. 180€)
- Vorteil: Laborqualität, Messungen sind veröffentlichbar und vergleichbar mit Crinacle/Headphones.com.

### 4. ⚠️ Funktioniert mein Setup? Der 60-Sekunden-Test

**Schritt-für-Schritt-Anleitung:**
1. Öffne InEar Snitch → Settings (oben rechts) → Routing Tab.
2. Wähle dein Interface als **Input** (das Gerät mit dem Mikrofon).
3. Wähle dein Interface oder den eingebauten Ausgang als **Output** (wo der IEM dranhängt).
4. Klicke "Save".
5. Drücke **"RTA"** in der unteren Leiste.
6. Siehst du eine **lebendige, zappelnde Kurve**? → Dein Mikrofon-Input funktioniert ✅
7. Hörst du **Pink Noise** (ein Rauschen) im IEM? → Dein Output funktioniert ✅
8. Stoppe RTA. Gehe zu Settings → Calibration Tab → "Start Auto-Calibration".
9. Die Balken MÜSSEN von links nach rechts **ANSTEIGEN** (leise → laut).
10. Wenn alle Balken gleich lang sind (ca. -40 dBFS): Dein Setup empfängt kein echtes Signal. Prüfe Verkabelung!

### 5. ❌ Was NICHT funktioniert

| Setup | Problem |
|-------|---------|
| **Apple USB-C auf 3.5mm Dongle** (und andere mit nur EINER Buchse) | Haben eine kombinierte TRRS-Buchse. Sie erkennen reine Messmikrofone nicht. Auch TRRS-Splitter-Kabel (Y-Kabel) funktionieren hier **nicht**! |
| **Bluetooth-Kopfhörer / AirPods** | Viel zu hohe Latenz, kein Sweep möglich. |
| **TWS Earbuds (kabellos)** | Können nicht in den Kuppler gesteckt werden. |
| **Handy-Kopfhörerausgang** | Zu schwach, meist kein Full-Duplex möglich. |
| **Windows: Unterschiedliche Sample Rates** | App crasht! Input UND Output müssen auf gleicher Sample Rate stehen (z.B. 48000 Hz). |

### 6. Empfohlene Kabel & Adapter

- **3.5mm auf 6.3mm Klinke-Adapter** (für Interface-Kopfhörerausgang → IEM, falls nötig)
- **TRS-auf-TRRS Adapter** (nur wenn du den MacBook-Jack gleichzeitig als Input nutzen willst – nicht empfohlen)
- ⚠️ **LEBENSWICHTIG: XLR-auf-Klinke Adapter für Messmikrofone**
  Wenn dein Audio-Interface nur XLR-Eingänge hat und der IEC711-Kuppler einen 3.5mm Klinkenstecker besitzt, mach nicht den Fehler, einen simplen Adapter zu kaufen! 
  - **Das Problem:** Audio-Interfaces liefern **48V Phantomspeisung** über XLR. Das kleine Mikrofon im Kuppler verträgt aber nur **3 bis 5 Volt (Plug-in-Power)**. Schickst du 48V direkt in das Mikrofon, brennt es sofort durch.
  - **Die Lösung:** Du brauchst zwingend einen Adapter mit integriertem Spannungswandler ("Power Converter").
  - **Wie du das in den Specs erkennst:** Achte in der Produktbeschreibung auf Formulierungen wie *"Converts 12-48V Phantom Power to 3-5V Plug-in Power"*. Steht das nicht explizit dort, leitet der Adapter die 48V ungebremst weiter!
  - **Empfehlung:** Kaufe den **Rode VXLR+** (das "Plus" ist wichtig!) oder den **Antlion Audio XLR Power Converter**.

### 7. 🔗 Nützliche Ressourcen & Community

- **[REW Forum (Room EQ Wizard)](https://www.avnirvana.com/forums/rew-room-eq-wizard.4/)** → Community-Erfahrungsberichte zu Audio-Interfaces für Messungen
- **[Head-Fi IEM Community](https://www.head-fi.org/)** → Die größte IEM-Community der Welt
- **[AudioScienceReview](https://www.audiosciencereview.com/)** → Objektive Reviews und Messungen von Audio-Hardware
- **[Squig.link](https://squig.link/)** → IEM-Frequenzgang-Vergleichstool (zum Vergleichen deiner eigenen Messungen)
- **[Crinacle IEM Rankings](https://crinacle.com/rankings/iems/)** → Referenz für IEM-Bewertungen basierend auf Messungen

**Suchbegriffe für Hardware:**
- AliExpress: `IEC711 coupler microphone`, `IEC711 ear simulator`, `artificial ear IEC711`
- Amazon: `USB audio interface recording`, `Behringer UM2`, `Focusrite Scarlett Solo`
- Speziell für Kuppler mit Kalibrierung: `IEC711 calibrated coupler with certificate`


## 1. Die Benutzeroberfläche (Tabs)

Die App ist in vier Hauptbereiche (Tabs) unterteilt:

- **Measurement (Messung):** Hier nehmen Sie in Echtzeit neue Frequenzgänge auf.
- **Analysis (Analyse):** Dieser Bereich widmet sich der detaillierten Untersuchung Ihrer Messungen, inkl. der "Automated Diagnostics Engine" (siehe unten) und detaillierten L/R-Vergleichen.
- **History (Verlauf / Vault):** Eine Datenbank/Historie all Ihrer bisherigen Messungen. Sie können alte Messungen laden, vergleichen und exportieren.
- **Profile:** Hier können Sie spezifische Profile für verschiedene IEM-Modelle hinterlegen (inkl. Target-Kurven und Bildern der Modelle).

## 2. Messungen durchführen (Measurement)

Im Tab **Measurement** (Messung) führen Sie die eigentlichen akustischen Messungen durch.

- **Multi-Sweep:** Für genauere Ergebnisse kann die Software mehrere Frequenz-Sweeps (Multi-Sweep) hintereinander ausgeben und den Durchschnitt bilden. Das minimiert Hintergrundrauschen und Störungen.
- **Smoothing (Glättung):** Rohe akustische Messdaten enthalten oft viele kleine, unhörbare Spitzen (Kammfilter-Effekte). Mit der *Smoothing*-Funktion (z.B. 1/12 oder 1/24 Oktave) wird die Kurve geglättet, sodass sie der menschlichen Wahrnehmung besser entspricht und visuell leichter lesbar wird.
- **Vorgang:** Um eine Messung zu starten, positionieren Sie den IEM im Mess-Kuppler (Coupler), stellen Sie sicher, dass alles dicht ist, und drücken Sie auf Start (oder `Space`). Sie können die gemessene Kurve anschließend speichern.

## 3. Settings Slide-Out (Routing & Calibration)

An der Seite der App finden Sie das **Settings Slide-Out** (die herausfahrbaren Einstellungen). 

- **Routing:** Hier legen Sie fest, welche Audio-Eingänge (Messmikrofon/Coupler) und Ausgänge (Kopfhörerausgang zum IEM) für die Messung verwendet werden sollen.
- **Calibration (Kalibrierung):** Mikrofone sind nie zu 100% linear. Hier können Sie eine Kalibrierungsdatei (`.cal` oder `.txt`) laden, um die spezifischen Abweichungen Ihres Mikrofons auszugleichen. Die Kalibrierung wird in Echtzeit auf alle eingehenden Messungen angewendet.

## 4. Automated Diagnostics Engine (Automatische Fehlerdiagnose)

Die "Automated Diagnostics Engine" (im Analysis-Tab) bewertet Ihre Messung und erkennt automatisch Hardware-Defekte oder Fehlbedienungen. Die akustischen Schwellenwerte basieren auf Industrie-Standards und psychoakustischer Fachliteratur (z.B. IEC 711 Standards).

### Wie die Diagnose funktioniert (und warum sie so streng ist):

*   **Relative Phase (Polarity / Phasendreher):** 
    Die Engine prüft nicht, ob ein einzelner IEM eine "absolute" Phasenumkehr hat (da dies oft durch Soundkarten, Kabel oder gewollte Crossover-Designs, wie z.B. bei Multi-BA IEMs, entsteht und für das Ohr ohnehin unhörbar ist). 
    Stattdessen prüft die Engine die **relative Phase**: Sind der linke und rechte Kanal *unterschiedlich* gepolt? Wenn ja, wird ein harter Fehler (FAIL) geworfen, da dies zu starken Bass-Auslöschungen und einem Zusammenbruch des Stereo-Bildes führt. (Überprüfen Sie in diesem Fall unbedingt die 2-Pin/MMCX-Kabel).

*   **Bass / Acoustic Seal (Akustisches Leck):**
    Die Engine vergleicht den Bassbereich (50 Hz) mit den Mitten (1 kHz). 
    - **WARNUNG:** Wird ausgelöst, wenn der Bass um mindestens -10 dB im Vergleich zu 1 kHz abfällt. Bei einem neutralen In-Ear (z.B. Etymotic oder Diffuse-Field Tuning) ist ein Abfall von -2 bis -6 dB völlig normal. Erst ab -10 dB deutet es stark auf einen nicht optimal sitzenden In-Ear im Messrohr hin (Leckage).
    - **FEHLER (FAIL):** Wird erst ab -18 dB ausgelöst. Ein solch extremer, steiler Abfall im Tieftonbereich verhält sich physikalisch wie ein Hochpassfilter und beweist ein massives Luftleck (Seal-Bruch) im Coupler oder einen defekten dynamischen Tieftöner.

*   **Highs / Wax Clog (Ohrenschmalz-Verstopfung):**
    Ein typischer Fehler bei einfachen Messsystemen ist es, exakt *eine* bestimmte Frequenz (z.B. 5 kHz) zu prüfen. Da Messröhrchen (IEC 711) jedoch natürliche stehende Wellen aufweisen, entstehen oft extrem schmale, tiefe Dips genau in diesem Bereich (sog. Notches). 
    Um falsche Alarme zu vermeiden, berechnet unsere Engine die **Durchschnittsenergie im gesamten Band von 4 kHz bis 8 kHz**. Ein echtes, mit Ohrenschmalz verstopftes Filtergitter wirkt physikalisch wie ein Tiefpassfilter und dämpft dieses gesamte Frequenzband breitbandig ab. Erst wenn dieser Durchschnitt extrem tief fällt (-15 dB für WARN, -20 dB für FAIL), schlägt die Software Alarm.

## 5. History Vault (Verlauf & Datenbank)

Der **History**-Tab fungiert als Ihr sicherer Tresor (Vault). Jede durchgeführte und gespeicherte Messung wird hier strukturiert abgelegt.
- Sie können mehrere historische Messungen übereinanderlegen (Overlay), um den Verschleiß eines IEMs über die Zeit zu prüfen oder die Konsistenz nach einer Reinigung zu verifizieren.
- Ausgewählte Kurven können einfach als CSV für externe Analysen oder zum Teilen exportiert werden.
- **Import CSV:** Klicken Sie auf "Import CSV", um eine externe Messung direkt zur Datenbank hinzuzufügen.
- **Save as Target:** Exportieren Sie jede Verlaufskurve direkt in Ihren Reference Targets Ordner. Dadurch steht sie sofort als Target-Kurve in der gesamten App zur Verfügung (ähnlich wie Squiglink-Targets).
- **Messungen umbenennen:** Machen Sie einen Doppelklick auf die Spalte "Notes", um Messungen direkt in der History-Datenbank umzubenennen.

## 6. "Fake 711" Kalibrierung erstellen (Auto-Generate from Reference)

Wenn Sie kein teures, kalibriertes IEC 711 Messmikrofon besitzen (sondern einen günstigen "Fake" Coupler), können Sie die App nutzen, um sich selbst eine passgenaue Kalibrierungsdatei zu erstellen!

Dazu nutzen Sie den Button **"🪄 Auto-Generate from Reference"** im Kalibrierungs-Menü (Calibration):

1. **Eigene Messung erstellen:** Messen Sie einen bekannten, hochwertigen IEM mit Ihrem eigenen (Fake) Coupler und speichern Sie diese Messung im Measurement-Tab als CSV ab.
2. **Button klicken:** Klicken Sie im Calibration-Menü (im Settings Slide-Out) auf den Button "🪄 Auto-Generate from Reference".
3. **Dateien auswählen:**
   - *Step 1:* Wählen Sie zuerst die eben erstellte CSV-Datei Ihrer EIGENEN Messung (mit dem Fake-Coupler) aus.
   - *Step 2:* Wählen Sie danach die professionelle CSV-Messung (die "True" Reference) desselben IEMs aus dem Ordner `reference_targets` aus.
4. **Magie!** Die Software interpoliert beide Kurven, gleicht die Lautstärke bei 500Hz automatisch an und berechnet exakt die Differenz. Daraus wird automatisch eine `Auto_Generated_Fake711_Cal.txt` Datei im `calibrations` Ordner erstellt und sofort angewendet. Ihr günstiges Mikrofon misst von nun an genauso linear wie das teure Referenz-Setup!

## 7. Datenbank-Management

Das Einstellungsmenü (Settings) verfügt nun über einen **Database Management** Bereich. Hier können Sie ein Backup Ihrer gesamten SQLite-Datenbank (`inearsnitch.db`) erstellen oder von vorherigen Backups wiederherstellen (Restore). Das System erstellt bei einer Wiederherstellung automatisch eine `.safety.bak`-Datei, um versehentlichen Datenverlust zu verhindern.

## 8. Intelligente Such-Dropdowns (Smart Searchable Dropdowns)

Die Target- und History-Comboboxen (Dropdown-Menüs) in der gesamten Anwendung sind nun vollständig durchsuchbar. Sie können einen beliebigen Teil des Namens (z.B. "v7") eingeben, um schnell die passenden Einträge zu finden (z.B. "Vision Ears v7").

## 9. Live Position Guide (RTA & Depth)

Unten rechts in der Hauptansicht finden Sie den **RTA (Real-Time Analyzer)** sowie den **Depth** Button. Dieser Modus spielt "Pink Noise" ab und zeigt das gemessene Frequenzspektrum in Echtzeit an. Er dient dazu, den In-Ear perfekt im Messkuppler zu positionieren, *bevor* die eigentliche Messung (Sweep) gestartet wird.

Wenn Sie den **Depth** Button aktivieren, führt Sie die App in Echtzeit durch zwei kritische physikalische Eigenschaften der Messung: **Dichtigkeit (Seal)** und **Einstecktiefe (Insertion Depth)**.

### 1. Dichtigkeit (Bass Seal / 40 Hz Linie)
Wenn der In-Ear Monitor nicht 100% luftdicht mit dem Kuppler abschließt, entweicht Druck und der Bass fällt massiv ab. 
- **Grüne 40 Hz Linie (Bass Seal OK):** Der Hörer dichtet perfekt ab.
- **Rote 40 Hz Linie (Bass Leak!):** Luft entweicht. Drücken Sie den In-Ear gerader in den Kuppler oder nutzen Sie einen anderen Schaumstoff/Silikon-Tip.

### 2. Einstecktiefe (IEC Guide / 8 kHz Linie)
Wenn der In-Ear in das Messrohr (IEC 711 Kuppler) eingeführt wird, entsteht ein kleiner Hohlraum, der bei einer bestimmten Frequenz resoniert. Für normgerechte Messungen muss der In-Ear exakt so tief eingesteckt werden, dass diese Resonanz in der grünen Zielzone zwischen **7.000 Hz und 8.600 Hz** liegt.
- **Gelber Text ("Push Deeper"):** Resonanz liegt unter 7 kHz -> Den In-Ear weiter in das Rohr schieben.
- **Gelber Text ("Pull Out Slightly"):** Resonanz liegt über 8.6 kHz -> Den In-Ear ein kleines Stück herausziehen.
- **Grüner Text ("Depth OK"):** Perfekte Einstecktiefe erreicht!

### Warum immer 8 kHz – selbst bei anderen Kalibrierungen?
Oft wird gefragt, warum der Guide *immer* auf 8 kHz zielt, selbst wenn man unterschiedliche Mikrofon-Kalibrierungsdateien geladen hat.
Die Antwort liegt in der **Physik**: Eine Kalibrierungsdatei korrigiert nur interne Schwankungen der Mikrofonkapsel. Das physische Metall-Rohr des Kupplers bleibt aber immer gleich lang. Daher verschiebt eine Kalibrierung niemals die physikalische Luft-Resonanz. Der Guide zeigt Ihnen also immer den akustisch korrekten physikalischen Sitz an, unabhängig von der gewählten Datei.

## 10. Health & Safety Disclaimer (EULA)

Beim allerersten Start von InEar Snitch erscheint ein **Sicherheits- und Gesundheitshinweis** (Health & Safety Disclaimer). Dieser Dialog informiert Sie über zwei wesentliche Risiken:

- **Gehörschäden:** Tragen Sie **niemals** IEMs im Ohr, während eine Messung (Sweep oder Stress-Test) läuft! Die dabei erzeugten Signalpegel können Ihr Gehör dauerhaft schädigen.
- **Hardware-Schäden:** Unsachgemäße Level-Einstellungen können empfindliche IEM-Treiber (insbesondere Balanced-Armature-Treiber) beschädigen.

Sie müssen **"Accept"** klicken, um die App verwenden zu können. Wenn Sie auf **"Decline"** klicken, wird die App sofort geschlossen. Dieser Dialog erscheint nur ein einziges Mal – Ihre Zustimmung wird dauerhaft in den Einstellungen gespeichert.

## 11. Output Level Calibration (Ausgangslautstärke-Kalibrierung)

Die App verfügt über eine automatische Lautstärke-Kalibrierung, die den optimalen **Output Level** (Ausgangspegel) für Ihre spezifische Hardware-Konfiguration ermittelt. Sie finden diese Funktion unter **Settings > "Start Auto-Calibration"**.

### Ablauf der Kalibrierung:
1. Die App spielt eine Serie aufsteigender Testtöne ab (beginnend bei niedrigem Level).
2. Sie analysiert den aufgenommenen Pegel und findet automatisch die optimale Sweep-Amplitude.
3. **Ziel-Recording-Peak:** -15 dBFS – dies gewährleistet einen sicheren Abstand zu Clipping bei gleichzeitig ausreichendem Signal-Rausch-Abstand.

### Mögliche Warnungen:
- **Recording-Peak zu niedrig (< -30 dBFS):** Das aufgenommene Signal ist trotz maximaler Sweep-Amplitude zu leise. **Lösung:** Erhöhen Sie den System-Output-Level (Betriebssystem-Lautstärke) und führen Sie die Kalibrierung erneut durch.
- **Stress-Test eingeschränkt:** Wenn der Stress-Test nicht lauter als der normale Sweep ausgegeben werden kann (beide am Amplitude-Cap), erscheint eine Warnung, dass die Rub & Buzz Erkennung unzuverlässig sein kann.

> ⚠️ **Wichtiger Hinweis zur Terminologie:** Diese Kalibrierung passt den **Output Level** (Ausgangslautstärke / Sweep-Amplitude) an – NICHT den Gain! Der Gain ist die Vorverstärkung am Mikrofon-Eingang Ihres Audio-Interfaces und wird von der App nicht verändert.

## 12. Preflight Level Check (Automatische Pegelprüfung vor jeder Messung)

Vor **jeder** Messung – sowohl beim normalen Sweep als auch beim Stress-Test – führt InEar Snitch automatisch einen schnellen **Preflight Level Check** durch.

### Ablauf:
1. Die App spielt einen kurzen Testton (100 ms) ab.
2. Der aufgenommene Pegel wird mit dem gespeicherten **Kalibrierungs-Referenzwert** verglichen.

### Erkannte Situationen:

- **Level-Abweichung > 4 dB:** Wenn sich der Pegel seit der letzten Kalibrierung um mehr als 4 dB verändert hat (z.B. weil jemand den System-Output-Level verändert hat), erscheint ein Pop-Up:
  > *„Level shifted by X dB since calibration. Do you want to continue anyway?"*
  
  Sie können mit **Yes** trotzdem fortfahren oder mit **No** abbrechen und zunächst eine Re-Kalibrierung durchführen.

- **Clipping erkannt (> -1 dBFS):** Das Eingangssignal übersteuert – der Pegel muss reduziert werden.
- **Kein Signal erkannt (< -55 dBFS):** Es wird kein verwertbares Signal empfangen – prüfen Sie Ihre Verkabelung und das Routing.

## 13. DSP/EQ Safety Cap (Sicherheitsbegrenzung bei aktivem EQ)

Wenn die eingebaute **DSP Engine** (der integrierte EQ) aktiv ist, können Frequenz-Boosts das Ausgangssignal über die ursprüngliche Sweep-Amplitude hinaus verstärken.

Um Schäden an empfindlichen Treibern zu verhindern, wendet InEar Snitch **nach dem EQ-Processing automatisch einen Sicherheits-Limiter** an. Dieser stellt sicher, dass EQ-Boosts die maximale Sweep-Amplitude **niemals** überschreiten können.

Dies ist besonders wichtig für empfindliche **Balanced-Armature-Treiber**, die bei Übersteuerung dauerhaft beschädigt werden können. Der Safety Cap arbeitet transparent im Hintergrund – Sie müssen nichts konfigurieren.

## 14. Störgeräusch-Robustheit & Farina-Dekonvolution (Noise Robustness & Farina Deconvolution)

InEar Snitch nutzt das wissenschaftlich etablierte **Log-Sine-Sweep-Dekonvolutionsverfahren nach Angelo Farina**. Diese mathematische Methode sorgt für eine außergewöhnlich hohe Unempfindlichkeit gegenüber Umgebungs- und Störgeräuschen während der akustischen Messung.

### Funktionsweise der Farina-Dekonvolution:
- **Mathematische Trennung von Impulsantwort und Störschall:** Während des Sweeps gibt die Software einen logarithmisch ansteigenden Sinuston aus und nimmt das Signal des Messmikrofons auf. Bei der anschließenden Dekonvolution mit dem zeitinversen Filter wird die reine lineare Impulsantwort des In-Ear-Monitors mathematisch präzise von unkorreliertem Hintergrundlärm getrennt (z. B. Sprechen, Tastaturklappern, Schläge auf den Schreibtisch oder Rosa Rauschen im Raum).
- **Verschiebung in die „negative Zeit“:** Unkorrelierte Störgeräusche sowie harmonische Verzerrungsprodukte werden bei der Dekonvolutions-Berechnung in die sogenannte „negative Zeit“ (zeitlich vor den Hauptimpuls) verschoben und vom Analyse-Fenster vollständig ignoriert und verworfen.
- **Saubere Messungen trotz Raumlärm:** Da unkorrelierter Störschall rechnerisch eliminiert wird, bleiben die **Frequenzgang- und THD-Graphen absolut sauber und präzise – selbst wenn während des Mess-Sweeps laute Geräusche im Raum auftreten!** Ein schalltoter Raum oder absolute Stille während des Sweeps sind daher nicht erforderlich.

### Die einzige Ausnahme: Pre-Flight Room Noise Check
Die einzige Phase, in der Umgebungsgeräusche eine Rolle spielen, ist die automatische **Pre-Flight Room Noise Prüfung**:
- Für **0,5 Sekunden *vor* Beginn des Sweeps** lauscht InEar Snitch kurzzeitig auf das Grundrauschen des Mikrofons (`Listening to room noise...`).
- Diese 0,5-sekündige Ruhephase dient dazu, eine Baseline für den Raum-Rauschpegel zu ermitteln und im Analyse-Report eine Warnung auszugeben, falls die Umgebung für verlässliche THD-Grenzwerte zu laut ist.
- Sobald der eigentliche Sweep startet, greift die Farina-Dekonvolution und schirmt die Messung zuverlässig gegen Störgeräusche ab.

## 15. Troubleshooting Guide: Auffällige Messungen

> **KERNBOTSCHAFT:** Im Zweifel: IEM rausnehmen, neu einsetzen, nochmal messen. Die meisten Probleme sind Seal-Probleme, keine Defekte.

| Symptom | Ursache | Lösung |
| :--- | :--- | :--- |
| **Clipping / Übersteuerung** (Frequenzgang sieht abgeschnitten aus, Plateau bei hohen dB) | Output Level zu hoch eingestellt | Level-Kalibrierung neu machen, Zielwert -15 dBFS |
| **Bass-Einbruch / Kein Bass** (Unter 200 Hz fällt der Graph steil ab) | 1. Schlechter Seal im Kuppler, 2. Schwacher Kopfhörer-Preamp, 3. Normaler BA-Driver Rolloff | IEM neu einsetzen, Blu-Tack prüfen, ggf. besseren Kopfhörerausgang nutzen |
| **Phase invertiert** (Diagnostik meldet "L/R OUT OF PHASE") | Billige USB-Soundkarten invertieren die Phase | 2-Pin Kabel-Orientierung prüfen. Wenn beide Seiten invertiert = kein Problem |
| **Hohe Verzerrung (THD)** (THD-Graph zeigt über 5% im Mittelton) | 1. Hintergrundgeräusche (Klima, Tritte), 2. Interface clippt intern | In ruhiger Umgebung messen, Level prüfen |
| **Zu leises Signal** (Graph < -50 dBFS, Diagnostik funktioniert nicht) | Mic-Gain am Interface zu niedrig | Gain am Preamp hochdrehen (nicht Output Level!) |
| **Inkonsistente Ergebnisse** (Jede Messung sieht anders aus) | Kuppler-Position variiert, IEM rutscht | 5x Sweep nutzen (Averaging), IEM mit Blu-Tack fixieren |
| **Treble-Peaks bei 8 kHz** (Scharfer Peak bei 8 kHz) | IEC-711 Kuppler-Eigenresonanz (normal!) | Das ist normal, kein Defekt. IEC Guide (Depth-Tool) nutzen, um Einstecktiefe zu kalibrieren |

## 16. Weitere Fehlerbehebung & Best Practices (WICHTIG!)

### 1. Mein Frequenzgang ist ein perfekt gerader Strich!
Wenn Sie nach dem Sweep eine fast perfekt flache, gerade Linie sehen, liegt dies in 99% der Fälle an **Betriebssystem-Filtern** (AGC / Auto-Gain / Voice Isolation):
- **macOS:** Klicken Sie oben rechts im Control Center auf das gelbe Mikrofon-Symbol und stellen Sie den Modus unbedingt auf **"Standard"** (NICHT "Sprachisolation").
- **Windows:** Deaktivieren Sie unter den Sound-Einstellungen des Mikrofons alle "Audio-Verbesserungen" (Audio Enhancements).
Diese Filter versuchen den extrem lauten Sweep künstlich leise zu regeln (Kompression) und zerstören so das Messsignal komplett, was zu einer völlig falschen, geraden Linie führt.

### 2. Warnung: "Signal too quiet" trotz hoher Lautstärke
Die Software gibt den Sweep absichtlich sehr leise aus (-20 dBFS), um zu verhindern, dass Ihr Mikrofon übersteuert. Ein In-Ear-Monitor erzeugt in einem abgedichteten Silikon-Coupler ohnehin über 115 dB SPL! Ein voll ausgesteuerter Sweep (0 dBFS) würde den ADC (Analog-Digital-Wandler) Ihrer Soundkarte zum "Clippen" bringen, was wiederum eine komplett flache, verfälschte Kurve erzeugt. Wenn das Signal zu leise ist, erhöhen Sie stattdessen den Gain am Mikrofon-Interface.

### 3. Understanding THD & Waterfall (CSD) Diagnostics

#### 1. THD Crossover Hump (Balanced Armatures):
Wenn bei Multi-BA In-Ears im Bereich von 300-500 Hz die THD-Werte auf z.B. 4% ansteigen, ist das KEIN Fehler in der Software. Das ist die physikalische Realität der Frequenzweiche (Crossover-Point), wo die Treiber elektrisch gegeneinander arbeiten. Dies ist völlig normal.

#### 2. THD Sub-Bass Limit:
BA-Treiber haben im Gegensatz zu dynamischen Treibern fast keinen mechanischen Hubraum. Wenn die App im Sub-Bass (z.B. 50 Hz) hohe THD-Werte (z.B. 5-10%) anzeigt, liegt das an der mangelnden Exkursionsfähigkeit der BA-Treiber bei hohen Pegeln. Auch das ist physikalisch korrekt und ein typisches Merkmal von BA-IEMs. Tipp: Mit einem geringeren Level (Ausgangslautstärke) messen verringert die Verzerrung! (Hinweis: Reduzieren Sie den Output Level, nicht den Mic-Gain.)

#### 3. Reading the Waterfall (CSD):
Das Waterfall-Diagramm (Cumulative Spectral Decay) zeigt das Ausklingen von Resonanzen über die Zeit. Es ist als echte "2D Spectral Decay"-Topographie aufgebaut. Die harten schwarzen Konturlinien repräsentieren verschiedene Zeit-Ebenen (Time Slices). Die Linien fallen organisch nach unten ab, weil das Signal mit der Zeit leiser wird. Wenn eine Resonanz nicht sofort abfällt, sehen Sie einen markanten "Grat" oder "Bergkamm", der lange stehen bleibt.

---

## 17. Haftungsausschluss & Hardware-Sicherheit (WICHTIG!)

Neben der Software besteht das InEar Snitch System aus physischen 3D-Druckteilen (TPU-Einlagen) und gegossenen Silikon-Adaptern. Bitte beachten Sie zwingend die folgenden Hinweise zur Hardware:

### Haftungsausschluss (Schäden an In-Ears)
> **Die Nutzung der Adapter und der Messvorrichtung erfolgt auf eigene Gefahr.**  
> Wenden Sie beim Einspannen der In-Ear-Monitore (insbesondere bei empfindlichen Custom In-Ears aus Acryl) niemals Gewalt an. Achten Sie darauf, die Schallröhrchen (Nozzles) nicht zu verkanten. **Wir haften nicht für mechanische oder kosmetische Schäden an Ihren In-Ear-Monitoren.**

### Materialien & Verträglichkeit
- **Peli-Insert / Wippe:** Das Hauptgehäuse besteht aus **TPU 95A** (Thermoplastisches Polyurethan). Es ist robust, dämpfend und chemisch stabil. Schützen Sie es jedoch vor extremer Hitze (z.B. im Auto im Hochsommer).
- **Mess-Adapter (Silikon):** Die flexiblen Adapter werden aus **TFC Silikon Kautschuk Typ 9 (Knetsilikon weich Shore 25 1:1)** gefertigt. Dieses additionsvernetzende (Platin-)Silikon gast nicht aus und enthält keine aggressiven Weichmacher oder Essigsäuren. Es ist chemisch neutral und greift den sensiblen Klarlack Ihrer Custom In-Ears nicht an.

### Best Practices für die Hardware
- **Dies ist kein Medizinprodukt:** Das gesamte Kit ist ein Mess-Werkzeug (Jig) und darf unter keinen Umständen in den menschlichen Gehörgang eingeführt werden.
- **Fester Sitz:** Prüfen Sie vor jeder Messung, ob der Silikon-Adapter sicher und bündig auf dem TPU-Pin der Wippe sitzt, damit Ihr In-Ear beim Aufdrücken nicht abrutscht.
- **Reinigung:** Verwenden Sie für die TPU- und Silikon-Teile keine aggressiven Lösungsmittel wie Aceton oder reines Isopropanol. Ein leicht feuchtes Tuch oder Brillenputztuch ist völlig ausreichend.
