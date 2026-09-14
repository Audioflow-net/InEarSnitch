---
name: 3D CAD Work Paper Rule
description: Enforces a strict, gapless history of dimensions, shapes, and ideas for all 3D printing tasks.
trigger: always_on
---

# 3D Printing & CAD Work Paper Rule
**KRITISCHE ANWEISUNG FÜR ALLE AGENTEN:**
Sobald es in einer Aufgabe um 3D-Druck, OpenSCAD-Code oder physikalische Bauteile geht, ist eine lückenlose Historie (ein "Work Paper") absolute PFLICHT. 

Wir raten nicht mehr und verlieren keine alten Maße aus den Augen. Jede Änderung an Hardware muss zwingend in der Datei `/Users/ben/Desktop/InEarSnitch/CHANGELOG.md` (unserem Work Paper) dokumentiert werden.

Bei JEDER Modifikation an einem 3D-Modell musst du dieses Work Paper updaten und exakt Folgendes protokollieren:
1. **Version / Datum:** (z.B. V28 - YYYY-MM-DD)
2. **Das betroffene Bauteil:** (z.B. Silikon-Gussform Stempel, TPU Tip)
3. **Maße (Alt vs. Neu):** (z.B. "Schaftdurchmesser von 17.5 mm auf exakt 13.0 mm reduziert")
4. **Formen-Änderung:** (Spezifische Geometrie-Anpassungen, z.B. "Entlüftungslöcher nach innen verschoben")
5. **Die Idee / Der Grund:** Warum wurde das geändert? (z.B. "Rückschritt auf V1-Größe (34x34 mm), weil dies massiv Druckzeit und Filament spart und der Formblock kompakt genug ist.")

**Bedingung:** Ohne einen entsprechenden Eintrag in das Work Paper darf kein aktualisierter CAD-Code an den User übergeben werden.
