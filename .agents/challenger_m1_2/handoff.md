# Challenger 2 Handoff Report: Cryptographic & Token Persistence Integrity (`config.py`)

## 1. Observation

Adversarial testing was executed directly against `/Users/ben/Desktop/InEarSnitch/config.py` using empirical verification harnesses.

### 1.1 Cryptographic Integrity & Hash Oracle Verification
- **Command**:
  ```bash
  python3 -c "
  import hashlib, config
  hashes = config.VALID_CODE_HASHES
  assert len(hashes) == 50
  for i in range(1, 51):
      code = f'SNITCH-PROKIT-2024-{i:03d}'
      h = hashlib.sha256(code.encode('utf-8')).hexdigest().lower()
      assert h in hashes
  "
  ```
- **Observed Result**:
  - `VALID_CODE_HASHES` in `config.py` lines 5–56 contains exactly 50 hashes.
  - Every single code `SNITCH-PROKIT-2024-001` through `SNITCH-PROKIT-2024-050` maps bijectively 1-to-1 to a hash in `VALID_CODE_HASHES`.
  - Zero duplicate hashes; set cardinality is exactly 50.
  - All hashes are exactly 64 lowercase hexadecimal characters `[0-9a-f]{64}`.
  - Exact match against the 50 hashes defined in `/Users/ben/Desktop/InEarSnitch/.agents/ORIGINAL_REQUEST.md` (lines 35–86).

### 1.2 Bypass, Collision, and Input Sanitization Stress Tests
- **Tested Scenarios**:
  - **Boundary & Off-by-one**: `SNITCH-PROKIT-2024-000`, `SNITCH-PROKIT-2024-051`, `SNITCH-PROKIT-2024-052`, `SNITCH-PROKIT-2024-100`, `SNITCH-PROKIT-2023-001`, `SNITCH-PROKIT-2025-001`, `SNITCH-PROKIT-2024-01`, `SNITCH-PROKIT-2024-1`, `SNITCH-PROKIT-2024-0001` -> All return `False`.
  - **Hash Reflection Attack**: Passing the 64-character SHA256 hex digest itself as the unlock code -> Returns `False`.
  - **Type Confusion**: `None`, `True`, `False`, `1`, `50`, `123.456`, `['SNITCH-PROKIT-2024-001']`, `{'code': ...}`, `b'SNITCH-PROKIT-2024-001'`, `object()` -> All return `False` without exceptions.
  - **Whitespace Handling**:
    - Outer whitespace/newlines (`"   SNITCH-PROKIT-2024-005   "`, `"\n\t\rSNITCH-PROKIT-2024-005\r\n"`, `"\u00a0SNITCH-PROKIT-2024-005\u2003"`) -> Returns `True` and unlocks cleanly.
    - Internal whitespace (`"SNITCH -PROKIT-2024-005"`, `"SNITCH-PROKIT -2024-005"`, `"SNITCH-PROKIT- 2024-005"`) -> Returns `False`.
  - **Case Normalization**: `"snitch-prokit-2024-005"` and `"SnItCh-PrOkIt-2024-005"` -> Return `True`.
  - **Injection Attacks**: Null byte injection (`"SNITCH-PROKIT-2024-005\x00"`), command injection (`"&& rm -rf /"`), and SQL injection patterns (`"\" OR \"1\"=\"1"`) -> All return `False`.
  - **Denial of Service**: 5 MB string input -> Completes instantaneously, returns `False`, no memory spike.

### 1.3 Token Persistence Format & Hex Digest Verification
- Tested across all 50 valid codes in isolated temporary directories.
- **Observed File Content**:
  - File path: `os.path.join(get_data_dir(), ".prokit_unlocked")`.
  - Byte size: Exactly 65 bytes (`64 bytes hex digest + 1 byte '\n'`).
  - Verbatim raw bytes: `hashlib.sha256(code.encode()).hexdigest().encode('utf-8') + b'\n'`.
  - Re-unlock with a new valid code overwrites the file cleanly without appending or corrupting prior data.
  - Failed unlock attempt with invalid code leaves existing valid token file intact.

### 1.4 Concurrency & Edge-Case Findings
- **Concurrent Unlocks & Checks**: 20 threads simultaneously unlocking and reading state completed 2,000 operations with 0 errors.
- **TOCTOU Race in `revoke_prokit()`**:
  - Lines 110–121 in `config.py`:
    ```python
    def revoke_prokit() -> bool:
        try:
            token_path = os.path.join(get_data_dir(), ".prokit_unlocked")
            if os.path.exists(token_path):
                os.remove(token_path)
            return True
        except OSError:
            return False
    ```
  - Observation: When multiple threads simultaneously invoke `revoke_prokit()`, Thread A removes the file between Thread B's `os.path.exists()` check and Thread B's `os.remove()` call. `os.remove()` raises `FileNotFoundError` (subclass of `OSError`), causing Thread B to return `False` instead of `True`.
  - Severity: **LOW** / Non-blocking for desktop UI (InEarSnitch UI thread invokes revocation sequentially).
- **Directory Bypass Edge Case**:
  - Observation: If `.prokit_unlocked` exists as a directory rather than a file, `is_prokit_unlocked()` returns `True` because it relies on `os.path.exists(token_path)` rather than `os.path.isfile(token_path)`.
  - Severity: **LOW** / Non-blocking.

---

## 2. Logic Chain

1. **Bijective Mapping Proves Cryptographic Soundness**: Calculating SHA256 hashes for the canonical series `SNITCH-PROKIT-2024-001` through `SNITCH-PROKIT-2024-050` and comparing against `VALID_CODE_HASHES` demonstrates an exact 50-to-50 correspondence. Because the set difference in both directions is empty (`hashes ^ expected == set()`), no unintended backdoor hashes exist in the codebase.
2. **Defensive Normalization Prevents False Rejections and Bypasses**: The implementation in `unlock_prokit()` utilizes `isinstance(code, str)` followed by `.strip().upper()`. Because Python's `strip()` handles unicode and ASCII whitespace, user copy-paste artifacts do not cause false lockouts. Because internal whitespace and delimiters are unstripped, no formatting bypasses succeed.
3. **Token File Integrity Aligns with Offline Security Model**: The system persists the 64-character SHA256 digest followed by a single newline. Verification confirmed that every unlock operation produces an exact 65-byte file matching the hash of the code provided. Overwriting an existing token replaces the contents rather than corrupting or appending.
4. **State Transitions are Deterministic**: The state machine correctly transitions from locked to unlocked on valid input, remains unlocked on invalid secondary input, and returns to locked on revocation. Read-only permissions and unwriteable directories are trapped by `except OSError:` and fail gracefully without unhandled exceptions or application crashes.
5. **Concurrency Assessment**: Although `revoke_prokit()` exhibits a TOCTOU race under synthetic multi-threaded hammer tests, desktop usage in InEarSnitch executes unlock and revocation strictly via the main Qt event loop. The system converges to the correct state (token file removed, feature locked).

---

## 3. Caveats

- **Local Storage Model**: The gate is an offline client-side validation system. Since client code runs locally on Python, any local user with root/user access can manually create `.prokit_unlocked` in `~/Documents/InEarSnitch`. This is by design per `ORIGINAL_REQUEST.md` (offline, no phone-home or DRM daemon).
- **Fixed Batch Scope**: `VALID_CODE_HASHES` is strictly bound to the 2024 batch (001–050). Codes outside this range require a future code update.
- **Hardware Failure / Power Cut**: Direct file writing via `with open(..., "w")` without an atomic rename pattern (`tempfile.NamedTemporaryFile` + `os.replace`) means a power cut mid-write could leave a 0-byte `.prokit_unlocked` file. Because `is_prokit_unlocked()` checks `os.path.exists`, a 0-byte file still unlocks the feature.

---

## 4. Conclusion

**Verdict: APPROVE**

The cryptographic and token persistence implementation of Milestone 1 (`config.py`) satisfies all requirements:
1. Exactly 50/50 cryptographic correspondence with `SNITCH-PROKIT-2024-001..050`.
2. 100% rejection rate against boundary, bypass, collision, type-confusion, and injection attacks.
3. Exact 65-byte SHA256 hex digest token persistence.
4. All 19 checks in `smoke_test.py` pass.
5. All 9 unit tests in `tests/test_prokit_gate.py` pass.

### Advisory Recommendations (Non-blocking):
1. **Idempotent Revoke**: Replace `if os.path.exists(token_path): os.remove(token_path)` with:
   ```python
   try:
       os.remove(token_path)
   except FileNotFoundError:
       pass
   ```
   This eliminates the multi-thread TOCTOU window.
2. **File Check**: Change `os.path.exists(token_path)` to `os.path.isfile(token_path)` in `is_prokit_unlocked()` to ensure directories cannot satisfy the unlock condition.

---

## 5. Verification Method

To independently execute and verify this challenge report:

1. **Verify Smoke Test & Existing Test Suite**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 smoke_test.py
   cd /Users/ben/Desktop/InEarSnitch && python3 -m unittest tests/test_prokit_gate.py
   ```

2. **Run Cryptographic Bijection Oracle**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 -c "
   import hashlib, config
   expected = {hashlib.sha256(f'SNITCH-PROKIT-2024-{i:03d}'.encode()).hexdigest() for i in range(1, 51)}
   assert config.VALID_CODE_HASHES == expected and len(expected) == 50
   print('✅ Cryptographic Oracle: 50/50 Perfect Match')
   "
   ```

3. **Run Adversarial Bypass & Persistence Verifier**:
   ```bash
   cd /Users/ben/Desktop/InEarSnitch && python3 -c "
   import tempfile, hashlib, os
   from unittest.mock import patch
   import config

   with tempfile.TemporaryDirectory() as td:
       with patch('config.get_data_dir', return_value=td):
           token = os.path.join(td, '.prokit_unlocked')
           assert not config.unlock_prokit('SNITCH-PROKIT-2024-000')
           assert not config.unlock_prokit('SNITCH-PROKIT-2024-051')
           assert not config.unlock_prokit(None)
           assert config.unlock_prokit('snitch-prokit-2024-001 ')
           with open(token, 'rb') as f:
               assert f.read() == (hashlib.sha256(b'SNITCH-PROKIT-2024-001').hexdigest() + '\n').encode()
           assert config.revoke_prokit()
           assert not config.is_prokit_unlocked()
   print('✅ Adversarial Bypass & Persistence: Verified')
   "
   ```
