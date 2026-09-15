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
        
        # Historical measurements for reference overlays
        # cursor.execute("DROP TABLE IF EXISTS Measurements")
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
                FOREIGN KEY (iem_id) REFERENCES IEM_Models (id)
            )
        """)
        
        try:
            cursor.execute("ALTER TABLE Measurements ADD COLUMN notes TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE Measurements ADD COLUMN photo_path TEXT")
        except:
            pass
        
        conn.commit()
        conn.close()

    def save_measurement(self, iem_id, freqs, mag_l, mag_r, phase_l, phase_r, gain_db="", notes="", photo_path=""):
        """Saves a measurement directly as binary numpy arrays for maximum efficiency."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert None to empty bytes for partial saves
        ml = mag_l.tobytes() if mag_l is not None else b''
        mr = mag_r.tobytes() if mag_r is not None else b''
        pl = phase_l.tobytes() if phase_l is not None else b''
        pr = phase_r.tobytes() if phase_r is not None else b''
        
        f_bytes = freqs.tobytes() if freqs is not None else b''
        
        cursor.execute("""
            INSERT INTO Measurements 
            (iem_id, gain_db, frequencies, magnitude_l, magnitude_r, phase_l, phase_r, notes, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (iem_id, gain_db, 
              f_bytes, ml, mr, pl, pr, notes, photo_path))
              
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
