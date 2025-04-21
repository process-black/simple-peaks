import os
import subprocess
import json
import shutil

# --- CONFIGURATION ---
# Set these to True/False to control which outputs are generated for each clip
OUTPUT_540P_MP4 = True      # Save a 540p version of each clip (mp4)
OUTPUT_540P_GIF = True      # Save a 540px-wide GIF of each clip
OUTPUT_270P_GIF = True      # Save a 270px-wide GIF of each clip
OUTPUT_SCROLLING_MP4 = True  # Save a "scrolling" all-I-frames MP4 (1-frame GOP)
# ---------------------

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

    # Define subfolders for each output type
    original_dir = os.path.join(output_dir, "original")
    mp4_540_dir = os.path.join(output_dir, "540")
    gif_540_dir = os.path.join(output_dir, "540_gif")
    gif_270_dir = os.path.join(output_dir, "270_gif")
    scrolling_dir = os.path.join(output_dir, "scrolling")
    # Ensure all subfolders exist
    for d in [original_dir, mp4_540_dir, gif_540_dir, gif_270_dir, scrolling_dir]:
        os.makedirs(d, exist_ok=True)

    for peak in peaks:
        source_file = peak["source_file"]
        abs_start_sec = peak["abs_start_sec"]
        duration_sec = peak["duration_sec"]
        base = os.path.splitext(os.path.basename(source_file))[0]
        out_name = f"{base}_{abs_start_sec:.3f}.mp4"
        out_path = os.path.join(original_dir, out_name)
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

        # Optionally create a 540p mp4 version
        if OUTPUT_540P_MP4:
            out_540p_name = os.path.splitext(out_name)[0] + "_540p.mp4"
            out_540p_path = os.path.join(mp4_540_dir, out_540p_name)
            cmd_540p = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", out_path,
                "-vf", "scale=-2:540",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-ac", "2",
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-y",
                out_540p_path
            ]
            print(f"Creating 540p mp4: {out_540p_path}")
            subprocess.run(cmd_540p, check=True)

        # Optionally create a scrolling (all-I-frames) MP4
        if OUTPUT_SCROLLING_MP4:
            out_scroll_name = os.path.splitext(out_name)[0] + "_scrolling.mp4"
            out_scroll_path = os.path.join(scrolling_dir, out_scroll_name)
            cmd_scroll = [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-i", out_path,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "18",
                "-g", "1",
                "-keyint_min", "1",
                "-sc_threshold", "0",
                "-pix_fmt", "yuv420p",
                "-an",
                "-movflags", "+faststart",
                "-y",
                out_scroll_path
            ]
            print(f"Creating scrolling all-I-frames mp4: {out_scroll_path}")
            subprocess.run(cmd_scroll, check=True)

        # Optionally create 540px and 270px GIFs
        for width, enabled in [(540, OUTPUT_540P_GIF), (270, OUTPUT_270P_GIF)]:
            if enabled:
                gif_dir = gif_540_dir if width == 540 else gif_270_dir
                out_gif_name = os.path.splitext(out_name)[0] + f"_{width}.gif"
                out_gif_path = os.path.join(gif_dir, out_gif_name)
                # Use palette for better GIF quality
                palette_name = os.path.splitext(out_name)[0] + f"_palette_{width}.png"
                palette_path = os.path.join(gif_dir, palette_name)
                # 1. Generate palette
                cmd_palette = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error",
                    "-i", out_path,
                    "-vf", f"fps=15,scale=-2:{width}:flags=lanczos,palettegen",
                    "-y",
                    palette_path
                ]
                subprocess.run(cmd_palette, check=True)
                # 2. Create GIF using palette
                cmd_gif = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error",
                    "-i", out_path,
                    "-i", palette_path,
                    "-filter_complex", f"fps=15,scale=-2:{width}:flags=lanczos[x];[x][1:v]paletteuse",
                    "-y",
                    out_gif_path
                ]
                print(f"Creating {width}px GIF: {out_gif_path}")
                subprocess.run(cmd_gif, check=True)
                # Remove palette file
                os.remove(palette_path)

    print(f"All clips extracted to: {output_dir}")
