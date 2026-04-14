# StoneFactory ERP - Video Meeting Analysis Pipeline

Extracts ERP requirements from client meeting recordings using **Twelve Labs AI** (Marengo 3.0 + Pegasus 1.2). Captures both **audio** (speech) and **visual** (screens, forms, spreadsheets) content.

---

## URGENT: Recover Missing Chunk (April 13, 30m-45m)

We have 7/8 chunks analyzed. One chunk from the **April 13 meeting (30m-45m)** hit the daily rate limit. To recover it:

### Prerequisites
```bash
pip install twelvelabs moviepy imageio_ffmpeg
```

### Steps

1. **Get a Twelve Labs API key** at https://playground.twelvelabs.io

2. **Edit `config.py`** -- paste your API key:
   ```python
   API_KEY = "tlk_YOUR_KEY_HERE"
   ```

3. **Place the April 13 meeting video** in the `raw_video/` folder:
   ```bash
   cp "MicrosoftTeams-video 13-Apr-26.mp4" raw_video/Link1.mp4
   ```
   The video is located at: `../Confer Solutions Meetings Recording/MicrosoftTeams-video 13-Apr-26.mp4`

4. **Place the existing results** -- copy `raw_analysis_apr13.json` from the `requirements/` folder:
   ```bash
   cp "../requirements/raw_analysis_apr13.json" data/raw_sop_output.json
   ```
   This file has chunks 0, 1, 3 already analyzed. The script will only process the missing chunk 2.

5. **Run the recovery script:**
   ```bash
   python run_missing_chunk.py
   ```

   This single command will:
   - Extract only the 30m-45m segment from the video (~2 sec)
   - Upload that one chunk to Twelve Labs (~1 min)
   - Create a new index and index it (~30 sec)
   - Analyze it with the ERP prompt (~2 min)
   - Merge the result into `data/raw_sop_output.json` (now has all 4 chunks)
   - Regenerate the full report at `StoneFactory_Meeting_Requirements.md`

6. **Hand back the output** -- copy these two files back:
   ```bash
   cp data/raw_sop_output.json "../requirements/raw_analysis_apr13.json"
   cp StoneFactory_Meeting_Requirements.md "../requirements/StoneFactory_Meeting_Requirements_Apr13.md"
   ```

**Total time: ~5 minutes. Total cost: ~1 chunk (15 min of video).**

---

## Rate Limits (Twelve Labs Free Tier)

| Limit | Value | Notes |
|-------|-------|-------|
| Output tokens | 4,000 / minute | ~1 chunk worth of analysis |
| Output tokens | 25,000 / day | ~5-6 chunks per day |
| Video duration | 3,600 sec / hour | ~60 min of video indexed per hour |

If you hit rate limits, wait for the reset time shown in the error message.

---

## Full Pipeline (Processing a new video from scratch)

```bash
pip install twelvelabs moviepy imageio_ffmpeg
# Edit config.py with your API key
cp "your-meeting.mp4" raw_video/Link1.mp4
python run_pipeline.py
```

### Pipeline Steps

| Step | Script | Time | What It Does |
|------|--------|------|-------------|
| 1 | `1_split_video.py` | ~2 min | Split video into 15-min chunks (FFmpeg) |
| 2 | `2_upload_assets.py` | ~2 min | Upload chunks to Twelve Labs cloud |
| 3 | `3_index_assets.py` | ~2 min | Index with Marengo 3.0 + Pegasus 1.2 |
| 4 | `4_analyze_video.py` | ~5-10 min | Analyze with ERP-specific prompt (75s cooldown) |
| 5 | `5_format_report.py` | instant | Format into Markdown + JSON |

### Resume After Failure

```bash
python run_pipeline.py --skip-split       # Already split
python run_pipeline.py --skip-upload      # Already uploaded
python run_pipeline.py --skip-index       # Already indexed
python run_pipeline.py --analyze-only     # Re-run analysis only
python run_pipeline.py --report-only      # Re-generate report only
```

---

## Output Files

| File | Description |
|------|-------------|
| `StoneFactory_Meeting_Requirements.md` | Formatted requirements document |
| `data/raw_sop_output.json` | Raw analysis per chunk (the main data file) |
| `data/structured_requirements.json` | Parsed structured requirements |
| `data/assets.json` | Upload tracking (asset IDs) |
| `data/index_map.json` | Index tracking (video IDs) |

---

## Configuration

Edit `config.py`:

| Setting | Description |
|---------|-------------|
| `API_KEY` | Your Twelve Labs key (required) |
| `INDEX_ID` | Leave empty for auto-create. Paste ID after first run to reuse. |
| `INDEX_NAME` | Name for the Twelve Labs index |
| `SLEEP_BETWEEN_ANALYSIS` | Seconds between API calls (default 75, increase if 429 errors) |
| `KNOWN_SPEAKERS` | Update speaker names per meeting |

---

## File Structure

```
twelve-labs-pipeline/
  config.py                    # API key, settings
  run_pipeline.py              # Full pipeline runner
  run_missing_chunk.py         # Single missing chunk recovery
  1_split_video.py             # Step 1: FFmpeg split
  2_upload_assets.py           # Step 2: Upload to Twelve Labs
  3_index_assets.py            # Step 3: Index with AI models
  4_analyze_video.py           # Step 4: Analyze with ERP prompt
  5_format_report.py           # Step 5: Format report
  prompts/
    stonefactory_erp.py        # The analysis prompt
  raw_video/                   # Place meeting MP4 here as Link1.mp4
  chunks/                      # Auto-generated 15-min chunks
  data/                        # State files + output
```
