# InEar Snitch — ProKit Unlock-System

Das ProKit-Feature-Gate ist ein **offline SHA256-Unlock-System** für Bens
custom-designed Ear Tips (Messrack-Aufsätze). Kein Internet erforderlich.

## Aktueller Status

| Was | Wo |
|-----|----|
| 50 Codes generiert | `SNITCH-PROKIT-2024-001` bis `-050` |
| Klartext-Codes | `PROKIT_CODES_SECRET.csv` (.gitignore ✅, NIE committen!) |
| SHA256-Hashes | `config.py` → `VALID_CODE_HASHES` (Set mit 50 Strings) |
| Unlock-Datei | `get_data_dir() + '/.prokit_unlocked'` |
| Code-Generator | `prokit_code_generator.py` (ebenfalls .gitignore ✅) |

## Gate-Pattern (PFLICHT für jedes ProKit-UI-Element)

```python
from config import is_prokit_unlocked
if is_prokit_unlocked():
    # ProKit UI hier hinzufügen
```

Kein ProKit-Feature darf ohne diesen Check sichtbar sein.

## Unlock-Dialog

Triple-Click auf App-Logo (InEar SNITCH Text oben links) →
`open_prokit_unlock_dialog()` in main.py (noch zu implementieren).

## Neue Codes für weitere Lieferungen

```bash
python3 /Users/ben/Desktop/InEarSnitch/prokit_code_generator.py --start 51 --count 50
# → Gibt neue Hashes aus → in config.py unter VALID_CODE_HASHES ergänzen
```

## Geplante DB-Erweiterungen (noch nicht implementiert)

```sql
-- Neue Tabelle (noch zu erstellen):
CREATE TABLE IF NOT EXISTS TipProfiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,        -- z.B. "ProKit V2"
    material TEXT,             -- "TPU", "Foam", "Silicone"
    color_hex TEXT,            -- Für Badge-Farbe in History
    icon_char TEXT,            -- Unicode-Zeichen für Mini-Darstellung
    is_default INTEGER DEFAULT 0
)

-- Measurements-Erweiterung (noch zu migrieren):
ALTER TABLE Measurements ADD COLUMN tip_id INTEGER REFERENCES TipProfiles(id)
```

Migration immer via try/except (bestehende DBs dürfen nicht brechen).
