import subprocess
import os
import math
import json
from config import Config

# Try to find the ffmpeg binary that came with moviepy/imageio
try:
    import imageio_ffmpeg
    FFMPEG_BINARY = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_BINARY = "ffmpeg" # Fallback to system path

def get_video_duration(file_path):
    """Get exact duration using ffprobe (comes with ffmpeg)."""
    cmd = [
        FFMPEG_BINARY, "-i", file_path, "-hide_banner"
    ]
    # FFmpeg prints duration to stderr
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    
    # Parse "Duration: 00:00:00.00" from stderr
    import re
    match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)", result.stderr)
    if match:
        hours, mins, secs = map(float, match.groups())
        return hours * 3600 + mins * 60 + secs
    return 0

def split_video():
    print(f"🎬 Loading video: {Config.RAW_VIDEO_PATH}")
    print(f"🔧 Using FFmpeg binary: {FFMPEG_BINARY}")
    
    if not os.path.exists(Config.RAW_VIDEO_PATH):
        print("❌ Error: Raw video not found.")
        return

    # 1. Get Duration
    duration = get_video_duration(Config.RAW_VIDEO_PATH)
    if duration == 0:
        print("❌ Error: Could not determine video duration.")
        return

    chunk_len = Config.CHUNK_DURATION_MINS * 60
    total_chunks = math.ceil(duration / chunk_len)
    
    print(f"🔪 Splitting {duration/60:.2f} min video into {total_chunks} chunks (Direct Stream Copy)...")

    # 2. Split Loop
    for i in range(total_chunks):
        start_time = i * chunk_len
        filename = f"part_{i:03d}.mp4"
        output_path = os.path.join(Config.CHUNKS_DIR, filename)
        
        # FFmpeg Command:
        # -ss [start] : Seek to start time
        # -t [duration] : Grab exactly this much time
        # -c copy : STREAM COPY (No re-encoding, instant speed)
        # -y : Overwrite if exists
        cmd = [
            FFMPEG_BINARY, 
            "-ss", str(start_time),
            "-i", Config.RAW_VIDEO_PATH,
            "-t", str(chunk_len),
            "-c", "copy",
            "-y",
            output_path
        ]
        
        print(f"   Writing {filename}...", end="", flush=True)
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(" Done.")

    print("\n✅ Splitting Complete!")

if __name__ == "__main__":
    split_video()