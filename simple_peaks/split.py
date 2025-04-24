"""
Video splitting utility for simple-peaks CLI.

Splits a 4K video (3840x2160) containing 4 1080p videos in its corners and 16 audio channels.
Exports each corner as a separate 1080p video with a selected mono audio channel mapped to both output channels.
"""
import argparse
import os
import subprocess

# Configuration: map corners to audio channel indices (0-based)
CONFIG = {
    'top_left': 7,        # e.g., channel 1
    'top_right': 3,       # e.g., channel 2
    'bottom_left': 5,     # e.g., channel 3
    'bottom_right': 9    # e.g., channel 4
}

# 4K video geometry
CORNERS = {
    'top_left':     {'x': 0,    'y': 0},
    'top_right':    {'x': 1920, 'y': 0},
    'bottom_left':  {'x': 0,    'y': 1080},
    'bottom_right': {'x': 1920, 'y': 1080}
}
WIDTH = 1920
HEIGHT = 1080

def split_video(input_path, output_dir):
    """
    Splits a 4K video into four 1080p videos (corners), each with a mapped mono audio channel (duplicated to stereo).
    If output_dir is not specified or is '.', creates an output directory named after the input file (without extension) in the same parent folder as the input.
    """
    if not output_dir or output_dir == ".":
        base = os.path.splitext(os.path.basename(input_path))[0]
        parent = os.path.dirname(input_path)
        output_dir = os.path.join(parent, f"{base}.split")
    os.makedirs(output_dir, exist_ok=True)
    for corner, audio_channel in CONFIG.items():
        crop = CORNERS[corner]
        output_path = os.path.join(output_dir, f"{corner}.mp4")
        # ffmpeg command to crop and map audio
        ffmpeg_cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-i", input_path,
            "-filter_complex",
            f"[0:v]crop={WIDTH}:{HEIGHT}:{crop['x']}:{crop['y']}[vout];[0:a]pan=stereo|c0=c{audio_channel}|c1=c{audio_channel}[aout]",
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path
        ]
        print(f"Exporting {corner} to {output_path} (audio channel {audio_channel})...")
        subprocess.run(ffmpeg_cmd, check=True)
    print(f"All corners exported to {output_dir}.")
