"""
download_model.py — Downloads model from Google Drive using gdown.
"""
import os
import sys
from pathlib import Path

MODEL_DIR  = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "traffic_sign_cnn.keras"


def download():
    MODEL_DIR.mkdir(exist_ok=True)

    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        print(f"[OK] Model already present ({MODEL_PATH.stat().st_size/1e6:.1f} MB)")
        return True

    # Accept either just the ID or a full URL — extract ID either way
    raw = os.environ.get("GDRIVE_FILE_ID", "").strip()
    if not raw:
        print("[ERROR] GDRIVE_FILE_ID not set.")
        return False

    # Extract pure file ID from full URL if user pasted the whole link
    import re
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", raw)
    file_id = match.group(1) if match else raw
    print(f"[INFO] File ID: {file_id}")

    try:
        import gdown
        url = f"https://drive.google.com/uc?id={file_id}"
        print(f"[INFO] Downloading via gdown ...")
        # gdown 6.x removed 'fuzzy' — use output path directly
        result = gdown.download(url, str(MODEL_PATH), quiet=False)

        if result and MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
            print(f"[OK] Downloaded {MODEL_PATH.stat().st_size/1e6:.1f} MB")
            return True
        else:
            print("[ERROR] File too small or download returned None.")
            return False

    except Exception as e:
        print(f"[ERROR] gdown failed: {e}")
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        return False


if __name__ == "__main__":
    ok = download()
    sys.exit(0 if ok else 1)