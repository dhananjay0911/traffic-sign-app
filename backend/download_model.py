"""
download_model.py — Downloads model from Hugging Face (reliable, no blocking).
Set MODEL_URL environment variable in Render to your HuggingFace direct link.
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

    url = os.environ.get("MODEL_URL", "").strip()
    if not url:
        print("[ERROR] MODEL_URL environment variable not set.")
        print("  1. Upload traffic_sign_cnn.keras to huggingface.co (free)")
        print("  2. Set MODEL_URL = https://huggingface.co/USER/REPO/resolve/main/traffic_sign_cnn.keras")
        return False

    print(f"[INFO] Downloading model from: {url}")
    try:
        import requests
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            written = 0
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        written += len(chunk)
                        if total:
                            pct = written / total * 100
                            print(f"\r[INFO] {written/1e6:.1f} MB / {total/1e6:.1f} MB ({pct:.0f}%)", end="", flush=True)
            print()

        size = MODEL_PATH.stat().st_size
        if size < 1_000_000:
            MODEL_PATH.unlink()
            print(f"[ERROR] Downloaded file too small ({size} bytes) — bad URL?")
            return False

        print(f"[OK] Model downloaded: {size/1e6:.1f} MB → {MODEL_PATH}")
        return True

    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        return False


if __name__ == "__main__":
    ok = download()
    sys.exit(0 if ok else 1)