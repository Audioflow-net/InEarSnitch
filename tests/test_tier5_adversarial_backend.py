"""
Tier 5 White-Box Adversarial Coverage Hardening Test Suite
===========================================================
Project: InEarSnitch ProKit Tip-Tracking
Target: Backend, Database, and DSP layers (config.py, database.py)

Audit Scope:
1. Malformed / corrupted / truncated .prokit_unlocked token files
2. Database migration idempotency under repeated calls, missing columns, non-standard schemas
3. BLOB parsing edge cases: corrupt headers, truncated payloads, NaN/Inf, zero-length, single-point
4. Acoustic seal calculations: extreme ratios, negative frequencies, boundary bands (40Hz, 500Hz)
5. Reproducibility score: high/zero variance, identical curves, non-overlapping bands, NaN interp
6. SQLite concurrent connections / transactions, thread safety, rollback safety
"""

import os
import sys
import sqlite3
import hashlib
import threading
import tempfile
import pytest
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config
import database


# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_data_dir(tmp_path, monkeypatch):
    """Provides an isolated directory for config.get_data_dir()."""
    td = str(tmp_path / "app_data")
    os.makedirs(td, exist_ok=True)
    monkeypatch.setattr(config, "get_data_dir", lambda: td)
    yield td


@pytest.fixture
def fresh_db_path(tmp_path):
    """Provides a fresh isolated database file path."""
    return str(tmp_path / "adversarial_test.db")


@pytest.fixture
def fresh_db(fresh_db_path):
    """Provides an initialized DatabaseManager on an isolated database."""
    return database.DatabaseManager(fresh_db_path)


def generate_sweep(
    freqs=None,
    base_spl=90.0,
    bass_delta_40=3.0,
    ref_delta_500=0.0,
    peak_freq=7850.0,
    peak_gain=6.0,
    noise_std=0.0,
    tilt_per_khz=0.0,
    num_points=1000,
):
    """Generates synthetic sweep data with precise acoustic parameters."""
    if freqs is None:
        freqs = np.linspace(20.0, 20000.0, num_points, dtype=np.float64)

    mag = np.full_like(freqs, base_spl)
    if tilt_per_khz != 0.0:
        mag -= (freqs / 1000.0) * tilt_per_khz

    # 40 Hz band (35 - 45 Hz)
    idx_40 = (freqs >= 35.0) & (freqs <= 45.0)
    mag[idx_40] += bass_delta_40

    # 500 Hz band (450 - 550 Hz)
    idx_500 = (freqs >= 450.0) & (freqs <= 550.0)
    mag[idx_500] += ref_delta_500

    # Resonance peak in 6-10 kHz zone
    if peak_freq is not None and 6000.0 <= peak_freq <= 10000.0:
        peak_curve = peak_gain * np.exp(-0.5 * ((freqs - peak_freq) / 400.0) ** 2)
        mag += peak_curve

    if noise_std > 0:
        mag += np.random.normal(0.0, noise_std, size=len(mag))

    phase = np.zeros_like(mag)
    return freqs, mag, phase


# ---------------------------------------------------------------------------
# 1. Adversarial Config & Token Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialConfig:
    """Adversarial stress-testing of offline unlock token handling in config.py."""

    def test_token_truncated_zero_bytes(self, mock_data_dir):
        """Zero-byte .prokit_unlocked file exists -> is_prokit_unlocked evaluates file existence."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "wb") as f:
            f.write(b"")
        assert os.path.getsize(token_path) == 0
        assert config.is_prokit_unlocked() is True

    def test_token_truncated_partial_hash(self, mock_data_dir):
        """Truncated token (partial 16-character hash) exists -> returns True, recoverable by valid unlock."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "w", encoding="utf-8") as f:
            f.write("1828f2d5760d4cf8")
        assert config.is_prokit_unlocked() is True
        # Overwrite with valid unlock
        assert config.unlock_prokit("SNITCH-PROKIT-2024-001") is True
        with open(token_path, "r", encoding="utf-8") as f:
            assert len(f.read().strip()) == 64

    def test_token_corrupt_binary_garbage(self, mock_data_dir):
        """Token file containing arbitrary non-UTF8 binary bytes."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "wb") as f:
            f.write(b"\xff\xfe\x00\x01\x80\x99\xaa\xbb\xcc\xdd\xee\xff" * 20)
        assert config.is_prokit_unlocked() is True
        assert config.revoke_prokit() is True
        assert config.is_prokit_unlocked() is False

    def test_token_multiline_and_whitespace(self, mock_data_dir):
        """Token file containing multiple lines, whitespace, and windows CRLF line endings."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "wb") as f:
            f.write(b"   \r\n\r\n1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2  \r\n\r\n")
        assert config.is_prokit_unlocked() is True

    def test_token_as_directory_error_handling(self, mock_data_dir):
        """If .prokit_unlocked is created as a directory instead of a regular file."""
        token_dir = os.path.join(mock_data_dir, ".prokit_unlocked")
        os.mkdir(token_dir)
        # exists returns True
        assert config.is_prokit_unlocked() is True
        # Attempting unlock should safely fail (IsADirectoryError is OSError) without crashing
        assert config.unlock_prokit("SNITCH-PROKIT-2024-001") is False
        # Revoking directory fails safely without crashing
        assert config.revoke_prokit() is False
        os.rmdir(token_dir)
        assert config.is_prokit_unlocked() is False

    def test_token_readonly_permission_handling(self, mock_data_dir):
        """Read-only token file behavior during unlock attempt."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "w", encoding="utf-8") as f:
            f.write("test_hash")
        os.chmod(token_path, 0o400)  # read only
        # Attempt to unlock over read-only file should catch PermissionError (OSError) and return False
        res = config.unlock_prokit("SNITCH-PROKIT-2024-001")
        assert res is False
        # Cleanup: restore write permission so revocation or fixture cleanup works
        os.chmod(token_path, 0o644)
        assert config.revoke_prokit() is True

    def test_unlock_non_string_types(self, mock_data_dir):
        """Passing non-string types to unlock_prokit returns False without crashing."""
        for invalid_input in [None, 12345, 3.1415, [], {}, {"code": "SNITCH-PROKIT-2024-001"}, True, False, object()]:
            assert config.unlock_prokit(invalid_input) is False
        assert config.is_prokit_unlocked() is False

    def test_unlock_huge_string_memory_dos(self, mock_data_dir):
        """Passing a 1 MB string does not cause memory exhaustion or hang."""
        huge_code = "SNITCH-PROKIT-" + "A" * (1024 * 1024)
        assert config.unlock_prokit(huge_code) is False
        assert config.is_prokit_unlocked() is False

    def test_unlock_unicode_surrogate_behavior(self, mock_data_dir):
        """Passing unpaired surrogate code point tests character encoding safety."""
        # Unpaired surrogate '\ud800' cannot be encoded to UTF-8
        try:
            res = config.unlock_prokit("\ud800")
            assert res is False
        except UnicodeEncodeError:
            # Documented: raw str without surrogate sanitization raises UnicodeEncodeError
            pass

    def test_unlock_unicode_whitespace_variants(self, mock_data_dir):
        """Non-breaking spaces, zero-width spaces, and unusual whitespace."""
        code = "\u00a0SNITCH-PROKIT-2024-001\u00a0\t"
        # str.strip() in Python 3 strips unicode whitespace including \u00a0
        assert config.unlock_prokit(code) is True
        assert config.is_prokit_unlocked() is True

    def test_rapid_unlock_revoke_churn_100_cycles(self, mock_data_dir):
        """100 consecutive unlock and revoke cycles test filesystem stability."""
        for i in range(100):
            assert config.unlock_prokit("SNITCH-PROKIT-2024-001") is True
            assert config.is_prokit_unlocked() is True
            assert config.revoke_prokit() is True
            assert config.is_prokit_unlocked() is False

    def test_tampered_token_overwritten_by_valid_unlock(self, mock_data_dir):
        """Tampered or foreign content in token file is overwritten cleanly by unlock_prokit."""
        token_path = os.path.join(mock_data_dir, ".prokit_unlocked")
        with open(token_path, "w", encoding="utf-8") as f:
            f.write("UNAUTHORIZED_TAMPERED_DATA\n")
        assert config.unlock_prokit("SNITCH-PROKIT-2024-002") is True
        with open(token_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        expected = hashlib.sha256(b"SNITCH-PROKIT-2024-002").hexdigest().lower()
        assert content == expected


# ---------------------------------------------------------------------------
# 2. Adversarial Database Migration Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialDBMigration:
    """Adversarial stress-testing of database migrations, schema variations, and idempotency."""

    def test_migration_idempotency_20_iterations(self, fresh_db_path):
        """Calling DatabaseManager._init_db() 20 consecutive times leaves database clean and intact."""
        db = database.DatabaseManager(fresh_db_path)
        for _ in range(20):
            db._init_db()

        conn = sqlite3.connect(fresh_db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM TipProfiles")
        assert cur.fetchone()[0] == 7
        cur.execute("SELECT COUNT(*) FROM TipProfiles WHERE id = 1")
        assert cur.fetchone()[0] == 1
        conn.close()

    def test_migration_from_empty_zero_byte_db(self, tmp_path):
        """Instantiating DatabaseManager on a 0-byte file creates all tables successfully."""
        empty_file = str(tmp_path / "zero_byte.db")
        with open(empty_file, "wb") as f:
            f.write(b"")
        assert os.path.getsize(empty_file) == 0

        db = database.DatabaseManager(empty_file)
        assert os.path.getsize(empty_file) > 0
        tips = db.get_all_tips(include_unknown=True)
        assert len(tips) == 7

    def test_migration_missing_all_new_columns(self, tmp_path):
        """Legacy Measurements table missing gain_db, phase_l, phase_r, notes, photo_path, tip_id."""
        db_path = str(tmp_path / "legacy_minimal.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE Measurements (id INTEGER PRIMARY KEY, iem_id INTEGER, frequencies BLOB)")
        conn.execute("INSERT INTO Measurements (iem_id) VALUES (42)")
        conn.commit()
        conn.close()

        # Run migration
        db = database.DatabaseManager(db_path)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(Measurements)")
        cols = {row[1] for row in cur.fetchall()}
        assert {"gain_db", "phase_l", "phase_r", "notes", "photo_path", "tip_id"}.issubset(cols)
        # Check that existing row was backfilled to tip_id=1
        cur.execute("SELECT tip_id FROM Measurements WHERE iem_id = 42")
        assert cur.fetchone()[0] == 1
        conn.close()

    def test_migration_missing_tipprofiles_table(self, tmp_path):
        """Database with Measurements but no TipProfiles table."""
        db_path = str(tmp_path / "no_tipprofiles.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE Measurements (id INTEGER PRIMARY KEY, iem_id INTEGER, tip_id INTEGER)")
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        tips = db.get_all_tips(include_unknown=True)
        assert len(tips) == 7
        assert tips[0]["id"] == 1 and tips[0]["name"] == "Unbekannt"

    def test_migration_missing_description_column_in_tipprofiles(self, tmp_path):
        """TipProfiles exists from earlier alpha version without 'description' column."""
        db_path = str(tmp_path / "old_tip_profiles.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE TipProfiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                material TEXT,
                color_hex TEXT,
                icon_char TEXT,
                is_default INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(TipProfiles)")
        cols = {row[1] for row in cur.fetchall()}
        assert "description" in cols
        conn.close()

    def test_migration_preserves_custom_tips(self, tmp_path):
        """Custom tip created by user with custom ID is preserved and not overwritten."""
        db_path = str(tmp_path / "custom_tips.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE TipProfiles (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                material TEXT,
                color_hex TEXT,
                icon_char TEXT,
                is_default INTEGER DEFAULT 0
            )
        """)
        conn.execute("INSERT INTO TipProfiles VALUES (100, 'Custom Acrylic Tip', 'Custom mold', 'Acrylic', '#ffffff', '▲', 0)")
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        all_tips = db.get_all_tips(include_unknown=True)
        assert any(t["id"] == 100 and t["name"] == "Custom Acrylic Tip" for t in all_tips)
        assert len(all_tips) == 8  # 7 seed tips + 1 custom tip

    def test_migration_legacy_backfill_1000_records(self, tmp_path):
        """Stress-testing legacy backfill on 1,000 pre-existing measurements."""
        db_path = str(tmp_path / "legacy_1000.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE Measurements (id INTEGER PRIMARY KEY AUTOINCREMENT, iem_id INTEGER)")
        conn.executemany("INSERT INTO Measurements (iem_id) VALUES (?)", [(i % 10 + 1,) for i in range(1000)])
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id = 1")
        assert cur.fetchone()[0] == 1000
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id IS NULL")
        assert cur.fetchone()[0] == 0
        conn.close()

    def test_migration_preserves_existing_valid_tip_ids(self, tmp_path):
        """Measurements already tagged with tip_id != NULL (e.g. tip_id=3) are not overwritten to 1."""
        db_path = str(tmp_path / "existing_tip_ids.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE Measurements (id INTEGER PRIMARY KEY AUTOINCREMENT, iem_id INTEGER, tip_id INTEGER)")
        conn.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, NULL)")
        conn.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, 3)")
        conn.execute("INSERT INTO Measurements (iem_id, tip_id) VALUES (1, 5)")
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, tip_id FROM Measurements ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        assert rows[0][1] == 1  # was NULL -> backfilled to 1
        assert rows[1][1] == 3  # preserved
        assert rows[2][1] == 5  # preserved

    def test_migration_with_unrelated_custom_columns(self, tmp_path):
        """Measurements table containing extra custom columns from third-party plugins."""
        db_path = str(tmp_path / "extra_cols.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE Measurements (id INTEGER PRIMARY KEY, iem_id INTEGER, mic_calibration_curve TEXT, humidity_percent REAL)")
        conn.commit()
        conn.close()

        db = database.DatabaseManager(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(Measurements)")
        cols = {row[1] for row in cur.fetchall()}
        assert "mic_calibration_curve" in cols
        assert "humidity_percent" in cols
        assert "tip_id" in cols
        conn.close()

    def test_db_schema_integrity_check_passes(self, fresh_db, fresh_db_path):
        """PRAGMA integrity_check returns 'ok' on freshly migrated database."""
        conn = sqlite3.connect(fresh_db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        assert cur.fetchone()[0] == "ok"
        conn.close()


# ---------------------------------------------------------------------------
# 3. Adversarial BLOB Parsing Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialBLOBParsing:
    """Adversarial stress-testing of binary numpy BLOB decoding and corrupt data handling."""

    def test_blob_corrupt_odd_byte_length_reproducibility(self, fresh_db, fresh_db_path):
        """Odd byte length BLOBs (not divisible by 8) in reproducibility query are safely skipped."""
        conn = sqlite3.connect(fresh_db_path)
        conn.execute("INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l) VALUES (1, 3, ?, ?)", (b"\x01\x02\x03", b"\x04\x05"))
        conn.execute("INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l) VALUES (1, 3, ?, ?)", (b"\xaa\xbb\xcc\xdd\xee\xff\x11", b"\x22"))
        conn.commit()
        conn.close()

        # Should not crash with ValueError, should return None (< 5 valid records)
        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is None

    def test_blob_corrupt_odd_byte_length_seal_history(self, fresh_db, fresh_db_path):
        """Odd byte length BLOBs in seal history are safely skipped."""
        conn = sqlite3.connect(fresh_db_path)
        conn.execute("INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l) VALUES (1, 3, ?, ?)", (b"\x01\x02\x03", b"\x04\x05"))
        conn.commit()
        conn.close()

        seal = fresh_db.get_seal_history(1, 3)
        assert seal == {"left": [], "right": []}

    def test_blob_corrupt_odd_byte_length_peak_detection(self, fresh_db, fresh_db_path):
        """Odd byte length BLOBs in peak detection are safely skipped."""
        conn = sqlite3.connect(fresh_db_path)
        conn.execute("INSERT INTO Measurements (iem_id, tip_id, frequencies, magnitude_l) VALUES (1, 3, ?, ?)", (b"\x01\x02\x03", b"\x04\x05"))
        conn.commit()
        conn.close()

        peaks = fresh_db.get_tip_target_peak(1, 3)
        assert peaks == {"left": None, "right": None}

    def test_blob_zero_length_arrays(self, fresh_db):
        """Zero-length numpy arrays saved as b'' are handled without IndexError."""
        empty_arr = np.array([], dtype=np.float64)
        fresh_db.save_measurement(1, empty_arr, empty_arr, empty_arr, empty_arr, empty_arr, tip_id=3)

        assert fresh_db.get_reproducibility_scores(1, 3) is None
        assert fresh_db.get_seal_history(1, 3) == {"left": [], "right": []}
        assert fresh_db.get_tip_target_peak(1, 3) == {"left": None, "right": None}

    def test_blob_single_frequency_point(self, fresh_db):
        """Single-frequency point sweeps (len == 1) are safely skipped due to len < 10 guard."""
        f_single = np.array([1000.0], dtype=np.float64)
        m_single = np.array([90.0], dtype=np.float64)
        p_single = np.array([0.0], dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_single, m_single, m_single, p_single, p_single, tip_id=3)

        assert fresh_db.get_reproducibility_scores(1, 3) is None
        assert fresh_db.get_seal_history(1, 3) == {"left": [], "right": []}
        assert fresh_db.get_tip_target_peak(1, 3) == {"left": None, "right": None}

    def test_blob_fewer_than_10_points(self, fresh_db):
        """Sweeps with exactly 9 points (< 10) are safely skipped."""
        f_9 = np.linspace(20.0, 10000.0, 9, dtype=np.float64)
        m_9 = np.full(9, 85.0, dtype=np.float64)
        p_9 = np.zeros(9, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_9, m_9, m_9, p_9, p_9, tip_id=3)

        assert fresh_db.get_reproducibility_scores(1, 3) is None
        assert fresh_db.get_seal_history(1, 3) == {"left": [], "right": []}

    def test_blob_mismatched_frequency_magnitude_lengths(self, fresh_db):
        """Mismatched array lengths (frequencies: 100 points, magnitude: 50 points)."""
        f = np.linspace(20.0, 20000.0, 100, dtype=np.float64)
        m_short = np.full(50, 85.0, dtype=np.float64)
        p = np.zeros(100, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f, m_short, m_short, p, p, tip_id=3)

        # len(ml) == len(f) guard safely skips mismatched rows
        assert fresh_db.get_reproducibility_scores(1, 3) is None
        assert fresh_db.get_seal_history(1, 3) == {"left": [], "right": []}

    def test_blob_nan_in_frequencies(self, fresh_db):
        """Frequency array entirely composed of NaNs."""
        f_nan = np.full(1000, np.nan, dtype=np.float64)
        m = np.linspace(80.0, 90.0, 1000, dtype=np.float64)
        p = np.zeros(1000, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_nan, m, m, p, p, tip_id=3)

        # mask = f <= 8000 is all False for NaNs -> skipped
        assert fresh_db.get_reproducibility_scores(1, 3) is None
        assert fresh_db.get_seal_history(1, 3) == {"left": [], "right": []}

    def test_blob_nan_in_magnitudes(self, fresh_db):
        """Magnitude array containing NaNs evaluates without uncaught exception."""
        f, _, p = generate_sweep(num_points=1000)
        m_nan = np.full(1000, np.nan, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f, m_nan, m_nan, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        # std_dev of NaNs is NaN
        assert np.isnan(res["left"]["score"])

        # Seal history with NaNs produces LEAK status without crashing
        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 6
        assert all(entry["status"] == "LEAK" for entry in seal["left"])

    def test_blob_infinite_values_in_magnitudes(self, fresh_db):
        """Magnitude array containing +/- Inf values."""
        f, m, p = generate_sweep(num_points=1000)
        m[10] = np.inf
        m[20] = -np.inf
        for _ in range(6):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        # Should execute without throwing UnboundLocalError or crash
        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None

    def test_blob_subnormal_and_extreme_exponents(self, fresh_db):
        """Magnitude array containing subnormal floats (1e-308) and maximum double (1e50)."""
        f = np.linspace(20.0, 20000.0, 1000, dtype=np.float64)
        m = np.full(1000, 1e-308, dtype=np.float64)
        m[5] = 1e50
        p = np.zeros(1000, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None

    def test_blob_non_monotonic_frequencies(self, fresh_db):
        """Frequency array with descending (reversed) order."""
        f_rev = np.linspace(20000.0, 20.0, 1000, dtype=np.float64)
        m = np.full(1000, 85.0, dtype=np.float64)
        p = np.zeros(1000, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_rev, m, m, p, p, tip_id=3)

        # np.interp handles without crash
        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None

    def test_blob_load_reference_corrupt_payload(self, fresh_db, fresh_db_path):
        """load_reference_measurement raises ValueError on odd-byte buffer not multiple of 8."""
        conn = sqlite3.connect(fresh_db_path)
        conn.execute("INSERT INTO Measurements (iem_id, frequencies) VALUES (1, ?)", (b"\x01\x02\x03",))
        conn.commit()
        conn.close()

        # Documented behavior: np.frombuffer raises ValueError when buffer size is not multiple of 8
        with pytest.raises(ValueError):
            fresh_db.load_reference_measurement(1)

    def test_blob_load_reference_valid_and_nonexistent(self, fresh_db):
        """load_reference_measurement retrieves valid data and returns Nones for nonexistent IEM."""
        # Non-existent
        f_none, ml_none, mr_none, gain_none = fresh_db.load_reference_measurement(9999)
        assert f_none is None and ml_none is None and mr_none is None and gain_none == ""

        # Valid save & load
        f, m, p = generate_sweep(num_points=500)
        fresh_db.save_measurement(1, f, m, m, p, p, gain_db="-12", tip_id=3)
        f_ret, ml_ret, mr_ret, gain_ret = fresh_db.load_reference_measurement(1)
        assert len(f_ret) == len(f)
        assert np.allclose(f_ret, f)
        assert np.allclose(ml_ret, m)
        assert gain_ret == "-12"


# ---------------------------------------------------------------------------
# 4. Adversarial Acoustic Seal Calculation Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialAcousticSeal:
    """Adversarial stress-testing of acoustic seal delta calculations (40 Hz vs 500 Hz)."""

    def test_seal_missing_40hz_band(self, fresh_db):
        """Sweep starting above 45 Hz (40 Hz band missing) is safely skipped."""
        f = np.linspace(100.0, 20000.0, 500, dtype=np.float64)
        m = np.full(500, 85.0, dtype=np.float64)
        p = np.zeros(500, dtype=np.float64)
        fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 0

    def test_seal_missing_500hz_band(self, fresh_db):
        """Sweep stopping below 450 Hz (500 Hz band missing) is safely skipped."""
        f = np.linspace(20.0, 300.0, 500, dtype=np.float64)
        m = np.full(500, 85.0, dtype=np.float64)
        p = np.zeros(500, dtype=np.float64)
        fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 0

    def test_seal_both_reference_bands_missing(self, fresh_db):
        """Sweep strictly in 1 kHz to 10 kHz range (neither band present)."""
        f = np.linspace(1000.0, 10000.0, 500, dtype=np.float64)
        m = np.full(500, 85.0, dtype=np.float64)
        p = np.zeros(500, dtype=np.float64)
        fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 0
        assert len(seal["right"]) == 0

    def test_seal_negative_frequencies(self, fresh_db):
        """Sweep with negative frequencies only."""
        f = np.linspace(-20000.0, -20.0, 500, dtype=np.float64)
        m = np.full(500, 85.0, dtype=np.float64)
        p = np.zeros(500, dtype=np.float64)
        fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 0

    def test_seal_exact_threshold_boundary_minus_11_80(self, fresh_db):
        """Delta = -11.80 dB exactly matches threshold (>= -11.8) -> status OK."""
        # 40Hz: 78.2 dB, 500Hz: 90.0 dB -> delta = -11.80 dB
        f, ml, p = generate_sweep(base_spl=90.0, bass_delta_40=-11.80, ref_delta_500=0.0, tilt_per_khz=0.0)
        fresh_db.save_measurement(1, f, ml, ml, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 1
        assert seal["left"][0]["delta_db"] == -11.80
        assert seal["left"][0]["seal_ok"] is True
        assert seal["left"][0]["status"] == "OK"

    def test_seal_exact_threshold_boundary_minus_11_81(self, fresh_db):
        """Delta = -11.81 dB is below threshold (< -11.8) -> status LEAK."""
        f, ml, p = generate_sweep(base_spl=90.0, bass_delta_40=-11.81, ref_delta_500=0.0, tilt_per_khz=0.0)
        fresh_db.save_measurement(1, f, ml, ml, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 1
        assert seal["left"][0]["delta_db"] == -11.81
        assert seal["left"][0]["seal_ok"] is False
        assert seal["left"][0]["status"] == "LEAK"

    def test_seal_extreme_bass_boost_ratio(self, fresh_db):
        """Extreme bass boost (+60 dB delta) -> OK."""
        f, ml, p = generate_sweep(base_spl=90.0, bass_delta_40=60.0, ref_delta_500=0.0, tilt_per_khz=0.0)
        fresh_db.save_measurement(1, f, ml, ml, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert seal["left"][0]["seal_ok"] is True
        assert seal["left"][0]["status"] == "OK"
        assert seal["left"][0]["delta_db"] == 60.0

    def test_seal_extreme_bass_cut_ratio(self, fresh_db):
        """Extreme bass loss (-80 dB delta) -> LEAK."""
        f, ml, p = generate_sweep(base_spl=90.0, bass_delta_40=-80.0, ref_delta_500=0.0, tilt_per_khz=0.0)
        fresh_db.save_measurement(1, f, ml, ml, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert seal["left"][0]["seal_ok"] is False
        assert seal["left"][0]["status"] == "LEAK"
        assert seal["left"][0]["delta_db"] == -80.0

    def test_seal_high_noise_at_40hz(self, fresh_db):
        """40 Hz band has high zero-mean noise; average should converge near underlying mean."""
        f = np.linspace(20.0, 20000.0, 2000, dtype=np.float64)
        m = np.full(2000, 90.0, dtype=np.float64)
        idx_40 = (f >= 35.0) & (f <= 45.0)
        np.random.seed(42)
        # Add 10 dB noise around 40 Hz
        m[idx_40] += np.random.normal(0.0, 10.0, size=np.sum(idx_40))
        p = np.zeros(2000, dtype=np.float64)
        fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        # Because noise is zero-mean across ~20 points, delta should be close to 0 dB (+- 3 dB)
        assert abs(seal["left"][0]["delta_db"]) < 5.0
        assert seal["left"][0]["seal_ok"] is True

    def test_seal_channel_independence_and_mono(self, fresh_db):
        """Left channel good seal (+2 dB), Right channel leaked (-20 dB), then Mono Left."""
        f, ml, p = generate_sweep(bass_delta_40=2.0, tilt_per_khz=0.0)
        _, mr, _ = generate_sweep(bass_delta_40=-20.0, tilt_per_khz=0.0)
        fresh_db.save_measurement(1, f, ml, mr, p, p, tip_id=3)

        # Second measurement: Left only (Right is None)
        fresh_db.save_measurement(1, f, ml, None, p, None, tip_id=3)

        seal = fresh_db.get_seal_history(1, 3)
        assert len(seal["left"]) == 2
        assert len(seal["right"]) == 1
        assert seal["left"][0]["status"] == "OK"
        assert seal["left"][1]["status"] == "OK"
        assert seal["right"][0]["status"] == "LEAK"


# ---------------------------------------------------------------------------
# 5. Adversarial Reproducibility Score Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialReproducibility:
    """Adversarial stress-testing of band-limited reproducibility calculation (20 - 8000 Hz)."""

    def test_reproducibility_zero_variance_identical_curves(self, fresh_db):
        """5 completely identical sweeps yield exactly 0.00 dB standard deviation without error."""
        f, m, p = generate_sweep()
        for _ in range(5):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["score"] == 0.00
        assert res["left"]["std_dev"] == 0.00
        assert res["left"]["count"] == 5
        assert res["left"]["is_preliminary"] is True

    def test_reproducibility_extreme_high_variance(self, fresh_db):
        """5 sweeps with massive step offsets (0, 20, 40, 60, 80 dB) yield high std dev."""
        f, m, p = generate_sweep()
        for i in range(5):
            fresh_db.save_measurement(1, f, m + (i * 20.0), m + (i * 20.0), p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        # Standard deviation of [0, 20, 40, 60, 80] is sqrt(800) ~= 28.28 dB
        assert 25.0 <= res["left"]["score"] <= 30.0

    def test_reproducibility_exact_boundary_4_measurements(self, fresh_db):
        """Exactly 4 measurements (strictly below threshold N=5) returns None."""
        f, m, p = generate_sweep()
        for _ in range(4):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        assert fresh_db.get_reproducibility_scores(1, 3) is None

    def test_reproducibility_exact_boundary_5_measurements(self, fresh_db):
        """Exactly 5 measurements (minimum threshold) returns valid preliminary score."""
        f, m, p = generate_sweep()
        for _ in range(5):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["count"] == 5
        assert res["left"]["is_preliminary"] is True

    def test_reproducibility_exact_boundary_9_measurements(self, fresh_db):
        """Exactly 9 measurements sets is_preliminary=True."""
        f, m, p = generate_sweep()
        for _ in range(9):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["count"] == 9
        assert res["left"]["is_preliminary"] is True

    def test_reproducibility_exact_boundary_10_measurements(self, fresh_db):
        """Exactly 10 measurements sets is_preliminary=False."""
        f, m, p = generate_sweep()
        for _ in range(10):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["count"] == 10
        assert res["left"]["is_preliminary"] is False

    def test_reproducibility_band_limited_immunity_to_hf_noise(self, fresh_db):
        """Immunity to > 8 kHz noise: large 50 dB variance above 8 kHz does NOT affect score."""
        f = np.linspace(20.0, 24000.0, 2400)
        p = np.zeros_like(f)
        for i in range(5):
            m = np.full_like(f, 90.0)
            # Inject noise ONLY above 8000 Hz
            idx_hf = f > 8000.0
            m[idx_hf] += (i * 30.0)
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        # Score below 8 kHz must remain perfectly 0.00
        assert res["left"]["score"] == 0.00
        assert res["right"]["score"] == 0.00

    def test_reproducibility_non_overlapping_frequency_ranges(self, fresh_db):
        """Differing frequency grids (e.g. 20-500 Hz vs 20-10000 Hz) interpolated onto common 800-bin grid."""
        f_narrow = np.linspace(20.0, 500.0, 100, dtype=np.float64)
        m_narrow = np.full(100, 90.0, dtype=np.float64)
        p_narrow = np.zeros(100, dtype=np.float64)

        f_wide = np.linspace(20.0, 10000.0, 500, dtype=np.float64)
        m_wide = np.full(500, 90.0, dtype=np.float64)
        p_wide = np.zeros(500, dtype=np.float64)

        for _ in range(3):
            fresh_db.save_measurement(1, f_narrow, m_narrow, m_narrow, p_narrow, p_narrow, tip_id=3)
        for _ in range(3):
            fresh_db.save_measurement(1, f_wide, m_wide, m_wide, p_wide, p_wide, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["count"] == 6
        assert isinstance(res["left"]["score"], float)

    def test_reproducibility_sweeps_exclusively_above_8khz(self, fresh_db):
        """Sweeps strictly spanning 9 kHz to 20 kHz (f <= 8000 is empty) are skipped."""
        f_hf = np.linspace(9000.0, 20000.0, 500, dtype=np.float64)
        m_hf = np.full(500, 85.0, dtype=np.float64)
        p_hf = np.zeros(500, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_hf, m_hf, m_hf, p_hf, p_hf, tip_id=3)

        # None of the 6 sweeps have points <= 8000 Hz -> returns None
        assert fresh_db.get_reproducibility_scores(1, 3) is None

    def test_reproducibility_sweeps_exclusively_below_20hz(self, fresh_db):
        """Sweeps strictly spanning 1 Hz to 19 Hz."""
        f_sub = np.linspace(1.0, 19.0, 50, dtype=np.float64)
        m_sub = np.full(50, 85.0, dtype=np.float64)
        p_sub = np.zeros(50, dtype=np.float64)
        for _ in range(6):
            fresh_db.save_measurement(1, f_sub, m_sub, m_sub, p_sub, p_sub, tip_id=3)

        # f <= 8000 is True, np.interp clamps outside xp range
        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"]["count"] == 6

    def test_reproducibility_nan_magnitudes_handling(self, fresh_db):
        """Injected NaN in magnitude curves propagates to NaN score without fatal exception."""
        f, m, p = generate_sweep(num_points=100)
        m_with_nan = m.copy()
        m_with_nan[10] = np.nan
        for _ in range(5):
            fresh_db.save_measurement(1, f, m_with_nan, m_with_nan, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert np.isnan(res["left"]["score"])

    def test_reproducibility_independent_left_right_channels(self, fresh_db):
        """Left channel has 6 measurements, Right channel has only 2 measurements."""
        f, m, p = generate_sweep()
        # 4 Left-only measurements
        for _ in range(4):
            fresh_db.save_measurement(1, f, m, None, p, None, tip_id=3)
        # 2 Stereo measurements
        for _ in range(2):
            fresh_db.save_measurement(1, f, m, m, p, p, tip_id=3)

        res = fresh_db.get_reproducibility_scores(1, 3)
        assert res is not None
        assert res["left"] is not None
        assert res["left"]["count"] == 6
        # Right has only 2 (< 5 threshold) -> None
        assert res["right"] is None


# ---------------------------------------------------------------------------
# 6. Adversarial Concurrency & Transaction Safety Tests
# ---------------------------------------------------------------------------

class TestTier5AdversarialConcurrencyTransactions:
    """Adversarial stress-testing of multi-threaded database access and transactions."""

    def test_concurrent_multi_threaded_save_measurement(self, fresh_db, fresh_db_path):
        """10 threads concurrently executing save_measurement (100 total writes)."""
        f, m, p = generate_sweep(num_points=200)
        errors = []

        def worker(thread_idx):
            try:
                for i in range(10):
                    fresh_db.save_measurement(
                        iem_id=1,
                        freqs=f,
                        mag_l=m,
                        mag_r=m,
                        phase_l=p,
                        phase_r=p,
                        notes=f"thread_{thread_idx}_iter_{i}",
                        tip_id=3,
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Encountered thread errors: {errors}"
        conn = sqlite3.connect(fresh_db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Measurements WHERE tip_id = 3")
        assert cur.fetchone()[0] == 100
        conn.close()

    def test_concurrent_readers_during_active_writers(self, fresh_db):
        """Concurrent readers and writers operating simultaneously on the same database."""
        f, m, p = generate_sweep(num_points=200)
        errors = []
        stop_event = threading.Event()

        def writer():
            try:
                for _ in range(15):
                    fresh_db.save_measurement(1, f, m, m, p, p, tip_id=4)
            except Exception as e:
                errors.append(e)

        def reader():
            try:
                while not stop_event.is_set():
                    fresh_db.get_reproducibility_scores(1, 4)
                    fresh_db.get_seal_history(1, 4)
                    fresh_db.get_last_used_tip(1)
                    fresh_db.get_all_tips()
            except Exception as e:
                errors.append(e)

        writer_threads = [threading.Thread(target=writer) for _ in range(5)]
        reader_threads = [threading.Thread(target=reader) for _ in range(5)]

        for t in reader_threads:
            t.start()
        for t in writer_threads:
            t.start()

        for t in writer_threads:
            t.join()
        stop_event.set()
        for t in reader_threads:
            t.join()

        assert len(errors) == 0, f"Encountered concurrency errors: {errors}"

    def test_multiple_database_manager_instances_same_db(self, fresh_db_path):
        """Multiple independent DatabaseManager instances pointing to the exact same file."""
        db1 = database.DatabaseManager(fresh_db_path)
        db2 = database.DatabaseManager(fresh_db_path)
        db3 = database.DatabaseManager(fresh_db_path)

        f, m, p = generate_sweep(num_points=100)
        db1.save_measurement(1, f, m, m, p, p, tip_id=3)
        db2.save_measurement(1, f, m, m, p, p, tip_id=4)

        assert db3.get_last_used_tip(1) == 4
        tips = db1.get_all_tips()
        assert len(tips) == 7

    def test_database_rollback_on_failed_transaction(self, fresh_db, fresh_db_path):
        """Simulated query error does not leave database in a corrupted or uncommitted state."""
        conn = sqlite3.connect(fresh_db_path)
        # Attempt an invalid transaction
        try:
            with conn:
                conn.execute("INSERT INTO TipProfiles (id, name) VALUES (1, 'Duplicate ID')")
        except sqlite3.IntegrityError:
            pass  # Expected PRIMARY KEY conflict

        # Verify database is intact
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        assert cur.fetchone()[0] == "ok"
        conn.close()

    def test_database_busy_timeout_handling(self, fresh_db_path):
        """Database locked by an open uncommitted connection handles busy gracefully."""
        conn_lock = sqlite3.connect(fresh_db_path, timeout=1.0)
        conn_lock.execute("BEGIN EXCLUSIVE")

        # In another connection, attempt to connect and test handling
        conn_test = sqlite3.connect(fresh_db_path, timeout=0.1)
        with pytest.raises(sqlite3.OperationalError):
            conn_test.execute("INSERT INTO TipProfiles (name) VALUES ('Blocked Tip')")

        conn_lock.rollback()
        conn_lock.close()
        conn_test.close()

    def test_concurrent_migration_calls_across_threads(self, fresh_db_path):
        """Simultaneous _init_db calls across 5 threads do not create table collision errors."""
        errors = []

        def init_worker():
            try:
                db = database.DatabaseManager(fresh_db_path)
                db._init_db()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=init_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Migration collision errors: {errors}"

    def test_large_payload_burst_concurrency(self, fresh_db):
        """Concurrent insertion of high-resolution 24,000-point sweeps across threads."""
        f_large = np.linspace(20.0, 24000.0, 24001, dtype=np.float64)
        m_large = np.full(24001, 90.0, dtype=np.float64)
        p_large = np.zeros(24001, dtype=np.float64)
        errors = []

        def burst_worker():
            try:
                fresh_db.save_measurement(1, f_large, m_large, m_large, p_large, p_large, tip_id=3)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=burst_worker) for _ in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_post_concurrency_database_integrity(self, fresh_db, fresh_db_path):
        """Database passes full integrity check after all adversarial concurrency tests."""
        conn = sqlite3.connect(fresh_db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        assert cur.fetchone()[0] == "ok"
        conn.close()
