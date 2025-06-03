const socket = io();
let lipsyncInterval = null;

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

  // Reset mouth to neutral when listening
  const mouth = document.getElementById("mouth");
  if (mouth) mouth.src = "/static/visemes/neutral.png";

  recognition.start();
});


recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  speechText.textContent = transcript;

  const mouth = document.getElementById("mouth");
  if (mouth) mouth.src = "/static/visemes/neutral.png";

  let responseText = "Sorry, I didn't get that.";

  fetch("/assistant/speak", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: transcript })
  })
    .then(res => res.json())
    .then(data => {
      if (typeof data.text === "string") {
        responseText = data.text;
      } else if (typeof data.response === "string") {
        responseText = data.response;
      } else if (typeof data.response === "object") {
        responseText = "Clark processed your request, but can't read this aloud.";
      }

      responseBox.textContent = responseText;

      if (data.image_preview_b64) {
        liveFeed.src = `data:image/jpeg;base64,${data.image_preview_b64}`;
        liveFeed.style.display = "block";
        setTimeout(() => {
          liveFeed.style.display = "none";
        }, 8000);
      }

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

      
      audio.onplay = () => {
        // delay animation to match Clark's voice
        setTimeout(() => {
          startLipsync(responseText);
        }, 700); 
      };

      audio.onended = () => {
      // stop lipsync when speech ends
        clearInterval(lipsyncInterval);
        const mouth = document.getElementById("mouth");
        if (mouth) mouth.src = "/static/visemes/neutral.png";
      };

      audio.play();
    })
    .catch(err => {
      console.error("Clark error:", err);
      responseBox.textContent = "Clark had an issue responding.";
    });
};



// --- Pause Button ---
document.getElementById("pause-btn").addEventListener("click", () => {
  if (audio && !audio.paused) audio.pause();

  // stop lipsync when paused
  clearInterval(lipsyncInterval);
  const mouth = document.getElementById("mouth");
  if (mouth) mouth.src = "/static/visemes/neutral.png";
});

// --- Stop Button ---
document.getElementById("stop-btn").addEventListener("click", () => {
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
  }

  // stop lipsync when stopped
  clearInterval(lipsyncInterval);
  const mouth = document.getElementById("mouth");
  if (mouth) mouth.src = "/static/visemes/neutral.png";
});



// --- Lips sync animation
function startLipsync(text) {
  clearInterval(lipsyncInterval);
  const mouth = document.getElementById("mouth");
  if (!mouth || !text) return;

  let index = 0;
  const letters = text.split("");

  lipsyncInterval = setInterval(() => {
    if (index >= letters.length) {
      mouth.src = "/static/visemes/neutral.png";
      clearInterval(lipsyncInterval);
      return;
    }

    const char = letters[index].toLowerCase();

    let visemeLabel = "neutral";
    for (const group in visemeGroups) {
      if (visemeGroups[group].includes(char)) {
        visemeLabel = group;
        break;
      }
    }

    mouth.src = `/static/visemes/${visemeLabel}.png`;
    index++;
  }, 100);
}




// --- Calendar module reminder
const bellAudio = new Audio('/static/bell.mp3');

setInterval(() => {
    fetch("/calendar/check")
        .then(res => res.json())
        .then(data => {
            if (data.reminder) {
                const bell = document.getElementById("bell");
                bell.classList.add("active");
                bell.style.display = "block";
                bell.dataset.message = data.reminder;
                bellAudio.play(); // notification sound
            }
        });
}, 5000);

document.getElementById("bell").addEventListener("click", () => {
    const bell = document.getElementById("bell");
    const message = bell.dataset.message;

    const spokenMessage = `This is your scheduled reminder: ${message}`;

    // Send to TTS
    fetch("/voice/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: spokenMessage })
    })
    .then(res => {
        if (!res.ok) throw new Error("TTS request failed.");
        return res.blob();
    })
    .then(blob => {
        if (blob.size === 0) throw new Error("Empty TTS response.");
        const audio = new Audio(URL.createObjectURL(blob));
        audio.play();
    })
    .catch(err => {
        console.error("TTS error:", err);
    });

    // Clear the reminder
    fetch("/calendar/clear");

    // Hide the bell
    bell.style.display = "none";
});
