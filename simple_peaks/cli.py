import argparse
import sys
from . import split_audio, find_loud

import math
import glob
import soundfile as sf

def main():
    import sys
    import os
    import json
    from . import split_audio, find_loud
    from .audio_utils import extract_audio_to_wav

    # List of valid subcommands
    valid_commands = {"split", "find", "analyze", "-h", "--help"}
    argv = sys.argv[1:]
    # If first arg is not a known subcommand or help, treat it as a file and run default workflow
    if argv and (argv[0] not in valid_commands and not argv[0].startswith("-")):
        input_path = argv[0]
        import math
        import glob
        import soundfile as sf
        base = os.path.splitext(os.path.basename(input_path))[0]
        out_dir = os.path.join(os.path.dirname(input_path), f"{base}.simple-peaks")
        os.makedirs(out_dir, exist_ok=True)
        # Default values
        sr = None
        channels = 1
        window = 2.0
        hop = 0.5
        # Parse any additional options
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("input")
        parser.add_argument("--sr", type=int, default=None)
        parser.add_argument("--channels", type=int, default=1)
        parser.add_argument("--window", type=float, default=2.0)
        parser.add_argument("--hop", type=float, default=0.5)
        opts = parser.parse_args(argv)
        sr = opts.sr
        channels = opts.channels
        window = opts.window
        hop = opts.hop
        # 2. Split to ≤900s wavs
        split_audio.check_ffmpeg()
        split_audio.split_audio(
            input_path, 900, out_dir, base, sr, channels
        )
        # 3. For each wav, determine duration and calculate top_n
        wavs = sorted(glob.glob(os.path.join(out_dir, f"{base}_*.wav")))
        if not wavs:
            # If only one segment, fallback to single wav extraction
            wav_path = os.path.join(out_dir, f"{base}.wav")
            extract_audio_to_wav(input_path, wav_path, sr=sr, channels=channels)
            wavs = [wav_path]
        # Compute offsets for each wav segment
        segment_offsets = []
        offset = 0.0
        wav_durations = []
        # Get durations for all wavs
        for wav in wavs:
            with sf.SoundFile(wav) as f:
                dur = f.frames / f.samplerate
            wav_durations.append(dur)
        for dur in wav_durations:
            segment_offsets.append(offset)
            offset += dur
        # Build a flat array of peaks with absolute positions
        all_peaks = []
        import soundfile as sf
        for i, wav in enumerate(wavs):
            # Detect sample rate if not set
            _sr = sr
            if _sr is None:
                with sf.SoundFile(wav) as f:
                    _sr = f.samplerate
            segs = find_loud.find_loud_segments(wav, _sr, window, hop, max(1, math.ceil(wav_durations[i] / 60)))
            for seg in segs:
                abs_start_sec = segment_offsets[i] + seg["start_sec"]
                all_peaks.append({
                    "wav_file": wav,
                    "start_sec": seg["start_sec"],
                    "duration_sec": seg["duration_sec"],
                    "abs_start_sec": abs_start_sec,
                    "source_file": input_path,
                    "rms_db": seg["rms_db"]
                })
        # Write as a single JSON array
        json_path = os.path.join(out_dir, f"{base}_peaks.json")
        with open(json_path, "w") as f:
            json.dump(all_peaks, f, indent=2)
        print(f"WAV segments written to: {out_dir}")
        print(f"Peak info written to: {json_path}")
        # Extract video clips for each peak
        from .extract_clips import extract_clips_from_peaks
        extract_clips_from_peaks(json_path, output_dir=out_dir)
        return

    # Otherwise, proceed with argparse as usual
    parser = argparse.ArgumentParser(description="Simple Peaks CLI Tool")
    parser.add_argument("--sr", type=int, default=None, help="Sample rate for WAV (default: native)")
    parser.add_argument("--channels", type=int, default=1, help="Number of audio channels (default: 1)")
    parser.add_argument("--window", type=float, default=2.0, help="Window size in seconds for peak analysis")
    parser.add_argument("--hop", type=float, default=0.5, help="Hop size in seconds for peak analysis")
    subparsers = parser.add_subparsers(dest="command")

    # Split subcommand
    split_parser = subparsers.add_parser('split', help='Split audio/video into segments')
    split_parser.add_argument("input", help="Path to input file (audio or video)")
    split_parser.add_argument("--segment-length", "-t", type=int, default=900, help="Segment length in seconds (default: 900)")
    split_parser.add_argument("--output-dir", "-o", default=".", help="Directory to write segments (default: current dir)")
    split_parser.add_argument("--prefix", "-p", default="segment", help="Prefix for output files (default: 'segment')")
    split_parser.add_argument("--sr", type=int, default=None, help="Resample audio to this sample rate (Hz)")
    split_parser.add_argument("--channels", type=int, default=2, help="Number of channels to extract (1 for mono, 2 for stereo)")

    # Find subcommand
    find_parser = subparsers.add_parser('find', help='Find loudest segments in an audio file')
    find_parser.add_argument("input", help="path to audio file (WAV/FLAC)")
    find_parser.add_argument("--sr", type=int, default=None, help="sample rate to resample to (None for native)")
    find_parser.add_argument("--window", type=float, default=2.0, help="window size in seconds")
    find_parser.add_argument("--hop", type=float, default=0.5, help="hop size in seconds")
    find_parser.add_argument("--top", type=int, default=10, help="number of top segments to return")

    # Analyze subcommand
    analyze_parser = subparsers.add_parser('analyze', help='Extract audio and find loudest peaks, saving results to a new folder')
    analyze_parser.add_argument("input", help="Path to input file (audio or video)")
    analyze_parser.add_argument("--sr", type=int, default=None, help="Sample rate for WAV (default: native)")
    analyze_parser.add_argument("--channels", type=int, default=1, help="Number of audio channels (default: 1)")
    analyze_parser.add_argument("--window", type=float, default=2.0, help="Window size in seconds for peak analysis")
    analyze_parser.add_argument("--hop", type=float, default=0.5, help="Hop size in seconds for peak analysis")
    analyze_parser.add_argument("--top", type=int, default=10, help="Number of top segments to return")

    args = parser.parse_args()

    # If input is provided and no subcommand, run main workflow
    if args.input and not args.command:
        import os
        import json
        from . import split_audio, find_loud
        from .audio_utils import extract_audio_to_wav
        # 1. Create output folder
        input_path = args.input
        base = os.path.splitext(os.path.basename(input_path))[0]
        out_dir = os.path.join(os.path.dirname(input_path), f"{base}.simple-peaks")
        os.makedirs(out_dir, exist_ok=True)
        # 2. Split to ≤900s wavs
        split_audio.check_ffmpeg()
        split_audio.split_audio(
            input_path, 900, out_dir, base, args.sr, args.channels
        )
        # 3. For each wav, determine duration and calculate top_n
        wavs = sorted(glob.glob(os.path.join(out_dir, f"{base}_*.wav")))
        if not wavs:
            # If only one segment, fallback to single wav extraction
            wav_path = os.path.join(out_dir, f"{base}.wav")
            extract_audio_to_wav(input_path, wav_path, sr=args.sr, channels=args.channels)
            wavs = [wav_path]
        all_peaks = {}
        for wav in wavs:
            with sf.SoundFile(wav) as f:
                duration = f.frames / f.samplerate
            top_n = max(1, math.ceil(duration / 60))
            segs = find_loud.find_loud_segments(wav, args.sr, args.window, args.hop, top_n)
            all_peaks[os.path.basename(wav)] = segs
        # 4. Write combined JSON
        json_path = os.path.join(out_dir, f"{base}_peaks.json")
        with open(json_path, "w") as f:
            json.dump(all_peaks, f, indent=2)
        print(f"WAV segments written to: {out_dir}")
        print(f"Peak info written to: {json_path}")
        return

    if args.command == 'split':
        split_audio.check_ffmpeg()
        split_audio.split_audio(
            args.input, args.segment_length, args.output_dir, args.prefix, args.sr, args.channels
        )
    elif args.command == 'find':
        segs = find_loud.find_loud_segments(
            args.input, args.sr, args.window, args.hop, args.top
        )
        import json
        print(json.dumps(segs, indent=2))
    elif args.command == 'analyze':
        import os
        import json
        from .audio_utils import extract_audio_to_wav
        # Make output folder
        input_path = args.input
        base = os.path.splitext(os.path.basename(input_path))[0]
        out_dir = os.path.join(os.path.dirname(input_path), f"{base}.simple-peaks")
        os.makedirs(out_dir, exist_ok=True)
        # Output WAV path
        wav_path = os.path.join(out_dir, f"{base}.wav")
        extract_audio_to_wav(input_path, wav_path, sr=args.sr, channels=args.channels)
        # Analyze peaks
        segs = find_loud.find_loud_segments(wav_path, args.sr, args.window, args.hop, args.top)
        # Write JSON
        json_path = os.path.join(out_dir, f"{base}_peaks.json")
        with open(json_path, "w") as f:
            json.dump(segs, f, indent=2)
        print(f"WAV written to: {wav_path}")
        print(f"Peak info written to: {json_path}")
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
