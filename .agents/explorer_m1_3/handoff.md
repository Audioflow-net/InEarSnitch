# Milestone 1 Verification & Safety Report: Offline Unlock System (`config.py`)

## 1. Observation

1. **Git Branch & Repository Status**:
   - Running `git branch --show-current` in `/Users/ben/Desktop/InEarSnitch` outputs `main`.
2. **Smoke Test Baseline**:
   - Running `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` exited with code 0:
     ```
     🔍 SMOKE TEST — InEar Snitch
     1️⃣  Syntax Check: main.py, analysis_ui.py, audio_engine.py, analysis.py (all passed)
     2️⃣  Critical Imports: PySide6, pyqtgraph (passed)
     3️⃣  Critical Widget References (main.py): 9 widgets (all passed)
     4️⃣  Data Flow & Anti-Regression: 4 checks (all passed)
     ==================================================
     ✅ ALL 19 CHECKS PASSED
     ==================================================
     ```
3. **Current State of `config.py`**:
   - File `/Users/ben/Desktop/InEarSnitch/config.py` has 24 lines:
     - Lines 4–13: `def get_data_dir(): ...` returning `~/Documents/InEarSnitch`.
     - Lines 15–24: `def get_db_path(): ...` returning `inearsnitch.db`.
     - Missing: `VALID_CODE_HASHES`, `is_prokit_unlocked()`, `unlock_prokit(code)`, `revoke_prokit()`.
4. **Current State of Token File**:
   - `os.path.join(get_data_dir(), '.prokit_unlocked')` (`/Users/ben/Documents/InEarSnitch/.prokit_unlocked`) evaluated to `Exists: False`.
5. **Secret Codes & Hashes Integrity**:
   - `/Users/ben/Desktop/InEarSnitch/PROKIT_CODES_SECRET.csv` contains 50 lines from `SNITCH-PROKIT-2024-001` to `SNITCH-PROKIT-2024-050`.
   - Running SHA256 computation over each code verified a 100% exact match against the 50 hashes listed in `ORIGINAL_REQUEST.md` (lines 35–86).
6. **Execution Environment**:
   - System python `/usr/bin/python3` has `unittest`, `hashlib`, `os`, `sys`, `tempfile`, and `unittest.mock`.
   - `pytest` is not installed globally (`No module named pytest`). Test commands must use standard `python3 -m unittest` or `python3 -c "..."`.

---

## 2. Logic Chain

1. **Observation 1 & 2** establish that the project is in a clean, working baseline state on `main` branch with 19/19 smoke checks passing.
2. **Observation 3** confirms that `config.py` does not yet have any ProKit gate functionality.
3. **Observation 4 & 5** confirm that the 50 hashes in `ORIGINAL_REQUEST.md` are cryptographically verified and that the machine currently has no `.prokit_unlocked` token file.
4. **Observation 6** implies all verification tools must rely on Python's built-in `unittest` runner or inline CLI scripts so that Workers and Reviewers can execute them without external dependency failures.
5. To guarantee test safety, unit tests must never overwrite or delete a developer's real `~/Documents/InEarSnitch/.prokit_unlocked` file during automated test runs. Therefore, test harnesses must patch `config.get_data_dir` to point to an isolated `tempfile.TemporaryDirectory()`.
6. To satisfy the TDD requirement:
   - Running the test harness against baseline `config.py` was directly observed to fail on 8 missing ProKit attributes/methods (Red phase).
   - Running the test harness against the reference implementation passed all 9 test methods cleanly (Green phase).

---

## 3. Caveats

1. **Input Normalization**:
   - Real users entering codes via dialogs may introduce leading/trailing spaces or lowercase text.
   - We recommend `code.strip().upper()` in `unlock_prokit()` so `snitch-prokit-2024-001` and `  SNITCH-PROKIT-2024-001  ` work seamlessly.
2. **Filesystem Safety & Permissions**:
   - `unlock_prokit()` and `revoke_prokit()` should use `try/except OSError` when writing or deleting files to prevent unexpected crashes on read-only filesystems or permission denials.
3. **Directory Policy**:
   - Under project rules, source and test files must not live in `.agents/`. The test file is staged at `/Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_3/proposed_test_prokit_gate.py`. The M1 Worker should copy it to `/Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py`.

---

## 4. Conclusion

The testing and verification plan for Milestone 1 is fully defined, validated, and documented.
- **Reference test suite created**: `.agents/explorer_m1_3/proposed_test_prokit_gate.py` with 9 test methods covering all edge cases.
- **Verification commands formulated**: 4 concrete commands spanning isolated CLI verification, real-filesystem verification with teardown, unit test runner, and regression smoke test.
- **Acceptance criteria finalized**: Explicit checks for hash set integrity, unlock validation, token persistence, revocation idempotency, and anti-regression.

---

## 5. Verification Method

### 1. Concrete Test Commands for Worker & Reviewers

#### Command A: Fast Isolated CLI Verification (Zero Side-Effects)
Execute in terminal:
```bash
cd /Users/ben/Desktop/InEarSnitch && python3 -c "
import tempfile, os
from unittest.mock import patch
import config

with tempfile.TemporaryDirectory() as td:
    with patch('config.get_data_dir', return_value=td):
        # 1. Hashes integrity
        assert hasattr(config, 'VALID_CODE_HASHES'), 'Missing VALID_CODE_HASHES'
        assert len(config.VALID_CODE_HASHES) == 50, 'VALID_CODE_HASHES must contain 50 items'
        
        # 2. Initial state
        assert not config.is_prokit_unlocked(), 'Must start locked'
        
        # 3. Invalid codes rejection
        for bad in ['WRONG-CODE', 'SNITCH-PROKIT-2024-000', 'SNITCH-PROKIT-2024-051', '', '   ', None, 12345]:
            assert not config.unlock_prokit(bad), f'Should fail for {bad}'
            assert not config.is_prokit_unlocked(), 'Should remain locked'
            assert not os.path.exists(os.path.join(td, '.prokit_unlocked')), 'No token file should exist'
        
        # 4. Valid unlock & token persistence
        assert config.unlock_prokit('SNITCH-PROKIT-2024-001'), 'Valid code should succeed'
        assert config.is_prokit_unlocked(), 'Must be unlocked'
        token_p = os.path.join(td, '.prokit_unlocked')
        assert os.path.exists(token_p), 'Token file must exist'
        with open(token_p, 'r', encoding='utf-8') as f:
            h = f.read().strip()
        assert h == '1828f2d5760d4cf839ca49453181698832d48e80f8c5a790333bd72d3783dbb2', 'Hash mismatch in token'
        
        # 5. Revocation
        assert config.revoke_prokit(), 'Revoke must return True'
        assert not config.is_prokit_unlocked(), 'Must be locked after revoke'
        assert not os.path.exists(token_p), 'Token file must be deleted'
        
        # 6. Idempotent revocation
        assert config.revoke_prokit(), 'Revoke again must return True without error'

print('✅ ALL PROKIT GATE CHECKS PASSED!')
"
```
**Expected Output**: `✅ ALL PROKIT GATE CHECKS PASSED!`

---

#### Command B: Real Filesystem Verification (with Safe Backup & Restore)
Tests the live `get_data_dir()` location, automatically restoring any prior state:
```bash
cd /Users/ben/Desktop/InEarSnitch && python3 -c "
import os, config
p = os.path.join(config.get_data_dir(), '.prokit_unlocked')
backup = None
if os.path.exists(p):
    with open(p, 'rb') as f:
        backup = f.read()

try:
    if os.path.exists(p):
        os.remove(p)
    assert not config.is_prokit_unlocked(), 'Should be locked initially'
    
    # Test invalid code
    assert not config.unlock_prokit('WRONG-CODE-TEST')
    assert not os.path.exists(p), 'File should not exist after invalid code'
    assert not config.is_prokit_unlocked()
    
    # Test valid code
    assert config.unlock_prokit('SNITCH-PROKIT-2024-001'), 'Valid code failed'
    assert os.path.exists(p), 'Token file was not created'
    assert config.is_prokit_unlocked(), 'is_prokit_unlocked returned False'
    
    # Test revoke
    assert config.revoke_prokit(), 'revoke_prokit returned False'
    assert not os.path.exists(p), 'Token file was not deleted'
    assert not config.is_prokit_unlocked(), 'is_prokit_unlocked returned True after revoke'
    print('✅ Real filesystem verification passed!')
finally:
    if backup is not None:
        with open(p, 'wb') as f:
            f.write(backup)
    elif os.path.exists(p):
        os.remove(p)
"
```
**Expected Output**: `✅ Real filesystem verification passed!`

---

#### Command C: Dedicated Unit Test Suite
Deploy and run the full 9-method unit test suite:
```bash
cp /Users/ben/Desktop/InEarSnitch/.agents/explorer_m1_3/proposed_test_prokit_gate.py /Users/ben/Desktop/InEarSnitch/tests/test_prokit_gate.py
cd /Users/ben/Desktop/InEarSnitch && python3 -m unittest tests/test_prokit_gate.py
```
**Expected Output**:
```
Ran 9 tests in 0.018s
OK
```

---

#### Command D: Anti-Regression Smoke Test
```bash
cd /Users/ben/Desktop/InEarSnitch && python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py
```
**Expected Output**:
```
✅ ALL 19 CHECKS PASSED
```

---

### 2. Acceptance Verification Criteria

| Criterion ID | Description | Validation Rule |
|--------------|-------------|-----------------|
| **AC-M1-1** | Hash Set Completeness | `len(config.VALID_CODE_HASHES) == 50` and all entries are 64-char lowercase SHA256 hex strings matching `ORIGINAL_REQUEST.md`. |
| **AC-M1-2** | Initial Locked State | `is_prokit_unlocked() == False` when `.prokit_unlocked` file is absent in `get_data_dir()`. |
| **AC-M1-3** | Invalid Code Rejection | `unlock_prokit(bad_code) == False` for wrong codes, empty strings, None, or malformed input. No file created. |
| **AC-M1-4** | Valid Code Unlock | `unlock_prokit("SNITCH-PROKIT-2024-001") == True`, creates `.prokit_unlocked` containing the SHA256 hash. |
| **AC-M1-5** | Unlock State Detection | `is_prokit_unlocked() == True` immediately after valid unlock. |
| **AC-M1-6** | Revocation & Cleanup | `revoke_prokit() == True`, deletes `.prokit_unlocked`, leaves `is_prokit_unlocked() == False`. |
| **AC-M1-7** | Revoke Idempotency | Calling `revoke_prokit()` when already locked returns `True` without exception. |
| **AC-M1-8** | Input Tolerances | `unlock_prokit()` tolerates leading/trailing whitespace and lowercase letters. |
| **AC-M1-9** | Existing API Preservation | `get_data_dir()` and `get_db_path()` remain unchanged and functional. |
| **AC-M1-10** | Anti-Regression | `python3 /Users/ben/Desktop/InEarSnitch/smoke_test.py` passes 19/19 checks. |

---

### 3. Invalidation Conditions
- Any hash in `VALID_CODE_HASHES` does not match the SHA256 of `SNITCH-PROKIT-2024-001` through `-050`.
- Calling `unlock_prokit("WRONG-CODE")` creates or alters `.prokit_unlocked`.
- `smoke_test.py` fails on any syntax, import, or widget check.
