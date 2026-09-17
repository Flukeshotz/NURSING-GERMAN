// Adds one "exact scene" picture per phrase card and emergency card, and sharpens vague word prompts.
const fs = require("fs"), path = require("path");
const A = require("./lib_load")();
const man = JSON.parse(fs.readFileSync(path.join(__dirname, "image_manifest.json"), "utf8"));
const STYLE = s => `Wide 3:2 landscape realistic photograph, main subject centred with a little space around it so nothing important touches the edges, in the style of professional healthcare stock photography, adults only, natural soft daylight, real modern German hospital, authentic and respectful, sharp focus on the main subject, shallow depth of field. ${s} Absolutely no text, no letters, no numbers, no speech bubbles, no logos. Not a cartoon, not a 3D render, not an illustration.`;
const WHO = {
  weber: "Frau Weber, an 82-year-old German woman patient with short grey hair, in a hospital gown",
  schmidt: "Herr Schmidt, a 67-year-old German man patient with glasses, in pyjamas",
  yilmaz: "Herr Yilmaz, a 45-year-old Turkish-German man patient with a short dark beard",
  lena: "Lena, a young blonde German nurse colleague in a light blue uniform",
  braun: "Dr. Braun, a middle-aged German doctor in a white coat with a stethoscope",
  anna: "Anna, a woman in her fifties visiting her elderly mother",
  nurse: "a young Indian nurse with dark hair in a ponytail, in a light blue uniform"
};
const FIX = { // sharper prompts for vague words
  "Duty": "a nurse arriving for her shift and checking her shift on a duty roster board next to a clock at 6 o'clock",
  "CT scan": "a short, thin ring-shaped CT scanner (not a tunnel) with a patient lying on the table",
  "MRI": "a long deep tunnel MRI scanner with a patient lying on the table sliding into the tunnel",
  "Motion (stool)": "a nurse politely asking an elderly patient in bed about going to the toilet, a bedpan on the side table",
  "So / well …": "a nurse starting a conversation with a patient with a thoughtful open hand gesture",
  "To get / receive": "a patient in bed receiving a small medicine cup with a tablet from a nurse's hand",
  "OD (once a day)": "one white tablet next to a morning sunrise",
  "BD (twice a day)": "two white tablets, one beside a morning sun and one beside an evening moon",
  "SOS / PRN": "a patient in bed pressing the call bell and a nurse bringing a single painkiller tablet",
  "NBM / NPO": "a patient in bed before surgery with an empty tray, a water glass turned upside down",
  "Hospital diet": "a hospital meal tray with a simple healthy lunch",
  "Bystander / attendant": "two relatives sitting on visitor chairs next to an elderly patient's hospital bed"
};
for (const it of man) if (it.type === "word" && FIX[it.en]) { it.prompt = STYLE(FIX[it.en] + ".").replace("  ", " "); it.redo = true; }
const have = new Set(man.map(m => m.id));
A.LEVELS.forEach((L, li) => {
  if (L.em) {
    A.EMERGENCY.forEach(([de, en], k) => {
      const id = `e-${String(k + 1).padStart(2, "0")}`;
      if (!have.has(id)) man.push({ id, file: `images/${id}.jpg`, type: "emergency", de, en,
        prompt: STYLE(`An urgent emergency moment on a German hospital ward: ${WHO.nurse} is saying "${en}" and acting it out clearly, showing exactly this situation.`) });
    });
    return;
  }
  const exs = A.exchangesFor(L.s);
  exs.forEach((ex, j) => {
    const id = `p-${String(L.s + 1).padStart(2, "0")}-${String(j + 1).padStart(2, "0")}`;
    if (have.has(id)) return;
    let scene;
    if (ex.sit) scene = `On a German hospital ward: ${WHO.nurse} in this situation: ${ex.en} Show her about to speak.`;
    else {
      const who = WHO[ex.sp] || WHO.nurse;
      const ctx = ex.ctx ? ` Context: ${ex.ctx}.` : "";
      scene = `On a German hospital ward: ${who} is saying to ${WHO.nurse}: "${ex.en || ex.ctx}".${ctx} Show exactly this moment with clear body language and the objects mentioned.`;
    }
    man.push({ id, file: `images/${id}.jpg`, type: "phrase", level: li + 1, de: ex.sit ? ex.replies[0].g : ex.de, en: ex.en, prompt: STYLE(scene) });
  });
});
for (const it of man) it.size = it.size || "1536x1024";
fs.writeFileSync(path.join(__dirname, "image_manifest.json"), JSON.stringify(man, null, 1));
console.log("manifest:", man.length, "images;", man.filter(m => m.redo).length, "to redo;", man.filter(m => m.type === "phrase").length, "phrase scenes;", man.filter(m => m.type === "emergency").length, "emergency scenes");
