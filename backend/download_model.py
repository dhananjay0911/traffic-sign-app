"""
download_model.py — Downloads model using gdown (most reliable for Google Drive).
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

    file_id = os.environ.get("GDRIVE_FILE_ID", "").strip()
    if not file_id:
        print("[ERROR] GDRIVE_FILE_ID not set in environment variables.")
        return False

    print(f"[INFO] Downloading model via gdown (ID: {file_id}) ...")
    try:
        import gdown
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, str(MODEL_PATH), quiet=False, fuzzy=True)

        if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
            print(f"[OK] Downloaded {MODEL_PATH.stat().st_size/1e6:.1f} MB → {MODEL_PATH}")
            return True
        else:
            print("[ERROR] Download failed — file too small or missing.")
            return False
    except Exception as e:
        print(f"[ERROR] gdown failed: {e}")
        return False


if __name__ == "__main__":
    ok = download()
    sys.exit(0 if ok else 1)