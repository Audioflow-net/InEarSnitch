# Milestone 1 Challenger Report: Offline Unlock System (`config.py`)

## Challenge Summary

- **Overall Risk Assessment**: LOW
- **Verdict**: **APPROVE**
- **Test Suite**: `/Users/ben/Desktop/InEarSnitch/tests/test_prokit_adversarial.py` (18 adversarial test methods, 100% pass)
- **Baseline Suite**: `/Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py` (9 unit test methods, 100% pass)
- **Smoke Test**: `/Users/ben/Desktop/InEarSnitch/smoke_test.py` (19/19 checks pass)

---

## 1. Observation

Direct observations from source code inspection and empirical test execution:

1. **Exact 50-Hash Mathematical Match**:
   - Source: `/Users/ben/Desktop/InEarSnitch/config.py:5-56` (`VALID_CODE_HASHES`).
   - Empirical test: `test_exact_hash_bijection_001_to_050`.
   - Result: `VALID_CODE_HASHES` is an exact 1:1 mathematical match with the set of SHA256 hashes generated from `"SNITCH-PROKIT-2024-001"` through `"SNITCH-PROKIT-2024-050"`. No spurious hashes exist; no required hashes are missing.

2. **Type Safety & Malformed Inputs**:
   - Source: `/Users/ben/Desktop/InEarSnitch/config.py:94-98`.
     ```python
     if not isinstance(code, str):
         return False
     normalized = code.strip().upper()
     if not normalized:
         return False
     ```
   - Tested 30+ non-string types (`None`, `int`, `float("nan")`, `bool`, `list`, `dict`, `set`, raw `bytes`, custom objects with throwing `__str__` / `strip`, lambdas, modules) and various whitespace variants (spaces, tabs, newlines, form feeds, non-breaking spaces `\u00a0`, ideographic spaces `\u3000`).
   - Result: All return `False`. Zero unhandled exceptions or crashes.

3. **Boundary Values and Injections**:
   - Codes tested: `SNITCH-PROKIT-2024-000` (lower boundary - 1), `SNITCH-PROKIT-2024-051` (upper boundary + 1), `SNITCH-PROKIT-2024-999`, missing leading zeros (`-1`), extra digits (`-0001`), negative offsets, year mutations (`2023`, `2025`), prefix mutations (`PROKIT-`, `SNITCH-`), delimiter changes (`_`, `/`, spaces), embedded null bytes (`\x00`), SQL injection strings (`'; DROP TABLE Measurements; --`), XSS tags, path traversals (`../../.prokit_unlocked`).
   - Result: All return `False`. Token file is not created; `is_prokit_unlocked()` remains `False`.

4. **DoS & Resource Exhaustion Resilience**:
   - Massive inputs: 1,000,000 characters junk string, 1,000,000 characters whitespace padding around valid code.
   - Result: SHA256 processes the string linearly in O(N) time without memory leak or crash. Padded valid code unlocks successfully; junk string returns `False`.

5. **State Transition, Idempotency & Concurrency**:
   - Idempotent revoke: 25 consecutive calls to `revoke_prokit()` when locked and 25 when unlocked all return `True`.
   - Idempotent unlock: 20 consecutive unlocks with same valid code and consecutive unlocks with alternating valid codes all return `True`.
   - Bad code safety: Calling `unlock_prokit("BAD")` when already unlocked returns `False` but preserves the unlocked state.
   - Rapid toggle: 200 consecutive unlock-then-revoke cycles executed with 100% state synchronization.
   - Concurrency stress: 10 threads running 50 iterations each of concurrent `is_prokit_unlocked()`, `unlock_prokit()`, and `revoke_prokit()` finished with 0 unhandled exceptions.

6. **Filesystem Permission & Simulated I/O Errors**:
   - Read-only data directory (`chmod 0o555`): `unlock_prokit` returns `False` without crashing. `revoke_prokit` on existing file in read-only dir returns `False` without crashing.
   - Read-only token file (`chmod 0o444`): Overwriting with `unlock_prokit` returns `False` without crashing.
   - Simulated disk errors: Mocking `open()` raising `OSError("Disk full (ENOSPC)")`, `os.path.exists()` raising `OSError("I/O error")`, and `os.remove()` raising `OSError("Read-only filesystem")` all gracefully return `False` without bubbling unhandled exceptions.
   - Unusual token paths: Testing data directories with spaces, German umlauts, and emoji (`Messung_München_🎧_2024`) works correctly.
   - Token is a directory: If `.prokit_unlocked` is a directory, `unlock_prokit` and `revoke_prokit` both safely return `False` without crashing (`IsADirectoryError` caught under `OSError`).

---

## 2. Logic Chain

1. **Premise**: An offline gate in a desktop audio measurement tool must be resilient to user input error, malicious payloads, file system anomalies, and resource constraints without terminating the parent application process.
2. **Observation 1 & 2**: `config.py` enforces explicit type filtering (`isinstance(code, str)`), string normalization (`strip().upper()`), and empty string checks (`if not normalized`) before any hashing or filesystem operations.
3. **Observation 3**: The exact bijection test demonstrates that only the exact 50 intended codes (`SNITCH-PROKIT-2024-001` through `-050`) can ever hash to a match in `VALID_CODE_HASHES`. No adjacent values (`-000`, `-051`) or malformed variants can match.
4. **Observation 4, 5 & 6**: Wrapping all I/O calls (`open()`, `os.path.exists()`, `os.remove()`) in `try...except OSError` ensures that no filesystem failure (unwritable folder, full disk, locked file, directory collision) can escape as an unhandled crash to PySide6.
5. **Conclusion**: The implementation in `config.py` satisfies all acceptance criteria, handles all boundary and failure modes gracefully, and introduces zero regressions into the application.

---

## 3. Caveats

1. **Existence-Based Gate Check**:
   - `is_prokit_unlocked()` checks `os.path.exists(token_path)`. It does not parse or re-verify the hash inside `.prokit_unlocked` against `VALID_CODE_HASHES`. This is by design according to the interface contract in `PROJECT.md` ("Returns True if .prokit_unlocked exists in get_data_dir()") and optimizes performance by avoiding repeated disk reads during UI rendering. If an empty `.prokit_unlocked` file is manually placed on disk, the gate will report `True`.
2. **Race Window in `revoke_prokit()`**:
   - In `revoke_prokit()`, if `.prokit_unlocked` is removed by an external process in the exact microsecond between `os.path.exists()` and `os.remove()`, `os.remove()` raises `FileNotFoundError`. The `except OSError` catches it and returns `False`. In a single-user desktop PySide6 app, this edge case does not cause crashes.
3. **Internal Whitespace**:
   - Leading and trailing whitespace is stripped, but internal whitespace (e.g. `SNITCH - PROKIT`) is not removed. Users must type or paste codes without internal spaces. This is standard behavior.

---

## 4. Conclusion

**Verdict: APPROVE**

The implementation in `/Users/ben/Desktop/InEarSnitch/config.py` is empirically robust:
- Validated with 18 comprehensive adversarial tests in `tests/test_prokit_adversarial.py`.
- Validated with 9 unit tests in `tests/test_prokit_gate.py`.
- Baseline `smoke_test.py` passes 19/19 checks cleanly.
- No unhandled exceptions, no crashes under hostile inputs, simulated I/O errors, or rapid state changes.

---

## 5. Verification Method

To reproduce all adversarial and gate test results independently:

```bash
# 1. Run Challenger 1 Adversarial Suite (18 tests)
python3 -m unittest -v tests/test_prokit_adversarial.py

# 2. Run Worker Gate Unit Suite (9 tests)
python3 -m unittest -v tests/test_prokit_gate.py

# 3. Run All ProKit Test Suites (27 tests total)
python3 -m unittest discover -s tests -p "test_prokit_*.py"

# 4. Run Application Baseline Smoke Test
python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```
