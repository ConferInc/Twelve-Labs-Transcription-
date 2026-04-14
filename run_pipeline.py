"""
StoneFactory Meeting Analysis - Full Pipeline Runner
=====================================================
Runs all 5 steps in sequence with resume capability.

Usage:
    python run_pipeline.py                    # Full pipeline
    python run_pipeline.py --skip-split       # Skip step 1
    python run_pipeline.py --skip-upload      # Skip steps 1-2
    python run_pipeline.py --skip-index       # Skip steps 1-3
    python run_pipeline.py --analyze-only     # Only step 4
    python run_pipeline.py --report-only      # Only step 5
    python run_pipeline.py --fast             # Lightweight prompt
"""

import sys
import time
import os
import importlib


def run_step(step_num, name, module_name, func_name):
    """Run a pipeline step."""
    print(f"\n{'#'*60}")
    print(f"# STEP {step_num}: {name}")
    print(f"{'#'*60}\n")

    start = time.time()
    try:
        mod = importlib.import_module(module_name)
        importlib.reload(mod)  # Ensure fresh config
        getattr(mod, func_name)()
        elapsed = int(time.time() - start)
        print(f"\n  Step {step_num} completed in {elapsed}s")
        return True
    except Exception as e:
        elapsed = int(time.time() - start)
        print(f"\n  Step {step_num} FAILED after {elapsed}s: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    args = sys.argv[1:]

    print("=" * 60)
    print("  STONEFACTORY ERP - MEETING ANALYSIS PIPELINE")
    print("=" * 60)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    steps = [
        (1, "Split Video into Chunks", "1_split_video", "split_video"),
        (2, "Upload Chunks to Twelve Labs", "2_upload_assets", "upload_assets"),
        (3, "Index with AI Models", "3_index_assets", "index_assets"),
        (4, "Analyze Video Content", "4_analyze_video", "analyze"),
        (5, "Format Requirements Report", "5_format_report", "generate_report"),
    ]

    start_step = 1
    end_step = 5
    if "--skip-split" in args:
        start_step = 2
    if "--skip-upload" in args:
        start_step = 3
    if "--skip-index" in args:
        start_step = 4
    if "--analyze-only" in args:
        start_step = 4
        end_step = 4
    if "--report-only" in args:
        start_step = 5
        end_step = 5

    steps = [s for s in steps if start_step <= s[0] <= end_step]

    print(f"\nRunning steps: {', '.join(str(s[0]) for s in steps)}")
    if "--fast" in args or "--lightweight" in args:
        print("  Using lightweight prompt mode")

    pipeline_start = time.time()

    for step_num, name, module, func in steps:
        success = run_step(step_num, name, module, func)
        if not success and step_num < 5:
            print(f"\n  Pipeline stopped at step {step_num}.")
            print(f"  Use --skip-split/--skip-upload/--skip-index to resume.")
            sys.exit(1)

    total = int(time.time() - pipeline_start)
    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE in {total // 60}m {total % 60}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
