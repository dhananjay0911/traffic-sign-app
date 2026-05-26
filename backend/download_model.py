import sys
from pathlib import Path
import requests

MODEL_DIR  = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "traffic_sign_cnn.keras"
URL = "https://huggingface.co/dhananjaybamhande/traffic-sign-cnn/resolve/main/traffic_sign_cnn.keras"

def download():
    MODEL_DIR.mkdir(exist_ok=True)
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 1_000_000:
        print(f"[OK] Model already present ({MODEL_PATH.stat().st_size/1e6:.1f} MB)")
        return True
    print(f"[INFO] Downloading from HuggingFace...")
    try:
        r = requests.get(URL, stream=True, timeout=300)
        r.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        size = MODEL_PATH.stat().st_size
        if size < 1_000_000:
            MODEL_PATH.unlink()
            print(f"[ERROR] File too small: {size} bytes")
            return False
        print(f"[OK] Downloaded {size/1e6:.1f} MB")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if download() else 1)