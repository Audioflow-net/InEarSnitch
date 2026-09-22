import sqlite3
import numpy as np

class DatabaseManager:
    def __init__(self, db_path="inearsnitch.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Core entity: Musician
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Musicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                band TEXT,
                notes TEXT,
                profile_pic TEXT
            )
        """)
        
        # Safe migration for existing databases
        try:
            cursor.execute("ALTER TABLE Musicians ADD COLUMN notes TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE Musicians ADD COLUMN profile_pic TEXT")
        except sqlite3.OperationalError:
            pass
        # In-Ear Monitors assigned to musicians
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS IEM_Models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musician_id INTEGER,
                model_name TEXT NOT NULL,
                serial_number TEXT,
                contact_person TEXT,
                service_notes TEXT,
                iem_pic TEXT,
                abbreviation TEXT,
                custom_name TEXT DEFAULT '',
                color TEXT DEFAULT '#2a2a2a',
                FOREIGN KEY (musician_id) REFERENCES Musicians (id)
            )
        """)
        
        try:
            cursor.execute("ALTER TABLE IEM_Models ADD COLUMN color TEXT DEFAULT '#2a2a2a'")
        except sqlite3.OperationalError:
            pass
        
        # TipProfiles entity for coupler ear tips catalog (ProKit)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TipProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                material TEXT,
                color_hex TEXT,
                icon_char TEXT,
                is_default INTEGER DEFAULT 0
            )
        """)

        # Migration: ensure description column exists in TipProfiles
        cursor.execute("PRAGMA table_info(TipProfiles)")
        tp_cols = [c[1] for c in cursor.fetchall()]
        if "description" not in tp_cols:
            try:
                cursor.execute("ALTER TABLE TipProfiles ADD COLUMN description TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass

        # Populate or update TipProfiles with the 7 real tips deterministically with IDs 1 to 7
        default_tips = [
            # id=1 MUST be "Unknown" (legacy fallback) — DO NOT CHANGE
            (1, "Unknown", "Legacy measurement without tip info", "", "#444444", "?", 0),
            (2, "No Tip", "Measured directly without tip", "", "#555555", "○", 0),
            (3, "V26 Straight", "Bester Allrounder — gerade 90°-Kante", "Silicone", "#22c55e", "▮", 1),
            (4, "V27 Rounded", "Komfort-Update — 2mm Abrundung an der Spitze", "Silicone", "#3b82f6", "▮", 0),
            (5, "V29-C Cone", "Konisch zulaufend — extremer Seal durch tiefes Einpressen", "Silicone", "#f97316", "◆", 0),
            (6, "V30-C Pro", "9mm Torus-Lippe, 4mm Loch — Stabilitäts-Upgrade", "Silicone", "#3b82f6", "◉", 0),
            (7, "V31-XL Panzer", "10mm Lippe, 6mm Loch — für fette Custom In-Ears", "Silicone", "#f97316", "◉", 0),
        ]
        for tip in default_tips:
            cursor.execute("""
                INSERT INTO TipProfiles (id, name, description, material, color_hex, icon_char, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    material=excluded.material,
                    color_hex=excluded.color_hex,
                    icon_char=excluded.icon_char,
                    is_default=excluded.is_default
                WHERE TipProfiles.name IN ('', 'Unknown', 'No Tip', 'Standard Foam', 'ProKit V1', 'ProKit V2', 'V26 Straight', 'V27 Rounded', 'V29-C Cone', 'V30-C Pro', 'V31-XL Panzer')
            """, tip)

        # Historical measurements for reference overlays
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iem_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                gain_db TEXT,
                frequencies BLOB,
                magnitude_l BLOB,
                magnitude_r BLOB,
                phase_l BLOB,
                phase_r BLOB,
                notes TEXT,
                photo_path TEXT,
                tip_id INTEGER DEFAULT 1,
                FOREIGN KEY (iem_id) REFERENCES IEM_Models (id),
                FOREIGN KEY (tip_id) REFERENCES TipProfiles (id)
            )
        """)
        
        # Idempotent migration for existing and legacy databases
        for col_def in [
            "gain_db TEXT",
            "phase_l BLOB",
            "phase_r BLOB",
            "notes TEXT",
            "photo_path TEXT",
            "tip_id INTEGER DEFAULT 1 REFERENCES TipProfiles(id)",
        ]:
            try:
                cursor.execute(f"ALTER TABLE Measurements ADD COLUMN {col_def}")
            except sqlite3.OperationalError:
                pass

        # Legacy backfill: assign existing measurements to Unknown (id=1)
        try:
            cursor.execute("UPDATE Measurements SET tip_id = 1 WHERE tip_id IS NULL")
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        conn.close()

    def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path="", tip_id=1):
        """Saves a measurement directly as binary numpy arrays for maximum efficiency."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert None to empty bytes for partial saves
        ml = mag_l.tobytes() if mag_l is not None else b''
        mr = mag_r.tobytes() if mag_r is not None else b''
        pl = phase_l.tobytes() if phase_l is not None else b''
        pr = phase_r.tobytes() if phase_r is not None else b''
        
        f_bytes = freqs.tobytes() if freqs is not None else b''
        
        actual_tip_id = tip_id if tip_id is not None else 1
        
        cursor.execute("""
            INSERT INTO Measurements 
            (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path, tip_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (iem_id, gain_db, 
              f_bytes, ml, mr, pl, pr, notes, photo_path, actual_tip_id))
              
        conn.commit()
        conn.close()

    def load_reference_measurement(self, iem_id):
        """Loads the most recent measurement for a given IEM to serve as a reference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT frequencies, magnitude_l, magnitude_r, gain_db
            FROM Measurements
            WHERE iem_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (iem_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            freqs = np.frombuffer(row[0], dtype=np.float64) if row[0] else None
            mag_l = np.frombuffer(row[1], dtype=np.float64) if row[1] else None
            mag_r = np.frombuffer(row[2], dtype=np.float64) if row[2] else None
            gain_db = row[3] if row[3] else ""
            return freqs, mag_l, mag_r, gain_db
            
        return None, None, None, ""

    def get_all_tips(self, include_unknown=True):
        """Returns all ear tips from the catalog as a list of dicts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if include_unknown:
                cursor.execute("SELECT id, name, description, material, color_hex, icon_char, is_default FROM TipProfiles ORDER BY id ASC")
            else:
                cursor.execute("SELECT id, name, description, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id != 1 ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2] if r[2] is not None else "",
                    "material": r[3],
                    "color_hex": r[4],
                    "icon_char": r[5],
                    "is_default": bool(r[6])
                }
                for r in rows
            ]
        finally:
            conn.close()

    def get_last_used_tip(self, iem_id):
        """
        Returns the ID of the most recently used known tip for the specified IEM.
        Excludes 'Unknown' (id=1) and NULL. Returns None if no known tip measurement exists.
        """
        if not iem_id:
            return None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT tip_id 
                FROM Measurements 
                WHERE iem_id = ? AND tip_id IS NOT NULL AND tip_id != 1
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
            """, (iem_id,))
            row = cursor.fetchone()
            return int(row[0]) if row and row[0] is not None else None
        finally:
            conn.close()

    def get_reproducibility_scores(self, iem_id, tip_id):
        """
        Computes the reproducibility score (mean standard deviation in dB) band-limited to 20-8000 Hz.
        Left and Right channels are computed strictly separately.
        Requires >= 5 measurements per channel (returns None if < 5).
        Sets is_preliminary = True if 5 <= count < 10, False if count >= 10.
        """
        if not iem_id or not tip_id:
            return None
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        curves_l = []
        curves_r = []
        common_grid = np.linspace(20.0, 8000.0, 800)
        
        for r in rows:
            f_blob, ml_blob, mr_blob = r[0], r[1], r[2]
            if not f_blob:
                continue
            try:
                f = np.frombuffer(f_blob, dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) < 10:
                continue
                
            mask = f <= 8000.0
            if not np.any(mask):
                continue
            f_sub = f[mask]
            if len(f_sub) < 2:
                continue
            
            if ml_blob:
                try:
                    ml = np.frombuffer(ml_blob, dtype=np.float64)
                    if len(ml) == len(f) and len(ml) >= 10:
                        curves_l.append(np.interp(common_grid, f_sub, ml[mask]))
                except Exception:
                    pass
                    
            if mr_blob:
                try:
                    mr = np.frombuffer(mr_blob, dtype=np.float64)
                    if len(mr) == len(f) and len(mr) >= 10:
                        curves_r.append(np.interp(common_grid, f_sub, mr[mask]))
                except Exception:
                    pass
                    
        def calc_channel_score(curves):
            n = len(curves)
            if n < 5:
                return None
            mat = np.array(curves)
            std_per_bin = np.std(mat, axis=0, ddof=0)
            mean_std = float(round(float(np.mean(std_per_bin)), 2))
            return {
                "score": mean_std,
                "std_dev": mean_std,
                "count": n,
                "is_preliminary": bool(n < 10)
            }
            
        res_l = calc_channel_score(curves_l)
        res_r = calc_channel_score(curves_r)
        
        if res_l is None and res_r is None:
            return None
            
        return {
            "left": res_l,
            "right": res_r
        }

    def get_seal_history(self, iem_id, tip_id):
        """
        Calculates historical acoustic seal (40 Hz vs 500 Hz delta) from stored BLOBs.
        Left and Right channels are computed strictly separately.
        """
        if not iem_id or not tip_id:
            return {"left": [], "right": []}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, timestamp, frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        history_l = []
        history_r = []
        
        for r in rows:
            meas_id, ts, f_blob, ml_blob, mr_blob = r[0], r[1], r[2], r[3], r[4]
            if not f_blob:
                continue
            try:
                f = np.frombuffer(f_blob, dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) < 10:
                continue
                
            mask_40 = (f >= 35.0) & (f <= 45.0)
            mask_500 = (f >= 450.0) & (f <= 550.0)
            if not np.any(mask_40) or not np.any(mask_500):
                continue
                
            if ml_blob:
                try:
                    ml = np.frombuffer(ml_blob, dtype=np.float64)
                    if len(ml) == len(f) and len(ml) >= 10:
                        val_40 = float(np.mean(ml[mask_40]))
                        val_500 = float(np.mean(ml[mask_500]))
                        delta = val_40 - val_500
                        delta_db = float(round(delta, 2))
                        seal_ok = bool(delta_db >= -11.8)
                        history_l.append({
                            "id": meas_id,
                            "timestamp": str(ts) if ts is not None else "",
                            "delta_db": delta_db,
                            "val_40": float(round(val_40, 2)),
                            "val_500": float(round(val_500, 2)),
                            "seal_ok": seal_ok,
                            "status": "OK" if seal_ok else "LEAK"
                        })
                except Exception:
                    pass
                    
            if mr_blob:
                try:
                    mr = np.frombuffer(mr_blob, dtype=np.float64)
                    if len(mr) == len(f) and len(mr) >= 10:
                        val_40 = float(np.mean(mr[mask_40]))
                        val_500 = float(np.mean(mr[mask_500]))
                        delta = val_40 - val_500
                        delta_db = float(round(delta, 2))
                        seal_ok = bool(delta_db >= -11.8)
                        history_r.append({
                            "id": meas_id,
                            "timestamp": str(ts) if ts is not None else "",
                            "delta_db": delta_db,
                            "val_40": float(round(val_40, 2)),
                            "val_500": float(round(val_500, 2)),
                            "seal_ok": seal_ok,
                            "status": "OK" if seal_ok else "LEAK"
                        })
                except Exception:
                    pass
                    
        return {
            "left": history_l,
            "right": history_r
        }

    def get_tip_target_peak(self, iem_id, tip_id):
        """
        Extracts tip-specific 8 kHz resonance peak (in 6-10 kHz zone) across stored BLOBs.
        Returns median peak frequency for Left and Right separately.
        """
        if not iem_id or not tip_id:
            return {"left": None, "right": None}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT frequencies, magnitude_l, magnitude_r
                FROM Measurements
                WHERE iem_id = ? AND tip_id = ?
                ORDER BY timestamp ASC, id ASC
            """, (iem_id, tip_id))
            rows = cursor.fetchall()
        finally:
            conn.close()
            
        peaks_l = []
        peaks_r = []
        for r in rows:
            if not r[0]:
                continue
            try:
                f = np.frombuffer(r[0], dtype=np.float64)
            except Exception:
                continue
            if f is None or len(f) < 10:
                continue
            
            mask = (f >= 6000.0) & (f <= 10000.0)
            if not np.any(mask):
                continue
            sub_f = f[mask]
            
            if r[1]:
                try:
                    ml = np.frombuffer(r[1], dtype=np.float64)
                    if len(ml) == len(f) and len(ml) >= 10:
                        peaks_l.append(float(sub_f[np.argmax(ml[mask])]))
                except Exception:
                    pass
            if r[2]:
                try:
                    mr = np.frombuffer(r[2], dtype=np.float64)
                    if len(mr) == len(f) and len(mr) >= 10:
                        peaks_r.append(float(sub_f[np.argmax(mr[mask])]))
                except Exception:
                    pass
                    
        return {
            "left": round(float(np.median(peaks_l)), 1) if peaks_l else None,
            "right": round(float(np.median(peaks_r)), 1) if peaks_r else None
        }
