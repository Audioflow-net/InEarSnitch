#!/usr/bin/env python3
"""
Analyze debug dumps from audio_engine.measure() to diagnose the flat-line bug.
Usage: cd /Users/ben/Desktop/InEarSnitch && python3 analyze_dump.py
"""
import numpy as np
import os, glob, sys

dump_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug_dumps')
files = sorted(glob.glob(os.path.join(dump_dir, '*.npz')))

if not files:
    print("No debug dumps found! Run a measurement first.")
    sys.exit(1)

path = files[-1]
print(f"=== Analyzing: {os.path.basename(path)} ===\n")

d = np.load(path, allow_pickle=True)

rec = d['rec_signal']
ir_raw = d['ir_raw']
ir_windowed = d['ir_windowed']
ir_shifted = d['ir_shifted']
freqs = d['freqs']
mag = d['mag_raw']
peak_idx = int(d['peak_idx'])
onset_idx = int(d['onset_idx'])
w_start = int(d['w_start'])
w_end = int(d['w_end'])
latency_ms = float(d['latency_ms'])
crest = float(d['crest_factor'])
peak_dbfs = float(d['peak_dbfs'])
spl_off = float(d['spl_offset_db'])
sr = int(d['sample_rate'])

print(f"Sample Rate: {sr} Hz")
print(f"Recording length: {len(rec)} samples = {len(rec)/sr:.3f}s")
print(f"Peak dBFS: {peak_dbfs:.1f}")
print(f"Latency: {latency_ms:.1f} ms")
print(f"Crest Factor: {crest:.1f} dB")
print(f"SPL Offset: {spl_off:.1f} dB")

print(f"\n--- IR Analysis ---")
print(f"IR length: {len(ir_raw)} samples")
print(f"Peak idx: {peak_idx}")
print(f"Onset idx: {onset_idx}")
print(f"Peak-to-onset: {(peak_idx - onset_idx)/sr*1000:.2f} ms")
print(f"Window: [{w_start}:{w_end}] = {w_end - w_start} samples = {(w_end - w_start)/sr*1000:.1f} ms")

rec_clip_pct = np.sum(np.abs(rec) > 0.99) / len(rec) * 100
print(f"\n--- Recording Clipping ---")
print(f"Samples > 0.99: {rec_clip_pct:.1f}%")
print(f"Max amplitude: {np.max(np.abs(rec)):.6f}")

windowed_energy = np.sum(ir_windowed**2)
raw_energy = np.sum(ir_raw**2)
print(f"\n--- Windowed IR ---")
print(f"Raw IR energy: {raw_energy:.2e}")
print(f"Windowed IR energy: {windowed_energy:.2e}")
print(f"Energy ratio: {windowed_energy/raw_energy*100:.1f}%")
print(f"Non-zero samples in windowed IR: {np.sum(np.abs(ir_windowed) > 1e-15)}")

valid = (freqs > 100) & (freqs < 10000)
mag_range = np.max(mag[valid]) - np.min(mag[valid])
print(f"\n--- Magnitude ---")
print(f"Range 100-10kHz: {mag_range:.1f} dB")
print(f"Value at 1kHz: {mag[(np.abs(freqs - 1000)).argmin()]:.1f} dB")
print(f"Value at 100Hz: {mag[(np.abs(freqs - 100)).argmin()]:.1f} dB")
print(f"Value at 5kHz: {mag[(np.abs(freqs - 5000)).argmin()]:.1f} dB")
print(f"Value at 10kHz: {mag[(np.abs(freqs - 10000)).argmin()]:.1f} dB")

if mag_range < 5.0:
    print(f"\n🚨 FLAT LINE DETECTED! Range is only {mag_range:.1f} dB!")
    print("Investigating cause...")
    
    shifted_peak = np.max(np.abs(ir_shifted))
    shifted_rms = np.sqrt(np.mean(ir_shifted**2))
    shifted_crest = 20 * np.log10(shifted_peak / (shifted_rms + 1e-12))
    print(f"  Shifted IR crest factor: {shifted_crest:.1f} dB (>60 = Dirac delta = flat)")
    
    windowed_slice = ir_raw[w_start:w_end]
    print(f"  Window slice max: {np.max(np.abs(windowed_slice)):.6f}")
    print(f"  Window slice RMS: {np.sqrt(np.mean(windowed_slice**2)):.6f}")
    
    big_peaks = np.where(np.abs(ir_raw) > 0.1 * np.max(np.abs(ir_raw)))[0]
    print(f"  Significant peaks (>10% of max) at samples: {big_peaks[:10]}")
    for p in big_peaks[:5]:
        print(f"    sample {p}: amp={np.abs(ir_raw[p]):.2f}, dist from peak={p-peak_idx} = {(p-peak_idx)/sr*1000:.1f}ms")
else:
    print(f"\n✅ Magnitude looks healthy ({mag_range:.1f} dB range)")

print(f"\n--- Diagnosis Summary ---")
if rec_clip_pct > 5:
    print(f"⚠️  Recording is clipping ({rec_clip_pct:.0f}%). May degrade measurement.")
if abs(spl_off) < 0.01:
    print(f"ℹ️  SPL offset is 0.0 - raw values will be low (expect ~-20 to +40 dB)")
if (w_end - w_start) < int(0.05 * sr):
    print(f"⚠️  Window very short ({(w_end-w_start)/sr*1000:.1f}ms). Bass resolution may suffer.")
if windowed_energy / (raw_energy + 1e-30) < 0.01:
    print(f"🚨 Windowed IR captures <1% of energy! Window may be misplaced!")
