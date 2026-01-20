import json
import time
from twelvelabs import TwelveLabs
from config import Config
import os

def index_assets():
    client = TwelveLabs(api_key=Config.API_KEY)
    
    # 1. Load Assets
    if not os.path.exists(Config.ASSETS_DB):
        print("❌ Assets DB missing. Run script #2 first.")
        return
    with open(Config.ASSETS_DB, "r") as f:
        assets = json.load(f)

    # 2. Get/Create Index
    target_index = None
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

    # 3. Bind Assets
    indexed_map = []
    # Load existing indexed map if available
    if os.path.exists(Config.INDEX_DB):
        try:
            with open(Config.INDEX_DB, "r") as f:
                indexed_map = json.load(f)
            print(f"📂 Loaded {len(indexed_map)} existing indexed assets from DB.")
        except Exception as e:
            print(f"⚠️ Could not load existing index DB: {e}")

    # Create a set of already indexed asset_ids for quick lookup
    existing_asset_ids = {item['asset_id'] for item in indexed_map}

    print(f"🔗 Binding {len(assets)} assets to Index...")
    
    new_bindings_count = 0
    for item in assets:
        if item['asset_id'] in existing_asset_ids:
            print(f"   ⏭️  Skipping {item['filename']} (Already indexed)")
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
            
            # Save incrementally
            with open(Config.INDEX_DB, "w") as f:
                json.dump(indexed_map, f, indent=2)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

    print(f"\n✅ Indexing Complete. {new_bindings_count} new assets bound. Map saved to {Config.INDEX_DB}")

if __name__ == "__main__":
    index_assets()