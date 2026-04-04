<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Voice Analyzer</title>

<style>
body {
  margin: 0;
  font-family: 'Courier New', monospace;
  background: linear-gradient(135deg,#0a0e1a,#0d1528,#0a0e1a);
  color: #e2e8f0;
  text-align: center;
}

.container {
  padding: 20px;
}

.card {
  background: rgba(15,23,42,0.9);
  border-radius: 15px;
  padding: 15px;
  margin: 10px 0;
}

button {
  padding: 15px;
  border-radius: 10px;
  border: none;
  font-weight: bold;
  font-size: 16px;
}

.start {
  background: #6366f1;
  color: white;
}

.stop {
  background: red;
  color: white;
}

.bar {
  height: 10px;
  background: linear-gradient(90deg,#6366f1,#22c55e,#f59e0b,#ef4444);
  border-radius: 5px;
  margin-top: 10px;
}

.pointer {
  width: 15px;
  height: 15px;
  background: white;
  border-radius: 50%;
  position: relative;
  top: -12px;
}

</style>
</head>

<body>

<div class="container">

<h2>🎙️ VOICE ANALYZER</h2>

<div class="card">
  <p><b>Frequency:</b> <span id="hz">--</span> Hz</p>
  <p><b>Words:</b> <span id="words">0</span></p>
  <p><b>Duration:</b> <span id="time">0</span> sec</p>
</div>

<div class="card">
  <p>Pitch Meter</p>
  <div class="bar">
    <div id="pointer" class="pointer"></div>
  </div>
</div>

<div class="card">
  <p id="text">Press START to begin</p>
</div>

<button id="btn" class="start">START</button>

</div>

<script>

let audioContext, analyser, mic, dataArray;
let running = false;
let animationId;
let seconds = 0;
let timer;

// -------- Pitch Detection --------
function autoCorrelate(buffer, sampleRate) {
  let SIZE = buffer.length;
  let rms = 0;

  for (let i = 0; i < SIZE; i++) {
    rms += buffer[i] * buffer[i];
  }
  rms = Math.sqrt(rms / SIZE);

  if (rms < 0.01) return null;

  let r1 = 0, r2 = SIZE - 1;
  for (let i = 0; i < SIZE/2; i++) {
    if (Math.abs(buffer[i]) < 0.2) { r1 = i; break; }
  }
  for (let i = 1; i < SIZE/2; i++) {
    if (Math.abs(buffer[SIZE-i]) < 0.2) { r2 = SIZE-i; break; }
  }

  buffer = buffer.slice(r1, r2);
  SIZE = buffer.length;

  let c = new Array(SIZE).fill(0);

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE-i; j++) {
      c[i] = c[i] + buffer[j]*buffer[j+i];
    }
  }

  let d = 0;
  while (c[d] > c[d+1]) d++;

  let maxval = -1, maxpos = -1;
  for (let i = d; i < SIZE; i++) {
    if (c[i] > maxval) {
      maxval = c[i];
      maxpos = i;
    }
  }

  let T0 = maxpos;
  return sampleRate / T0;
}

// -------- Start Mic --------
async function start() {
  const stream = await navigator.mediaDevices.getUserMedia({audio:true});

  audioContext = new AudioContext();
  analyser = audioContext.createAnalyser();
  mic = audioContext.createMediaStreamSource(stream);

  mic.connect(analyser);

  dataArray = new Float32Array(analyser.fftSize);

  runPitch();

  // Timer
  timer = setInterval(() => {
    seconds++;
    document.getElementById("time").innerText = seconds;
  },1000);

  // Speech recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const rec = new SpeechRecognition();
    rec.continuous = true;
    rec.onresult = (e) => {
      let text = "";
      for (let i = 0; i < e.results.length; i++) {
        text += e.results[i][0].transcript;
      }
      document.getElementById("text").innerText = text;
      document.getElementById("words").innerText = text.split(" ").length;
    };
    rec.start();
  }
}

// -------- Loop --------
function runPitch() {
  analyser.getFloatTimeDomainData(dataArray);

  let freq = autoCorrelate(dataArray, audioContext.sampleRate);

  if (freq) {
    document.getElementById("hz").innerText = freq.toFixed(1);

    let pct = Math.min(Math.max(freq,50),500);
    pct = ((pct-50)/450)*100;

    document.getElementById("pointer").style.left = pct + "%";
  }

  animationId = requestAnimationFrame(runPitch);
}

// -------- Stop --------
function stop() {
  cancelAnimationFrame(animationId);
  clearInterval(timer);
  audioContext.close();
}

// -------- Button --------
document.getElementById("btn").onclick = async () => {
  if (!running) {
    running = true;
    document.getElementById("btn").innerText = "STOP";
    document.getElementById("btn").className = "stop";
    start();
  } else {
    running = false;
    document.getElementById("btn").innerText = "START";
    document.getElementById("btn").className = "start";
    stop();
  }
};

</script>

</body>
</html>
