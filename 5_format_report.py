import json
import re
from config import Config
import os   

def stitch_timestamps(text, chunk_index):
    offset = chunk_index * Config.CHUNK_DURATION_MINS
    def replace(match):
        m, s = map(int, match.group(1).split(':'))
        return f"[{m + offset:02d}:{s:02d}]"
    return re.sub(r'\[(\d{1,2}:\d{2})\]', replace, text)

def generate_report():
    if not os.path.exists(Config.RAW_SOP_DB):
        print("❌ Raw Data missing. Run script #4 first.")
        return
        
    with open(Config.RAW_SOP_DB, "r") as f:
        data = json.load(f)

    report = "# MOXI GLOBAL - MASTER TECHNICAL SOP\n\n"
    report += f"**Generated:** {len(data)} Sections\n\n"

    for item in data:
        print(f"Processing {item['filename']}...")
        
        # 1. Stitch Time
        final_text = stitch_timestamps(item['raw_text'], item['chunk_index'])
        
        # 2. Add Headers
        start = item['chunk_index'] * Config.CHUNK_DURATION_MINS
        end = (item['chunk_index'] + 1) * Config.CHUNK_DURATION_MINS
        
        report += f"\n## SECTION {item['chunk_index']+1}: {item['filename']} ({start}m - {end}m)\n"
        report += "="*80 + "\n\n"
        report += final_text + "\n\n"
        report += "="*80 + "\n"

    with open(Config.FINAL_REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ SUCCESS! Final SOP saved to: {Config.FINAL_REPORT}")

if __name__ == "__main__":
    generate_report()