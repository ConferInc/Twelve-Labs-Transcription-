"""
Step 4: Analyze Video Chunks with StoneFactory ERP Prompt
=========================================================
Sends each indexed video chunk to Twelve Labs for analysis using a
comprehensive prompt that captures BOTH audio (speech, discussions,
requirements) AND visual (SAP screens, Excel data, flow charts,
UI mockups, documents).

Usage:
    python 4_analyze_video.py              # Full comprehensive prompt
    python 4_analyze_video.py --fast       # Lightweight prompt (faster)
    python 4_analyze_video.py --lightweight # Same as --fast

Output: data/raw_sop_output.json
"""

import json
import time
import os
import sys
from twelvelabs import TwelveLabs
from config import Config
from prompts.stonefactory_erp import get_analysis_prompt, get_lightweight_prompt


def load_transcript():
    """Load and clean the VTT transcript file for context injection."""
    if not os.path.exists(Config.TRANSCRIPT_PATH):
        print("  [INFO] No transcript.vtt found. Proceeding without speaker context.")
        print("         (Speaker attribution will be less accurate)")
        return ""
    lines = []
    with open(Config.TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" not in line and "WEBVTT" not in line and line.strip():
                lines.append(line.strip())
    transcript = " ".join(lines)
    print(f"  [OK] Loaded transcript: {len(transcript)} chars, {len(transcript.split())} words")
    return transcript


def get_transcript_chunk(full_text, index):
    """
    Extract the portion of transcript corresponding to a video chunk.
    Each 15-min chunk maps to roughly 2,250 words of speech.
    Adds 200-word overlap for context continuity.
    """
    if not full_text:
        return ""
    words = full_text.split()
    chunk_size = 2250
    start = index * chunk_size
    overlap_start = max(0, start - 100)
    overlap_end = start + chunk_size + 200
    return " ".join(words[overlap_start:overlap_end])


def analyze():
    """Main analysis loop."""
    client = TwelveLabs(api_key=Config.API_KEY)

    # 1. Load index map
    if not os.path.exists(Config.INDEX_DB):
        print("[ERROR] Index DB missing. Run script #3 first.")
        return
    with open(Config.INDEX_DB, "r") as f:
        videos = json.load(f)

    if not videos:
        print("[ERROR] No videos in index map. Check script #3 output.")
        return

    # 2. Load transcript for context
    full_transcript_text = load_transcript()

    # 3. Load existing results (for resume capability)
    results = []
    if os.path.exists(Config.RAW_SOP_DB):
        try:
            with open(Config.RAW_SOP_DB, "r") as f:
                results = json.load(f)
            print(f"  [OK] Loaded {len(results)} existing analysis results.")
        except Exception as e:
            print(f"  [WARN] Could not load existing results: {e}")

    analyzed_filenames = {item['filename'] for item in results}

    # 4. Check prompt mode
    use_lightweight = "--lightweight" in sys.argv or "--fast" in sys.argv
    if use_lightweight:
        print("  [MODE] Using LIGHTWEIGHT prompt (faster, less detailed)")

    # 5. Run analysis
    print(f"\n{'='*60}")
    print(f"  STONEFACTORY ERP - VIDEO ANALYSIS")
    print(f"{'='*60}")
    print(f"  Videos to analyze: {len(videos)}")
    print(f"  Cooldown: {Config.SLEEP_BETWEEN_ANALYSIS}s between calls")
    print(f"  Prompt: {'Lightweight' if use_lightweight else 'Full (Comprehensive)'}")
    print(f"{'='*60}\n")

    new_count = 0
    skip_count = 0
    error_count = 0

    for i, video in enumerate(videos):
        if video['filename'] in analyzed_filenames:
            print(f"  [SKIP] [{i+1}/{len(videos)}] {video['filename']} (already done)")
            skip_count += 1
            continue

        print(f"\n  [{i+1}/{len(videos)}] Analyzing {video['filename']}...")
        print(f"    Chunk {i}: {i * Config.CHUNK_DURATION_MINS}m - {(i+1) * Config.CHUNK_DURATION_MINS}m")

        # Prepare transcript context
        zoom_context = get_transcript_chunk(full_transcript_text, i)
        if zoom_context:
            print(f"    Transcript context: {len(zoom_context.split())} words")

        # Select and build prompt
        if use_lightweight:
            prompt = get_lightweight_prompt(i, zoom_context)
        else:
            prompt = get_analysis_prompt(i, zoom_context)
        print(f"    Prompt size: {len(prompt)} chars")

        # Call Twelve Labs API
        try:
            print("    Generating", end="", flush=True)
            stream = client.analyze_stream(
                video_id=video['video_id'],
                prompt=prompt
            )

            text_out = ""
            dot_count = 0
            for event in stream:
                if event.event_type == "text_generation":
                    text_out += event.text
                    dot_count += 1
                    if dot_count % 5 == 0:
                        print(".", end="", flush=True)

            print(f" Done! ({len(text_out)} chars)")

            results.append({
                "filename": video['filename'],
                "raw_text": text_out,
                "chunk_index": i,
                "prompt_mode": "lightweight" if use_lightweight else "full",
                "transcript_context_words": len(zoom_context.split()) if zoom_context else 0
            })
            new_count += 1

            # Save incrementally (crash-safe)
            results.sort(key=lambda x: x.get('chunk_index', 0))
            with open(Config.RAW_SOP_DB, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"    Saved to {Config.RAW_SOP_DB}")

        except Exception as e:
            error_msg = str(e)
            print(f"\n    [ERROR] {error_msg}")
            error_count += 1
            if "429" in error_msg or "rate" in error_msg.lower():
                wait_time = Config.SLEEP_BETWEEN_ANALYSIS * 3
                print(f"    Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)

        # Cooldown (except last chunk)
        if i < len(videos) - 1:
            print(f"    Cooling down {Config.SLEEP_BETWEEN_ANALYSIS}s...")
            time.sleep(Config.SLEEP_BETWEEN_ANALYSIS)

    # Summary
    print(f"\n{'='*60}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"    New:     {new_count}")
    print(f"    Skipped: {skip_count}")
    print(f"    Errors:  {error_count}")
    print(f"    Total:   {len(results)}")
    print(f"    Output:  {Config.RAW_SOP_DB}")
    print(f"{'='*60}")


if __name__ == "__main__":
    analyze()
