import re

with open('manual_de.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the automated diagnostics engine section and replace it with the updated, detailed version.
old_section = r'## 4\. Automated Diagnostics Engine.*?## 5\. History Vault'
new_section = """## 4. Automated Diagnostics Engine (Automatische Fehlerdiagnose)

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

## 5. History Vault"""

content = re.sub(old_section, new_section, content, flags=re.DOTALL)

with open('manual_de.md', 'w', encoding='utf-8') as f:
    f.write(content)
