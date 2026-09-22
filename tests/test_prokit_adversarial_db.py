"""
InEar Snitch ProKit Tip-Tracking — Adversarial Database & Migration Test Suite
=============================================================================

Authored by M2 Empirical Challenger 2.
Adversarially challenges and stress-tests database schema, migrations, idempotency,
query APIs, legacy backfill, orphaned keys, corrupt BLOBs, and concurrent access in database.py.

CRITICAL SAFETY:
All tests strictly execute on temporary databases (tempfile/tmp_path).
NEVER touch production inearsnitch.db.
"""

import os
import sys
import time
import sqlite3
import tempfile
import threading
import unittest
import numpy as np

# Ensure project root is on sys.path
cur = os.path.dirname(os.path.abspath(__file__))
while cur != os.path.dirname(cur):
    if os.path.exists(os.path.join(cur, "database.py")):
        if cur not in sys.path:
            sys.path.insert(0, cur)
        break
    cur = os.path.dirname(cur)

import database


def make_dummy_sweep(n_points=24001, bass_boost=3.0, leak_db=0.0, peak_hz=7850.0):
    freqs = np.linspace(20.0, 24000.0, n_points, dtype=np.float64)
    mag = 90.0 - (freqs / 1000.0) * 0.4
    idx_40 = (freqs >= 35.0) & (freqs <= 45.0)
    mag[idx_40] += (bass_boost - leak_db)
    if peak_hz:
        mag += 6.0 * np.exp(-0.5 * ((freqs - peak_hz) / 450.0) ** 2)
    phase = np.zeros_like(mag)
    return freqs, mag, phase


class TestRepeatedInitAndIdempotency(unittest.TestCase):
    """Scenario 1: Repeated DatabaseManager initialization and schema integrity."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_init_idempotency.db")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_repeated_initialization_100_times(self):
        """Repeated initialization (100 times) must not duplicate seed tips or corrupt schema."""
        for _ in range(100):
            db = database.DatabaseManager(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Verify integrity check
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")

        # Verify TipProfiles count is exactly 7
        cur.execute("SELECT COUNT(*) FROM TipProfiles")
        self.assertEqual(cur.fetchone()[0], 7)

        # Verify Unbekannt is id=1
        cur.execute("SELECT name, material, color_hex, icon_char, is_default FROM TipProfiles WHERE id = 1")
        row = cur.fetchone()
        self.assertEqual(row, ("Unbekannt", "", "#444444", "?", 0))

        # Verify exactly one default tip (V26 Straight)
        cur.execute("SELECT id, name FROM TipProfiles WHERE is_default = 1")
        defaults = cur.fetchall()
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults[0], (3, "V26 Straight"))
        conn.close()

    def test_concurrent_initialization_stress(self):
        """Concurrent DatabaseManager initializations across threads must not cause deadlocks or corruptions."""
        errors = []

        def init_worker():
            try:
                database.DatabaseManager(self.db_path)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=init_worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent init errors: {errors}")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM TipProfiles")
        self.assertEqual(cur.fetchone()[0], 7)
        cur.execute("PRAGMA integrity_check")
        self.assertEqual(cur.fetchone()[0], "ok")
        conn.close()


class TestLargeLegacyMigration(unittest.TestCase):
    """Scenario 2: Large legacy database migration with 1,000+ unmigrated records."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_legacy_large.db")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _create_legacy_db(self, n_records=1000):
        """Creates a legacy database schema before M2 tip_id existed."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE Musicians (id INTEGER PRIMARY KEY, name TEXT)")
        cur.execute("CREATE TABLE IEM_Models (id INTEGER PRIMARY KEY, musician_id INTEGER, model_name TEXT)")
        cur.execute("""
            CREATE TABLE Measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iem_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frequencies BLOB,
                magnitude_l BLOB,
                magnitude_r BLOB
            )
        """)
        f, m, p = make_dummy_sweep(n_points=100)
        fb, mb = f.tobytes(), m.tobytes()

        # Insert records: alternating between with-blobs and empty-blobs
        records = []
        for i in range(n_records):
            if i % 2 == 0:
                records.append((i % 10 + 1, fb, mb, mb))
            else:
                records.append((i % 10 + 1, None, None, None))

        cur.executemany("INSERT INTO Measurements (iem_id, frequencies, magnitude_l, magnitude_r) VALUES (?, ?, ?, ?)", records)
        conn.commit()
        conn.close()

    def test_migration_1000_legacy_records(self):
        """Migrating 1,000 legacy records must backfill all to tip_id=1 within 2.0s."""
        self._create_legacy_db(1000)

        t0 = time.perf_counter()
        db = database.DatabaseManager(self.db_path)
        elapsed = time.perf_counter() - t0

        self.assertLess(elapsed, 2.0, f"Migration took too long: {elapsed:.3f}s")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Verify 1000 records all have tip_id = 1
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id = 1")
        self.assertEqual(cur.fetchone()[0], 1000)

        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id IS NULL")
        self.assertEqual(cur.fetchone()[0], 0)

        # PRAGMA check
        cur.execute("PRAGMA table_info(Measurements)")
        cols = {row[1]: row for row in cur.fetchall()}
        self.assertIn("tip_id", cols)
        self.assertIn(str(cols["tip_id"][4]), ("1", "'1'"))
        conn.close()

    def test_migration_5000_legacy_records_stress(self):
        """Stress migration with 5,000 legacy records ensures stability and correct backfill."""
        self._create_legacy_db(5000)

        t0 = time.perf_counter()
        db = database.DatabaseManager(self.db_path)
        elapsed = time.perf_counter() - t0

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id = 1")
        self.assertEqual(cur.fetchone()[0], 5000)
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id IS NULL")
        self.assertEqual(cur.fetchone()[0], 0)
        conn.close()


class TestPreExistingCustomTipProfiles(unittest.TestCase):
    """Scenario 3: Pre-existing custom TipProfiles table preserving id=1 without being overwritten."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_custom_tips.db")

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_pre_existing_id1_custom_preserved(self):
        """If a database already has TipProfiles with id=1 as a custom tip, it must NOT be overwritten."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE TipProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                material TEXT,
                color_hex TEXT,
                icon_char TEXT,
                is_default INTEGER DEFAULT 0
            )
        """)
        cur.execute("""
            INSERT INTO TipProfiles (id, name, material, color_hex, icon_char, is_default)
            VALUES (1, 'Custom SpinFit', 'Silicone', '#ff00ff', '✦', 1)
        """)
        conn.commit()
        conn.close()

        # Now instantiate DatabaseManager
        db = database.DatabaseManager(self.db_path)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name, material, color_hex, icon_char FROM TipProfiles WHERE id = 1")
        row = cur.fetchone()
        conn.close()

        # Check that id=1 was preserved
        self.assertEqual(row, ("Custom SpinFit", "Silicone", "#ff00ff", "✦"))

        # Check seed tips 2..7 were inserted
        tips = db.get_all_tips(include_unknown=True)
        self.assertEqual(len(tips), 7)
        self.assertEqual(tips[0]["name"], "Custom SpinFit")
        self.assertEqual(tips[1]["name"], "Kein Aufsatz")
        self.assertEqual(tips[2]["name"], "V26 Straight")
        self.assertEqual(tips[3]["name"], "V27 Rounded")
        self.assertEqual(tips[4]["name"], "V29-C Cone")
        self.assertEqual(tips[5]["name"], "V30-C Pro")
        self.assertEqual(tips[6]["name"], "V31-XL Panzer")

    def test_pre_existing_tips_with_sparse_ids(self):
        """Pre-existing table with sparse IDs (e.g. 10, 20) must preserve custom entries and add missing seeds."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE TipProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                material TEXT,
                color_hex TEXT,
                icon_char TEXT,
                is_default INTEGER DEFAULT 0
            )
        """)
        cur.execute("INSERT INTO TipProfiles (id, name) VALUES (10, 'Custom 10')")
        cur.execute("INSERT INTO TipProfiles (id, name) VALUES (20, 'Custom 20')")
        conn.commit()
        conn.close()

        db = database.DatabaseManager(self.db_path)

        tips = db.get_all_tips(include_unknown=True)
        # Seeds 1..7 plus custom 10 and 20 -> 9 total
        self.assertEqual(len(tips), 9)
        ids = [t["id"] for t in tips]
        self.assertEqual(ids, [1, 2, 3, 4, 5, 6, 7, 10, 20])


class TestGetLastUsedTipAdversarial(unittest.TestCase):
    """Scenario 4: get_last_used_tip with mixed measurements, unknown tips, deleted IEMs, None/0."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_last_used.db")
        self.db = database.DatabaseManager(self.db_path)
        self.f, self.m, self.p = make_dummy_sweep()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_only_unknown_tips_returns_none(self):
        """IEM having ONLY measurements with tip_id=1 must return None (Design Decision 3 & PROJECT.md)."""
        for _ in range(5):
            self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=1)
        self.assertIsNone(self.db.get_last_used_tip(1))

    def test_interleaving_unknown_and_prokit_tips(self):
        """Interleaving tip_id=1 with known tips must correctly return the latest KNOWN tip."""
        # Measurement 1: Tip 4 (t=1)
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=4)
        self.assertEqual(self.db.get_last_used_tip(1), 4)

        # Measurement 2: Tip 1 (Unknown)
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=1)
        self.assertEqual(self.db.get_last_used_tip(1), 4, "tip_id=1 should not shadow previous known tip")

        # Measurement 3: Tip 5 (ProKit V2)
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=5)
        self.assertEqual(self.db.get_last_used_tip(1), 5)

        # Measurement 4: Tip 1 (Unknown) again
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=1)
        self.assertEqual(self.db.get_last_used_tip(1), 5, "tip_id=1 should not shadow previous known tip")

        # Measurement 5: Tip 3 (Standard Foam)
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=3)
        self.assertEqual(self.db.get_last_used_tip(1), 3)

    def test_same_second_tie_breaking(self):
        """When multiple measurements share identical timestamps, id DESC must break the tie deterministically."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Measurements (iem_id, timestamp, tip_id)
            VALUES (1, '2026-09-22 10:00:00', 4)
        """)
        cur.execute("""
            INSERT INTO Measurements (iem_id, timestamp, tip_id)
            VALUES (1, '2026-09-22 10:00:00', 5)
        """)
        conn.commit()
        conn.close()

        # Measurement with tip_id=5 was inserted second, having higher id
        self.assertEqual(self.db.get_last_used_tip(1), 5)

    def test_invalid_iem_ids(self):
        """None, 0, negative, string, or nonexistent IEM IDs must return None safely."""
        self.assertIsNone(self.db.get_last_used_tip(None))
        self.assertIsNone(self.db.get_last_used_tip(0))
        self.assertIsNone(self.db.get_last_used_tip(999999))
        self.assertIsNone(self.db.get_last_used_tip(-5))

    def test_multi_iem_isolation(self):
        """Measurements for different IEMs must remain completely isolated."""
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=4)
        self.db.save_measurement(2, self.f, self.m, self.m, self.p, self.p, tip_id=5)
        self.db.save_measurement(3, self.f, self.m, self.m, self.p, self.p, tip_id=1)

        self.assertEqual(self.db.get_last_used_tip(1), 4)
        self.assertEqual(self.db.get_last_used_tip(2), 5)
        self.assertIsNone(self.db.get_last_used_tip(3))


class TestSaveMeasurementAdversarial(unittest.TestCase):
    """Scenario 5: save_measurement with tip_id=None, tip_id=999, negative tip_id, corrupt arrays."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_save_adv.db")
        self.db = database.DatabaseManager(self.db_path)
        self.f, self.m, self.p = make_dummy_sweep()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_save_with_tip_id_none_defaults_to_1(self):
        """save_measurement(tip_id=None) must store actual_tip_id = 1."""
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=None)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements ORDER BY id DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], 1)
        conn.close()

    def test_save_with_nonexistent_tip_id_999(self):
        """save_measurement(tip_id=999) stores 999 without crashing (SQLite FKs off by default)."""
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=999)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements ORDER BY id DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], 999)
        conn.close()

    def test_save_with_negative_tip_id(self):
        """save_measurement(tip_id=-1) stores -1."""
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=-1)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements ORDER BY id DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], -1)
        conn.close()

    def test_save_with_all_none_numpy_arrays(self):
        """save_measurement with all array parameters None must store b'' without throwing exceptions."""
        try:
            self.db.save_measurement(1, None, None, None, None, None, tip_id=4)
        except Exception as e:
            self.fail(f"save_measurement failed on None arrays: {e}")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT frequencies, magnitude_l, magnitude_r, tip_id FROM Measurements ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row[0], b'')
        self.assertEqual(row[1], b'')
        self.assertEqual(row[2], b'')
        self.assertEqual(row[3], 4)

    def test_save_with_large_arrays_100k_bins(self):
        """Saving large frequency arrays (100,000 bins) executes cleanly and preserves float precision."""
        f_large = np.linspace(10.0, 48000.0, 100000, dtype=np.float64)
        m_large = np.full_like(f_large, 94.5)
        p_large = np.zeros_like(f_large)

        self.db.save_measurement(1, f_large, m_large, m_large, p_large, p_large, tip_id=5)

        freqs, ml, mr, _ = self.db.load_reference_measurement(1)
        self.assertEqual(len(freqs), 100000)
        self.assertEqual(len(ml), 100000)
        self.assertAlmostEqual(ml[50000], 94.5)


class TestDSPAPIsAdversarial(unittest.TestCase):
    """Scenario 6: Adversarial inputs to reproducibility, seal history, and target peak."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_dsp_adv.db")
        self.db = database.DatabaseManager(self.db_path)
        self.f, self.m, self.p = make_dummy_sweep()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_reproducibility_corrupt_blobs_and_odd_bytes(self):
        """Corrupt BLOBs (random odd bytes not divisible by 8) must be skipped without crashing."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Insert 3 corrupted records
        for i in range(3):
            cur.execute("""
                INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l, magnitude_r)
                VALUES (1, 4, ?, ?, ?)
            """, (b'CORRUPT_BYTES_NOT_DIVISIBLE_BY_8', b'ODD_BYTES', b''))
        # Insert 5 valid records
        for i in range(5):
            cur.execute("""
                INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l, magnitude_r)
                VALUES (1, 4, ?, ?, ?)
            """, (self.f.tobytes(), self.m.tobytes(), self.m.tobytes()))
        conn.commit()
        conn.close()

        # Exactly 5 valid records -> should compute score and flag is_preliminary=True
        scores = self.db.get_reproducibility_scores(1, 4)
        self.assertIsNotNone(scores)
        self.assertEqual(scores["left"]["count"], 5)
        self.assertTrue(scores["left"]["is_preliminary"])

    def test_reproducibility_extreme_frequencies_out_of_band(self):
        """Measurements whose frequencies lie strictly outside 20-8000 Hz must be skipped."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Ultrasonic frequencies (10 kHz - 40 kHz)
        f_ultra = np.linspace(10000.0, 40000.0, 500, dtype=np.float64)
        m_ultra = np.full_like(f_ultra, 80.0)
        for _ in range(6):
            cur.execute("""
                INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l, magnitude_r)
                VALUES (1, 4, ?, ?, ?)
            """, (f_ultra.tobytes(), m_ultra.tobytes(), m_ultra.tobytes()))
        conn.commit()
        conn.close()

        # None of the curves had <8000Hz points, so valid curve count is 0 (< 5) -> returns None
        scores = self.db.get_reproducibility_scores(1, 4)
        self.assertIsNone(scores)

    def test_seal_history_exact_boundary_11_8_db(self):
        """Seal status classification: delta >= -11.8 is OK, delta < -11.8 is LEAK."""
        # Case 1: Delta = -11.79 dB -> OK
        f, m1, p = make_dummy_sweep()
        # Set 40Hz and 500Hz directly
        idx_40 = (f >= 35.0) & (f <= 45.0)
        idx_500 = (f >= 450.0) & (f <= 550.0)
        m1[idx_500] = 90.0
        m1[idx_40] = 90.0 - 11.79
        self.db.save_measurement(1, f, m1, m1, p, p, tip_id=4)

        # Case 2: Delta = -11.81 dB -> LEAK
        m2 = np.copy(m1)
        m2[idx_40] = 90.0 - 11.81
        self.db.save_measurement(1, f, m2, m2, p, p, tip_id=4)

        # Case 3: Delta = -11.80 dB -> exact threshold -> OK
        m3 = np.copy(m1)
        m3[idx_40] = 90.0 - 11.80
        self.db.save_measurement(1, f, m3, m3, p, p, tip_id=4)

        hist = self.db.get_seal_history(1, 4)
        left = hist["left"]
        self.assertEqual(len(left), 3)
        self.assertTrue(left[0]["seal_ok"], "delta -11.79 should be OK")
        self.assertEqual(left[0]["status"], "OK")

        self.assertFalse(left[1]["seal_ok"], "delta -11.81 should be LEAK")
        self.assertEqual(left[1]["status"], "LEAK")

        self.assertTrue(left[2]["seal_ok"], "delta -11.80 should be OK")
        self.assertEqual(left[2]["status"], "OK")

    def test_seal_history_missing_frequency_bands(self):
        """Measurements with frequencies that do not span 40Hz or 500Hz are skipped."""
        f_mid = np.linspace(1000.0, 5000.0, 500, dtype=np.float64)
        m_mid = np.full_like(f_mid, 85.0)
        p_mid = np.zeros_like(f_mid)
        self.db.save_measurement(1, f_mid, m_mid, m_mid, p_mid, p_mid, tip_id=4)

        hist = self.db.get_seal_history(1, 4)
        self.assertEqual(len(hist["left"]), 0)
        self.assertEqual(len(hist["right"]), 0)

    def test_target_peak_flat_or_narrow_spectrum(self):
        """get_tip_target_peak on spectrum with flat response or missing 6-10kHz."""
        # Missing 6-10kHz band
        f_low = np.linspace(20.0, 5000.0, 1000, dtype=np.float64)
        m_low = np.full_like(f_low, 80.0)
        self.db.save_measurement(1, f_low, m_low, m_low, np.zeros_like(f_low), np.zeros_like(f_low), tip_id=4)

        peaks = self.db.get_tip_target_peak(1, 4)
        self.assertIsNone(peaks["left"])
        self.assertIsNone(peaks["right"])

        # Valid peak at 8000 Hz
        f_norm, m_peak, p_norm = make_dummy_sweep(peak_hz=8000.0)
        self.db.save_measurement(1, f_norm, m_peak, m_peak, p_norm, p_norm, tip_id=4)
        peaks = self.db.get_tip_target_peak(1, 4)
        self.assertIsNotNone(peaks["left"])
        self.assertAlmostEqual(peaks["left"], 8000.0, delta=20.0)


class TestConcurrencyAndMultithreading(unittest.TestCase):
    """Scenario 7: Multithreaded concurrent reads and writes."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_concurrency.db")
        self.db = database.DatabaseManager(self.db_path)
        self.f, self.m, self.p = make_dummy_sweep(n_points=500)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_concurrent_reads_and_writes(self):
        """Simultaneous write and query operations must complete without locking crashes."""
        errors = []

        def writer(worker_id):
            try:
                for i in range(10):
                    self.db.save_measurement(
                        iem_id=worker_id % 3 + 1,
                        freqs=self.f,
                        mag_l=self.m,
                        mag_r=self.m,
                        phase_l=self.p,
                        phase_r=self.p,
                        tip_id=(i % 4) + 2,
                    )
            except Exception as e:
                errors.append(e)

        def reader(worker_id):
            try:
                for _ in range(10):
                    self.db.get_last_used_tip(iem_id=worker_id % 3 + 1)
                    self.db.get_all_tips(include_unknown=True)
                    self.db.get_reproducibility_scores(iem_id=worker_id % 3 + 1, tip_id=4)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=writer, args=(i,)))
            threads.append(threading.Thread(target=reader, args=(i,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent database errors: {errors}")


class TestExtremeCornerCases(unittest.TestCase):
    """Scenario 8: Extreme edge cases, type coercion, and schema transitions."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_extreme.db")
        self.db = database.DatabaseManager(self.db_path)
        self.f, self.m, self.p = make_dummy_sweep()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_mixed_legacy_migration_does_not_overwrite_known_tips(self):
        """Backfill only targets tip_id IS NULL; pre-existing known tips (tip_id=4, 5) remain untouched."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # Insert a mix of records: some with tip_id=4, some with tip_id=NULL
        cur.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, 4)")
        cur.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, NULL)")
        cur.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, 5)")
        cur.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, NULL)")
        conn.commit()
        conn.close()

        # Re-trigger init_db (migration)
        self.db._init_db()

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, tip_id FROM Measurements ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()

        # Rows 1 and 3 should retain 4 and 5; Rows 2 and 4 should be backfilled to 1
        self.assertEqual(rows[0][1], 4)
        self.assertEqual(rows[1][1], 1)
        self.assertEqual(rows[2][1], 5)
        self.assertEqual(rows[3][1], 1)

    def test_save_measurement_numeric_coercion(self):
        """Passing float (4.0) or string ('4') to tip_id is handled gracefully by SQLite."""
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=4.0)
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id="5")

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tip_id FROM Measurements ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        self.assertEqual(rows[-2][0], 4)
        self.assertEqual(rows[-1][0], 5)

    def test_all_apis_on_empty_tables(self):
        """All query and DSP APIs must return valid empty / None states without exceptions on empty DB."""
        self.assertEqual(self.db.get_last_used_tip(1), None)
        self.assertEqual(self.db.get_reproducibility_scores(1, 4), None)
        self.assertEqual(self.db.get_seal_history(1, 4), {"left": [], "right": []})
        self.assertEqual(self.db.get_tip_target_peak(1, 4), {"left": None, "right": None})
        ref_f, ref_l, ref_r, gain = self.db.load_reference_measurement(1)
        self.assertIsNone(ref_f)
        self.assertIsNone(ref_l)
        self.assertIsNone(ref_r)
        self.assertEqual(gain, "")

    def test_orphaned_tip_id_in_get_last_used_tip(self):
        """
        Adversarial test: If an orphaned/deleted tip_id (e.g. 999) is recorded in Measurements,
        verify empirical behavior: get_last_used_tip returns 999 because Foreign Keys are unenforced
        in SQLite by default and get_last_used_tip does not JOIN TipProfiles.
        """
        self.db.save_measurement(1, self.f, self.m, self.m, self.p, self.p, tip_id=999)
        val = self.db.get_last_used_tip(1)
        self.assertEqual(val, 999)


if __name__ == "__main__":
    unittest.main()

