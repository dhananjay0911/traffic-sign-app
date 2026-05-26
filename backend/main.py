"""
main.py — Traffic Sign Classifier  (FastAPI + local CNN)

No API key. No internet needed after training. Fully offline.

Run:
    python main.py

Requires model to be trained first:
    python train.py
"""

import io
import base64
import time
import multiprocessing
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────────
MODEL_PATH = Path(__file__).parent / "models" / "traffic_sign_cnn.h5"
IMG_SIZE   = 32
THRESHOLD  = 0.55   # minimum softmax confidence to report a detection

# ── Load model at startup ────────────────────────────────────────────────────
# ── Auto-download model if not present (runs on Render and locally) ──────────
import os as _os
if not (Path(__file__).parent / "models" / "traffic_sign_cnn.h5").exists():
    try:
        from download_model import download
        download()
    except Exception as _e:
        print(f"[WARN] Model auto-download failed: {_e}")

model = None

def load_model():
    global model
    if not MODEL_PATH.exists():
        print("\n" + "=" * 55)
        print("  [WARN] No trained model found!")
        print(f"  Expected: {MODEL_PATH}")
        print("  Run:  python train.py   (one-time, ~20-40 min)")
        print("=" * 55 + "\n")
        return
    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")

    # Method 1: standard load
    try:
        model = tf.keras.models.load_model(str(MODEL_PATH))
        print(f"[OK] Model loaded  input={model.input_shape}  params={model.count_params():,}")
        return
    except Exception as e1:
        print(f"[WARN] Standard load failed: {e1}")

    # Method 2: compile=False (fixes Keras version mismatch)
    try:
        model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        print(f"[OK] Model loaded (compile=False)  input={model.input_shape}  params={model.count_params():,}")
        return
    except Exception as e2:
        print(f"[WARN] compile=False failed: {e2}")

    # Method 3: rebuild architecture + load weights only
    try:
        from model import build_cnn
        rebuilt = build_cnn(num_classes=43, input_shape=(32, 32, 3))
        rebuilt.load_weights(str(MODEL_PATH))
        model = rebuilt
        print(f"[OK] Model loaded via weights  input={model.input_shape}  params={model.count_params():,}")
        return
    except Exception as e3:
        print(f"[ERROR] All load methods failed: {e3}")

    # Method 4: load h5 with legacy format
    try:
        import h5py
        model = tf.keras.models.load_model(str(MODEL_PATH), compile=False,
                                           options=tf.saved_model.LoadOptions())
        print(f"[OK] Model loaded via legacy h5")
        return
    except Exception as e4:
        print(f"[ERROR] Legacy h5 failed: {e4}")

load_model()

# ── GTSRB class labels (43 classes) ─────────────────────────────────────────
CLASSES = {
     0: "Speed limit (20 km/h)",     1: "Speed limit (30 km/h)",
     2: "Speed limit (50 km/h)",     3: "Speed limit (60 km/h)",
     4: "Speed limit (70 km/h)",     5: "Speed limit (80 km/h)",
     6: "End of speed limit (80 km/h)", 7: "Speed limit (100 km/h)",
     8: "Speed limit (120 km/h)",    9: "No passing",
    10: "No passing (trucks)",      11: "Right-of-way at intersection",
    12: "Priority road",            13: "Yield",
    14: "Stop",                     15: "No vehicles",
    16: "No trucks",                17: "No entry",
    18: "General caution",          19: "Dangerous curve left",
    20: "Dangerous curve right",    21: "Double curve",
    22: "Bumpy road",               23: "Slippery road",
    24: "Road narrows right",       25: "Road work",
    26: "Traffic signals",          27: "Pedestrians",
    28: "Children crossing",        29: "Bicycles crossing",
    30: "Beware of ice / snow",     31: "Wild animals crossing",
    32: "End of all limits",        33: "Turn right ahead",
    34: "Turn left ahead",          35: "Ahead only",
    36: "Go straight or right",     37: "Go straight or left",
    38: "Keep right",               39: "Keep left",
    40: "Roundabout mandatory",     41: "End of no passing",
    42: "End no passing (trucks)",
}

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(title="Traffic Sign Classifier — CNN", version="1.0.0")

# Allow all origins — includes Vercel preview URLs and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FrameRequest(BaseModel):
    image_base64: str
    frame_number: int = 0


def preprocess(img_bytes: bytes) -> np.ndarray:
    """Decode image bytes, resize to 32×32, normalise to [0, 1]."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)   # (1, 32, 32, 3)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "api":    "Traffic Sign Classifier (CNN — no API key)",
        "model":  "GTSRB CNN — LeNet/VGG style",
        "status": "ready" if model else "no_model",
        "hint":   "Run python train.py first" if not model else "Model loaded OK",
        "docs":   "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status":  "ok" if model else "no_model",
        "model":   MODEL_PATH.name if MODEL_PATH.exists() else "not_trained",
        "classes": len(CLASSES),
        "ready":   model is not None,
    }


@app.post("/classify")
async def classify(req: FrameRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="MODEL_NOT_READY|Run python train.py first to train the CNN model.",
        )

    t0 = time.time()
    try:
        img_bytes = base64.b64decode(req.image_base64)
        inp       = preprocess(img_bytes)

        preds    = model.predict(inp, verbose=0)[0]   # shape: (43,)
        top3_idx = np.argsort(preds)[-3:][::-1]

        predictions = [
            {
                "class_id":   int(i),
                "label":      CLASSES.get(int(i), f"Class {i}"),
                "confidence": round(float(preds[i]), 4),
            }
            for i in top3_idx
        ]

        top      = predictions[0]
        detected = top["confidence"] >= THRESHOLD
        latency  = round((time.time() - t0) * 1000)

        return {
            "success":        True,
            "frame_number":   req.frame_number,
            "latency_ms":     latency,
            "sign_detected":  detected,
            "top_prediction": top if detected else None,
            "top3":           predictions,
            "threshold":      THRESHOLD,
            "model":          "CNN (GTSRB — offline)",
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/classes")
async def get_classes():
    return {"classes": CLASSES, "total": len(CLASSES)}


@app.get("/model-info")
async def model_info():
    if model is None:
        return {"loaded": False, "message": "Run python train.py to train the model."}
    return {
        "loaded":      True,
        "input_shape": str(model.input_shape),
        "output":      f"{model.output_shape[-1]} classes",
        "params":      model.count_params(),
        "path":        str(MODEL_PATH),
    }


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    multiprocessing.freeze_support()
    import os, uvicorn
    port = int(os.environ.get("PORT", 8000))   # Render injects PORT automatically
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)