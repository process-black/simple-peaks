import os
import shutil
import subprocess
import sys

def extract_audio_to_wav(input_path, output_wav_path, sr=None, channels=1):
    """
    Extract audio from input file to WAV using ffmpeg.
    """
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not on PATH.", file=sys.stderr)
        sys.exit(1)
    # Always extract stereo (channels 1 and 2)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", input_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ac", "2",
        "-y",  # Overwrite output
    ]
    if sr:
        cmd += ["-ar", str(sr)]
    cmd += [output_wav_path]
    subprocess.run(cmd, check=True)
    return output_wav_path
