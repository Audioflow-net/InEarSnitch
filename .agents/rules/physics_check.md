# Realness & Physics Check Rule
**KRITISCHE ANWEISUNG FÜR ALLE AGENTEN:**
Bevor dem User vorgeschlagen wird, ein mechanisches Teil zu drucken ("Starte den Druck", "Slice das Modell"), MUSS zwingend ein "Realness Check" (virtuelle Physik-Simulation) durchgeführt werden.

Der Agent muss folgende Faktoren zwingend mathematisch und logisch prüfen und das Ergebnis im Chat posten:
1. **Hubweg & Kinematik (Stroke):** Reicht die absolute Länge/Bewegungsfreiheit der Bauteile physikalisch aus, um das Ziel zu erreichen? (Bsp: Ist ein Gurt überhaupt lang genug, um ein Objekt aus einem Schacht zu heben, oder spannt er sich vorher auf?)
2. **Hebelwirkung & Schwerpunkt (Leverage & CoG):** Wo greift die Kraft an? Führt das Ziehen/Drücken zum Kippen, Verkanten oder Blockieren des Objekts?
3. **Material-Mechanik:** Ist das Material (z.B. TPU 95A, 1.6mm dick) flexibel genug oder zu starr für den geplanten Biegewinkel?
4. **Kollisionen:** Gibt es beim Bewegen des Teils harte Kollisionen mit anderen Bauteilen?

**Bedingung:** Erst wenn diese Punkte durchgerechnet wurden und das Design in der realen physikalischen Welt Sinn ergibt, darfst du den User zum Drucken auffordern. Keine reinen Geometrie-Blindflüge mehr!
