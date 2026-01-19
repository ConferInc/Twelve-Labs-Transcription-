# 🤖 Moxi Global Video Analysis Pipeline

**Automated Generation of Technical SOPs from Zoom Cloud Recordings**

This repository contains the modular pipeline for processing large video files (Zooms) into detailed standard operating procedures (SOPs) using **TwelveLabs AI**.

---

## 📂 Project Structure

```text
Moxi_Pipeline/
├── raw_video/             # [INPUT] Place your 'Link1.mp4' here (Ignored by Git)
├── chunks/                # [TEMP] generated 15m video parts (Ignored by Git)
├── data/                  # [STATE] JSON files tracking progress (Ignored by Git)
├── transcript.vtt         # [INPUT] Zoom transcript for context injection
├── config.py              # [SETTINGS] API Keys & Folder Paths
├── 1_split_video.py       # [STEP 1] Splits large video -> 15m chunks
├── 2_upload_assets.py     # [STEP 2] Uploads chunks to TwelveLabs Cloud
├── 3_index_assets.py      # [STEP 3] Binds uploads to an AI Index
├── 4_analyze_video.py     # [STEP 4] Generates the SOP content
└── 5_format_report.py     # [STEP 5] Compiles the Final Markdown Report
```

## 🚀 Setup & Installation

### 1. Prerequisites
*   **Python 3.10+**
*   **FFmpeg** (Usually installed via `imageio-ffmpeg` automatically)
*   **TwelveLabs API Key** (Get one at [playground.twelvelabs.io](https://playground.twelvelabs.io))

### 2. Install Dependencies
```bash
pip install twelvelabs moviepy imageio_ffmpeg
```

### 3. Configuration
Open `config.py` and set your API key:
```python
API_KEY = "tlk_YOUR_API_KEY_HERE"
```

---

## 🔁 The Workflow (How it Works)

The pipeline is split into **5 discrete steps** to ensure reliability. If one step fails, you don't lose progress. State is saved in `data/`.

### **STEP 1: Split Video (`1_split_video.py`)**
*   **What it does:** Takes the large files in `raw_video/` and slices them into **15-minute chunks** using FFmpeg "Direct Stream Copy". 
*   **Why?** TwelveLabs processes shorter videos more accurately for "Stream" analysis, and it prevents timeouts.
*   **Output:** Populates `chunks/` folder.

### **STEP 2: Upload (`2_upload_assets.py`)**
*   **What it does:** Uploads each chunk to the TwelveLabs **Assets** library.
*   **Why?** Assets are the raw storage layer. Uploading them once allows us to re-index them differently later without re-uploading.
*   **State:** Creates `data/assets.json`.

### **STEP 3: Index (`3_index_assets.py`)**
*   **What it does:** Creates an Index (using **Marengo 2.7** for Visuals & **Pegasus 1.2** for Audio) and binds the assets to it.
*   **Why?** Indexing runs the AI perception models (seeing & hearing) on the video.
*   **State:** Creates `data/index_map.json` linking Files <-> Video IDs.

### **STEP 4: Analyze (`4_analyze_video.py`)**
*   **What it does:** 
    1.  Reads the `transcript.vtt` to find the exact context (Speaker Names, Topics) for that 15m segment.
    2.  Injects this context into a **"Nuclear Prompt"**.
    3.  Asks TwelveLabs to generate a detailed Technical SOP including specific button clicks and speaker actions.
*   **Rate Limiting:** Sleeps between calls to avoid API limits.
*   **State:** Creates `data/raw_sop_output.json`.

### **STEP 5: Format (`5_format_report.py`)**
*   **What it does:** 
    1.  Reads the raw JSON analysis.
    2.  **Stitches Timestamps**: Converts local "00:00" chunk times to Global "01:15:00" video times.
    3.  Compiles everything into a clean Markdown document.
*   **Output:** `Moxi_Master_SOP.md`.

---

## 🛑 Troubleshooting

*   **"Raw video not found"**: ensure your file is named `Link1.mp4` (or update `config.py`) and is inside `raw_video/`.
*   **Rate Limit Errors**: Increase `SLEEP_BETWEEN_ANALYSIS` in `config.py`.
*   **Missing Speaker Names**: Ensure `transcript.vtt` exists in the root folder.
