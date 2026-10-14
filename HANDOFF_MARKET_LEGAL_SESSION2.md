# HANDOFF: MARKTEINFÜHRUNG & COMPLIANCE, SESSION 2 (Stand 07.10.2026, ca. 19:30)

**Ergänzt:** `HANDOFF_MARKET_LEGAL.md` (Rolle und Phasen 1 bis 4).
**Projekt:** InEar Snitch, physisches IEM-Mess-Set plus Software, Verkauf in Deutschland.
**Rolle des Agenten:** Legal-, Compliance- und Hardware-Business-Experte (EU/DE). Business-Einschätzung, **keine Rechtsberatung**.
**Start-Protokoll:** Die erste Antwort einer neuen Session beginnt laut Nutzerregel mit dem Wort `eisteepfirsich`. Danach direkt zur Sache, keine Begrüßungsfloskeln.

> **Verlässlichkeit:** Vieles stammt aus Websuche-Zusammenfassungen oder Vorwissen. **Belegt** ist nur, was unten unter "Belegte Fakten" steht. Alles andere gilt als **ungeprüft**.

---

## 0. Wichtigste Punkte auf einen Blick

1. **Der "Coupler" ist ein Elektret-Mikrofon im Stahlgehäuse**, kein passives Rohr. Er hat BNC-Anschluss, ein Kabel BNC auf 3,5-mm-Klinke liegt bei. Das ist **Elektronik** und der kritische Punkt des Sets.
2. **Die IHK hat geantwortet** und ein Telefonat für **Do., 08.10.2026, 12 bis 16 Uhr** angeboten. Der Nutzer ruft selbst an (0561 7891-284, Michael Dietzsch, IHK Kassel-Marburg).
3. **Das Interface (LOKUKA LC8) ist registrierungsseitig belegt** (WEEE 55378485). DoC fehlt noch.
4. **Offene Kernfrage:** Gilt der Coupler als Elektrogerät, und bleibt der Nutzer mit Aufkleber und Software in der **Händlerrolle (Fall A)**?
5. **Arbeitspapier für das Telefonat:** `ihk_gespraech_paper.md` im Artefaktordner der Session (Pfad unten).

---

## 1. Der Nutzer und der Kontext

- Name laut IHK-Mail: Degenhardt. Gewerbe **Veranstaltungstechnik** besteht bereits.
- Arbeitet auf einem **Konzert-Kreuzfahrtschiff**, nachts, **Telefonnetz nur im Hafen**. Termine am Telefon deshalb im Hafen planen, sonst schriftlich per E-Mail.
- Will ein **Komplett-Set in einer Kiste** an **Monitor-Operator** verkaufen (Zielgruppe klar), **nicht** nur Software oder Innenleben.
- **Budget:** 1.500 bis 3.000 € Eigenkapital. **Zielpreis höchstens 300 €.** Wenig Bürokratie, kein hartes Vorfinanzieren.
- Wünscht **konkrete Antworten, keine Rückfragen-Schleifen.** Er hat mehrfach kritisiert, die Antworten klängen "schlecht informiert". Daher: belegen, markieren, ehrlich korrigieren.
- Kommuniziert knapp mit Tippfehlern. Im Zweifel großzügig deuten, aber wichtige Annahmen bestätigen lassen.

---

## 2. Das Produkt (Stand jetzt)

| Bestandteil | Beschreibung | Status |
|---|---|---|
| **Coupler / Ohrsimulator-Nachbau** | **Elektret-Mikrofon im Stahlgehäuse** mit BNC. Kabel BNC auf 3,5 mm liegt bei. Strom über Plug-in-Power (ca. 2 bis 5 V), nicht kalibriert. AliExpress "Typ 4". | Hersteller unbekannt, keine WEEE, keine DoC |
| **USB-Adapter** | LOKUKA LC8, USB-C auf zwei 3,5-mm-Buchsen (Kopfhörer und Mikrofon), Marke auf dem Stecker | Registrierung belegt, DoC offen |
| **Adapter, Silikonhalter** | Eigener 3D-Druck und Silikonguss, nur zum Halten des IEM im Coupler, **kein Hautkontakt** | Eigenfertigung |
| **Koffer** | Peli 1020, kleines Logo "InEar Snitch" als Aufkleber | geplant |
| **Software** | InEar Snitch, **separate Download-Lizenz** | Eigenentwicklung |
| **Beipackzettel** | Gehörschutz, Treiberschaden beim Stresstest, kein Medizinprodukt | Entwurf im Chat |

**Maße (aus `HARDWARE_CONSTRAINTS.md`):** Überwurfmutter 13,0 mm, Flansch 20,0 mm, **Mikrofonloch 7,5 mm** ("wird über das Mikrofon gestülpt"), Mold 40 x 40 mm. Das konkrete Coupler-Maß des Typ-4-Muster ist **unbekannt**, bis der Nutzer es misst.

**Nicht im Set:** Funk, Batterie, Netzteil.

**Vermarktung (geplant):** Set heißt beschreibend ("Messkoffer-Set für IEM-Messungen"). Marke nur auf Software, Shop und kleinem Koffer-Aufkleber. **Nicht** verwenden: "System", "kalibriert", "IEC-711-konform", Vergleich mit GRAS/B&K.

---

## 3. Entscheidungen und wie sie zustande kamen

| Thema | Entscheidung / Stand |
|---|---|
| Rolle | Angestrebt: **Händler (Fall A der IHK)**. Marke nur auf Koffer, Karte, Software, nicht auf Elektrogeräten |
| Preis | Höchstens 300 € netto, Wareneinsatz neu gerechnet ca. 100 bis 150 € (mit Peli), ca. 75 bis 115 € mit günstigem Koffer |
| Vertrieb | B2B-Shop, **Vorbestellung** mit 30 bis 50 % Anzahlung und Mindestmenge. **Crowdfunding verworfen** (falsche Zielgruppe, mehr Verbraucherrecht) |
| Finanzierung | Kleine Charge (10 bis 15 Kits), Material aus Anzahlungen |
| Gewerbe | Bestehendes Gewerbe nutzen, Tätigkeit beim Gewerbeamt **erweitern** (Herstellung und Verkauf), Versicherer informieren |
| Marke auf dem Koffer | Kleiner Aufkleber ist **wahrscheinlich unkritisch**, **nicht** auf Interface oder Mikrofon, Anschrift auf Karte oder zweitem Aufkleber |
| 100 Kits aus China | **Verworfen** (Kapitalbedarf grob 11.000 bis 33.000 USD) |
| Eigene Elektronik aus China | **Verworfen** (EMV-Prüfung, RoHS, WEEE: ca. 5.000 bis 10.000 € einmalig) |
| Mikrofon separat kaufen | **Hinfällig**, weil der Coupler selbst das Mikrofon ist |

---

## 4. Korrekturen der Session (damit der nächste Agent sie nicht wiederholt)

1. **"Typ 4 = passives Rohr"** war **falsch**. Es ist ein Elektret-Mikrofon im Stahlgehäuse. Alles, was dazu über "keine CE, keine WEEE, keine Nachweise nötig" gesagt wurde, ist **ungültig**.
2. **"Selbstbau-Set hält dich in der Händlerrolle"** war zu optimistisch. Nach den Suchergebnissen kann eine **Kombination als Funktionseinheit** ein neues Gerät sein. Die IHK bestätigt das als **Fall B**.
3. **Wareneinsatz 150 bis 230 €** war zu hoch (basierte auf Coupler 80 bis 120 €). Die Zahl lieferte das Recherche-Team, ich habe sie nicht an die Einkaufsdaten des Nutzers angepasst.
4. **GPSR bei B2B:** Ein reiner AGB-Hinweis "nur für Unternehmen" reicht nicht. Es braucht eine technische Zugangskontrolle (USt-ID-Pflichtfeld). Die Pflichten gelten, wenn Verbraucher das Produkt vorhersehbar nutzen könnten.
5. **WEEE-Suche:** Die Nummer steht im ear-Register **ohne "DE"-Präfix** (55378485). Die erste Suche mit "DE" lieferte 0 Treffer und führte zu einer unnötigen Warnung.
6. **Primo EM172/EM272** haben ca. 10 mm Durchmesser und passen **nicht** in ein 7,5-mm-Loch (ein Agent behauptete 6 mm).
7. **Recherche-Agenten (Typ `research`) haben nur `search_web`**, kein `read_url_content`. Die Ergebnisse sind Zusammenfassungen ohne Produkt-URLs und Preise. Seiten wie eBay.de blocken den Abruf (HTTP 403). Auf belegte Daten nur verlassen, wenn der Nutzer Screenshots liefert.

---

## 5. Belegte Fakten (vom Nutzer per Screenshot oder PDF bestätigt)

| Fakt | Beleg |
|---|---|
| IHK-Antwort mit Fall A und B, Termin 08.10.2026, 12 bis 16 Uhr | E-Mail von Michael Dietzsch, Referent Innovation und Digitales, IHK Kassel-Marburg |
| Coupler-Listing | AliExpress, Item 1005003442162211, 31,79 €, "Typ 4: Einziges 711-Kunsthohr ohne Kalibrierungsdatei", Typ 5 hat ICP-Vorstufe, Typ 2 "kalibriert + Software" |
| Coupler-Verkäufer | Shenzhen SanLiangSan Electronic Technology Co., Ltd., Longhua District, Shenzhen, gegründet 27.08.2020 (Geschäftsinformationen) |
| Coupler-Bauweise | **Aussage des Nutzers:** Elektret-Mikrofon im Stahlgehäuse, BNC, Kabel BNC auf Miniklinke dabei |
| LOKUKA LC8 | Amazon.de, 7,99 € (Prime), 29 cm, Marke LOKUKA auf dem USB-C-Stecker, Verkäufer XTOP-Digital DE, Versand durch Amazon |
| WEEE für LOKUKA | ear-Register: Nr. **55378485**, Marke **LOKUKA**, "ECOPV-EU GmbH für XTOP DIGITAL (HK) LIMITED", 65760 Eschborn, Kategorie Kleine IKT-Geräte bzw. Kleingeräte, Marktaustritt leer. PDF vom Nutzer erzeugt |

---

## 6. Ungeprüfte Aussagen und Einschätzungen

- **Typische 711-Clones** enthalten eine Elektret-Kapsel mit FET-Vorverstärker, arbeiten mit Plug-in-Power (2 bis 5 V) und sind **nicht IEPE**. BNC auf 3,5 mm deutet auf Elektret hin. Nicht an 48 V Phantomspeisung anschließen (Quelle: ASR/Reddit-Zusammenfassungen).
- **Ob dein Coupler** eine zusätzliche Platine hat, ist unbekannt.
- **Einstufung als Elektrogerät:** Ich halte es für wahrscheinlich, nicht verbindlich. Offen ist auch, ob die EMV-Ausnahme "inhärent harmlos" greift.
- **EU-Händler für einen 711-Clone mit Nachweisen:** nicht gefunden (vier Agenten, alle ohne Seitenzugriff).
- **Alternativen:** Crysound CRY711/718 über GOmeasure.se (Preis auf Anfrage), GRAS ab ca. 1.500 € (Aussage des Nutzers), Norsonic-Tippkemper (DE, auf Anfrage), miniDSP EARS ca. 309 bis 350 € (Kopfhörer-Messkopf, für IEMs fraglich).
- **Fertigung in der EU:** CNC-Dienstleister (Xometry, Protolabs, Laserhub) für ein Rohr nach Zeichnung, Schätzung ca. 40 bis 120 € bei 10 Stück. Für den Coupler als Mikrofon **nicht anwendbar**.
- **Mikrofon-Kandidaten** (hinfällig, falls der Coupler sein Mikrofon enthält): Dayton iMM-6, Rode smartLav+, Sennheiser MKE 1, Boya BY-M1.

---

## 7. Offene Punkte

| # | Punkt | Wer klärt es |
|---|---|---|
| 1 | Gilt der Coupler als **Elektrogerät** (ElektroG, RoHS) und EMV-Gerät? | IHK am 08.10., danach ggf. Bundesnetzagentur und stiftung ear |
| 2 | Bleibt das Set mit Aufkleber und separater Software in **Fall A**? | IHK am 08.10. |
| 3 | **DoC** des LOKUKA LC8 und **EU-Verantwortlicher** (GPSR) | Verkäufer XTOP-Digital DE, Amazon "Sicherheitsbilder und Kontakte" |
| 4 | Hersteller, Material, **Durchmesser des Mikrofonlochs** und Bauweise des Couplers | AliExpress-Verkäufer |
| 5 | Pinbelegung und Bias an der LC8-Mikrofonbuchse (CTIA/OMTP, Spannung) | Test mit Muster |
| 6 | Streuung der Coupler | 5 Muster bestellen und messen |
| 7 | Haftpflicht mit **Produkthaftung** und Heimproduktion | Versicherer |
| 8 | **Gewerbeerweiterung** | Gewerbeamt, nach IHK-Antwort |
| 9 | **EORI-Nummer** und Zolltarifnummer für den Import | Zoll, Spediteur |
| 10 | AGB (B2B, USt-ID-Pflichtfeld), Beipackzettel, Shop-Text | noch zu schreiben, Anwaltscheck ca. 300 € |

---

## 8. Nächste Schritte (empfohlene Reihenfolge)

1. **08.10.2026, 12 bis 16 Uhr:** IHK anrufen (im Hafen). Arbeitspapier benutzen, Antworten eintragen, schriftliche Zusammenfassung erbitten.
2. **Nachricht an den AliExpress-Verkäufer** senden (Hersteller, Material, Bauweise, Versorgung, Mikrofonloch-Durchmesser, Rechnung auf Firma, Preise für 10, 25, 50 Stück). Text liegt im Chat vor.
3. **Nachricht an XTOP-Digital DE** senden (DoC, WEEE, EU-Bevollmächtigter für den LC8).
4. **5 Muster Coupler und 5 LC8** bestellen, am LC8 testen und gegeneinander messen.
5. **Mail an den Versicherer** (Produkthaftpflicht, Heimproduktion). Entwurf liegt im Chat vor.
6. **EORI-Nummer** beantragen (kostenlos, Zoll online), falls Import bestätigt wird.
7. Je nach IHK-Antwort **Weg 1, 2 oder 3** wählen (siehe Abschnitt 9).
8. Danach: AGB und Shop-Text, Beipackzettel finalisieren, Vorbestellung vorbereiten, Anwaltscheck.

---

## 9. Entscheidungswege für den Coupler

| Weg | Inhalt | Auswirkung |
|---|---|---|
| **Weg 1** | Kunde kauft den Coupler selbst, du lieferst Rest und Kaufempfehlung | Keine Elektro-Pflichten für den Coupler, aber kein vollständiges Set |
| **Weg 2** | Du registrierst dich bei der stiftung ear und trägst die Pflichten als Einführer | Aufwand und Kosten (unbekannt, recherchieren, wenn die IHK Elektrogerät bestätigt) |
| **Weg 3** | Lieferant mit EU-Bevollmächtigtem, WEEE-Nr. und DoC | Gesucht, noch nicht gefunden. Möglicher Anker: Crysound über GOmeasure.se (teuer) |

**Falls die IHK sagt "Bauteil / inhärent harmlos":** Der Weg ist frei. Dann reichen Einführerpflichten für ein Bauteil, GPSR-Angaben, Materialnachweis und ehrliche Werbung.

---

## 10. Vorbereitete Texte im Chat (bei Bedarf neu erzeugen oder aus dem Verlauf kopieren)

- Anfrage an die **IHK** (mit bestehendem Gewerbe) und Antwort auf die IHK-Mail (Rückruf im Hafen).
- Fragenkatalog für das Telefonat (jetzt als `ihk_gespraech_paper.md`).
- Anfragen an **Bundesnetzagentur** (EMV) und **stiftung ear** (ElektroG).
- Nachricht an **AliExpress-Verkäufer** (Englisch) und **XTOP-Digital DE** (Deutsch).
- **Mail an den Versicherer** (Produkthaftpflicht).
- **Beipackzettel** (Sicherheitshinweise, Inhalt, Kurzstart).
- Aufkleber-Text für den Koffer.

---

## 11. Dateien und Pfade

| Datei | Pfad |
|---|---|
| Arbeitspapier IHK-Gespräch | `/Users/ben/.gemini/antigravity/brain/08adde73-3c8b-46d4-8299-cf51801182fd/ihk_gespraech_paper.md` |
| Ursprüngliches Handoff | `/Users/ben/Desktop/InEarSnitch/HANDOFF_MARKET_LEGAL.md` |
| Maße und Constraints | `/Users/ben/Desktop/InEarSnitch/HARDWARE_CONSTRAINTS.md` |
| Changelog (CAD-Historie) | `/Users/ben/Desktop/InEarSnitch/CHANGELOG.md` |
| Projektlore | `/Users/ben/Desktop/InEarSnitch/PLAN.md` |

**Projektregeln, die weiterhin gelten:** Audio- und Messcode ist eingefroren (`AGENTS.md`). CAD-Änderungen am Adapter müssen im `CHANGELOG.md` mit Alt/Neu-Maßen dokumentiert werden. Terminal-Befehle immer mit absolutem Pfad vorschlagen.

---

## 12. Empfehlungen für die nächste Session

- **Zuerst** die IHK-Antworten auswerten und auf Weg 1, 2 oder 3 festlegen.
- **Nicht** erneut Recherche-Agenten für Produktsuche losschicken, solange sie kein `read_url_content` haben. Stattdessen mit Screenshots des Nutzers arbeiten oder eigene Abrufe nutzen.
- **Alle Aussagen markieren:** belegt oder ungeprüft. Der Nutzer reagiert empfindlich auf unbelegte Behauptungen.
- **Keine Rückfragenschleifen.** Entscheiden, begründen, Risiko nennen.
- **Kontext kurz halten.** Diese Session war weit über 15 Nachrichten lang. Eine neue Session starten (Cmd+L).
