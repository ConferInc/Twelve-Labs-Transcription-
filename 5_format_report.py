"""
Step 5: Format Analysis into StoneFactory Requirements Document
================================================================
Reads the raw analysis JSON and produces:
1. A structured Markdown requirements document (for human review)
2. A structured JSON file (for automated validation pipeline)

Output:
  - StoneFactory_Meeting_Requirements.md
  - data/structured_requirements.json
"""

import json
import re
import os
from datetime import datetime
from config import Config


def stitch_timestamps(text, chunk_index):
    """Convert local chunk timestamps [MM:SS] to global video timestamps."""
    offset = chunk_index * Config.CHUNK_DURATION_MINS

    def replace(match):
        time_str = match.group(1)
        parts = time_str.split(':')
        if len(parts) == 2:
            m, s = int(parts[0]), int(parts[1])
            global_m = m + offset
            hours = global_m // 60
            mins = global_m % 60
            if hours > 0:
                return f"[{hours}:{mins:02d}:{s:02d}]"
            return f"[{mins:02d}:{s:02d}]"
        return match.group(0)

    return re.sub(r'\[(\d{1,2}:\d{2})\]', replace, text)


def extract_structured_data(raw_text):
    """
    Parse the raw markdown analysis into structured requirement blocks.
    Each block starts with '### [' and contains labeled fields.
    """
    requirements = []
    blocks = re.split(r'(?=###\s+\[)', raw_text)

    for block in blocks:
        block = block.strip()
        if not block or not block.startswith('###'):
            continue

        req = {}

        # Extract timestamp and title
        header_match = re.match(r'###\s+\[([^\]]+)\]\s+(.*)', block)
        if header_match:
            req['timestamp'] = header_match.group(1).strip()
            req['title'] = header_match.group(2).strip()
        else:
            continue

        # Extract labeled fields
        field_patterns = {
            'module': r'\*\*Module:\*\*\s*(.*)',
            'type': r'\*\*Type:\*\*\s*(.*)',
            'priority': r'\*\*Priority:\*\*\s*(.*)',
            'source': r'\*\*Source:\*\*\s*(.*)',
            'speaker': r'\*\*Speaker:\*\*\s*(.*)',
        }

        for field_name, pattern in field_patterns.items():
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                req[field_name] = match.group(1).strip()

        # Extract description
        desc_match = re.search(
            r'\*\*Description:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if desc_match:
            req['description'] = desc_match.group(1).strip()

        # Extract fields/data list
        fields_match = re.search(
            r'\*\*Fields/Data Identified:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if fields_match:
            fields_text = fields_match.group(1).strip()
            if fields_text and fields_text != "N/A":
                req['fields'] = [
                    line.strip().lstrip('- ')
                    for line in fields_text.split('\n')
                    if line.strip() and line.strip() != '-'
                ]

        # Extract business rules
        rules_match = re.search(
            r'\*\*Business Rules:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if rules_match:
            rules_text = rules_match.group(1).strip()
            if rules_text and rules_text != "N/A":
                req['business_rules'] = [
                    line.strip().lstrip('- ')
                    for line in rules_text.split('\n')
                    if line.strip() and line.strip() != '-'
                ]

        # Extract visual content
        visual_match = re.search(
            r'\*\*Visual Content.*?:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if visual_match:
            visual_text = visual_match.group(1).strip()
            if visual_text and visual_text != "N/A":
                req['visual_content'] = visual_text

        # Extract SAP reference
        sap_match = re.search(
            r'\*\*Current SAP Reference:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\n---|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if sap_match:
            sap_text = sap_match.group(1).strip()
            if sap_text and sap_text != "N/A":
                req['sap_reference'] = sap_text

        # Extract relationships
        rel_match = re.search(
            r'\*\*Relationships:\*\*\s*\n?(.*?)(?=\n\*\*[A-Z]|\Z)',
            block, re.DOTALL | re.IGNORECASE
        )
        if rel_match:
            rel_text = rel_match.group(1).strip()
            if rel_text and rel_text != "N/A":
                req['relationships'] = [
                    line.strip().lstrip('- ')
                    for line in rel_text.split('\n')
                    if line.strip() and line.strip() != '-'
                ]

        if req.get('title'):
            requirements.append(req)

    return requirements


def count_by_field(requirements, field):
    """Count requirements grouped by a field value."""
    counts = {}
    for req in requirements:
        val = req.get(field, 'unclassified')
        counts[val] = counts.get(val, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def generate_report():
    """Generate the formatted requirements document and structured JSON."""
    if not os.path.exists(Config.RAW_SOP_DB):
        print("[ERROR] Raw analysis data missing. Run script #4 first.")
        return

    with open(Config.RAW_SOP_DB, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("[ERROR] No analysis data found.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_chunks = len(data)

    # Build Markdown report
    report = f"""# {Config.PROJECT_NAME} - Meeting Requirements Analysis

> **Client:** {Config.CLIENT_NAME} ({Config.CLIENT_INDUSTRY})
> **Generated:** {now}
> **Source:** {total_chunks} video segments analyzed via Twelve Labs AI
> **Pipeline:** Video -> Twelve Labs (Marengo 2.7 + Pegasus 1.2) -> Structured Requirements

---

## How to Read This Document

This document was automatically generated by analyzing meeting video recordings using AI.
It captures **both audio discussions and visual content shown on screen** (SAP forms, Excel
spreadsheets, flow charts, UI mockups, documents).

Each requirement block includes:
- **Timestamp**: When in the video this was discussed/shown
- **Module**: Which ERP module this belongs to
- **Type**: Category (feature, entity, workflow, field, rule, etc.)
- **Source**: Whether captured from audio, visual, or both
- **Priority**: As indicated by the speakers (if mentioned)

---

"""

    # Collect structured requirements
    all_requirements = []
    for item in data:
        chunk_reqs = extract_structured_data(item['raw_text'])
        for req in chunk_reqs:
            req['chunk_index'] = item['chunk_index']
            req['source_file'] = item['filename']
        all_requirements.extend(chunk_reqs)

    # Summary statistics
    module_counts = count_by_field(all_requirements, 'module')
    type_counts = count_by_field(all_requirements, 'type')
    priority_counts = count_by_field(all_requirements, 'priority')
    source_counts = count_by_field(all_requirements, 'source')

    report += f"## Executive Summary\n\n"
    report += f"**Total Requirements Captured:** {len(all_requirements)}\n\n"

    report += "### By Module\n\n| Module | Count |\n|--------|-------|\n"
    for mod, cnt in module_counts.items():
        report += f"| {mod} | {cnt} |\n"

    report += "\n### By Type\n\n| Type | Count |\n|------|-------|\n"
    for typ, cnt in type_counts.items():
        report += f"| {typ} | {cnt} |\n"

    report += "\n### By Source (Audio vs Visual)\n\n| Source | Count |\n|--------|-------|\n"
    for src, cnt in source_counts.items():
        report += f"| {src} | {cnt} |\n"

    report += "\n### By Priority\n\n| Priority | Count |\n|----------|-------|\n"
    for pri, cnt in priority_counts.items():
        report += f"| {pri} | {cnt} |\n"

    report += "\n---\n\n"

    # Detailed sections by video chunk
    for item in data:
        chunk_idx = item['chunk_index']
        start = chunk_idx * Config.CHUNK_DURATION_MINS
        end = (chunk_idx + 1) * Config.CHUNK_DURATION_MINS

        print(f"  Processing {item['filename']} (chunk {chunk_idx})...")

        final_text = stitch_timestamps(item['raw_text'], chunk_idx)

        report += f"\n## SEGMENT {chunk_idx + 1}: {item['filename']} ({start}m - {end}m)\n"
        report += "=" * 80 + "\n\n"
        report += final_text + "\n\n"
        report += "=" * 80 + "\n"

    # Module-grouped index
    report += "\n\n---\n\n## Requirements Index (Grouped by Module)\n\n"
    for module in sorted(module_counts.keys()):
        module_reqs = [r for r in all_requirements if r.get('module') == module]
        report += f"### {module} ({len(module_reqs)} items)\n\n"
        for req in module_reqs:
            ts = req.get('timestamp', '??:??')
            title = req.get('title', 'Untitled')
            rtype = req.get('type', 'unknown')
            priority = req.get('priority', '-')
            report += f"- **[{ts}]** {title} _{rtype}_ (Priority: {priority})\n"
        report += "\n"

    # Save Markdown
    with open(Config.FINAL_REPORT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  [OK] Markdown report: {Config.FINAL_REPORT}")

    # Save structured JSON
    structured_output = {
        "project": Config.PROJECT_NAME,
        "client": Config.CLIENT_NAME,
        "generated": now,
        "total_segments": total_chunks,
        "total_requirements": len(all_requirements),
        "summary": {
            "by_module": module_counts,
            "by_type": type_counts,
            "by_priority": priority_counts,
            "by_source": source_counts,
        },
        "requirements": all_requirements,
    }

    with open(Config.FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Structured JSON: {Config.FINAL_JSON}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"  REPORT SUMMARY")
    print(f"{'='*60}")
    print(f"    Total requirements:  {len(all_requirements)}")
    print(f"    Modules covered:     {len(module_counts)}")
    visual_count = sum(1 for r in all_requirements if r.get('source') in ['visual', 'both'])
    audio_count = sum(1 for r in all_requirements if r.get('source') in ['audio', 'both'])
    print(f"    Visual captures:     {visual_count}")
    print(f"    Audio captures:      {audio_count}")
    high_count = priority_counts.get('high', 0) + priority_counts.get('urgent', 0)
    print(f"    High/Urgent items:   {high_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    generate_report()
