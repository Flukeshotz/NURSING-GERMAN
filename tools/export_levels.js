// Exports every level as content/levels/level-XX.json (+ index.json). Zips are made by tools/zip_levels.py.
const fs = require("fs"), path = require("path");
const A = require("./lib_load")();
const OUT = path.join(__dirname, "..", "content", "levels");
fs.mkdirSync(OUT, { recursive: true });
const pad = n => String(n).padStart(2, "0");
const IMGDIR = path.join(__dirname, "..", "images");
const img = id => id && fs.existsSync(path.join(IMGDIR, id + ".jpg")) ? id + ".jpg" : null;
const plain = A.plain;
const TYPE = { need: "picture_choice", where: "body_part_choice", say: "choose_reply", who: "choose_reply_sie_du", do: "situation_choice", num: "listen_and_note" };
const LETTER = A.LETTER;

const index = [];
A.LEVELS.forEach((L, i) => {
  const n = i + 1, title = A.levelTitle(i);
  const images = new Set();
  const use = id => { const f = img(id); if (f) images.add(f); return f; };

  const flashcards = A.levelDeck(i).map((c, k) => {
    const back = A.backParts(c);
    const card = { order: k + 1, type: { word: "word", em: "emergency", pattern: "pattern", phrase: "phrase", doc: "document", spell: "spelling" }[c.kind],
      front: { german: c.kind === "spell" ? "Wie schreibt man das?" : plain(c.de), speaker: c.sp || null, label: c.label || c.title || null,
               image: c.kind === "word" ? use("w-" + A.slugId(c.meaning)) : c.pic ? use(c.pic) : null },
      back: { meaning_en: c.meaning, label: back.label, german: back.line, english: back.sub, note: back.note || null } };
    if (c.kind === "word") { const w = A.wordByEn(c.meaning); card.article_word = w.de; card.false_friend = !!w.false; }
    if (c.kind === "pattern") card.pattern = A.GOALS[L.s].find(g => g.t === c.title).p;
    if (c.kind === "doc") card.document = { title_de: c.de, title_en: c.meaning, html: c.doc, key_words: c.keys.map(([de, en]) => ({ de, en })) };
    if (c.kind === "spell") card.spelling = { name: c.de, letters: c.letters.map(x => ({ letter: x, say: LETTER[x] || x })) };
    if (c.kind === "phrase" && c.replies) card.replies = c.replies.map(r => ({ label: r.label, german: r.g, english: r.en || null }));
    return card;
  });

  const quiz = [];
  const words = L.words.map(A.wordByEn).filter(Boolean);
  const others = (w, field) => words.filter(x => x !== w).concat(A.WORDS.filter(x => !words.includes(x))).map(x => x[field]).filter((v, k, a) => v !== w[field] && a.indexOf(v) === k).slice(0, 3);
  words.forEach(w => {
    quiz.push({ type: "image_choice", instruction: "Match the correct word to this image", image: use("w-" + A.slugId(w.en)), options: [w.de, ...others(w, "de")], answer: w.de });
    quiz.push({ type: "meaning_choice", instruction: "Choose the correct meaning", german: w.de, options: [w.en, ...others(w, "en")], answer: w.en });
  });
  if (L.em) {
    A.DRILL.forEach(d => quiz.push({ type: "emergency_drill", time_limit_seconds: 8, situation_en: d.s, options: d.o, answer: d.o[0] }));
  } else {
    A.SHIFTS[L.s].r.forEach(r => {
      const q = { type: TYPE[r.t], speaker: r.sp, prompt_de: r.de || null, prompt_en: r.en };
      if (r.t === "need") { q.options = r.o.map(o => { const [emoji, lab] = o.split("|"); return { german: plain(lab), english: A.TR[lab] || null, image: use("i-" + A.slugId(lab)) }; }); q.answer = plain(r.o[0].split("|")[1]); }
      else if (r.t === "where") { q.options = r.o.map(k => ({ german: A.BODY[k][0], english: A.TR[A.BODY[k][0]] || null, body_part: k })); q.answer = A.BODY[r.o[0]][0]; }
      else { q.options = r.o.slice(); q.answer = r.o[0]; }
      if (r.fb) q.feedback_de = r.fb, q.feedback_en = A.TR[r.fb] || null;
      quiz.push(q);
    });
    (L.docs || []).forEach(id => { const d = A.DOCS.find(x => x.id === id); d.qs.forEach(qq => quiz.push({ type: "document_question", document: d.title, document_de: d.de, question_en: qq.q, options: qq.o, answer: qq.o[0] })); });
    (A.SPELL[L.spell] || []).forEach(s => quiz.push({ type: "spelling", audio_letters: s.name.toUpperCase().split(""), options: s.o, answer: s.name }));
  }

  const file = `level-${pad(n)}.json`;
  const data = { level: n, cefr: "A1", title_en: title, title_de: L.em ? "Notfall-Deutsch" : A.SHIFTS[L.s].de,
    unlock: n === 1 ? null : { requires_level: n - 1, pass_mark: 0.7 },
    flow: ["flashcards", "quick_check_every_20_cards", "level_quiz", "next_level"],
    rules: { quick_check_every_cards: 20, quiz_pass_mark: 0.7, quiz_questions_per_attempt: L.em ? 10 : Math.min(quiz.length, 3 + 8 + (L.docs || []).length * 2 + (A.SPELL[L.spell] || []).length) },
    goals: L.em ? [] : A.GOALS[L.s].map(g => ({ title: g.t, pattern: g.p, pattern_en: g.pe, tip: g.tip || null })),
    flashcards, quiz_pool: quiz, images_zip: `level-${pad(n)}-images.zip`, images: [...images].sort() };
  fs.writeFileSync(path.join(OUT, file), JSON.stringify(data, null, 2));
  index.push({ level: n, title_en: title, file, images_zip: data.images_zip, flashcards: flashcards.length, quiz_pool: quiz.length, images: images.size });
});
fs.writeFileSync(path.join(OUT, "index.json"), JSON.stringify({ course: "Nursing German", cefr: "A1", levels: index }, null, 2));
console.log(index.map(x => `L${x.level} ${x.title_en}: ${x.flashcards} cards, ${x.quiz_pool} questions, ${x.images} images`).join("\n"));
