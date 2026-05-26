<div align="center">

# 🚦 Traffic Sign Classifier

### Real-Time CNN-Powered Traffic Sign Detection & Classification

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![Render](https://img.shields.io/badge/Render-Backend-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com)
[![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/dhananjaybamhande/traffic-sign-cnn)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**No API key. No cloud AI. Fully offline CNN inference. Smart NLP driver alerts.**

[🚀 Live Demo](https://traffic-sign-app.vercel.app) · [🤖 Model on HuggingFace](https://huggingface.co/dhananjaybamhande/traffic-sign-cnn) · [📖 API Docs](https://traffic-sign-app-dm8o.onrender.com/docs)

![Traffic Sign Classifier Demo](https://raw.githubusercontent.com/dhananjay0911/traffic-sign-app/main/assets/demo.png)

</div>

---

## 📌 What This Project Does

Upload any dashcam or road video — the app analyzes every frame using a **locally trained Convolutional Neural Network**, detects traffic signs in real time, and displays:

- ✅ The detected sign name with confidence percentage
- 🎨 Color-coded urgency level (red for danger, amber for caution, blue for info)
- 💬 Smart driver instruction generated per detection
- 📊 Top-3 alternative predictions with confidence bars
- 🚦 Live banner that updates with every new frame
- 🔖 Browser tab icon and title that changes to the detected sign

**Everything runs locally — zero external AI APIs, zero cost per inference.**

---

## 🛠 Tech Stack

### Machine Learning & Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **TensorFlow** | 2.15.1 | CNN training and inference engine |
| **Keras** | 2.15.0 | High-level neural network API |
| **NumPy** | 1.26.4 | Array operations and preprocessing |
| **Pillow** | 10.3.0 | Image loading, resizing, conversion |
| **FastAPI** | 0.111.0 | High-performance REST API server |
| **Uvicorn** | 0.29.0 | ASGI server with async support |
| **Pydantic** | 2.7.1 | Data validation and serialization |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **React** | 18.3 | Component-based UI framework |
| **Vite** | 5.4 | Ultra-fast frontend build tool |
| **CSS Variables** | — | Dynamic theming and glassmorphism UI |

### Deployment & Infrastructure
| Service | Purpose |
|---------|---------|
| **Render** | Backend hosting (Python, FastAPI) |
| **Vercel** | Frontend hosting (React, Vite) |
| **HuggingFace Hub** | Trained model storage and delivery |
| **GitHub** | Version control and CI/CD trigger |

### Dataset
| Detail | Info |
|--------|------|
| **Dataset** | GTSRB — German Traffic Sign Recognition Benchmark |
| **Classes** | 43 traffic sign categories |
| **Training images** | 39,209 |
| **Test images** | 12,630 |
| **Source** | Institut für Neuroinformatik, Ruhr-Universität Bochum |

---

## 🧠 CNN Architecture

Custom architecture inspired by **LeNet** and **VGG** design principles, built from scratch using TensorFlow/Keras:

```
Input: 32 × 32 × 3 (RGB image)
│
├── Block 1: Conv2D(32, 3×3) → BatchNormalization → MaxPooling2D(2×2)
├── Block 2: Conv2D(64, 3×3) → BatchNormalization → MaxPooling2D(2×2)
├── Block 3: Conv2D(128, 3×3) → BatchNormalization → MaxPooling2D(2×2)
│
├── Flatten → Dense(512, ReLU) → Dropout(0.5)
└── Dense(43, Softmax) → 43 class probabilities
```

| Metric | Value |
|--------|-------|
| Total Parameters | 1,165,291 |
| Trainable Parameters | 1,164,843 |
| Model Size | ~14 MB |
| Test Accuracy | ~95% on GTSRB |
| Inference Latency | ~50ms per frame (CPU) |
| Input Shape | (32, 32, 3) |
| Output | 43-class softmax probabilities |

### Training Configuration
- **Optimizer:** Adam (lr=0.001) with ReduceLROnPlateau
- **Loss:** Sparse Categorical Crossentropy
- **Epochs:** Up to 30 with Early Stopping (patience=6)
- **Batch Size:** 64
- **Augmentation:** Random brightness, contrast, horizontal flip
- **Regularization:** Batch Normalization + Dropout(0.5)

---

## 🚦 43 Traffic Sign Classes Supported

| Category | Signs |
|----------|-------|
| **Speed Limits** | 20, 30, 50, 60, 70, 80, 100, 120 km/h |
| **End of Limits** | End of 80 km/h, End of all restrictions |
| **Prohibitory** | No passing, No passing for trucks, No vehicles, No trucks, No entry |
| **Mandatory** | Turn right/left ahead, Ahead only, Keep right/left, Roundabout |
| **Warning** | Curves, Bumpy road, Slippery road, Road narrows, Road work, Traffic signals, Pedestrians, Children, Bicycles, Ice/snow, Wild animals |
| **Priority** | Right of way at intersection, Priority road, Yield, Stop |

---

## ✨ Key Features

### 🎯 Real-Time CNN Inference
- Processes video frames every 1–10 seconds (user-controlled interval)
- ~50ms latency per frame on CPU
- Confidence threshold at 55% — only reports high-confidence detections
- Top-3 predictions shown for every frame with confidence bars

### 💡 Smart NLP Driver Alerts
- Unique instruction generated per detection based on sign type + confidence level
- 4 confidence tiers: ⚡ Confirmed (>95%) / ✅ Detected (80-95%) / ⚠️ Likely (60-80%) / ❓ Possible (<60%)
- Color-coded urgency: 🛑 Stop Now / ⛔ Prohibited / 🐢 Slow Down / 🚧 Road Work / ⚠️ Caution / 👑 Priority Road
- Zero API cost — all logic runs locally in the browser

### 🎨 Dynamic UI
- Live advice banner updates with every detected frame
- Browser tab icon and title change to show current sign (e.g. `👑 Priority road (99.6%) — CNN`)
- Animated glassmorphism background with smooth gradient transitions
- Frame thumbnail strip with green highlight on detected frames
- Fully responsive — works on desktop and mobile

### 🔒 Fully Offline Inference
- CNN model runs entirely on the server — no third-party AI APIs
- No Gemini, no OpenAI, no Claude API for classification
- Works without internet after initial load

---

## 🗂 Project Structure

```
traffic-sign-app/
│
├── backend/                        ← Python / FastAPI
│   ├── model.py                    ← CNN architecture definition
│   ├── train.py                    ← Training script (GTSRB dataset)
│   ├── main.py                     ← FastAPI REST API server
│   ├── download_model.py           ← Auto-downloads model from HuggingFace
│   ├── requirements.txt            ← Python dependencies
│   ├── runtime.txt                 ← Python 3.11 for Render
│   ├── pyrightconfig.json          ← VS Code type checking config
│   ├── data/                       ← GTSRB dataset (not in git, 300 MB)
│   └── models/                     ← Trained model (not in git, on HuggingFace)
│
├── frontend/                       ← React / Vite
│   ├── index.html                  ← Entry HTML with dynamic tab title
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   │   └── favicon.svg             ← Traffic sign SVG favicon
│   └── src/
│       ├── App.jsx                 ← Main app + NLP logic + 43-class advice
│       ├── App.css                 ← Glassmorphism UI styles
│       └── main.jsx
│
├── render.yaml                     ← Render deployment config
├── .gitignore                      ← Excludes dataset, model, node_modules
├── LICENSE
└── README.md
```

---

## 🚀 Live Deployment

| Service | URL | Platform |
|---------|-----|---------|
| 🌐 Frontend | https://traffic-sign-app.vercel.app | Vercel |
| ⚙️ Backend API | https://traffic-sign-app-dm8o.onrender.com | Render |
| 📖 API Docs | https://traffic-sign-app-dm8o.onrender.com/docs | Swagger UI |
| 🤖 CNN Model | https://huggingface.co/dhananjaybamhande/traffic-sign-cnn | HuggingFace |

> **Note:** Backend is on Render free tier — wakes up in ~30 seconds after 15 min idle. Frontend shows "Backend Offline" briefly then switches to "CNN Ready".

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service status and info |
| `GET` | `/health` | Model readiness check |
| `POST` | `/classify` | Classify a video frame |
| `GET` | `/classes` | All 43 class labels |
| `GET` | `/model-info` | Model architecture info |

### POST /classify — Request
```json
{
  "image_base64": "<base64 encoded JPEG>",
  "frame_number": 1
}
```

### POST /classify — Response
```json
{
  "sign_detected": true,
  "latency_ms": 48,
  "top_prediction": {
    "class_id": 12,
    "label": "Priority road",
    "confidence": 0.996
  },
  "top3": [
    { "class_id": 12, "label": "Priority road",  "confidence": 0.996 },
    { "class_id": 17, "label": "No entry",        "confidence": 0.003 },
    { "class_id":  9, "label": "No passing",      "confidence": 0.001 }
  ],
  "threshold": 0.55,
  "model": "CNN (GTSRB — offline)"
}
```

---

## 💻 Local Setup

### Requirements
| Tool | Version |
|------|---------|
| Python | 3.9–3.11 (from python.org — NOT Microsoft Store) |
| Node.js | 18+ |
| npm | 9+ |
| Disk | ~2 GB for dataset + model |

### 1. Clone
```bash
git clone https://github.com/dhananjay0911/traffic-sign-app.git
cd traffic-sign-app
```

### 2. Install backend packages
```bash
cd backend
pip install -r requirements.txt
```

### 3. Download GTSRB Dataset
**Option A — Kaggle (free account):**
https://www.kaggle.com/datasets/meowmeowmeowmeowmeow/gtsrb-german-traffic-sign

**Option B — Direct download (no login):**
- Training: https://sid.erda.dk/public/archives/daaeac0d503fb0c59d4c9c07a71a39ba/GTSRB_Final_Training_Images.zip
- Test images: https://sid.erda.dk/public/archives/daaeac0d503fb0c59d4c9c07a71a39ba/GTSRB_Final_Test_Images.zip
- Test labels: https://sid.erda.dk/public/archives/daaeac0d503fb0c59d4c9c07a71a39ba/GTSRB_Final_Test_GT.zip

Place extracted files in:
```
backend/data/
  Train/  0/ 1/ 2/ ... 42/
  Test/
    Images/
    GT-final_test.csv
```

### 4. Train the CNN (once, ~20–40 min on CPU)
```bash
python train.py
```

### 5. Start backend
```bash
python main.py
```

### 6. Start frontend
```bash
cd ../frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| Training samples | 39,209 |
| Test accuracy | ~95% |
| Confidence threshold | 55% |
| Inference speed | ~50ms/frame (CPU) |
| Model file size | 14.1 MB |
| Parameters | 1,165,291 |

---

## 🏗 What I Built & Learned

- Designed and trained a **custom CNN from scratch** — no pre-trained model used
- Implemented **3-block Conv architecture** with BatchNorm and Dropout regularization
- Built a complete **REST API** with FastAPI serving real-time CNN predictions
- Created a **React frontend** with live video frame capture using Canvas API
- Implemented **confidence-aware NLP alerts** — 4 tiers with 9 urgency categories covering all 43 signs
- Solved **cross-version Keras compatibility** issues for cloud deployment
- Deployed **full-stack ML application** across Render + Vercel + HuggingFace
- Automated **model download from HuggingFace** during Render build step
- Built **dynamic browser tab updates** — tab icon and title change per detected sign
- Achieved **~50ms inference latency** on CPU with no GPU required

---

## 🙏 Credits

- **GTSRB Dataset:** Institut für Neuroinformatik, Ruhr-Universität Bochum, Germany
- **Paper:** Stallkamp et al., "The German Traffic Sign Recognition Benchmark: A multi-class classification competition", IJCNN 2011
- **Model Hosting:** HuggingFace Hub

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built with ❤️ by [Dhananjay Bamhande](https://github.com/dhananjay0911)**

⭐ Star this repo if you found it useful!

</div>