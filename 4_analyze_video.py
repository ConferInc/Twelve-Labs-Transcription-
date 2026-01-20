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
    
    # Load existing results if available
    if os.path.exists(Config.RAW_SOP_DB):
        try:
            with open(Config.RAW_SOP_DB, "r") as f:
                results = json.load(f)
            print(f"📂 Loaded {len(results)} existing analysis results from DB.")
        except Exception as e:
            print(f"⚠️ Could not load existing results DB: {e}")

    # Create set of analyzed filenames
    analyzed_filenames = {item['filename'] for item in results}

    print(f"🤖 Starting Analysis on {len(videos)} videos...")

    new_analysis_count = 0
    for i, video in enumerate(videos):
       # if video['filename'] in analyzed_filenames:
            # print(f"   ⏭️  Skipping {video['filename']} (Already analyzed)")
            # Optional: less verbose if many files
        #    continue

        print(f"\n[{i+1}/{len(videos)}] Analyzing {video['filename']}...")
        
        # 1. Prepare Context
        zoom_context = get_transcript_chunk(full_transcript_text, i)
        start_min = i * Config.CHUNK_DURATION_MINS
        end_min = (i + 1) * Config.CHUNK_DURATION_MINS
        
        # 2. The Nuclear Prompt (Mortgage SOP Edition)
        prompt = f"""
        ROLE: Expert Mortgage Operations Analyst & Technical Writer.
        
        OBJECTIVE: Reverse-engineer a granule, Click-by-Click Standard Operating Procedure (SOP) from this video.
        SCENARIO: A "Dummy Applicant" loan file is being processed (likely Encompass/Moxi flow).
        
        INPUT CONTEXT (For Speaker Identification & Speech):
        '''{zoom_context[:4000]}...'''
        
        INSTRUCTIONS:
        1. **VISUAL PRECISION**: You MUST describe exactly what is on the screen. 
           - If a Form is shown, list the visible fields and values entered.
           - If a Button is clicked, state the EXACT button label (e.g. "Create Loan" vs "Submit").
           - Identify the software screen (e.g., "1003 Form", "Borrower Summary", "Email Automation").
           
        2. **CLICK-BY-CLICK ACCURACY**: Record every single interaction.
           - "User clicked dropdown 'Loan Type' -> Selected 'FHA'".
           - "User checked box 'First Time Homebuyer'".
           
        3. **SPEAKER & TRANSCRIPT**: 
           - Attribute actions/speech to the correct person (use names from Context).
           - Provide the KEY PHRASE said during the action (Verbatim if possible).

        4. **STRICT FORMAT**:
           For every distinct action or screen change, output a structured block:
           
           ### [MM:SS] {{Action Summary}}
           - **Screen**: {{Detailed description of UI/Form}}
           - **Action**: {{Click-by-click interaction}}
           - **Data Input**: 
               * {{Field}}: {{Value}}
               * {{Field}}: {{Value}}
           - **Speaker**: {{Name}} ("{{Quote}}")
           
        5. **NO HALLUCINATIONS**: Only list what you SEE and HEAR. If a screen is blurry, say "Unclear".
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
            new_analysis_count += 1
            
            # Save Incremental
            # Sort by chunk_index to ensure order
            results.sort(key=lambda x: x.get('chunk_index', 0))
            with open(Config.RAW_SOP_DB, "w") as f:
                json.dump(results, f, indent=2)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

        # 4. Rate Limit Sleep
        if i < len(videos) - 1:
            print(f"   ⏳ Cooling down {Config.SLEEP_BETWEEN_ANALYSIS}s...")
            time.sleep(Config.SLEEP_BETWEEN_ANALYSIS)

    print(f"\n✅ Analysis Complete. {new_analysis_count} new videos analyzed. Saved to {Config.RAW_SOP_DB}")

if __name__ == "__main__":
    analyze()