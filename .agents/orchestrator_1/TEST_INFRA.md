# E2E Test Infra: InEar Snitch ProKit Tip-Tracking

## Test Philosophy
- Opaque-box, requirement-driven. Derived from `ORIGINAL_REQUEST.md` and user specifications, independent of internal implementation code.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinations + Real-World Workload Scenarios.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| 1 | R1 config.py Offline Unlock System | ORIGINAL_REQUEST §R1 | ≥5 | ≥5 | ✓ | ✓ |
| 2 | R2 database.py TipProfiles & Migration | ORIGINAL_REQUEST §R2 | ≥5 | ≥5 | ✓ | ✓ |
| 3 | R2 database.py Reproducibility & Seal Queries | ORIGINAL_REQUEST §R2 | ≥5 | ≥5 | ✓ | ✓ |
| 4 | R3 main.py Bottom-Bar Tip Selector | ORIGINAL_REQUEST §R3 | ≥5 | ≥5 | ✓ | ✓ |
| 5 | R3 main.py Triple-Click Logo Unlock | ORIGINAL_REQUEST §R3 | ≥5 | ≥5 | ✓ | ✓ |
| 6 | R4 history_ui.py Badges & Seal Status | ORIGINAL_REQUEST §R4 | ≥5 | ≥5 | ✓ | ✓ |
| 7 | R5 analysis_ui.py Diagnostics Tip Card & Resonance | ORIGINAL_REQUEST §R5 | ≥5 | ≥5 | ✓ | ✓ |

## Test Architecture
- Test runner: `pytest -v tests/test_prokit_e2e.py`
- Test case format: Pytest test suites utilizing isolated temporary environments (`tmp_path`) and synthetic measurement data
- Directory layout: `/Users/ben/Desktop/InEarSnitch/tests/`

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full measurement workflow with custom tip selection and persistence | F1, F2, F4, F6 | Medium |
| 2 | Legacy database migration and backward compatibility verification | F2, F3, F6 | High |
| 3 | Statistical reproducibility calculation across repeated session measurements | F1, F3, F7 | High |
| 4 | Acoustic seal degradation and leak identification across multiple tips | F1, F3, F6, F7 | High |
| 5 | ProKit activation and feature unlocking roundtrip | F1, F4, F5, F6, F7 | Medium |

## Coverage Thresholds
- Tier 1: ≥5 per feature
- Tier 2: ≥5 per feature (boundary and error conditions)
- Tier 3: Pairwise coverage of major feature interactions
- Tier 4: ≥5 realistic application scenarios
