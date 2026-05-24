"""
train.py  —  Train the Traffic Sign CNN on GTSRB data.

Place the dataset here:
    backend/data/
        Train/   0/ 1/ 2/ ... 42/    ← class folders with .ppm/.png images
        Test/
            (images anywhere inside)
            GT-final_test.csv

Run:
    python train.py

Output:
    backend/models/traffic_sign_cnn.keras
"""

import os
import sys
import csv
import time
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
from PIL import Image

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATA_DIR    = BASE_DIR / "data"
TRAIN_DIR   = DATA_DIR / "Train"
TEST_DIR    = DATA_DIR / "Test"
TEST_CSV    = TEST_DIR / "GT-final_test.csv"
MODEL_DIR   = BASE_DIR / "models"
MODEL_PATH  = MODEL_DIR / "traffic_sign_cnn.keras"
MODEL_DIR.mkdir(exist_ok=True)

IMG_SIZE    = 32
BATCH_SIZE  = 64
EPOCHS      = 30
NUM_CLASSES = 43


# ── Environment check ────────────────────────────────────────────────────────

def check_environment():
    print("\n" + "=" * 55)
    print("  Environment check")
    print("=" * 55)
    pv = sys.version_info
    print(f"  Python  : {pv.major}.{pv.minor}.{pv.micro}")
    try:
        import numpy as np
        print(f"  NumPy   : {np.__version__}  ✓")
    except ImportError:
        print("  NumPy   : MISSING  →  pip install numpy==1.26.4")
        sys.exit(1)
    try:
        import PIL
        print(f"  Pillow  : {PIL.__version__}  ✓")
    except ImportError:
        print("  Pillow  : MISSING  →  pip install Pillow==10.3.0")
        sys.exit(1)
    try:
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        print(f"  TF      : {tf.__version__}  ✓")
        gpus = tf.config.list_physical_devices("GPU")
        if gpus:
            print(f"  Device  : GPU  ✓")
        else:
            print("  Device  : CPU  (training ~20–40 min)")
    except ImportError:
        print("  TF      : MISSING  →  pip install tensorflow==2.15.1 keras==2.15.0")
        sys.exit(1)
    print("=" * 55 + "\n")


# ── Dataset validation ───────────────────────────────────────────────────────

def check_train_dir():
    if not TRAIN_DIR.exists():
        print(f"\n[ERROR] Train folder not found: {TRAIN_DIR}")
        print("  Download GTSRB and place Train/ inside backend/data/")
        sys.exit(1)
    class_dirs = [d for d in TRAIN_DIR.iterdir() if d.is_dir()]
    if not class_dirs:
        print(f"\n[ERROR] Train/ folder is empty. Expected 43 sub-folders (0–42).")
        sys.exit(1)
    total = sum(
        len(list(d.glob("*.png")) + list(d.glob("*.ppm")) + list(d.glob("*.jpg")))
        for d in class_dirs
    )
    print(f"  ✓  Train/  — {len(class_dirs)} class folders, {total:,} images")
    return total > 0


def find_test_image(filename: str) -> Path | None:
    """
    Search for a test image by trying every possible sub-path under TEST_DIR.
    Handles all known GTSRB extraction layouts:
      Test/Images/xxxxx.ppm
      Test/xxxxx.ppm
      Test/GTSRB/Final_Test/Images/xxxxx.ppm
    """
    # 1. Try the exact relative path from CSV
    p = TEST_DIR / filename
    if p.exists():
        return p

    # 2. Try just the bare filename anywhere in TEST_DIR (recursive)
    bare = Path(filename).name
    for found in TEST_DIR.rglob(bare):
        return found   # return first match

    return None


# ── Image helpers ────────────────────────────────────────────────────────────

def load_image(path: Path) -> np.ndarray:
    img = Image.open(path).convert("RGB").resize(
        (IMG_SIZE, IMG_SIZE), Image.LANCZOS
    )
    return np.array(img, dtype=np.float32) / 255.0


def load_train():
    print("[1/4] Loading training images …")
    X, y = [], []
    class_dirs = sorted([d for d in TRAIN_DIR.iterdir() if d.is_dir()])
    for d in class_dirs:
        cid = int(d.name)
        files = list(d.glob("*.png")) + list(d.glob("*.ppm")) + list(d.glob("*.jpg"))
        for f in files:
            try:
                X.append(load_image(f))
                y.append(cid)
            except Exception:
                pass
    print(f"      {len(X):,} training images loaded")
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def load_test():
    """
    Load test images. Returns (None, None) if test data is unavailable —
    training will proceed without validation in that case.
    """
    if not TEST_CSV.exists():
        print("  [WARN] GT-final_test.csv not found — skipping test set.")
        return None, None

    print("      Loading test images …")
    X, y, missing = [], [], 0

    with open(TEST_CSV, newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            filename = row.get("Filename") or row.get("filename") or ""
            class_id = int(row.get("ClassId") or row.get("classId") or 0)
            p = find_test_image(filename)
            if p is None:
                missing += 1
                continue
            try:
                X.append(load_image(p))
                y.append(class_id)
            except Exception:
                missing += 1

    if missing:
        print(f"      [WARN] {missing} test images not found (path mismatch — harmless)")

    if len(X) == 0:
        print("      [WARN] No test images loaded — training without validation set.")
        return None, None

    print(f"      {len(X):,} test images loaded")
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


# ── tf.data pipelines ────────────────────────────────────────────────────────

def make_dataset(X, y, augment=False, shuffle=False):
    import tensorflow as tf
    ds = tf.data.Dataset.from_tensor_slices((X, y))
    if augment:
        def aug(img, lbl):
            img = tf.image.random_brightness(img, 0.2)
            img = tf.image.random_contrast(img, 0.8, 1.2)
            img = tf.image.random_flip_left_right(img)
            img = tf.clip_by_value(img, 0.0, 1.0)
            return img, lbl
        ds = ds.map(aug, num_parallel_calls=tf.data.AUTOTUNE)
    if shuffle:
        ds = ds.shuffle(5000)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


# ── Main ─────────────────────────────────────────────────────────────────────

def train():
    check_environment()

    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")

    if MODEL_PATH.exists():
        print(f"[OK]  Model already trained → {MODEL_PATH}")
        print("      Delete that file and re-run to retrain.\n")
        return

    print("Checking dataset …")
    check_train_dir()

    X_train, y_train = load_train()
    X_test,  y_test  = load_test()

    has_test = X_test is not None and len(X_test) > 0

    # Split 10% of training data as validation if no test set available
    if not has_test:
        print("      Using 10% of training data as validation set instead.")
        split = int(len(X_train) * 0.9)
        idx   = np.random.permutation(len(X_train))
        X_val, y_val     = X_train[idx[split:]], y_train[idx[split:]]
        X_train, y_train = X_train[idx[:split]], y_train[idx[:split]]
        val_ds = make_dataset(X_val, y_val)
    else:
        val_ds = make_dataset(X_test, y_test)

    train_ds = make_dataset(X_train, y_train, augment=True, shuffle=True)

    print("\n[2/4] Building CNN …")
    from model import build_cnn
    model = build_cnn(num_classes=NUM_CLASSES, input_shape=(IMG_SIZE, IMG_SIZE, 3))
    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(MODEL_PATH),
            save_best_only=True,
            monitor="val_accuracy",
            verbose=1,
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=6,
            restore_best_weights=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print(f"\n[3/4] Training — up to {EPOCHS} epochs …")
    t0 = time.time()
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )
    mins = (time.time() - t0) / 60

    print(f"\n[4/4] Done in {mins:.1f} min")
    best = tf.keras.models.load_model(str(MODEL_PATH))
    loss, acc = best.evaluate(val_ds, verbose=0)
    print(f"  Validation accuracy : {acc * 100:.2f}%")
    print(f"  Validation loss     : {loss:.4f}")
    print(f"\n  Model saved → {MODEL_PATH}")
    print("  Next:  python main.py")


if __name__ == "__main__":
    train()
