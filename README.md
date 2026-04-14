# StoneFactory ERP - Video Meeting Analysis Pipeline

**Automated extraction of ERP requirements from client meeting recordings using Twelve Labs AI**

This pipeline processes video recordings of client meetings and produces structured requirements documents by analyzing **both audio (speech)** and **visual (screen content)** channels.

---

## Quick Start

```bash
pip install twelvelabs moviepy imageio_ffmpeg
# Edit config.py with your API key
cp "your-meeting.mp4" raw_video/Link1.mp4
python run_pipeline.py
```

## What It Captures

| Channel | What's Extracted |
|---------|-----------------|
| **Audio** | Feature requirements, business rules, approval workflows, UOM discussions, process flows, pain points, priorities |
| **Visual** | SAP forms with field labels/values, Excel spreadsheets with column headers and data, flow charts, UI mockups, document templates, handwritten notes |

## Pipeline Steps

| Step | Script | Time | What It Does |
|------|--------|------|-------------|
| 1 | `1_split_video.py` | ~2 min | Split video into 15-min chunks (FFmpeg stream copy) |
| 2 | `2_upload_assets.py` | ~15 min | Upload chunks to Twelve Labs cloud |
| 3 | `3_index_assets.py` | ~20 min | Index with Marengo 2.7 + Pegasus 1.2 (visual+audio AI) |
| 4 | `4_analyze_video.py` | ~5-10 min | Analyze with ERP-specific prompt |
| 5 | `5_format_report.py` | ~1 min | Format into Markdown + JSON requirements document |

## Resume / Skip Steps

```bash
python run_pipeline.py --skip-split       # Already split
python run_pipeline.py --skip-upload      # Already uploaded
python run_pipeline.py --skip-index       # Already indexed
python run_pipeline.py --analyze-only     # Re-run analysis only
python run_pipeline.py --report-only      # Re-generate report only
python run_pipeline.py --fast             # Lightweight prompt (faster)
```

## Output

- `StoneFactory_Meeting_Requirements.md` - Human-readable requirements with timestamps
- `data/structured_requirements.json` - Machine-readable JSON for validation pipeline

## Configuration

Edit `config.py`:
- `API_KEY` - Your Twelve Labs key (get at playground.twelvelabs.io)
- `KNOWN_SPEAKERS` - Update per meeting
- `SLEEP_BETWEEN_ANALYSIS` - Increase if getting 429 errors
