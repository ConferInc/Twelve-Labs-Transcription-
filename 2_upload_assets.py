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

    assets_db = []
    
    print(f"🚀 Found {len(chunk_files)} chunks to upload...")
    
    for file_path in chunk_files:
        filename = os.path.basename(file_path)
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
        except Exception as e:
            print(f"\n❌ Error uploading {filename}: {e}")

    # Save DB
    with open(Config.ASSETS_DB, "w") as f:
        json.dump(assets_db, f, indent=2)
    print(f"\n✅ Uploads Complete. Database saved to {Config.ASSETS_DB}")

if __name__ == "__main__":
    upload_assets()