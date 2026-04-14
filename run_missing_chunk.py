"""
Run ONLY the missing chunk (April 13 meeting, chunk 2: 30m-45m)
================================================================

This script handles everything for a single missing chunk:
1. Splits the April 13 video (if not already split)
2. Uploads ONLY chunk part_002.mp4 (if not already uploaded)
3. Creates/uses an index and indexes the chunk
4. Analyzes ONLY that chunk with the StoneFactory ERP prompt
5. Merges the result into the existing raw_sop_output.json
6. Regenerates the final report

PREREQUISITES:
  - pip install twelvelabs moviepy imageio_ffmpeg
  - Place API key in config.py
  - Place "MicrosoftTeams-video 13-Apr-26.mp4" in raw_video/Link1.mp4

USAGE:
  python run_missing_chunk.py
"""

import json
import os
import sys
import time
import math
import subprocess
import re

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from prompts.stonefactory_erp import get_analysis_prompt

MISSING_CHUNK_INDEX = 2
MISSING_FILENAME = "part_002.mp4"


def step1_ensure_chunk_exists():
    """Split video if the chunk doesn't exist yet."""
    chunk_path = os.path.join(Config.CHUNKS_DIR, MISSING_FILENAME)
    if os.path.exists(chunk_path):
        size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"[1/5] Chunk already exists: {MISSING_FILENAME} ({size_mb:.1f} MB)")
        return True

    print(f"[1/5] Splitting video to extract {MISSING_FILENAME}...")
    if not os.path.exists(Config.RAW_VIDEO_PATH):
        print(f"  ERROR: Video not found at {Config.RAW_VIDEO_PATH}")
        print(f"  Copy the April 13 meeting video to: raw_video/Link1.mp4")
        return False

    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg = "ffmpeg"

    chunk_len = Config.CHUNK_DURATION_MINS * 60
    start_time = MISSING_CHUNK_INDEX * chunk_len

    cmd = [ffmpeg, "-ss", str(start_time), "-i", Config.RAW_VIDEO_PATH,
           "-t", str(chunk_len), "-c", "copy", "-y", chunk_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(chunk_path):
        size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
        print(f"  Extracted {MISSING_FILENAME} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERROR: Failed to extract chunk")
        return False


def step2_upload_chunk():
    """Upload only the missing chunk."""
    from twelvelabs import TwelveLabs
    client = TwelveLabs(api_key=Config.API_KEY)

    chunk_path = os.path.join(Config.CHUNKS_DIR, MISSING_FILENAME)
    print(f"[2/5] Uploading {MISSING_FILENAME}...")

    try:
        asset = client.assets.create(file=open(chunk_path, "rb"), method="direct")
        print(f"  Uploaded. Asset ID: {asset.id}")
        return asset.id
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def step3_index_chunk(asset_id):
    """Create/use index and index the chunk."""
    from twelvelabs import TwelveLabs
    client = TwelveLabs(api_key=Config.API_KEY)

    # Get or create index
    target_index = None
    idx_id = Config.INDEX_ID.strip() if Config.INDEX_ID else ""

    if idx_id:
        try:
            target_index = client.indexes.retrieve(idx_id)
            print(f"[3/5] Using existing index: {target_index.id}")
        except:
            print(f"  Configured INDEX_ID not found, creating new...")

    if not target_index:
        for idx in client.indexes.list():
            if getattr(idx, "index_name", "") == Config.INDEX_NAME:
                target_index = idx
                print(f"[3/5] Found index by name: {idx.id}")
                break

    if not target_index:
        print(f"[3/5] Creating new index '{Config.INDEX_NAME}'...")
        target_index = client.indexes.create(
            index_name=Config.INDEX_NAME,
            models=[
                {"model_name": "marengo3.0", "model_options": ["visual", "audio"]},
                {"model_name": "pegasus1.2", "model_options": ["visual", "audio"]}
            ]
        )
        print(f"  Created index: {target_index.id}")
        print(f"  UPDATE config.py: INDEX_ID = \"{target_index.id}\"")

    # Index the asset
    print(f"  Indexing {MISSING_FILENAME}...", end="", flush=True)
    try:
        ia = client.indexes.indexed_assets.create(
            index_id=target_index.id, asset_id=asset_id
        )
        while True:
            status = client.indexes.indexed_assets.retrieve(
                index_id=target_index.id, indexed_asset_id=ia.id
            ).status
            if status == "ready":
                print(" Ready!")
                return ia.id
            elif status == "failed":
                print(" FAILED!")
                return None
            time.sleep(2)
    except Exception as e:
        print(f"\n  ERROR: {e}")
        return None


def step4_analyze_chunk(video_id):
    """Analyze only the missing chunk."""
    from twelvelabs import TwelveLabs
    client = TwelveLabs(api_key=Config.API_KEY)

    print(f"[4/5] Analyzing {MISSING_FILENAME} (chunk {MISSING_CHUNK_INDEX}: {MISSING_CHUNK_INDEX*15}m-{(MISSING_CHUNK_INDEX+1)*15}m)...")

    prompt = get_analysis_prompt(MISSING_CHUNK_INDEX)
    print(f"  Prompt: {len(prompt)} chars")

    try:
        print("  Generating", end="", flush=True)
        stream = client.analyze_stream(video_id=video_id, prompt=prompt)
        text_out = ""
        dot_count = 0
        for event in stream:
            if event.event_type == "text_generation":
                text_out += event.text
                dot_count += 1
                if dot_count % 5 == 0:
                    print(".", end="", flush=True)
        print(f" Done! ({len(text_out)} chars)")
        return text_out
    except Exception as e:
        print(f"\n  ERROR: {e}")
        return None


def step5_merge_and_report(analysis_text):
    """Merge the new chunk into existing results and regenerate report."""
    print(f"[5/5] Merging into existing results...")

    # Load existing results
    results = []
    if os.path.exists(Config.RAW_SOP_DB):
        with open(Config.RAW_SOP_DB, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"  Loaded {len(results)} existing chunks")

    # Remove old chunk 2 if it exists (shouldn't, but safety)
    results = [r for r in results if r.get("chunk_index") != MISSING_CHUNK_INDEX]

    # Add new chunk
    results.append({
        "filename": MISSING_FILENAME,
        "raw_text": analysis_text,
        "chunk_index": MISSING_CHUNK_INDEX,
        "prompt_mode": "full",
        "transcript_context_words": 0
    })

    # Sort by chunk index
    results.sort(key=lambda x: x.get("chunk_index", 0))

    # Save
    with open(Config.RAW_SOP_DB, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(results)} chunks to {Config.RAW_SOP_DB}")

    # Regenerate report
    print("  Regenerating report...")
    from importlib import import_module
    fmt = import_module("5_format_report")
    fmt.generate_report()


def main():
    print("=" * 60)
    print("  MISSING CHUNK RECOVERY")
    print(f"  Target: April 13 meeting, chunk {MISSING_CHUNK_INDEX} ({MISSING_CHUNK_INDEX*15}m-{(MISSING_CHUNK_INDEX+1)*15}m)")
    print("=" * 60)
    print()

    # Step 1: Ensure chunk file exists
    if not step1_ensure_chunk_exists():
        sys.exit(1)

    # Step 2: Upload
    asset_id = step2_upload_chunk()
    if not asset_id:
        sys.exit(1)

    # Step 3: Index
    video_id = step3_index_chunk(asset_id)
    if not video_id:
        sys.exit(1)

    # Step 4: Analyze
    text = step4_analyze_chunk(video_id)
    if not text:
        sys.exit(1)

    # Step 5: Merge and report
    step5_merge_and_report(text)

    print()
    print("=" * 60)
    print("  DONE! Missing chunk recovered successfully.")
    print(f"  Report: {Config.FINAL_REPORT}")
    print("=" * 60)


if __name__ == "__main__":
    main()
