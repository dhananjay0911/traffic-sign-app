"""
download_model.py

Run this ONCE after deploying to Render to upload your trained model.
The model file is too large for git so it must be uploaded separately.

Option A — Google Drive (recommended):
  1. Upload backend/models/traffic_sign_cnn.keras to Google Drive
  2. Share it: right-click → Share → Anyone with link → Viewer
  3. Copy the file ID from the URL:
     https://drive.google.com/file/d/FILE_ID_HERE/view
  4. Set GDRIVE_FILE_ID environment variable in Render dashboard
  5. Render will auto-download on startup

Option B — Direct URL:
  Set MODEL_URL environment variable in Render to any direct download link.
"""

import os
import sys
from pathlib import Path

MODEL_DIR  = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "traffic_sign_cnn.keras"

def download():
    MODEL_DIR.mkdir(exist_ok=True)

    if MODEL_PATH.exists():
        print(f"[OK] Model already present at {MODEL_PATH}")
        return True

    # Option A: Google Drive
    file_id = os.environ.get("GDRIVE_FILE_ID", "")
    if file_id:
        print(f"[INFO] Downloading model from Google Drive (ID: {file_id}) ...")
        try:
            import requests
            url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
            r = requests.get(url, stream=True, timeout=120)
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    f.write(chunk)
            size = MODEL_PATH.stat().st_size / 1024 / 1024
            print(f"[OK] Model downloaded ({size:.1f} MB) → {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"[ERROR] Google Drive download failed: {e}")
            return False

    # Option B: Direct URL
    url = os.environ.get("MODEL_URL", "")
    if url:
        print(f"[INFO] Downloading model from {url} ...")
        try:
            import requests
            r = requests.get(url, stream=True, timeout=120)
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    f.write(chunk)
            size = MODEL_PATH.stat().st_size / 1024 / 1024
            print(f"[OK] Model downloaded ({size:.1f} MB) → {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"[ERROR] Direct URL download failed: {e}")
            return False

    print("[WARN] No model found and no GDRIVE_FILE_ID or MODEL_URL set.")
    print("       Set one of these in Render Environment Variables.")
    return False

if __name__ == "__main__":
    ok = download()
    sys.exit(0 if ok else 1)
