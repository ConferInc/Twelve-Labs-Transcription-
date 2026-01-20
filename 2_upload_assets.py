import os
import glob
import json
from twelvelabs import TwelveLabs
from config import Config

def upload_assets():
    client = TwelveLabs(api_key=Config.API_KEY)
    
    chunk_files = sorted(glob.glob(os.path.join(Config.CHUNKS_DIR, "*.mp4")))
    if not chunk_files:
        print("❌ No chunks found! Run script #1 first.")
        return

    # Load existing assets if available
    assets_db = []
    if os.path.exists(Config.ASSETS_DB):
        try:
            with open(Config.ASSETS_DB, "r") as f:
                assets_db = json.load(f)
            print(f"📂 Loaded {len(assets_db)} existing assets from DB.")
        except Exception as e:
            print(f"⚠️ Could not load existing assets DB: {e}")

    # Create a set of already uploaded filenames for quick lookup
    existing_filenames = {item['filename'] for item in assets_db}
    
    print(f"🚀 Found {len(chunk_files)} chunks to process...")
    
    new_uploads_count = 0
    for file_path in chunk_files:
        filename = os.path.basename(file_path)
        
        if filename in existing_filenames:
            # check if the file path is correct in the db, update if moved (optional but good)
            # For now, just skip
            print(f"   ⏭️  Skipping {filename} (Already uploaded)")
            continue

        print(f"   ⬆️  Uploading {filename}...", end="", flush=True)
        
        try:
            # SDK v1.3: method='direct', no 'name'
            asset = client.assets.create(file=open(file_path, "rb"), method="direct")
            print(f" Done. ID: {asset.id}")
            
            assets_db.append({
                "filename": filename,
                "asset_id": asset.id,
                "path": file_path
            })
            new_uploads_count += 1
            
            # Save incrementally in case of crash
            with open(Config.ASSETS_DB, "w") as f:
                json.dump(assets_db, f, indent=2)

        except Exception as e:
            print(f"\n❌ Error uploading {filename}: {e}")

    print(f"\n✅ Uploads Complete. {new_uploads_count} new files uploaded. Database saved to {Config.ASSETS_DB}")

if __name__ == "__main__":
    upload_assets()