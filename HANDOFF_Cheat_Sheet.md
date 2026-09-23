# HANDOFF: InEar Snitch - Peli 1020 Cheat Sheet & Deckel-Design

## 1. Übersicht & Status
- **Projekt:** Design eines professionellen Referenz-Kärtchens ("Metrology Lab Legend") für den Deckel des Peli 1020 Micro Case.
- **Ziel:** Dem Nutzer einen schnellen Überblick über die 7 mitgelieferten Hardware-Tips (Silikon, Metall, TPU) sowie Software-Zugänge zu geben.
- **Status:** HTML-Prototyp / Druckvorlage (2026 Dark Mode Tech Ästhetik) ist erfolgreich generiert und abgenommen.

## 2. Hardware-Constraints & Maße (Peli 1020)
- **Maximale Bodenmaße:** Exakt **134.2 x 89.8 mm**. (Das Peli 1020 PDF zeigt 142.1 x 97.7 mm an der Öffnung. Über die Tiefe von 18.8mm und den 10° Draft-Angle schrumpft der verfügbare flache Boden im Deckel auf dieses Maß).
- **Eckenradius:** 8.35 mm (am Boden).
- **KRITISCHE KOLLISIONS-WARNUNG (Tower Clearance):** Der innere PETG-Tower des Chassis ragt bei geschlossenem Koffer fast bis an die Decke (die Tower-Höhe liegt nach Kürzungen bei 41.5 mm). Es verbleibt **weniger als 1 mm Luft** bis zum Deckel-Boden. 
- **Fazit:** Jegliche Befestigung des Flyers *muss* ultra-flach sein. Dicke Trägerplatten (z.B. 2mm Forex) blockieren das Schließen des Cases und beschädigen den Tower!

## 3. Befestigung im Deckel (No-Glue Lösungen)
Da der Deckel aus glattem, nacktem Polycarbonat besteht (der abdichtende Gummi/O-Ring sitzt beim Peli 1020 *in der Bodenschale* und kann nicht zum Einklemmen genutzt werden), sind dies die freigegebenen rückstandslosen Befestigungs-Ideen:
1. **Adhäsionsfolie (Static Cling):** Hauchdünne Folie (ca. 0,15 mm). Haftet extrem fest am Deckelplastik rein durch statische Aufladung. Komplett ohne Klebstoff und jederzeit spurlos abziehbar.
2. **Yupo Tako (Mikrosaugnäpfe):** Fühlt sich an wie mattes Papier, haftet über Mikrovakuum an der Rückseite. Zerkratzt nicht und hinterlässt keine Reste.

## 4. Design-System & Layout (8-Slot Grid)
Das Design nutzt einen strengen "2026 Aerospace / Metrology" Look in tiefschwarz mit leuchtenden Akzentfarben. Die Grafiken der Silikon-Tips sind **True CAD Impressions** – sie wurden algorithmisch aus den exakten mathematischen Parametern (Radien, Taper) der `MASTER_Silikon_Formen.scad` extrahiert.

**Das 4x2 Raster beinhaltet:**
- **Slot 1 (Blau):** V27 Classic (Flacher 13mm Standard-Schaft).
- **Slot 2 (Amber):** V29 Cone (Konischer Kern für flache Nozzles).
- **Slot 3 (Smaragd):** V30 Pro Grip (Massiver Reibungsgrip für schlanke Nozzles).
- **Slot 4 (Pink):** V31 XL Panzer (10mm dicke Torus-Lippe gegen Reißen).
- **Slot 5 (Silber):** Metal Base (Die Standard IEC711 Stahl-Referenz).
- **Slot 6 (Grau):** Stock Seal (Die vormontierte Gummikuppel des Couplers).
- **Slot 7 (Lila):** TPU Pancake (Der komplett flache Zero-Distance Adapter ohne Stopper).
- **Slot 8 (Tech/Auth):** Ein UI-Terminal Bereich, der in zwei Sektionen unterteilt ist: 
  - Oben: Ein `PRO LICENSE KEY` Eingabefeld (4 Blöcke).
  - Unten: Ein High-Contrast **QR-Code-Platzhalter** für den Software-Download der "kibatools".

**Branding:** 
Das InEarSnitch Logo (`icon_1024.png`) wurde in seiner aktuellen Form (ohne Text, schwarzer Hintergrund, abgerundetes Rechteck) verwendet und als roher Base64-String direkt in den HTML-Code geschweißt, um Browser-Sicherheitsblockaden in iFrames zu verhindern.

## 5. Nächste Schritte / Produktion
Für den finalen Gang zur Druckerei:
1. HTML-Datei (`Tip_Cheat_Sheet.html`) in Google Chrome öffnen.
2. Via `Drucken -> Als PDF speichern` exportieren.
   * Parameter: Ränder = "Keine", Skalierung = "100%", "Hintergrundgrafiken" = Aktiviert.
3. PDF an eine professionelle Druckerei als **"Freiform-Aufkleber auf Adhäsionsfolie matt"** mit den exakten Schnittmaßen 134.2 x 89.8 mm übergeben.
