const socket = io();

let audio = null;
let micBtn = document.getElementById("mic-btn");
let speechText = document.getElementById("speech-text");
let voiceAnim = document.getElementById("voice-anim");
let responseBox = document.getElementById("output");
const liveFeed = document.getElementById("live-feed");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "en-US";
recognition.continuous = false;

micBtn.addEventListener("click", () => {
  speechText.textContent = "Listening...";
  voiceAnim.style.display = "block";
  recognition.start();
});

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  speechText.textContent = transcript;
  voiceAnim.style.display = "none";

  fetch("/assistant/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: transcript })
  })
    .then(res => res.json())
    .then(data => {
    let responseText = "Sorry, I didn't get that.";
    if (typeof data.text === "string") {
      responseText = data.text;
    } else if (typeof data.response === "string") {
      responseText = data.response;
    } else if (typeof data.response === "object") {
      responseText = "Clark processed your request, but can't read this aloud.";
    }

      responseBox.textContent = responseText;

      // Show Clark's vision frame if vision or ocr or crossing
      if (data.image_preview_b64) {
        liveFeed.src = `data:image/jpeg;base64,${data.image_preview_b64}`;
        liveFeed.style.display = "block";
        setTimeout(() => {
          liveFeed.style.display = "none";
        }, 8000);
      }

      // Trigger voice
      return fetch("/voice/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: responseText })
      });
    })
    .then(res => {
      if (!res.ok) throw new Error(`TTS failed with status ${res.status}`);
      return res.blob();
    })
    .then(blob => {
      if (blob.size === 0) throw new Error("Empty audio response");
      if (audio) audio.pause();
      audio = new Audio(URL.createObjectURL(blob));
      audio.play();
    })
    .catch(err => {
      console.error("Clark error:", err);
      responseBox.textContent = "Clark had an issue responding.";
    });
};

// --- Pause & Stop buttons
document.getElementById("pause-btn").addEventListener("click", () => {
  if (audio && !audio.paused) audio.pause();
});

document.getElementById("stop-btn").addEventListener("click", () => {
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
  }
});
