"""
Adversarial stress-test suite for Milestone 1 (config.py ProKit Offline Unlock Gate).
Authored by Challenger 1.

Verifies boundaries, type safety, invalid formats, idempotency, rapid state toggle,
file permissions, simulated disk failures, and guarantees no unhandled exceptions.
"""

import os
import sys
import unittest
import tempfile
import stat
import threading
from unittest.mock import patch, mock_open

# Ensure project root is on sys.path
cur = os.path.dirname(os.path.abspath(__file__))
while cur != os.path.dirname(cur):
    if os.path.exists(os.path.join(cur, "config.py")):
        if cur not in sys.path:
            sys.path.insert(0, cur)
        break
    cur = os.path.dirname(cur)

import config


class TestProKitAdversarial(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.token_path = os.path.join(self.test_dir.name, ".prokit_unlocked")
        self.patcher = patch("config.get_data_dir", return_value=self.test_dir.name)
        self.mock_get_data_dir = self.patcher.start()

    def tearDown(self):
        # Restore permissions if any test altered directory mode so cleanup succeeds
        try:
            os.chmod(self.test_dir.name, stat.S_IRWXU)
            if os.path.exists(self.token_path):
                os.chmod(self.token_path, stat.S_IRWXU)
        except OSError:
            pass
        self.patcher.stop()
        self.test_dir.cleanup()

    # =========================================================================
    # 0. MATHEMATICAL AND CRYPTOGRAPHIC BIJECTION
    # =========================================================================

    def test_exact_hash_bijection_001_to_050(self):
        """Verify VALID_CODE_HASHES is an EXACT 1:1 match to SHA256('SNITCH-PROKIT-2024-001'..'050')."""
        import hashlib
        generated_hashes = {
            hashlib.sha256(f"SNITCH-PROKIT-2024-{i:03d}".encode("utf-8")).hexdigest()
            for i in range(1, 51)
        }
        self.assertEqual(len(generated_hashes), 50)
        self.assertEqual(
            config.VALID_CODE_HASHES,
            generated_hashes,
            "VALID_CODE_HASHES does not exactly match the generated hashes of SNITCH-PROKIT-2024-001 through -050!"
        )

    # =========================================================================
    # 1. NON-STRING AND BIZARRE TYPE INPUTS (No crashes, returns False)
    # =========================================================================

    def test_non_string_types(self):
        """Adversarial non-string types must return False without crashing."""
        class CustomObj:
            def __str__(self):
                raise RuntimeError("Explosive string conversion")

        class ExplodingType:
            def strip(self):
                raise RuntimeError("Explosive strip")

        non_strings = [
            None,
            0,
            1,
            -1,
            2024,
            10**50,
            3.14159,
            float("nan"),
            float("inf"),
            float("-inf"),
            True,
            False,
            [],
            [None],
            ["SNITCH-PROKIT-2024-001"],
            (),
            ("SNITCH-PROKIT-2024-001",),
            {},
            {"code": "SNITCH-PROKIT-2024-001"},
            set(),
            {"SNITCH-PROKIT-2024-001"},
            frozenset(),
            b"SNITCH-PROKIT-2024-001",
            bytearray(b"SNITCH-PROKIT-2024-001"),
            memoryview(b"SNITCH-PROKIT-2024-001"),
            object(),
            CustomObj(),
            ExplodingType(),
            lambda: "SNITCH-PROKIT-2024-001",
            config,
        ]

        for bad_input in non_strings:
            try:
                res = config.unlock_prokit(bad_input)
                self.assertFalse(res, f"Expected False for {type(bad_input)}: {bad_input!r}")
                self.assertFalse(config.is_prokit_unlocked(), f"Gate unlocked for {bad_input!r}")
                self.assertFalse(os.path.exists(self.token_path), f"File created for {bad_input!r}")
            except Exception as exc:
                self.fail(f"unlock_prokit raised unhandled exception {type(exc).__name__} for input {bad_input!r}: {exc}")

    # =========================================================================
    # 2. STRING BOUNDARY VALUES & WHITESPACE VARIANTS
    # =========================================================================

    def test_empty_and_whitespace_only_strings(self):
        """Empty strings and all whitespace variants must return False without crashing."""
        whitespace_variants = [
            "",
            " ",
            "    ",
            "\t",
            "\t\t\t",
            "\n",
            "\r\n",
            "\r",
            "\v",
            "\f",
            " \t \r \n \f \v ",
            "\u00a0",  # Non-breaking space
            "\u2000",  # En quad
            "\u2001",  # Em quad
            "\u2003",  # Em space
            "\u3000",  # Ideographic space
        ]

        for ws in whitespace_variants:
            try:
                res = config.unlock_prokit(ws)
                self.assertFalse(res, f"Expected False for whitespace input {ws!r}")
                self.assertFalse(config.is_prokit_unlocked())
                self.assertFalse(os.path.exists(self.token_path))
            except Exception as exc:
                self.fail(f"Unhandled exception for whitespace {ws!r}: {exc}")

    def test_case_and_whitespace_robustness_on_valid_codes(self):
        """Valid codes with arbitrary casing and surrounding whitespace must succeed."""
        valid_variations = [
            "snitch-prokit-2024-001",
            "Snitch-ProKit-2024-001",
            "sNiTcH-pRoKiT-2024-001",
            "  snitch-prokit-2024-001  ",
            "\t\n  SNITCH-PROKIT-2024-001  \r\n",
            " \v\f SNITCH-PROKIT-2024-001 \t ",
        ]
        for variant in valid_variations:
            config.revoke_prokit()
            self.assertFalse(config.is_prokit_unlocked())
            res = config.unlock_prokit(variant)
            self.assertTrue(res, f"Failed to unlock with variant: {variant!r}")
            self.assertTrue(config.is_prokit_unlocked())

    def test_code_boundary_values(self):
        """Boundary values (-000, -051, -999, year boundaries, format mutations) must fail."""
        boundary_cases = [
            # Lower boundary out-of-range
            "SNITCH-PROKIT-2024-000",
            # Upper boundary out-of-range
            "SNITCH-PROKIT-2024-051",
            "SNITCH-PROKIT-2024-052",
            "SNITCH-PROKIT-2024-099",
            "SNITCH-PROKIT-2024-100",
            "SNITCH-PROKIT-2024-999",
            # Digit format variations
            "SNITCH-PROKIT-2024-1",
            "SNITCH-PROKIT-2024-01",
            "SNITCH-PROKIT-2024-0001",
            "SNITCH-PROKIT-2024--001",
            "SNITCH-PROKIT-2024-+001",
            # Year variations
            "SNITCH-PROKIT-2023-001",
            "SNITCH-PROKIT-2025-001",
            "SNITCH-PROKIT-2024-2024-001",
            # Prefix variations
            "PROKIT-2024-001",
            "SNITCH-2024-001",
            "SNITCH-PROKIT-001",
            "SNITCH-PROKIT-2024",
            # Delimiter mutations
            "SNITCH_PROKIT_2024_001",
            "SNITCH PROKIT 2024 001",
            "SNITCH/PROKIT/2024/001",
            "SNITCH--PROKIT--2024--001",
            "SNITCH - PROKIT - 2024 - 001",
            "SNITCH-PROKIT-2024 - 001",
            "SNITCH-PROKIT- 2024-001",
            # Injected characters and payloads
            "SNITCH-PROKIT-2024-001\x00",
            "SNITCH-PROKIT-2024-001\x00EXTRA",
            "\x00SNITCH-PROKIT-2024-001",
            "SNITCH-PROKIT-2024-001-EXTRA",
            "PREFIX-SNITCH-PROKIT-2024-001",
            "SNITCH-PROKIT-2024-001\nSNITCH-PROKIT-2024-002",
            "'; DROP TABLE Measurements; --",
            "<script>alert('xss')</script>",
            "../../.prokit_unlocked",
            "\\..\\..\\.prokit_unlocked",
        ]

        for code in boundary_cases:
            try:
                res = config.unlock_prokit(code)
                self.assertFalse(res, f"Boundary case unexpectedly unlocked: {code!r}")
                self.assertFalse(config.is_prokit_unlocked())
                self.assertFalse(os.path.exists(self.token_path))
            except Exception as exc:
                self.fail(f"Unhandled exception on boundary case {code!r}: {exc}")

    def test_massive_string_dos_resilience(self):
        """Massive inputs (up to 1MB) should be hashed safely without memory exhaustion or crash."""
        massive_junk = "A" * 1_000_000
        res = config.unlock_prokit(massive_junk)
        self.assertFalse(res)

        massive_padded = (" " * 500_000) + "SNITCH-PROKIT-2024-001" + (" " * 500_000)
        res = config.unlock_prokit(massive_padded)
        self.assertTrue(res)
        self.assertTrue(config.is_prokit_unlocked())

    # =========================================================================
    # 3. IDEMPOTENCY, CONSECUTIVE UNLOCKS, RAPID TOGGLE & CONCURRENCY
    # =========================================================================

    def test_idempotent_revoking(self):
        """Calling revoke_prokit multiple times consecutively must always return True."""
        # When locked:
        self.assertFalse(config.is_prokit_unlocked())
        for i in range(25):
            res = config.revoke_prokit()
            self.assertTrue(res, f"revoke_prokit returned False on locked iteration {i}")
            self.assertFalse(config.is_prokit_unlocked())

        # When unlocked:
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        self.assertTrue(config.is_prokit_unlocked())
        for i in range(25):
            res = config.revoke_prokit()
            self.assertTrue(res, f"revoke_prokit returned False on unlocked iteration {i}")
            self.assertFalse(config.is_prokit_unlocked())

    def test_multiple_consecutive_unlocks(self):
        """Calling unlock_prokit repeatedly (same code or different codes) must succeed."""
        # Repeat same code
        for i in range(20):
            res = config.unlock_prokit("SNITCH-PROKIT-2024-001")
            self.assertTrue(res, f"unlock_prokit failed on repetition {i}")
            self.assertTrue(config.is_prokit_unlocked())

        # Alternate between different valid codes
        for i in range(1, 10):
            code = f"SNITCH-PROKIT-2024-{i:03d}"
            res = config.unlock_prokit(code)
            self.assertTrue(res, f"Failed consecutive unlock with {code}")
            self.assertTrue(config.is_prokit_unlocked())

    def test_invalid_unlock_does_not_revoke_existing_unlock(self):
        """Attempting to unlock with an invalid code when already unlocked does not disturb unlocked state."""
        self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
        self.assertTrue(config.is_prokit_unlocked())

        res = config.unlock_prokit("INVALID-CODE-XYZ")
        self.assertFalse(res)
        # Verify state is still unlocked and file still exists
        self.assertTrue(config.is_prokit_unlocked())
        self.assertTrue(os.path.exists(self.token_path))

    def test_unicode_and_special_character_paths(self):
        """Verify unlock, check, and revoke work when data directory contains unicode and spaces."""
        special_dir = os.path.join(self.test_dir.name, "Messung_München_🎧_2024")
        os.makedirs(special_dir, exist_ok=True)
        with patch("config.get_data_dir", return_value=special_dir):
            self.assertFalse(config.is_prokit_unlocked())
            self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
            self.assertTrue(config.is_prokit_unlocked())
            token = os.path.join(special_dir, ".prokit_unlocked")
            self.assertTrue(os.path.exists(token))
            self.assertTrue(config.revoke_prokit())
            self.assertFalse(config.is_prokit_unlocked())

    def test_token_file_contains_whitespace_or_newlines(self):
        """Existing token file containing hashes with trailing newlines or spaces still unlocks."""
        # unlock_prokit writes hash + "\n"
        self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
        self.assertTrue(config.is_prokit_unlocked())
        # Even if token has extra newlines/spaces
        with open(self.token_path, "w", encoding="utf-8") as f:
            f.write("\n\n  1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2  \n\n")
        self.assertTrue(config.is_prokit_unlocked())

    def test_rapid_unlock_revoke_toggle(self):
        """Rapidly toggling between unlock and revoke (200 cycles) must maintain exact state consistency."""
        for i in range(200):
            # Unlock
            res_u = config.unlock_prokit("SNITCH-PROKIT-2024-005")
            self.assertTrue(res_u, f"Toggle unlock failed at cycle {i}")
            self.assertTrue(config.is_prokit_unlocked(), f"Toggle is_prokit_unlocked False at cycle {i}")
            self.assertTrue(os.path.exists(self.token_path), f"Token missing at cycle {i}")

            # Revoke
            res_r = config.revoke_prokit()
            self.assertTrue(res_r, f"Toggle revoke failed at cycle {i}")
            self.assertFalse(config.is_prokit_unlocked(), f"Toggle is_prokit_unlocked True after revoke at cycle {i}")
            self.assertFalse(os.path.exists(self.token_path), f"Token still present at cycle {i}")

    def test_multithreaded_concurrency(self):
        """Concurrent calls to unlock, revoke, and is_prokit_unlocked across 10 threads must not crash."""
        errors = []

        def worker(thread_id):
            try:
                for i in range(50):
                    config.is_prokit_unlocked()
                    if i % 3 == 0:
                        config.unlock_prokit("SNITCH-PROKIT-2024-010")
                    elif i % 3 == 1:
                        config.revoke_prokit()
                    else:
                        config.unlock_prokit("INVALID-CONCURRENT")
            except Exception as exc:
                errors.append((thread_id, exc))

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent execution produced errors: {errors}")

    # =========================================================================
    # 4. FILE PERMISSION & READ-ONLY DISK SIMULATION
    # =========================================================================

    def test_read_only_directory_unlock_fails_gracefully(self):
        """When data directory is read-only (0o555), unlock_prokit must return False without crashing."""
        os.chmod(self.test_dir.name, 0o555)
        try:
            res = config.unlock_prokit("SNITCH-PROKIT-2024-001")
            self.assertFalse(res)
            self.assertFalse(config.is_prokit_unlocked())
        finally:
            os.chmod(self.test_dir.name, 0o755)

    def test_read_only_directory_revoke_existing_token_fails_gracefully(self):
        """When token exists but directory is read-only (cannot unlink), revoke_prokit returns False without crashing."""
        self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
        self.assertTrue(config.is_prokit_unlocked())

        os.chmod(self.test_dir.name, 0o555)
        try:
            res = config.revoke_prokit()
            # On POSIX, unlinking a file requires write permission on the directory.
            # config.revoke_prokit catches OSError and returns False.
            self.assertFalse(res)
            # Token should still exist
            self.assertTrue(config.is_prokit_unlocked())
        finally:
            os.chmod(self.test_dir.name, 0o755)
            # Now cleanup should succeed
            self.assertTrue(config.revoke_prokit())
            self.assertFalse(config.is_prokit_unlocked())

    def test_read_only_token_file_unlock_fails_gracefully(self):
        """When token file exists and is read-only (0o444), overwriting it with unlock_prokit returns False."""
        self.assertTrue(config.unlock_prokit("SNITCH-PROKIT-2024-001"))
        os.chmod(self.token_path, 0o444)
        try:
            res = config.unlock_prokit("SNITCH-PROKIT-2024-002")
            self.assertFalse(res)
        finally:
            os.chmod(self.token_path, 0o644)

    def test_simulated_disk_io_errors(self):
        """Simulate severe I/O errors (disk full, I/O error, permission denied) via mock."""
        # 1. IOError on open() during unlock
        with patch("builtins.open", side_effect=OSError("Disk full (ENOSPC)")):
            res = config.unlock_prokit("SNITCH-PROKIT-2024-001")
            self.assertFalse(res, "unlock_prokit should return False on disk full")

        # 2. OSError on os.path.exists during is_prokit_unlocked
        with patch("os.path.exists", side_effect=OSError("I/O error on stat")):
            res = config.is_prokit_unlocked()
            self.assertFalse(res, "is_prokit_unlocked should return False on stat error")

        # 3. OSError on os.remove during revoke_prokit
        # First ensure file is there
        config.unlock_prokit("SNITCH-PROKIT-2024-001")
        with patch("os.remove", side_effect=OSError("Read-only filesystem (EROFS)")):
            res = config.revoke_prokit()
            self.assertFalse(res, "revoke_prokit should return False when os.remove fails")

    def test_token_is_directory_handling(self):
        """If .prokit_unlocked exists as a directory, operations must not crash."""
        os.mkdir(self.token_path)
        self.assertTrue(os.path.isdir(self.token_path))

        # unlock_prokit tries open() which raises IsADirectoryError (OSError)
        res = config.unlock_prokit("SNITCH-PROKIT-2024-001")
        self.assertFalse(res)

        # revoke_prokit tries os.remove() which raises IsADirectoryError (OSError)
        res = config.revoke_prokit()
        self.assertFalse(res)

        # Cleanup
        os.rmdir(self.token_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
