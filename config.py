import os

class Config:
    # ============================================================
    # STONEFACTORY ERP - VIDEO ANALYSIS PIPELINE CONFIGURATION
    # ============================================================

    # [ACTION REQUIRED] PASTE YOUR API KEY HERE
    API_KEY = "tlk_2DBEN7P0HJPGWB2XD5H0C391XWS3"

    # INDEX CONFIGURATION
    # Clear INDEX_ID to create a fresh index for StoneFactory
    INDEX_ID = ""  # Leave empty to auto-create
    INDEX_NAME = "StoneFactory_ERP_Meeting_Analysis_v1"

    # PROCESSING SETTINGS
    CHUNK_DURATION_MINS = 15  # 15-minute chunks (optimal for Twelve Labs accuracy)
    SLEEP_BETWEEN_ANALYSIS = 45  # Seconds between API calls (reduced from 60 for faster processing)

    # PATHS
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_VIDEO_DIR = os.path.join(BASE_DIR, "raw_video")
    RAW_VIDEO_PATH = os.path.join(RAW_VIDEO_DIR, "Link1.mp4")  # Rename your video to this
    CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    TRANSCRIPT_PATH = os.path.join(BASE_DIR, "transcript.vtt")

    # STATE FILES
    ASSETS_DB = os.path.join(DATA_DIR, "assets.json")
    INDEX_DB = os.path.join(DATA_DIR, "index_map.json")
    RAW_SOP_DB = os.path.join(DATA_DIR, "raw_sop_output.json")

    # OUTPUT
    FINAL_REPORT = os.path.join(BASE_DIR, "StoneFactory_Meeting_Requirements.md")
    FINAL_JSON = os.path.join(DATA_DIR, "structured_requirements.json")

    # STONEFACTORY CONTEXT
    # These are injected into the analysis prompt for better accuracy
    PROJECT_NAME = "StoneFactory ERP"
    CLIENT_NAME = "Global Impex Pvt. Ltd."
    CLIENT_INDUSTRY = "Natural Stone Import/Export"

    # Known speakers in meetings (update per video)
    KNOWN_SPEAKERS = [
        "Alok",       # Client - Primary Contact, Business Owner
        "Uday",       # Client - IT Contact
        "Yatin",      # Confer - Project Lead
        "Tanmay",     # Confer - Technical Lead
        "Shrikanth",  # Confer - Data/AI Engineer
    ]

    # ERP Modules for classification
    ERP_MODULES = [
        "Masters",           # Stone types, colors, shapes, items, customers, suppliers
        "Sales",             # Quotes, PIs, orders, invoices, commercial invoices
        "Purchase",          # POs, GRNs, supplier management
        "Inventory",         # Stock, warehouses, locations, crate tracking
        "Production",        # Job cards, work orders, contractor management, BOM
        "Finance",           # GST, payments, receivables, payables, Tally integration
        "Logistics",         # Shipments, containers, packing lists, ports
        "Dashboard",         # KPIs, reports, analytics
        "Mobile",            # Field inspector, stock counting, QR scanning
        "Approvals",         # Approval workflows, role hierarchy
        "CRM",               # Leads, opportunities, communications
        "Settings",          # Company, branches, GST registration
        "UOM",               # Unit of measurement, conversions, density factors
        "Reports",           # Print formats, export documents
    ]

# Ensure directories exist
os.makedirs(Config.CHUNKS_DIR, exist_ok=True)
os.makedirs(Config.DATA_DIR, exist_ok=True)
