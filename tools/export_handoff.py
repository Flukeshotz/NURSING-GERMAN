#!/usr/bin/env python3
"""Build the implementation handoff: one folder per chapter with chapter.json + the images it uses."""
import json, os, re, shutil, glob
from html.parser import HTMLParser

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(APP), "handoff", "nursing-german-a1")
CONTENT = os.path.join(OUT, "content")

VOICE = {"weber": "patient_old_female", "schmidt": "patient_old_male", "yilmaz": "patient_male",
         "lena": "colleague_female", "braun": "doctor_male", "anna": "visitor_female",
         "nurse": "learner_nurse_female", None: "learner_nurse_female"}
SPEAKER_NAME = {"weber": "Frau Weber", "schmidt": "Herr Schmidt", "yilmaz": "Herr Yılmaz",
                "lena": "Lena", "braun": "Dr. Braun", "anna": "Anna Weber", "nurse": "You"}
Q_LABEL = {"translate_to_german": "Translate into German", "translate_to_english": "Translate into English",
           "choose_reply": "What do you answer?", "choose_reply_sie_du": "What do you answer?",
           "situation_choice": "What do you say?", "picture_choice": "What does this person need?",
           "body_part_choice": "Where is the problem?", "listen_and_note": "What do you write down?",
           "document_question": "Read the document", "spelling": "Listen to the spelling",
           "emergency_translate": "Emergency · translate into German"}
ARTICLES = ("der ", "die ", "das ")

def slug(s):
    s = s.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

class DocParser(HTMLParser):
    """Turn the prototype's document HTML into structured blocks (inline tags keep their text)."""
    BLOCK = {"h4", "div", "p", "td", "th", "li", "table", "tr", "ul"}
    def __init__(self):
        super().__init__(); self.blocks = []; self.stack = []; self.buf = ""; self.table = None
        self.row = None; self.list = None; self.fields = None; self.span_hi = False; self.colspan = 1; self.cell_hi = False; self.row_th = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); c = a.get("class", "")
        self.stack.append((tag, c))
        if tag in self.BLOCK and not (self.fields is not None and tag not in ("div",)): self.buf = ""
        if tag == "table": self.table = {"type": "table", "header": [], "rows": [], "highlight": []}
        elif tag == "tr": self.row = []; self.row_th = False
        elif tag in ("td", "th"):
            self.cell_hi = "hi" in c; self.colspan = int(a.get("colspan", 1)); self.row_th = self.row_th or tag == "th"
        elif tag == "ul": self.list = {"type": "list", "items": []}
        elif tag == "div" and "band" in c: self.fields = {"type": "fields", "items": [], "highlight": []}
        elif self.fields is not None and tag in ("b", "span"): self.buf = ""; self.span_hi = "hi" in c
    def handle_endtag(self, tag):
        tag0, c = self.stack.pop() if self.stack else (tag, "")
        text = " ".join(self.buf.split())
        if tag == "h4": self.blocks.append({"type": "heading", "text": text}); self.buf = ""
        elif tag == "div" and "dmeta" in c: self.blocks.append({"type": "subtitle", "text": text}); self.buf = ""
        elif tag == "div" and "sign-h" in c: self.blocks.append({"type": "heading", "text": text}); self.buf = ""
        elif tag in ("td", "th") and self.row is not None:
            self.row.append(text if self.colspan == 1 else {"text": text, "colspan": self.colspan})
            if self.cell_hi: self.table["highlight"].append(text)
            self.buf = ""
        elif tag == "tr" and self.table is not None:
            if self.row_th and not self.table["header"]: self.table["header"] = self.row
            else: self.table["rows"].append(self.row)
            self.row = None
        elif tag == "table": self.blocks.append(self.table); self.table = None
        elif tag == "li" and self.list is not None: self.list["items"].append(text); self.buf = ""
        elif tag == "ul": self.blocks.append(self.list); self.list = None
        elif tag == "p" and self.table is None: self.blocks.append({"type": "text", "text": text}); self.buf = ""
        elif tag in ("b", "span") and self.fields is not None:
            if text: self.fields["items"].append(text)
            if self.span_hi and text: self.fields["highlight"].append(text)
            self.buf = ""
        elif tag == "div" and "band" in c: self.blocks.append(self.fields); self.fields = None; self.buf = ""
    def handle_data(self, d):
        self.buf += d
    def get(self):
        return [b for b in self.blocks if b and (b.get("text") or b.get("rows") or b.get("items"))]

def parse_doc(html):
    p = DocParser(); p.feed(html); return p.get()

def audio(text, speaker):
    return {"text": text, "voice": VOICE.get(speaker, VOICE[None]), "lang": "de-DE"} if text else None

def main():
    if os.path.exists(CONTENT): shutil.rmtree(CONTENT)
    os.makedirs(CONTENT)
    idx = json.load(open(os.path.join(APP, "content", "levels", "index.json")))
    chapters_index = []
    totals = {"cards": 0, "questions": 0, "images": 0}
    for lv in idx["levels"]:
        src = json.load(open(os.path.join(APP, "content", "levels", lv["file"])))
        n = src["level"]; cid = f"ch{n:02d}"
        folder = f"chapter-{n:02d}-{slug(src['title_en'])}"
        fdir = os.path.join(CONTENT, folder); os.makedirs(fdir)
        goals = [{"id": f"{cid}-g{k+1}", "title_en": g["title"], "pattern_de": g["pattern"],
                  "pattern_en": g["pattern_en"], "tip_en": g["tip"]} for k, g in enumerate(src["goals"])]
        goal_by_title = {g["title_en"]: g["id"] for g in goals}
        cards = []; card_by_key = {}; current_goal = None; used = set()
        for k, c in enumerate(src["flashcards"]):
            t = c["type"]; card_id = f"{cid}-c{k+1:02d}"
            front_de = c["front"]["german"]
            if t == "pattern": current_goal = goal_by_title.get(c["front"]["label"])
            card = {"id": card_id, "order": k + 1, "type": t,
                    "goal_id": current_goal if t in ("pattern", "phrase") else None,
                    "image": c["front"]["image"],
                    "front": {"german": front_de, "label": c["front"]["label"],
                              "speaker": c["front"]["speaker"], "speaker_name": SPEAKER_NAME.get(c["front"]["speaker"])},
                    "back": {"meaning_en": c["back"]["meaning_en"], "label": c["back"]["label"],
                             "german": c["back"]["german"], "english": c["back"]["english"], "note": c["back"]["note"]}}
            if t == "word":
                w = c.get("article_word") or front_de
                art = next((a.strip() for a in ARTICLES if w.startswith(a)), None)
                card["word"] = {"article": art, "plural": w.endswith("·pl"), "false_friend": c.get("false_friend", False)}
            if t == "pattern":
                card["front"]["pattern_de"] = c.get("pattern")
            if t == "phrase" and c.get("replies"):
                card["replies"] = c["replies"]
            if t == "document":
                d = c["document"]
                card["document"] = {"title_de": d["title_de"], "title_en": d["title_en"], "blocks": parse_doc(d["html"]),
                                    "key_words": d["key_words"]}
            if t == "spelling":
                card["spelling"] = c["spelling"]
                card["front"]["german"] = "Wie schreibt man das?"
            front_audio_text = ", ".join(x["letter"] for x in c["spelling"]["letters"]) if t == "spelling" else front_de.replace(" / ", ", ").replace("·pl", "")
            card["audio"] = {"front": audio(front_audio_text, c["front"]["speaker"]),
                             "back": audio(c["back"]["german"], "nurse") if c["back"]["label"] not in ("Key words",) else audio(", ".join(x["de"] for x in c.get("document", {}).get("key_words", [])), "nurse")}
            if t == "spelling": card["audio"]["back"] = None
            cards.append(card); used.add(card["image"])
            card_by_key[front_de] = card_id
            if c.get("article_word"): card_by_key[c["article_word"]] = card_id
            if t == "spelling": card_by_key[c["spelling"]["name"]] = card_id
        questions = []
        for k, q in enumerate(src["quiz_pool"]):
            t = q["type"]; qq = {"id": f"{cid}-q{k+1:03d}", "type": t, "label": Q_LABEL[t],
                                 "card_id": card_by_key[q["from_card"]]}
            card = next(x for x in cards if x["id"] == qq["card_id"])
            qq["image"] = card["image"]
            if t in ("translate_to_german", "translate_to_english", "emergency_translate"):
                qq["question_en"] = q["question_en"]
                if t == "translate_to_english": qq["german"] = q["german"]; qq["audio"] = audio(q["german"], None)
            elif t in ("choose_reply", "choose_reply_sie_du", "picture_choice", "body_part_choice", "listen_and_note"):
                sp = q["speaker"]
                qq["speaker"] = sp; qq["speaker_name"] = SPEAKER_NAME.get(sp)
                qq["prompt_de"] = q["prompt_de"]; qq["prompt_en"] = q["prompt_en"]
                qq["audio"] = audio(q["prompt_de"], sp)
            elif t == "situation_choice":
                qq["question_en"] = q["prompt_en"]
            elif t == "document_question":
                qq["question_en"] = q["question_en"]; qq["document_card_id"] = qq["card_id"]
            elif t == "spelling":
                qq["question_en"] = "Which name is spelled?"; qq["prompt_de"] = "Wie schreibt man das?"
                qq["audio"] = {"text": ", ".join(q["audio_letters"]), "voice": VOICE["braun"], "lang": "de-DE", "pause_between_items_ms": 400}
            qq["options"] = q["options"]; qq["answer"] = q["answer"]
            if q.get("feedback_de"): qq["feedback_de"] = q["feedback_de"]; qq["feedback_en"] = q.get("feedback_en")
            qq["time_limit_seconds"] = q.get("time_limit_seconds")
            assert qq["answer"] in qq["options"], qq["id"]
            questions.append(qq)
        for img in sorted(used):
            shutil.copy2(os.path.join(APP, "images", img), os.path.join(fdir, img))
        is_em = all(c["type"] == "emergency" for c in cards)
        ch = {"schema_version": 1, "module": "nursing_german", "cefr": "A1",
              "chapter_id": f"nursing-a1-{cid}", "chapter_number": n,
              "title_en": src["title_en"], "title_de": src["title_de"],
              "unlock": {"requires_chapter": None if n == 1 else n - 1, "requires_quiz_pass": n != 1},
              "rules": {"quick_check_every_cards": 20, "quick_check_questions": 5,
                        "quiz_pass_mark": 0.7, "quiz_questions_per_attempt": src["rules"]["quiz_questions_per_attempt"],
                        "quiz_composition": ({"emergency_translate": 10} if is_em else
                                             {"word_cards": 4, "phrase_cards": 8, "document_questions_per_document": 2, "spelling": "all"})},
              "goals": goals, "cards": cards, "questions": questions,
              "images": sorted(used)}
        json.dump(ch, open(os.path.join(fdir, "chapter.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        chapters_index.append({"chapter_number": n, "chapter_id": ch["chapter_id"], "title_en": ch["title_en"],
                               "title_de": ch["title_de"], "folder": folder, "cards": len(cards),
                               "questions": len(questions), "images": len(used)})
        totals["cards"] += len(cards); totals["questions"] += len(questions); totals["images"] += len(used)
    shutil.copy2(os.path.join(APP, "images", "h-nursing-german.jpg"), os.path.join(CONTENT, "cover.jpg"))
    json.dump({"module": "nursing_german", "cefr": "A1", "schema_version": 1, "cover_image": "cover.jpg",
               "chapters": chapters_index, "totals": totals},
              open(os.path.join(CONTENT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(totals))

if __name__ == "__main__":
    main()
