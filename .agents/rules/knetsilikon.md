---
description: "Regeln für das CAD-Design von Gussformen für zähes Knetsilikon"
trigger: "path: *.scad"
---
# Knetsilikon (Silicone Putty) CAD-Regeln

1. **Micro-Flash Venting & Makellose Tamper:** 
   Nutze NIEMALS vertikale Löcher (Tentakel reißen ab). Nutze NIEMALS horizontale Entlüftungsrillen am Tamperboden (das ruiniert die plane Dichtfläche zum Mikrofon). Der pressende Tamperboden MUSS 100% spiegelglatt sein. Das Silikon entweicht unter dem massiven Druck der Keilpresse von selbst als "Micro-Flash" über die Trennnähte der Formblöcke.

2. **Druckaufbau (Mechanisch statt Handkraft):** 
   Knetsilikon ist zu zäh, um per Hand blasenfrei gepresst zu werden. Gussformen benötigen externe Press-Mechanismen (z.B. eine Keil-Presse V3 mit schwimmender Druckplatte) mit enormem mechanischen Vorteil.

3. **Keine Rotationskräfte (Torsion):** 
   Verwende niemals Schraubkappen, die direkt auf einen Stempel (Piston) drücken. Die Torsionsreibung verdreht das zähe Silikon in der Form und bricht 3D-gedruckte Zentrier-Pins ab. Presskräfte dürfen ausschließlich rein linear (vertikal) erfolgen.

4. **Plane Kraftübertragung (Text gravieren):**
   Text auf pressenden Bauteilen (wie Tamper-Deckeln) MUSS immer mit `difference()` eingraviert werden. Er darf nicht abstehen (`linear_extrude` ohne Abzug), da sonst die Druckplatte der Presse kippelt und die 100% vertikale Krafteinleitung zerstört wird.

5. **Scientific Suites (Parameterisierung):**
   Erstelle für einen Gussform-Block immer mehrere Tamper-Varianten (z.B. mit 4mm, 5mm und 6mm Eintrittsloch für verschiedene In-Ear-Nozzles). So hat der User maximale wissenschaftliche Flexibilität, ohne die großen, zeitaufwändigen Formblöcke neu drucken zu müssen.
