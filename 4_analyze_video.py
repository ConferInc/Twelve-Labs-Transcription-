import json
import time
import re
from twelvelabs import TwelveLabs
from config import Config
import os

def load_transcript():
    if not os.path.exists(Config.TRANSCRIPT_PATH):
        return ""
    lines = []
    with open(Config.TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" not in line and "WEBVTT" not in line and line.strip():
                lines.append(line.strip())
    return " ".join(lines)

def get_transcript_chunk(full_text, index):
    words = full_text.split()
    chunk_size = 2250 # ~15 min
    start = index * chunk_size
    return " ".join(words[start : start + chunk_size + 200])

def analyze():
    client = TwelveLabs(api_key=Config.API_KEY)
    
    if not os.path.exists(Config.INDEX_DB):
        print("❌ Index DB missing. Run script #3 first.")
        return
    with open(Config.INDEX_DB, "r") as f:
        videos = json.load(f)

    full_transcript_text = load_transcript()
    results = []

    print(f"🤖 Starting Analysis on {len(videos)} videos...")

    for i, video in enumerate(videos):
        print(f"\n[{i+1}/{len(videos)}] Analyzing {video['filename']}...")
        
        # 1. Prepare Context
        zoom_context = get_transcript_chunk(full_transcript_text, i)
        start_min = i * Config.CHUNK_DURATION_MINS
        end_min = (i + 1) * Config.CHUNK_DURATION_MINS
        
        # 2. The Nuclear Prompt
        prompt = f"""
        ROLE: Senior Technical Analyst.
        
        CONTEXT (Speaker Identification Source):
        '''{zoom_context[:3500]}...'''

        TASK: Analyze video segment ({start_min}m-{end_min}m).
        
        REQUIREMENTS:
        1. Use SPEAKER NAMES from context (e.g. Yasin) instead of "Speaker".
        2. CAPTURE EVERY BUTTON CLICK with exact label (e.g. Click **[Save]**).
        3. FORMAT: Markdown Tables for forms; Lists for actions.
        """
        
        # 3. Call API
        try:
            stream = client.analyze_stream(video_id=video['video_id'], prompt=prompt)
            print("   Generating", end="", flush=True)
            text_out = ""
            for event in stream:
                if event.event_type == "text_generation":
                    text_out += event.text
                    print(".", end="", flush=True)
            print(" Done.")
            
            results.append({
                "filename": video['filename'],
                "raw_text": text_out,
                "chunk_index": i
            })
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

        # 4. Rate Limit Sleep
        if i < len(videos) - 1:
            print(f"   ⏳ Cooling down {Config.SLEEP_BETWEEN_ANALYSIS}s...")
            time.sleep(Config.SLEEP_BETWEEN_ANALYSIS)

    # Save Results
    with open(Config.RAW_SOP_DB, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Analysis Complete. Saved to {Config.RAW_SOP_DB}")

if __name__ == "__main__":
    analyze()