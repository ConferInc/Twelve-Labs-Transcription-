import json
import time
from twelvelabs import TwelveLabs
from config import Config
import os

def index_assets():
    client = TwelveLabs(api_key=Config.API_KEY)
    
    # 1. Load Assets (Local or synced)
    if not os.path.exists(Config.ASSETS_DB):
        print("❌ Assets DB missing. Run script #2 first.")
        return
    with open(Config.ASSETS_DB, "r") as f:
        assets = json.load(f)

    # 2. Get/Create Index (Use configured ID)
    target_index = None
    if getattr(Config, "INDEX_ID", None):
        try:
            target_index = client.indexes.retrieve(Config.INDEX_ID)
            print(f"✅ Using Configured Index: {target_index.id} ('{target_index.index_name}')")
        except Exception as e:
            print(f"❌ Error retrieving configured index: {e}")
            return
            
    if not target_index:
        # Fallback to search (legacy)
        for idx in client.indexes.list():
            if getattr(idx, "index_name", "") == Config.INDEX_NAME:
                target_index = idx
                print(f"✅ Found existing Index: {idx.id}")
                break
    
    if not target_index:
        print(f"🆕 Creating Index '{Config.INDEX_NAME}'...")
        target_index = client.indexes.create(
            index_name=Config.INDEX_NAME,
            models=[
                {"model_name": "marengo2.7", "model_options": ["visual", "audio"]},
                {"model_name": "pegasus1.2", "model_options": ["visual", "audio"]}
            ]
        )
        print(f"✅ Created Index: {target_index.id}")
        
    # 3. Sync Remote Index State
    print(f"🌍 Verifying contents of Index {target_index.id}...")
    remote_indexed_video_ids = {} # filename -> video_id
    
    # We need to map Asset ID -> Filename (reverse lookup)
    asset_id_to_filename = {item['asset_id']: item['filename'] for item in assets}
    
    try:
        # Fetch all indexed assets
        # Note: pagination might be needed for large sets, ignoring for now
        indexed_assets = client.indexes.indexed_assets.list(index_id=target_index.id)
        for val in indexed_assets:
            # val.id is the VIDEO_ID used for analysis
            # val.asset_id is the uploaded asset ID
            if hasattr(val, 'asset_id') and val.asset_id in asset_id_to_filename:
                fname = asset_id_to_filename[val.asset_id]
                remote_indexed_video_ids[fname] = val.id
                
        print(f"🌍 Found {len(remote_indexed_video_ids)} assets already in this Index.")
    except Exception as e:
        print(f"⚠️ Could not verify index contents: {e}")

    # Re-build index_map from what we KNOW is there
    indexed_map = []
    
    # Add known remote items to map
    for fname, vid_id in remote_indexed_video_ids.items():
        # Find asset_id
        aid = next((a['asset_id'] for a in assets if a['filename'] == fname), None)
        if aid:
            indexed_map.append({
                "filename": fname,
                "video_id": vid_id,
                "asset_id": aid
            })

    print(f"🔗 Binding {len(assets)} assets to Index...")
    
    new_bindings_count = 0
    for item in assets:
        if item['filename'] in remote_indexed_video_ids:
            # Already indexed and in our map
            print(f"   ✅ {item['filename']} is indexed ({remote_indexed_video_ids[item['filename']]})")
            continue

        print(f"   Processing {item['filename']}...", end="", flush=True)
        try:
            # Bind
            ia = client.indexes.indexed_assets.create(
                index_id=target_index.id,
                asset_id=item['asset_id']
            )
            
            # Wait for Ready
            while True:
                status = client.indexes.indexed_assets.retrieve(
                    index_id=target_index.id,
                    indexed_asset_id=ia.id
                ).status
                if status == "ready":
                    print(" Ready!")
                    break
                elif status == "failed":
                    print(" Failed!")
                    break
                time.sleep(1)
            
            indexed_map.append({
                "filename": item['filename'],
                "video_id": ia.id, # This is the ID used for analysis
                "asset_id": item['asset_id']
            })
            new_bindings_count += 1
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
    # Save DB
    with open(Config.INDEX_DB, "w") as f:
        json.dump(indexed_map, f, indent=2)
    print(f"\n✅ Indexing Complete. {new_bindings_count} new assets bound. Map synced with Remote.")

if __name__ == "__main__":
    index_assets()