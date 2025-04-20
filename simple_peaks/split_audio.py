#!/usr/bin/env python3
"""
Split an input file into WAV audio segments of fixed duration using ffmpeg.

Usage:
  python -m simple_peaks.split_audio input_file [--segment-length SECONDS] [--output-dir DIR]
                           [--prefix PREFIX] [--sr SAMPLE_RATE] [--channels CHANNELS]

Examples:
  python -m simple_peaks.split_audio video.mov
  python -m simple_peaks.split_audio podcast.mp3 --segment-length 600 --output-dir chunks --prefix part --sr 16000 --channels 2
"""
import argparse
import os
import shutil
import subprocess
import sys

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not on PATH.", file=sys.stderr)
        sys.exit(1)

def split_audio(input_path, segment_length, output_dir, prefix, sr, channels):
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, f"{prefix}_%03d.wav")
    # Always extract stereo (channels 1 and 2)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", input_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ac", "2",
        "-f", "segment",
        "-segment_time", str(segment_length),
        "-reset_timestamps", "1",
        output_pattern
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Segments written to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Split input into WAV segments by duration.")
    parser.add_argument("input", help="Path to input file (audio or video)")
    parser.add_argument("--segment-length", "-t", type=int, default=900, help="Segment length in seconds (default: 900)")
    parser.add_argument("--output-dir", "-o", default=".", help="Directory to write segments (default: current dir)")
    parser.add_argument("--prefix", "-p", default="segment", help="Prefix for output files (default: 'segment')")
    parser.add_argument("--sr", type=int, default=None, help="Resample audio to this sample rate (Hz)")
    parser.add_argument("--channels", type=int, default=1, help="Number of audio channels (1=mono, 2=stereo; default: 1)")
    args = parser.parse_args()
    check_ffmpeg()
    split_audio(args.input, args.segment_length, args.output_dir, args.prefix, args.sr, args.channels)

if __name__ == "__main__":
    main()
