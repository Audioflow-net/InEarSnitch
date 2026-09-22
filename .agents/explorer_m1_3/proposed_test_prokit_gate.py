"""
Unit tests for Milestone 1: config.py ProKit gate.
Covers:
- VALID_CODE_HASHES structure and completeness (50 hashes)
- is_prokit_unlocked()
- unlock_prokit(code) with valid, invalid, malformed, and edge-case inputs
- revoke_prokit() and idempotency
- Persistence of .prokit_unlocked token file in isolated temporary environment
"""

import os
import sys
import unittest
import tempfile
import hashlib
from unittest.mock import patch

# Ensure project root is on sys.path by walking up directories until config.py is found
cur = os.path.dirname(os.path.abspath(__file__))
while cur != os.path.dirname(cur):
    if os.path.exists(os.path.join(cur, "config.py")):
        if cur not in sys.path:
            sys.path.insert(0, cur)
        break
    cur = os.path.dirname(cur)

import config


class TestProKitConfigGate(unittest.TestCase):
    def setUp(self):
        # Create isolated temporary directory for data_dir
        self.test_dir = tempfile.TemporaryDirectory()
        self.token_path = os.path.join(self.test_dir.name, ".prokit_unlocked")
        self.patcher = patch("config.get_data_dir", return_value=self.test_dir.name)
        self.mock_get_data_dir = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.test_dir.cleanup()

    def test_01_valid_code_hashes_set(self):
        """Verify VALID_CODE_HASHES contains exactly 50 valid lowercase sha256 hex strings."""
        self.assertTrue(hasattr(config, "VALID_CODE_HASHES"), "config must define VALID_CODE_HASHES")
        hashes = config.VALID_CODE_HASHES
        self.assertIsInstance(hashes, (set, frozenset), "VALID_CODE_HASHES must be a set or frozenset")
        self.assertEqual(len(hashes), 50, f"Expected 50 hashes, got {len(hashes)}")
        for h in hashes:
            self.assertIsInstance(h, str)
            self.assertEqual(len(h), 64, f"Hash {h} must be 64 hex characters")
            self.assertEqual(h, h.lower(), f"Hash {h} must be lowercase")

    def test_02_initial_state_locked(self):
        """Initial state must be locked when .prokit_unlocked does not exist."""
        self.assertFalse(os.path.exists(self.token_path))
        self.assertFalse(config.is_prokit_unlocked())

    def test_03_unlock_invalid_codes(self):
        """Invalid codes must return False and create no file."""
        invalid_inputs = [
            "WRONG-CODE",
            "SNITCH-PROKIT-2024-000",
            "SNITCH-PROKIT-2024-051",
            "SNITCH-PROKIT-2024-999",
            "PROKIT-001",
            "",
            "   ",
            None,
            12345,
            [],
            "'; DROP TABLE Measurements; --",
            "\x00",
        ]
        for bad_code in invalid_inputs:
            result = config.unlock_prokit(bad_code)
            self.assertFalse(result, f"unlock_prokit should return False for {bad_code!r}")
            self.assertFalse(os.path.exists(self.token_path), f"File created on invalid code {bad_code!r}")
            self.assertFalse(config.is_prokit_unlocked(), f"Unlocked on invalid code {bad_code!r}")

    def test_04_unlock_valid_code_and_persistence(self):
        """Valid code must return True, create .prokit_unlocked with hash, and is_prokit_unlocked() must be True."""
        code = "SNITCH-PROKIT-2024-001"
        expected_hash = "1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2"
        self.assertTrue(config.unlock_prokit(code))
        self.assertTrue(os.path.exists(self.token_path), ".prokit_unlocked file was not created")
        with open(self.token_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        self.assertEqual(content, expected_hash, "Token file does not contain expected SHA256 hash")
        self.assertTrue(config.is_prokit_unlocked())

    def test_05_unlock_case_and_whitespace_insensitivity(self):
        """Unlock should handle leading/trailing whitespace and lowercase gracefully."""
        self.assertTrue(config.unlock_prokit("  SNITCH-PROKIT-2024-002  "))
        self.assertTrue(config.is_prokit_unlocked())
        config.revoke_prokit()
        self.assertTrue(config.unlock_prokit("snitch-prokit-2024-002"))
        self.assertTrue(config.is_prokit_unlocked())

    def test_06_unlock_all_50_codes(self):
        """Verify all 50 codes SNITCH-PROKIT-2024-001 through -050 are accepted."""
        for i in range(1, 51):
            code = f"SNITCH-PROKIT-2024-{i:03d}"
            config.revoke_prokit()
            self.assertFalse(config.is_prokit_unlocked())
            unlocked = config.unlock_prokit(code)
            self.assertTrue(unlocked, f"Failed to unlock with valid code: {code}")
            self.assertTrue(config.is_prokit_unlocked())

    def test_07_revoke_prokit(self):
        """revoke_prokit must remove .prokit_unlocked and return True."""
        self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
        self.assertTrue(config.is_prokit_unlocked())
        self.assertTrue(os.path.exists(self.token_path))

        res = config.revoke_prokit()
        self.assertTrue(res)
        self.assertFalse(os.path.exists(self.token_path))
        self.assertFalse(config.is_prokit_unlocked())

    def test_08_revoke_idempotency(self):
        """Calling revoke_prokit when already locked should not fail and return True."""
        self.assertFalse(config.is_prokit_unlocked())
        res = config.revoke_prokit()
        self.assertTrue(res)
        self.assertFalse(config.is_prokit_unlocked())

    def test_09_existing_config_functions(self):
        """Ensure get_data_dir and get_db_path remain functional."""
        self.patcher.stop()  # Test real unpatched get_data_dir
        try:
            d = config.get_data_dir()
            self.assertIsInstance(d, str)
            self.assertTrue(os.path.isdir(d))
            db = config.get_db_path()
            self.assertIsInstance(db, str)
        finally:
            self.patcher.start()


if __name__ == "__main__":
    unittest.main(verbosity=2)
