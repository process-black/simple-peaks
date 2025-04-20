#!/usr/bin/env python3
"""
Usage:
  python -m simple_peaks.find_loud input.flac \
    --window 2.0 --hop 0.5 --top 10
"""
import argparse, json
import numpy as np
import librosa

def find_loud_segments(path, sr, window, hop, top_n=None):
    """
    Find top peaks per 15-minute bin (default: 5 per bin, at least 1 per file).
    """
    y, _ = librosa.load(path, sr=sr, mono=True)
    n = len(y)
    win_length = int(window * sr)
    hop_length = int(hop * sr)
    duration = n / sr
    bin_size = 900  # 15 minutes
    peaks_per_bin = 5
    segments = []
    # Always at least 1 bin
    num_bins = max(1, int(np.ceil(duration / bin_size)))
    for b in range(num_bins):
        bin_start = b * bin_size
        bin_end = min((b + 1) * bin_size, duration)
        # Find candidate frames in this bin
        candidates = []
        min_rms = 0.005
        for i in range(0, n - win_length + 1, hop_length):
            start_sec = i / sr
            if start_sec < bin_start or start_sec >= bin_end:
                continue
            seg = y[i:i+win_length]
            rms_val = np.sqrt(np.mean(seg ** 2))
            if rms_val >= min_rms:
                candidates.append({
                    "rms": float(rms_val),
                    "start": start_sec,
                    "idx": i
                })
        # Sort by rms descending
        candidates.sort(key=lambda x: x["rms"], reverse=True)
        selected = []
        selected_intervals = []
        for cand in candidates:
            c_start = cand["start"]
            c_end = c_start + window
            overlap = False
            for (s, e) in selected_intervals:
                if not (c_end <= s or c_start >= e):
                    overlap = True
                    break
            if not overlap:
                selected.append(cand)
                selected_intervals.append((c_start, c_end))
            if len(selected) >= peaks_per_bin:
                break
        # Always select at least 1 (the loudest) if bin has any candidates
        if not selected and candidates:
            selected.append(candidates[0])
        segments.extend({
            "start_sec":    float(round(cand["start"], 3)),
            "duration_sec": float(round(window, 3)),
            "rms_db":       float(round(float(cand["rms"]), 3))
        } for cand in sorted(selected, key=lambda x: x["start"]))
    return segments

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="path to audio file (WAV/FLAC)")
    p.add_argument("--sr", type=int, default=None, help="sample rate to resample to (None for native)")
    p.add_argument("--window", type=float, default=2.0, help="window size in seconds")
    p.add_argument("--hop", type=float, default=0.5, help="hop size in seconds")
    p.add_argument("--top", type=int, default=10, help="number of top segments to return")
    args = p.parse_args()
    segs = find_loud_segments(args.input, args.sr, args.window, args.hop, args.top)
    print(json.dumps(segs, indent=2))

if __name__ == "__main__":
    main()
