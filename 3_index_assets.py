"""
Step 3: Index Uploaded Assets with Twelve Labs AI Models
=========================================================
Creates an Index using Marengo 2.7 (visual+audio) and Pegasus 1.2 (visual+audio),
then binds all uploaded video chunks to it.

These models enable BOTH audio transcription AND visual screen analysis.

Output: data/index_map.json
"""

import json
import time
from twelvelabs import TwelveLabs
from config import Config
import os


def index_assets():
    client = TwelveLabs(api_key=Config.API_KEY)

    # 1. Load Assets
    if not os.path.exists(Config.ASSETS_DB):
        print("[ERROR] Assets DB missing. Run script #2 first.")
        return
    with open(Config.ASSETS_DB, "r") as f:
        assets = json.load(f)

    if not assets:
        print("[ERROR] No assets found. Check script #2 output.")
        return

    # 2. Get or Create Index
    target_index = None

    # Try configured INDEX_ID first (if not empty)
    idx_id = getattr(Config, "INDEX_ID", "")
    if idx_id and idx_id.strip():
        try:
            target_index = client.indexes.retrieve(idx_id)
            print(f"  [OK] Using configured Index: {target_index.id} ('{target_index.index_name}')")
        except Exception as e:
            print(f"  [WARN] Configured INDEX_ID not found: {e}")
            print(f"         Will search for or create '{Config.INDEX_NAME}' instead.")

    # Search for existing index by name
    if not target_index:
        try:
            for idx in client.indexes.list():
                if getattr(idx, "index_name", "") == Config.INDEX_NAME:
                    target_index = idx
                    print(f"  [OK] Found existing Index: {idx.id} ('{Config.INDEX_NAME}')")
                    break
        except Exception as e:
            print(f"  [WARN] Could not search indexes: {e}")

    # Create new index if needed
    if not target_index:
        print(f"  [NEW] Creating Index '{Config.INDEX_NAME}'...")
        print(f"        Models: Marengo 2.7 (visual+audio) + Pegasus 1.2 (visual+audio)")
        target_index = client.indexes.create(
            index_name=Config.INDEX_NAME,
            models=[
                {"model_name": "marengo2.7", "model_options": ["visual", "audio"]},
                {"model_name": "pegasus1.2", "model_options": ["visual", "audio"]}
            ]
        )
        print(f"  [OK] Created Index: {target_index.id}")
        print(f"       TIP: Save this in config.py: INDEX_ID = \"{target_index.id}\"")

    # 3. Check what's already indexed
    print(f"\n  Checking index contents...")
    remote_indexed_video_ids = {}
    asset_id_to_filename = {item['asset_id']: item['filename'] for item in assets}

    try:
        indexed_assets = client.indexes.indexed_assets.list(index_id=target_index.id)
        for val in indexed_assets:
            if hasattr(val, 'asset_id') and val.asset_id in asset_id_to_filename:
                fname = asset_id_to_filename[val.asset_id]
                remote_indexed_video_ids[fname] = val.id
        print(f"  Found {len(remote_indexed_video_ids)} assets already indexed.")
    except Exception as e:
        print(f"  [WARN] Could not verify index contents: {e}")

    # 4. Build index map from known state
    indexed_map = []
    for fname, vid_id in remote_indexed_video_ids.items():
        aid = next((a['asset_id'] for a in assets if a['filename'] == fname), None)
        if aid:
            indexed_map.append({
                "filename": fname,
                "video_id": vid_id,
                "asset_id": aid
            })

    # 5. Index new assets
    print(f"\n  Binding {len(assets)} assets to Index...")
    new_bindings_count = 0

    for item in assets:
        if item['filename'] in remote_indexed_video_ids:
            print(f"    [OK] {item['filename']} already indexed")
            continue

        print(f"    Indexing {item['filename']}...", end="", flush=True)
        try:
            ia = client.indexes.indexed_assets.create(
                index_id=target_index.id,
                asset_id=item['asset_id']
            )

            wait_start = time.time()
            while True:
                status = client.indexes.indexed_assets.retrieve(
                    index_id=target_index.id,
                    indexed_asset_id=ia.id
                ).status
                if status == "ready":
                    elapsed = int(time.time() - wait_start)
                    print(f" Ready! ({elapsed}s)")
                    break
                elif status == "failed":
                    print(" FAILED!")
                    break
                time.sleep(2)

            indexed_map.append({
                "filename": item['filename'],
                "video_id": ia.id,
                "asset_id": item['asset_id']
            })
            new_bindings_count += 1

        except Exception as e:
            print(f"\n    [ERROR] {e}")

    # 6. Save map
    indexed_map.sort(key=lambda x: x['filename'])
    with open(Config.INDEX_DB, "w") as f:
        json.dump(indexed_map, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  INDEXING COMPLETE")
    print(f"    New indexed: {new_bindings_count}")
    print(f"    Total:       {len(indexed_map)}")
    print(f"    Index ID:    {target_index.id}")
    print(f"    Output:      {Config.INDEX_DB}")
    print(f"{'='*60}")


if __name__ == "__main__":
    index_assets()
