# Modern UI Redesign Plan (No more 1995 Neon Box)

1. **`theme.py` (MusicianCard Styling)**: 
   Ich entferne den harten, altmodischen Cyan-Kasten. Stattdessen nutze ich ein sehr modernes Design-Pattern: Die Karte bekommt im selektierten Zustand eine weiche Hintergrund-Hervorhebung (`bg_hover`) und einen fetten, edlen Accent-Balken (4px) am linken Rand (`border-left`), während der Rest des Rahmens subtil grau bleibt. Das sieht aus wie in modernen SaaS-Apps (Notion, Slack).

2. **`main.py` (Avatar Buttons in MusicianCard)**:
   Die runden Buttons ("P", "S", "O") nutzen aktuell auch noch gehardcodete, neon-cyanfarbene Styles (`#00FFFF`). Ich stelle sie auf das gleiche QSS-Klassensystem um (`avatar_btn`). Dadurch wirken auch sie edler und passen sich automatisch an Light/Dark-Mode an, statt wie 90er-Jahre-Buttons zu leuchten.

## WICHTIG FÜR ALLE AGENTEN:
Lies vor JEDER Konstruktion zwingend die `HARDWARE_CONSTRAINTS.md` im Projektordner. Dort stehen die absolut kritischen physikalischen Limits (wie das 13 mm Loch der Überwurfmutter), die niemals gebrochen werden dürfen!

## LÜCKENLOSE MITSCHRIFT (Hardware)
Jede CAD-Änderung an Adaptern, Formen oder dem Case MUSS ab sofort zwingend in der Datei `/Users/ben/Desktop/InEarSnitch/CHANGELOG.md` dokumentiert werden! Begründung, altes Maß und neues Maß müssen notiert sein.
