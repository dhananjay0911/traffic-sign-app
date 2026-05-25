"""
download_model.py — Downloads trained model from Google Drive on startup.

Set environment variable in Render:
    GDRIVE_FILE_ID = 1ysN53DVU5PkKmZ6r4M6M7Rb7wEE5U_Rb
"""

import os
import sys
from pathlib import Path

MODEL_DIR  = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "traffic_sign_cnn.keras"


def download():
    MODEL_DIR.mkdir(exist_ok=True)

    if MODEL_PATH.exists():
        size = MODEL_PATH.stat().st_size
        if size > 1_000_000:   # at least 1 MB — valid model
            print(f"[OK] Model already present ({size/1024/1024:.1f} MB)")
            return True
        else:
            print(f"[WARN] Model file too small ({size} bytes) — re-downloading")
            MODEL_PATH.unlink()

    file_id = os.environ.get("GDRIVE_FILE_ID", "").strip()
    if not file_id:
        print("[WARN] GDRIVE_FILE_ID not set — model will not be downloaded.")
        print("       Set it in Render: Environment → GDRIVE_FILE_ID = your_file_id")
        return False

    print(f"[INFO] Downloading model from Google Drive (ID: {file_id}) ...")

    try:
        import requests

        # Step 1: try direct download
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        session = requests.Session()
        r = session.get(url, stream=True, timeout=120)

        # Step 2: handle Google's virus-scan confirmation page for large files
        token = None
        for key, val in r.cookies.items():
            if "download_warning" in key or "download_warning" in val:
                token = val
                break

        # Also check response content for confirmation token
        if not token and r.headers.get("Content-Type", "").startswith("text"):
            content = r.text
            import re
            match = re.search(r'confirm=([0-9A-Za-z_\-]+)', content)
            if match:
                token = match.group(1)

        if token:
            print(f"[INFO] Large file — using confirmation token ...")
            url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={token}"
            r = session.get(url, stream=True, timeout=180)

        # Step 3: write file
        r.raise_for_status()
        total = 0
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)

        size = MODEL_PATH.stat().st_size
        if size < 1_000_000:
            MODEL_PATH.unlink()
            print(f"[ERROR] Downloaded file too small ({size} bytes) — likely an HTML error page.")
            print("        Check your GDRIVE_FILE_ID and that sharing is set to 'Anyone with link'.")
            return False

        print(f"[OK] Model downloaded successfully ({size/1024/1024:.1f} MB) → {MODEL_PATH}")
        return True

    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        return False


if __name__ == "__main__":
    ok = download()
    sys.exit(0 if ok else 1)