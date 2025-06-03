const visemeGroups = {
  AEI: ["a", "e", "i"],
  BMP: ["b", "m", "p"],
  CDGKNSTXYZ: ["c", "d", "g", "k", "n", "s", "t", "x", "y", "z"],
  CHSHJ: ["ch", "sh", "j"],
  FV: ["f", "v"],
  L: ["l"],
  O: ["o"],
  QW: ["q", "w"],
  R: ["r"],
  U: ["u"],
  TH: ["th"]
};

function mapCharToViseme(char) {
  const lower = char.toLowerCase();

  for (const [viseme, group] of Object.entries(visemeGroups)) {
    if (group.includes(lower)) return viseme;
  }

  return "neutral";
}

// function Clark calls from script
function lipsyncFromText(text) {
  const mouth = document.getElementById("mouth");
  if (!mouth || !text) return;

  const letters = text.split("");
  let index = 0;

  const interval = setInterval(() => {
    if (index >= letters.length) {
      mouth.src = "/static/visemes/neutral.png";
      clearInterval(interval);
      return;
    }

    const viseme = mapCharToViseme(letters[index]);
    mouth.src = `/static/visemes/${viseme}.png`;
    index++;
  }, 100); 
}




