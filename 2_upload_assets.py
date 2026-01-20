import os
import glob
import json
from twelvelabs import TwelveLabs
from config import Config

def upload_assets():
    client = TwelveLabs(api_key=Config.API_KEY)
    
    chunk_files = sorted(glob.glob(os.path.join(Config.CHUNKS_DIR, "*.mp4")))
    if not chunk_files:
        print("❌ No chunks found in directory.")
        return
    # 1. Fetch Remote State (Source of Truth)
    print("🌍 Fetching verifiable state from TwelveLabs...")
    remote_assets = {}
    try:
        # Fetch all assets (ignoring pagination for now as list is small)
        tl_assets = client.assets.list()
        for a in tl_assets:
            # map filename -> asset object
            remote_assets[a.name] = a.id
        print(f"🌍 Found {len(remote_assets)} assets in TwelveLabs account.")
    except Exception as e:
        print(f"⚠️ Could not fetch remote assets: {e}")

    # 2. Sync Local DB with Remote Truth
    assets_db = []
    # If we have a local DB, we can try to preserve data, but remote is truth for IDs
    if os.path.exists(Config.ASSETS_DB):
        try:
            with open(Config.ASSETS_DB, "r") as f:
                local_data = json.load(f)
                # We can use this to grab file paths if we need them, 
                # but we're re-scanning chunks dir anyway.
        except:
            pass
    
    # Re-build assets_db based on chunks dir + remote status
    # This ensures assets_db contains ALL chunks, pointing to remote IDs if they exist
    
    print(f"🚀 Found {len(chunk_files)} chunks to process...")
    
    new_uploads_count = 0
    final_assets_list = []

    for file_path in chunk_files:
        filename = os.path.basename(file_path)
        
        # Check if exists remotely
        if filename in remote_assets:
            print(f"   ✅ {filename} exists remotely ({remote_assets[filename]})")
            final_assets_list.append({
                "filename": filename,
                "asset_id": remote_assets[filename],
                "path": file_path
            })
            continue # Skip upload

        # If not, upload it
        print(f"   ⬆️  Uploading {filename}...", end="", flush=True)
        try:
            # SDK v1.3: method='direct', no 'name'
            asset = client.assets.create(file=open(file_path, "rb"), method="direct")
            print(f" Done. ID: {asset.id}")
            
            final_assets_list.append({
                "filename": filename,
                "asset_id": asset.id,
                "path": file_path
            })
            new_uploads_count += 1
            
        except Exception as e:
            print(f"\n❌ Error uploading {filename}: {e}")

    # Save verified DB
    with open(Config.ASSETS_DB, "w") as f:
        json.dump(final_assets_list, f, indent=2)

    print(f"\n✅ Sync Complete. {new_uploads_count} new files uploaded. DB synced with Remote.")

if __name__ == "__main__":
    upload_assets()