import os
import subprocess
import json
import shutil

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is not installed or not on PATH.")

def extract_clips_from_peaks(peaks_json_path, output_dir=None):
    check_ffmpeg()
    with open(peaks_json_path, "r") as f:
        peaks = json.load(f)
    if not peaks:
        print("No peaks found in JSON.")
        return
    # Use the output dir of the peaks file if not specified
    if output_dir is None:
        output_dir = os.path.dirname(peaks_json_path)
    for peak in peaks:
        source_file = peak["source_file"]
        abs_start_sec = peak["abs_start_sec"]
        duration_sec = peak["duration_sec"]
        base = os.path.splitext(os.path.basename(source_file))[0]
        out_name = f"{base}_{abs_start_sec:.3f}.mp4"
        out_path = os.path.join(output_dir, out_name)
        # ffmpeg command for Mac QuickTime compatibility
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(abs_start_sec),
            "-i", source_file,
            "-t", str(duration_sec),
            "-map", "0:v:0", "-map", "0:a:0",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-y",  # Overwrite
            out_path
        ]
        print(f"Extracting: {out_path}")
        subprocess.run(cmd, check=True)
    print(f"All clips extracted to: {output_dir}")
