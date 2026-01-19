import os

class Config:
    # [ACTION REQUIRED] PASTE NEW API KEY HERE
    API_KEY = "tlk_1R29YQK19F8J7M2X896HX2TAN7H7" 
    
    # Global Settings
    INDEX_NAME = "Moxi_Global_Analysis_Final_v3"
    CHUNK_DURATION_MINS = 15
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_VIDEO_PATH = os.path.join(BASE_DIR, "raw_video", "Link1.mp4") # <--- Rename if needed
    CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    TRANSCRIPT_PATH = os.path.join(BASE_DIR, "transcript.vtt")
    
    # State Files (These keep track of IDs so you can stop/resume)
    ASSETS_DB = os.path.join(DATA_DIR, "assets.json")
    INDEX_DB = os.path.join(DATA_DIR, "index_map.json")
    RAW_SOP_DB = os.path.join(DATA_DIR, "raw_sop_output.json")
    FINAL_REPORT = os.path.join(BASE_DIR, "Moxi_Master_SOP.md")
    
    # Rate Limiting
    SLEEP_BETWEEN_ANALYSIS = 60 # Seconds (Critical to avoid 429 Errors)

# Ensure directories exist
os.makedirs(Config.CHUNKS_DIR, exist_ok=True)
os.makedirs(Config.DATA_DIR, exist_ok=True)