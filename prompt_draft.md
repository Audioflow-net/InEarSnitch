# Teamwork Project Prompt — Draft

> Status: Launched — Skipping interactive phase (triggered via /goal)
> Goal: Deep Physics, Math, and Logic Audit of InEar Snitch
> Requested team: Armada of 3 DeepInvestigator agents

## Requirements

### R1. Acoustic & Physics Audit
Review coupler resonance assumptions, THD calculations, microphone calibration application, and RTA thresholds.

### R2. DSP & Mathematics Audit
Review FFT normalization, impulse response (Farina) extraction, windowing, and EQ filter math.

### R3. Logic & State Audit
Review thread safety, EMA state tracking, channel routing, and race conditions in workers.

## Acceptance Criteria

### Audit Quality
- [ ] List all potential errors found across the codebase.
- [ ] For each error, provide the file/line and explain *why* it is an error mathematically or physically.
- [ ] **Crucial:** For each error, hypothesize *why* the original author might have written it that way (historical context or potential edge-case justifications).
- [ ] **Strict:** Do NOT modify any files. Report findings only.
