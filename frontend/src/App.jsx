import { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const API  = import.meta.env.VITE_API_URL || "http://localhost:8000";
const EXTS = new Set(["mp4","webm","mov","avi","mkv","m4v","wmv","flv","ogv","ts","3gp"]);
const isVideo = f => f && (f.type.startsWith("video/") || EXTS.has(f.name.split(".").pop().toLowerCase()));

const SIGN_ADVICE = {
   0: { icon:"🐢", color:"#4dd9b8", urgency:"slowdown", msg:"Speed Limit 20 km/h — Slow zone ahead, reduce speed immediately." },
   1: { icon:"🐢", color:"#4dd9b8", urgency:"slowdown", msg:"Speed Limit 30 km/h — Residential or school zone, keep speed at 30 km/h." },
   2: { icon:"🚙", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 50 km/h — Urban road limit, do not exceed 50 km/h." },
   3: { icon:"🚙", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 60 km/h — Maintain speed at or below 60 km/h." },
   4: { icon:"🚙", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 70 km/h — Stay within 70 km/h on this road." },
   5: { icon:"🚙", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 80 km/h — Rural road limit, do not exceed 80 km/h." },
   6: { icon:"✅", color:"#7ddf6a", urgency:"clear",    msg:"End of 80 km/h Zone — Speed restriction lifted, resume normal speed." },
   7: { icon:"🏎️", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 100 km/h — Expressway limit, stay at or below 100 km/h." },
   8: { icon:"🏎️", color:"#ffb84d", urgency:"limit",    msg:"Speed Limit 120 km/h — Motorway limit, monitor speed carefully." },
   9: { icon:"🚫", color:"#ff6b6b", urgency:"prohibit", msg:"No Passing — Overtaking prohibited on this stretch, stay behind." },
  10: { icon:"🚛", color:"#ff6b6b", urgency:"prohibit", msg:"No Passing for Trucks — Heavy vehicles must not overtake here." },
  11: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Right of Way at Intersection — You have priority, watch for crossing traffic." },
  12: { icon:"👑", color:"#6eb6ff", urgency:"priority", msg:"Priority Road — You have right of way, side road traffic must yield to you." },
  13: { icon:"⛔", color:"#ff6b6b", urgency:"prohibit", msg:"Yield / Give Way — Let all oncoming traffic pass before you proceed." },
  14: { icon:"🛑", color:"#ff2222", urgency:"stop",     msg:"STOP Sign — Come to a complete stop, check all sides before moving." },
  15: { icon:"🚫", color:"#ff6b6b", urgency:"prohibit", msg:"No Vehicles — Road closed to all motor vehicles, find alternate route." },
  16: { icon:"🚛", color:"#ff6b6b", urgency:"prohibit", msg:"No Trucks — Heavy vehicles prohibited, trucks must use another route." },
  17: { icon:"⛔", color:"#ff2222", urgency:"stop",     msg:"No Entry — Wrong way! Do not enter, turn around immediately." },
  18: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"General Caution — Hazard ahead, reduce speed and stay alert." },
  19: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Dangerous Left Curve — Sharp left bend ahead, slow down before turning." },
  20: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Dangerous Right Curve — Sharp right bend ahead, reduce speed now." },
  21: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Double / Reverse Bend — Two bends ahead, slow down and stay in lane." },
  22: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Bumpy / Rough Road — Speed breakers or uneven surface ahead, slow down." },
  23: { icon:"🌊", color:"#ffb84d", urgency:"caution",  msg:"Slippery Road — Surface is slippery, avoid sudden braking or steering." },
  24: { icon:"⚠️", color:"#ffb84d", urgency:"caution",  msg:"Road Narrows — Narrow bridge or lane ahead, merge carefully." },
  25: { icon:"🚧", color:"#ff9f4d", urgency:"roadwork", msg:"Men at Work — Road repairs ahead, slow down and watch for workers." },
  26: { icon:"🚦", color:"#ffb84d", urgency:"caution",  msg:"Traffic Signals Ahead — Traffic lights coming up, be ready to stop." },
  27: { icon:"🚶", color:"#ffb84d", urgency:"caution",  msg:"Pedestrian Crossing — Zebra crossing ahead, slow down and watch for walkers." },
  28: { icon:"👧", color:"#ff4444", urgency:"stop",     msg:"School Ahead — Children may be crossing, slow down significantly." },
  29: { icon:"🚲", color:"#ffb84d", urgency:"caution",  msg:"Bicycle Crossing — Cyclists crossing ahead, give way to them." },
  30: { icon:"🧊", color:"#6eb6ff", urgency:"caution",  msg:"Ice or Snow — Road may be icy, drive slowly and avoid sharp inputs." },
  31: { icon:"🦌", color:"#ff6b6b", urgency:"prohibit", msg:"Cattle / Animals — Livestock or wildlife may be on road, slow down." },
  32: { icon:"✅", color:"#7ddf6a", urgency:"clear",    msg:"End of All Restrictions — All limits lifted, resume normal driving." },
  33: { icon:"➡️", color:"#6eb6ff", urgency:"info",     msg:"Turn Right Ahead — Road turns right, get in right lane and signal." },
  34: { icon:"⬅️", color:"#6eb6ff", urgency:"info",     msg:"Turn Left Ahead — Road turns left, move to left lane and signal." },
  35: { icon:"⬆️", color:"#6eb6ff", urgency:"info",     msg:"Ahead Only — No turning permitted, continue straight ahead." },
  36: { icon:"↗️", color:"#6eb6ff", urgency:"info",     msg:"Go Straight or Turn Right — Choose your lane at the upcoming junction." },
  37: { icon:"↖️", color:"#6eb6ff", urgency:"info",     msg:"Go Straight or Turn Left — Choose your lane at the upcoming junction." },
  38: { icon:"➡️", color:"#6eb6ff", urgency:"info",     msg:"Keep Right — Stay to the right of the divider or obstruction ahead." },
  39: { icon:"⬅️", color:"#6eb6ff", urgency:"info",     msg:"Keep Left — Stay to the left of the divider or obstruction ahead." },
  40: { icon:"🔄", color:"#6eb6ff", urgency:"info",     msg:"Roundabout Ahead — Give way to circulating traffic, enter when clear." },
  41: { icon:"✅", color:"#7ddf6a", urgency:"clear",    msg:"End of No Passing Zone — Overtaking now permitted where safe." },
  42: { icon:"✅", color:"#7ddf6a", urgency:"clear",    msg:"End of No Passing for Trucks — Trucks may overtake again where safe." },
};

const URGENCY_STYLE = {
  stop:     { bg:"rgba(255,34,34,0.15)",   border:"rgba(255,34,34,0.6)",    label:"🛑 STOP NOW" },
  prohibit: { bg:"rgba(255,107,107,0.12)", border:"rgba(255,107,107,0.5)",  label:"⛔ PROHIBITED" },
  slowdown: { bg:"rgba(77,217,184,0.12)",  border:"rgba(77,217,184,0.5)",   label:"🐢 SLOW DOWN" },
  roadwork: { bg:"rgba(255,159,77,0.12)",  border:"rgba(255,159,77,0.5)",   label:"🚧 ROAD WORK" },
  caution:  { bg:"rgba(255,184,77,0.10)",  border:"rgba(255,184,77,0.45)",  label:"⚠️ CAUTION" },
  limit:    { bg:"rgba(255,184,77,0.08)",  border:"rgba(255,184,77,0.35)",  label:"🚗 SPEED LIMIT" },
  priority: { bg:"rgba(110,182,255,0.10)", border:"rgba(110,182,255,0.45)", label:"👑 PRIORITY ROAD" },
  info:     { bg:"rgba(110,182,255,0.08)", border:"rgba(110,182,255,0.30)", label:"ℹ️ INFO" },
  clear:    { bg:"rgba(125,223,106,0.08)", border:"rgba(125,223,106,0.30)", label:"✅ ALL CLEAR" },
};

// ── Smart local NLP — no API, no quota, no cost, works forever ───────────────
const CONFIDENCE_PHRASES = {
  certain:  "⚡ Confirmed",   // >95%
  high:     "✅ Detected",    // 80-95%
  moderate: "⚠️ Likely",      // 60-80%
  low:      "❓ Possible",    // <60%
};

const URGENCY_ACTION = {
  stop:     ["Come to a complete stop before proceeding.",
             "Stop immediately and check all directions.",
             "Full stop required — do not roll through."],
  prohibit: ["This action is not permitted here.",
             "Restriction must be obeyed — no exceptions.",
             "Violation risks safety and fines."],
  slowdown: ["Reduce speed significantly right now.",
             "This zone requires very low speed.",
             "Slow down — vulnerable road users nearby."],
  roadwork: ["Workers may be on the road ahead.",
             "Expect lane changes and reduced speed zones.",
             "Construction zone — stay alert and slow down."],
  caution:  ["Stay alert and reduce speed.",
             "Hazard ahead — increase following distance.",
             "Drive carefully through this section."],
  limit:    ["Do not exceed the posted speed limit.",
             "Maintain this speed on the road ahead.",
             "Stay within the speed restriction."],
  priority: ["You have right of way on this road.",
             "Side roads must yield to you.",
             "Continue with priority but stay alert at junctions."],
  info:     ["Follow the direction indicated by the sign.",
             "Position your vehicle in the correct lane.",
             "Prepare for the road layout ahead."],
  clear:    ["Normal driving rules now apply.",
             "Restrictions have been lifted — resume speed.",
             "All limits ended — standard road rules apply."],
};

function getConfLevel(c) {
  return c >= 0.95 ? "certain" : c >= 0.80 ? "high" : c >= 0.60 ? "moderate" : "low";
}

function generateNlpMsg(classId, label, confidence, urgencyLabel, staticMsg) {
  const advice  = SIGN_ADVICE[Number(classId)];
  if (!advice) return Promise.resolve(staticMsg);
  const level   = getConfLevel(confidence);
  const prefix  = CONFIDENCE_PHRASES[level];
  const conf    = (confidence * 100).toFixed(1);
  const actions = URGENCY_ACTION[advice.urgency] ?? URGENCY_ACTION.info;
  const action  = actions[Number(classId) % actions.length];
  return Promise.resolve(`${prefix}: ${label} (${conf}%) — ${action}`);
}

export default function App() {
  const videoRef   = useRef(null);
  const canvasRef  = useRef(null);
  const timerRef   = useRef(null);
  const thumbsRef  = useRef(null);
  const frameRef   = useRef(0);
  const runningRef = useRef(false);
  const ivRef      = useRef(2);

  const [loaded,     setLoaded]     = useState(false);
  const [running,    setRunning]    = useState(false);
  const [analyzing,  setAnalyzing]  = useState(false);
  const [dragging,   setDragging]   = useState(false);
  const [fileName,   setFileName]   = useState("");
  const [resolution, setResolution] = useState("");
  const [interval,   setInterval_]  = useState(2);
  const [results,    setResults]    = useState([]);
  const [thumbs,     setThumbs]     = useState([]);
  const [stats,      setStats]      = useState({ frames:0, detections:0, latency:"—" });
  const [bgPhase,    setBgPhase]    = useState(0);
  const [backend,    setBackend]    = useState({ status:"checking", ready:false });
  const [vidErr,     setVidErr]     = useState("");
  const [noModel,    setNoModel]    = useState(false);
  const [liveAdvice, setLiveAdvice] = useState(null);
  const [nlpStatus,  setNlpStatus]  = useState("ready");

  useEffect(() => { ivRef.current = interval; }, [interval]);

  const BGAS = [
    "radial-gradient(ellipse at 20% 50%,#1a0533 0%,#0d1b4b 40%,#001a2e 100%)",
    "radial-gradient(ellipse at 80% 20%,#0d2a1a 0%,#001433 40%,#1a0a2e 100%)",
    "radial-gradient(ellipse at 50% 80%,#1a2a00 0%,#0a1a3a 40%,#1a0020 100%)",
    "radial-gradient(ellipse at 30% 30%,#1a1500 0%,#0a0d2e 40%,#001a1a 100%)",
  ];
  useEffect(() => {
    const t = setInterval(() => setBgPhase(p => (p + 1) % 4), 4000);
    return () => clearInterval(t);
  }, []);

  // ── Dynamic browser tab title + icon when sign detected ──────────────────
  useEffect(() => {
    if (liveAdvice?.advice) {
      const { advice, label, confidence } = liveAdvice;
      const conf = (confidence * 100).toFixed(0);
      document.title = `${advice.icon} ${label} (${conf}%) — CNN`;
    } else if (running) {
      document.title = "🔍 Analyzing... — CNN";
    } else {
      document.title = "🚦 Traffic Sign Classifier — CNN";
    }
  }, [liveAdvice, running]);

  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3000) });
        const d = await r.json();
        setBackend({ status: d.ready ? "online" : "no_model", ready: d.ready });
        setNoModel(!d.ready);
      } catch {
        setBackend({ status: "offline", ready: false });
      }
    };
    check();
    const t = setInterval(check, 8000);
    return () => clearInterval(t);
  }, []);

  const loadVideo = useCallback(file => {
    setVidErr("");
    if (!isVideo(file)) { setVidErr(`"${file?.name}" — not a video.`); return; }
    const v = videoRef.current; if (!v) return;
    if (v.src?.startsWith("blob:")) URL.revokeObjectURL(v.src);
    v.src = URL.createObjectURL(file); v.load();
    setFileName(file.name); setLoaded(false);
    v.onloadedmetadata = () => { setResolution(`${v.videoWidth}×${v.videoHeight}`); setLoaded(true); };
    v.onerror = () => setVidErr(`Cannot play "${file.name}". Try MP4 H.264.`);
  }, []);

  const grab = useCallback(() => {
    const v = videoRef.current, c = canvasRef.current;
    if (!v || !c || v.readyState < 2) return null;
    c.width = 160; c.height = Math.round(v.videoHeight * 160 / v.videoWidth) || 90;
    c.getContext("2d").drawImage(v, 0, 0, c.width, c.height);
    const thumb = c.toDataURL("image/jpeg", 0.4);
    c.width = 640; c.height = Math.round(v.videoHeight * 640 / v.videoWidth) || 360;
    c.getContext("2d").drawImage(v, 0, 0, c.width, c.height);
    const full = c.toDataURL("image/jpeg", 0.8).split(",")[1];
    return { full, thumb };
  }, []);

  const classify = useCallback(async () => {
    if (!runningRef.current) return;
    const grabbed = grab(); if (!grabbed) return;
    const fn = ++frameRef.current;
    setAnalyzing(true);
    setThumbs(p => [...p, { src: grabbed.thumb, frame: fn, detected: false }]);
    requestAnimationFrame(() => { if (thumbsRef.current) thumbsRef.current.scrollLeft = 99999; });
    const t0 = performance.now();
    try {
      const res = await fetch(`${API}/classify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: grabbed.full, frame_number: fn }),
      });
      const latency = Math.round(performance.now() - t0);
      const data    = await res.json();

      if (!res.ok) {
        const msg = (data.detail || "").replace("MODEL_NOT_READY|", "");
        if (data.detail?.includes("MODEL_NOT_READY")) setNoModel(true);
        push({ type: "error", fn, msg, latency });
        return;
      }

      if (data.sign_detected && data.top_prediction) {
        const cid    = Number(data.top_prediction.class_id);
        const advice = SIGN_ADVICE[cid] ?? null;
        const us     = advice ? (URGENCY_STYLE[advice.urgency] ?? URGENCY_STYLE.info) : null;
        const baseMsg = advice?.msg ?? `${data.top_prediction.label} detected — stay alert.`;

        setThumbs(p => p.map((t, i) => i === p.length - 1 ? { ...t, detected: true } : t));
        setStats(s => ({ ...s, frames: fn, detections: s.detections + 1, latency: latency + "ms" }));

        // Show static message instantly, then update with Gemini response
        push({ type: "ok", fn, data, latency, nlpMsg: baseMsg });
        setLiveAdvice({ ...data.top_prediction, advice, fn, nlpMsg: baseMsg });

        // Call Gemini in background — non-blocking
        generateNlpMsg(cid, data.top_prediction.label, data.top_prediction.confidence, us?.label ?? "INFO", baseMsg)
          .then(nlpMsg => {
            setNlpStatus("ready");
            // Update live banner
            setLiveAdvice(prev => prev?.fn === fn ? { ...prev, nlpMsg } : prev);
            // Update the card in results list
            setResults(prev => prev.map(r =>
              r.fn === fn && r.type === "ok" ? { ...r, nlpMsg } : r
            ));
          });
      } else {
        setStats(s => ({ ...s, frames: fn, latency: latency + "ms" }));
        push({ type: "ok", fn, data, latency, nlpMsg: null });
      }
    } catch (e) {
      push({ type: "error", fn, msg: e.message, latency: Math.round(performance.now() - t0) });
    } finally {
      setAnalyzing(false);
    }
  }, [grab]);

  const push = r => setResults(p => [r, ...p].slice(0, 80));

  const start = useCallback(() => {
    const v = videoRef.current; if (!v || !loaded) return;
    setResults([]); setThumbs([]); setLiveAdvice(null);
    setStats({ frames: 0, detections: 0, latency: "—" });
    frameRef.current = 0; runningRef.current = true; setRunning(true);
    v.currentTime = 0; v.play().catch(console.error);
    setTimeout(() => classify(), 300);
    timerRef.current = setInterval(() => { if (runningRef.current) classify(); }, ivRef.current * 1000);
    v.onended = () => stop();
  }, [loaded, classify]);

  const stop = useCallback(() => {
    runningRef.current = false; setRunning(false); setAnalyzing(false);
    clearInterval(timerRef.current); timerRef.current = null;
    videoRef.current?.pause();
  }, []);

  const reset = useCallback(() => {
    stop(); setLoaded(false); setFileName(""); setResolution("");
    setResults([]); setThumbs([]); setVidErr(""); setLiveAdvice(null);
    setStats({ frames: 0, detections: 0, latency: "—" });
    frameRef.current = 0;
    const v = videoRef.current;
    if (v) { if (v.src?.startsWith("blob:")) URL.revokeObjectURL(v.src); v.src = ""; v.load(); }
    const i = document.getElementById("fi"); if (i) i.value = "";
  }, [stop]);

  const drop = e => { e.preventDefault(); setDragging(false); loadVideo(e.dataTransfer.files[0]); };
  const statusColor = backend.status === "online" ? "st-on" : backend.status === "no_model" ? "st-warn" : "st-off";
  const statusText  = backend.status === "online" ? "CNN Ready" : backend.status === "no_model" ? "Model Not Trained" : "Backend Offline";

  return (
    <div className="app" style={{ background: BGAS[bgPhase] }}>
      <div className="orb o1"/><div className="orb o2"/><div className="orb o3"/>
      <div className="wrap">

        {/* Header */}
        <header className="glass hdr">
          <div className="hdr-l">
            <span className="chip">CNN</span>
            <div>
              <h1>Traffic Sign Classifier</h1>
              <p className="sub">Local CNN · GTSRB · 43 Classes · Smart NLP · Offline</p>
            </div>
          </div>
          <div style={{ display:"flex", gap:"8px", alignItems:"center" }}>
            <div className={`pill nlp-pill ${nlpStatus === "ready" ? "nlp-on" : "nlp-off"}`}>
              <span className="dot"/>
              "✨ Smart NLP"
            </div>
            <div className={`pill ${statusColor}`}>
              <span className="dot"/>
              {statusText}
            </div>
          </div>
        </header>

        {noModel && (
          <div className="no-model-banner">
            <span className="nm-icon">🧠</span>
            <div>
              <strong>CNN model not trained yet.</strong>
              <span> Run <code>python train.py</code> in the <code>backend/</code> folder.</span>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="stats">
          {[
            { l:"Frames",     v:stats.frames,     c:"a" },
            { l:"Detections", v:stats.detections, c:"t" },
            { l:"Latency",    v:stats.latency,    c:"b" },
            { l:"Interval",   v:interval + "s",   c:"p" },
          ].map(s => (
            <div key={s.l} className={`glass sc sc-${s.c}`}>
              <div className="sl">{s.l}</div>
              <div className="sv">{s.v}</div>
            </div>
          ))}
        </div>

        {/* Live Advice Banner */}
        {liveAdvice?.advice && (() => {
          const { advice, label, confidence, fn, nlpMsg } = liveAdvice;
          const us = URGENCY_STYLE[advice.urgency] ?? URGENCY_STYLE.info;
          return (
            <div className="advice-banner" style={{ background:us.bg, borderColor:us.border }}>
              <div className="adv-icon">{advice.icon}</div>
              <div className="adv-body">
                <div className="adv-urgency" style={{ color:advice.color }}>{us.label}</div>
                <div className="adv-msg">{nlpMsg || advice.msg}</div>
                <div className="adv-meta">{label} · {(confidence*100).toFixed(1)}% · Frame #{fn} "· ✨ Smart NLP"</div>
              </div>
              <button className="adv-close" onClick={() => setLiveAdvice(null)}>✕</button>
            </div>
          );
        })()}

        <div className="grid">
          {/* Video panel */}
          <div className="glass vpanel">
            <div className="ph">
              <span className="ptitle">📹 Video Feed</span>
              {fileName   && <span className="fname" title={fileName}>{fileName}</span>}
              {resolution && <span className="rbadge">{resolution}</span>}
              {loaded     && <button className="btn-sm" onClick={reset}>↩ Change</button>}
            </div>

            <input id="fi" type="file" style={{ display:"none" }}
              onChange={e => e.target.files?.[0] && loadVideo(e.target.files[0])}/>

            {vidErr && (
              <div className="ebar">
                ⚠ {vidErr}
                <button className="ecl" onClick={() => setVidErr("")}>✕</button>
              </div>
            )}

            <div className={`dz ${dragging?"drag":""} ${loaded?"gone":""}`}
              onClick={() => document.getElementById("fi").click()}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={drop}>
              <div className="di">⬆</div>
              <div className="dt">Click or drop any video file</div>
              <div className="ds">MP4 · MOV · AVI · WebM · MKV</div>
            </div>

            <div className={`vwrap ${loaded?"":"gone"}`}>
              <video ref={videoRef} playsInline muted className="vel"/>
              {analyzing && (
                <div className="aov">
                  <div className="scanline"/>
                  <span className="scantxt">Classifying…</span>
                </div>
              )}
            </div>

            <div className="ctrl">
              <button className="btn bp" onClick={start} disabled={!loaded||running||noModel}>▶ Analyze</button>
              <button className="btn bs" onClick={stop}  disabled={!running}>■ Stop</button>
              <div className="ic">
                <span className="il">Every {interval}s</span>
                <input type="range" min="1" max="10" step="1" value={interval}
                  disabled={running} onChange={e => setInterval_(+e.target.value)} className="rng"/>
              </div>
            </div>

            <div className="tip">🖥 Local CNN · "✨ Smart NLP active — confidence-aware messages"</div>

            {thumbs.length > 0 && (
              <div className="tstrip" ref={thumbsRef}>
                {thumbs.map((t, i) => (
                  <img key={i} src={t.src} alt={`F${t.frame}`} title={`Frame ${t.frame}`}
                    className={`th ${t.detected?"th-det":""}`}/>
                ))}
              </div>
            )}
          </div>

          {/* Results panel */}
          <div className="glass rpanel">
            <div className="ph">
              <span className="ptitle">🚦 CNN Predictions</span>
              <button className="btn-sm" onClick={() => setResults([])}>Clear</button>
            </div>
            <div className="rl">
              {results.length === 0
                ? <div className="es"><div className="ei">🧠</div>Upload a video to start</div>
                : results.map((r, i) => <Card key={i} r={r}/>)
              }
            </div>
          </div>
        </div>
      </div>
      <canvas ref={canvasRef} style={{ display:"none" }}/>
    </div>
  );
}

function Card({ r }) {
  if (r.type === "error") return (
    <div className="rc rerr">
      <div className="ct"><span className="ft">Frame #{r.fn}</span><span className="lt">{r.latency}ms</span></div>
      <div className="em">⚠ {r.msg}</div>
    </div>
  );

  const d    = r.data;
  const det  = d?.sign_detected;
  const top  = d?.top_prediction;
  const top3 = d?.top3 || [];
  const cid    = top ? Number(top.class_id) : null;
  const advice = (det && cid !== null) ? (SIGN_ADVICE[cid] ?? null) : null;
  const us     = advice ? (URGENCY_STYLE[advice.urgency] ?? URGENCY_STYLE.info) : null;

  // r.nlpMsg is null initially, then updated by Gemini response
  const displayMsg = r.nlpMsg || advice?.msg || (top ? `${top.label} detected — stay alert.` : "");

  return (
    <div className={`rc ${det?"rdet":""}`}
      style={det && us ? { borderColor:us.border, background:us.bg } : {}}>

      <div className="ct">
        <span className="ft">Frame #{r.fn}</span>
        <span className="lt">{r.latency}ms · CNN</span>
      </div>

      {det && top ? (
        <>
          <div className="top-label">{advice?.icon ?? "🚸"} {top.label}</div>

          <div className="top-conf-row">
            <div className="top-bar-bg">
              <div className="top-bar-fill"
                style={{ width:`${top.confidence*100}%`, background:advice?.color ?? "var(--gn)" }}/>
            </div>
            <span className="top-pct" style={{ color:advice?.color ?? "var(--gn)" }}>
              {(top.confidence*100).toFixed(1)}%
            </span>
          </div>

          {/* NLP advice box */}
          <div className="adv-card"
            style={{ borderColor:us?.border ?? "rgba(125,223,106,0.3)",
                     background: us?.bg     ?? "rgba(125,223,106,0.08)" }}>
            <div className="adv-card-header">
              <span className="adv-card-icon">{advice?.icon ?? "🚸"}</span>
              <span className="adv-card-badge"
                style={{ color:advice?.color ?? "var(--gn)",
                         borderColor:us?.border ?? "rgba(125,223,106,0.3)" }}>
                {us?.label ?? "ℹ INFO"}
              </span>
              {r.nlpMsg && <span className="gemini-tag">✨ Gemini</span>}
            </div>
            <p className="adv-card-msg">{displayMsg}</p>
          </div>

          <div className="top3">
            {top3.map((p, i) => (
              <div key={i} className="p3-row">
                <span className="p3-label">{SIGN_ADVICE[Number(p.class_id)]?.icon ?? "•"} {p.label}</span>
                <div className="p3-bar-bg">
                  <div className="p3-bar" style={{ width:`${p.confidence*100}%`, opacity:1-i*0.25 }}/>
                </div>
                <span className="p3-pct">{(p.confidence*100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="no-det">
          <span className="ns">Below threshold ({((d?.threshold ?? 0.55)*100).toFixed(0)}%)</span>
          {top3[0] && <span className="ns-hint">Best: {top3[0].label} ({(top3[0].confidence*100).toFixed(1)}%)</span>}
        </div>
      )}
    </div>
  );
}
