# Hardware Constraints & Dimension Registry (InEar Snitch)

Dieses Dokument ist die **Single Source of Truth** für alle physikalischen Maße und Restriktionen. 
**Jeder KI-Agent MUSS diese Maße zwingend berücksichtigen.**

## 1. IEC711 Coupler (Messkupplung) - "The Golden V26 Dimensions"
*Basierend auf den in der Praxis getesteten, perfekten V26_MASTER Drucken.*

- **Überwurfmutter (Nut) Durchlass:** **13.0 mm** (CAD-Maß).
  - *Regel:* Der Schaft von Adaptern, der durch die Mutter geht, wird im CAD exakt auf **13.0 mm** konstruiert (dies liefert beim FDM-Druck den perfekten Fit).
- **Base/Flansch (unter der Mutter):** **20.0 mm** Durchmesser.
  - *Regel:* Die Sockelplatte wird exakt auf **20.0 mm** konstruiert.
- **Mikrofon-Messkanal (Mic Hole):** **7.5 mm** Durchmesser.
  - *Regel:* Das Loch, das über das Mikrofon gestülpt wird, benötigt **7.5 mm** im CAD für einen geschmeidigen Fit in der Realität.

## 2. CIEMs (Custom In-Ear Monitors)
- **Düsendurchmesser (Nozzles):** Variieren extrem zwischen **5 mm und 12+ mm**.
- **Form:** Anatomisch unregelmäßig, oft abgewinkelt geschnitten.
- *Regel:* Keine harten, flachen Anschlag-Stufen (Hard-Stops) im Messkanal verbauen (Wedge-Gap Gefahr). Ein gerader Grip-Schaft (7mm bis 10mm) ist ideal für Halt.

## 3. Silikon-Gussform (Mold) Spezifikationen
- **Außenmaß der Form (Mold Block):** 40 x 40 mm.
- **Einwurf-Hülse (Sleeve) Innenmaß:** 40 x 40 mm.
- **Materialverhalten (Silikon):** Shore 25 Silikon ist extrem dehnbar. Ein 7.0 mm Loch reicht für sehr dicke CIEMs.
- *Regel für Guss-Stempel:* Keine Hinterschnitte in starren Formen. Der Stempel zentriert sich am Außenrand (39.5 mm Deckelplatte) in der Hülse, um Volumenverdrängung zu vermeiden.
