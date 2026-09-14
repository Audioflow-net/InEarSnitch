# DESIGN-SPEZIFIKATION & ARCHITEKTUR: Peli 1020 TPU Insert (Audio Diagnostics)

**WICHTIGE REFERENZ FÜR ALLE ENTWICKLER & KI-AGENTEN:** 
Lies dieses Basis-Dokument sorgfältig durch, bevor du Änderungen an `Peli1020_TPU_Insert_V30.scad` vornimmst. Dieses Bauteil besitzt extrem präzise mechanische Abhängigkeiten, die in über 115 Iterationen perfektioniert wurden. Diese Dokumentation dient als langfristiges Regelwerk für die Geometrie.

## 1. Kern-Mechanik: Push-to-Eject Wippe (Mic-Ramp)
Damit das Mikrofon (IEC711 Coupler) ohne Werkzeug entnommen werden kann, fungiert das TPU-Inlay als Wippe.
* **Die Rampe (`ramp_pocket`)**: Startet ganz links bei `X=9.65` auf einer Tiefe von **`Z=2.0`** (Maximaler Tiefgang). Sie steigt organisch an und endet exakt bei `X=75.65` (auf Höhe `Z=14.12` = Unterkante des Mikrofons).
* **Der Pivot-Block (Hebelpunkt)**: Zwischen `X=75.65` und `X=87.65` (Start des dicken Korpus) liegt massives, flaches TPU. Dieser 12mm lange Block ist zwingend erforderlich, damit der Schaft beim Drücken einen harten Drehpunkt hat. 
* **Ergebnis**: Drückt man die Spitze (links) um 12,1mm nach unten, hebt sich der dicke Korpus (rechts) um 7,5mm aus der Form (insgesamt ragt er dann ca. 15mm heraus und lässt sich perfekt greifen).
* **WICHTIG**: Der PETG-Support-Block B (unter dem Mic) wurde auf `Z=2.0` abgesenkt, um diesen enormen Tiefgang der Rampe zu ermöglichen! Nicht wieder erhöhen!

## 2. Kabel-Geometrie (Das harmonische L)
Der User hasst "wilde" oder unsaubere Überschneidungen. Alle Kanäle sind geometrisch exakt konstruiert, inklusive 6mm Wannen-Boden (`br=6`) und 2mm Top-Chamfer.
* **Vertikaler Kanal**: Breite = 15.0mm (exakt passend zum Mic-Schaft). Geht von `X=9.65` bis `24.65`.
* **Horizontales Hauptfach**: Breite = 24.0mm. Startet ebenfalls bei `X=9.65`.
* **Außen-Ecken (Links)**: Damit die linke Außenkante identisch zur rechten Kante aussieht (gerader Rand mit engen Ecken), haben BEIDE Kanäle einen Eckradius von exakt **`R=6.0`**. Keine riesigen "Pill-Shapes"!
* **Innen-Radius (Der TPU-Mittelstreifen)**: Die massive TPU-Wand ("Halbinsel") zwischen Mic-Rampe und Hauptfach ist 10mm breit (`Y=52.65` bis `62.65`) und endet bei `X=24.65`. Ihre Spitze wird durch eine exakt platzierte 10x10 Wanne (`R=5.0`, `br=5.0`) zu einem perfekten Halbkreis abgerundet. Dadurch verschmelzen die Böden nahtlos.

## 3. TPU Tower Sleeve & BNC Connector
Die rechte Seite des Mikrofons (BNC) steckt in einem runden Tower. 
* **Das Problem**: Die seitlichen Bajonett-Flügel (Lugs) des BNC-Steckers bleiben beim Einstecken hängen.
* **Die Lösung (Die 4 Flutes)**: Im inneren Zylinder (`d=14.0`) des Towers sind vier Rillen/Flutes (Radius `r=1.75`) bei den Radien +6.0, -6.0 in X und Y eingelassen. Die Lugs können reibungslos durchgleiten, aber 80% der TPU-Wand bleiben intakt für einen brutalen Grip am glatten Schaft.
* Die Sleeve-Höhe muss zwingend bei `Z=17.5` enden ("Fliegender Deckel" Bug gefixt).

## 4. Tip-Halter (Silikon-Aufsätze)
* 3 Halter im unteren Bereich. Abgerückt auf `tip_y = 15.0` für ausreichend Wandstärke zum Hauptfach.
* **Außenkante**: 20.5mm Durchmesser. Zwingend **ohne Fase (scharfe 90-Grad-Kante)**, da die Silikon-Tips sonst von der Schräge abrutschen.
* **Innerer Pin**: Erhöht auf 6.0mm Durchmesser für massiven Grip in den Tips. Nur ganz oben gibt es eine 1.0mm Fase zum leichteren Aufstecken.

## 5. Support-freie Druck-Features (Balconies)
* Um das riesige Hauptfach ohne Support drucken zu können, gibt es 6 `wedge_tab` Balkone an den Wänden (im Raster `X = 35.0, 57.5, 80.0`).
* Sie sind im 45-Grad-Winkel modelliert. Sie helfen nicht nur beim 3D-Druck, sondern fungieren gleichzeitig als geniale Kabel-Niederhalter (Clips)!

## 6. Design-Philosophie (User-Vorgaben)
1. **Kein Lazy-Design**: Keine einfachen, scharfen Zylinder-Löcher. Alles muss weich ineinanderfließen (Wannenböden, Chamfers).
2. **Symmetrie**: Formen müssen klare Fluchten haben.
3. **Funktionalität**: Der Grip (Sleeve, Wippen-Schultern) hat höchste Priorität.
