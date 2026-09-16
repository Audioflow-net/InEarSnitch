# Realness & Physics Check Rule
**KRITISCHE ANWEISUNG FÜR ALLE AGENTEN:**
Bevor dem User vorgeschlagen wird, ein mechanisches Teil zu drucken ("Starte den Druck", "Slice das Modell"), MUSS zwingend ein "Realness Check" (virtuelle Physik-Simulation) durchgeführt werden.

Der Agent muss folgende Faktoren zwingend mathematisch und logisch prüfen und das Ergebnis im Chat posten:
1. **Hubweg & Kinematik (Stroke):** Reicht die absolute Länge/Bewegungsfreiheit der Bauteile physikalisch aus, um das Ziel zu erreichen? (Bsp: Ist ein Gurt überhaupt lang genug, um ein Objekt aus einem Schacht zu heben, oder spannt er sich vorher auf?)
    * **Regel:** Bei Rotationen (Hebel/Wippen) kippen hohe Bauteile beim Schwingen kreisförmig nach hinten. Cutouts für den Schwingweg (Sweep) MÜSSEN zwingend über einen `hull()` zwischen Start- und Endwinkel geschnitten werden, nicht als statischer Quader.
    * **Regel:** Schubladen-Effekt (Linear-Sliding) vermeiden! Starre Teile in engen TPU-Schächten verkanten durch hohe Reibung. Klasse-2-Hebel (Scharnier) rollen sauber ab und binden nicht.
2. **Hebelwirkung & Schwerpunkt (Leverage & CoG):** Wo greift die Kraft an? Führt das Ziehen/Drücken zum Kippen, Verkanten oder Blockieren des Objekts?
3. **Material-Mechanik:** Ist das Material (z.B. TPU 95A, 1.6mm dick) flexibel genug oder zu starr für den geplanten Biegewinkel?
    * **Regel:** "Wet Noodle Effect": TPU schluckt Zugkräfte extrem. Für das Herausschieben schwerer oder strammer Objekte (hohe Friktion) MUSS ein starrer Hebel (PETG/PLA) verwendet werden, da TPU-Gurte sich nur dehnen, ohne nennenswerte Kraft zu übertragen.
4. **Kollisionen:** Gibt es beim Bewegen des Teils harte Kollisionen mit anderen Bauteilen?

**Bedingung:** Erst wenn diese Punkte durchgerechnet wurden und das Design in der realen physikalischen Welt Sinn ergibt, darfst du den User zum Drucken auffordern. Keine reinen Geometrie-Blindflüge mehr!
