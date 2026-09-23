# Nursing German (A1): implementation instructions

**Audience:** the agent/developer who has access to the production SkillCase codebase.
**Goal:** add Nursing German as a new A1 practice module that behaves exactly like the existing A1 practice modules, using the content in `content/`.

**Ground rules for you**
- The codebase is in production. **Reuse what exists.** Follow the patterns of the A1 Flashcard module (frontend and backend) for routing, data loading, progress saving, quizzes, usage limits, feature flags, analytics, TTS and admin upload. Do not introduce new architecture, libraries or patterns.
- Where this document names an existing file or function, mirror it. If something in the codebase differs from what is described here, **the codebase wins for *how*; this document wins for *what* the learner sees and how the feature behaves.**
- All learner-facing content comes from the JSON in `content/`. Do not rewrite German text, translations or answers.
- A clickable reference of the intended behaviour is live at **https://nursing-german.vercel.app**. It is a throwaway prototype: use it to see behaviour, not code. Add `?audit` to the URL to see the correct quiz answers highlighted.

---

## 1. What the feature is

Skillcase learners are nurses preparing to work in Germany. The existing A1 modules teach general German. **Nursing German** teaches the German a nurse needs on the ward from day one, all within A1 grammar:

- hospital words, chart abbreviations, roles, places, equipment, organs, false friends
- short exchanges with patients, colleagues, doctors and visitors
- reading real ward documents (medication plan, vital-signs chart, duty roster…)
- spelling names on the phone
- emergency phrases

It is **one linear path of 22 chapters**. Each chapter **teaches first with flashcards, then asks questions** about exactly what it taught. Passing a chapter's quiz unlocks the next chapter. The learner never has to choose what to study.

| | |
|---|---|
| Chapters | 22 |
| Flashcards | 419 |
| Quiz questions (pool) | 474 |
| Images | 356 (one per flashcard, reused by that card's questions) + 1 cover |
| Explanation language | English only |
| German level | A1 only |

---

## 2. Where it lives in the app

| What | Where / how (mirror existing) |
|---|---|
| **Entry tile** | Add a tile to `a1RevampFeatures` in `src/pages/landing/components/FeatureCardsGrid.jsx`, same shape as the other A1 tiles: `id: "a1-revamp-nursing"`, `title: "Nursing German"`, `description: "Ward words, phrases and documents for nurses"`, `link` to the new chapter-select route. Use `content/cover.jpg` as the tile/header image, added the way other feature images are added to `assets/images`. |
| **Feature flag** | Gate the tile and routes with `useFeatureFlags().isFeatureEnabled(...)`, the same way `study_notes` is gated. Suggested key: `nursing_german`. |
| **Usage limits** | Register the module like the other A1 modules: add `"a1-revamp-nursing": { level: "A1", module_key: "nursing" }` to `MODULE_MAP` in `FeatureCardsGrid.jsx`, the matching entry in the backend `MODULE_REGISTRY` (`util/usageLimits.js`), and use `useUsageLimitModule("A1", "nursing")` on the screens, exactly as `A1FlashcardSelect` / `A1Flashcard` use `("A1", "flashcard")`. |
| **Routes** | Two routes next to the A1 flashcard routes in `App.jsx`, loaded with `lazyScreen(...)`, e.g. `/a1/nursing` (chapter select) and `/a1/nursing/:chapterId` (chapter runner). |
| **Chapter select screen** | Mirror `src/pages/a1/flashcard/A1FlashcardSelect.jsx` and render with `src/components/a1/ChapterSelectTemplate.jsx`. |
| **Chapter runner** (flashcards + quick check + quiz) | Mirror `src/pages/a1/flashcard/A1Flashcard.jsx` with `A1FlashcardDeck` and `A1FlashcardCard` (`src/components/a1/`). |
| **API client** | Mirror the flashcard functions in `src/api/a1Api.js` (`getFlashcardChapters`, `getFlashcards`, `saveFlashcardProgress`, `generateMiniQuiz`, `generateFinalQuiz`, `submitFlashcardQuiz`) with their own cache tag, e.g. `a1:nursing`. Backend endpoints follow the existing `/a1/flashcard/*` equivalents. |
| **Content upload** | Mirror the existing admin upload used for A1 modules (`/admin/a1/upload/{module}`, JSON file + images ZIP, images matched **by filename**). Each chapter folder here is one upload (§11). |
| **Audio** | Use the existing `useTextToSpeech` hook (`/tts/speak` with browser fallback). |
| **Streaks** | Same as A1 Flashcards (`FloatingStreakCounter`, `StreakCelebrationModal`): card advances count toward the daily goal. |
| **Analytics** | `useFirstPartyAnalytics`, same events as A1 Flashcards (§10). |
| **Progress bar** | Same 20-card segmented progress bar as the A1 flashcard runner. |

---

## 3. Teaching rules (must hold everywhere)

1. **Teach first, then ask.** Each chapter: flashcards → quiz. A quick check after every 20 cards only asks about cards already seen.
2. **Only ask what the chapter taught.** Every question has `card_id` pointing to a card in the same chapter. Never mix questions from other chapters into a chapter quiz.
3. **Questions are in words; options are text.** A picture is only context above the question. **Never use pictures as answer options, and never ask a question with a picture alone.** Pictures are ambiguous.
4. **One path, no choices.** No menus of content types. The only learner decisions are Continue / Try again / Review the cards.
5. **Content is fixed.** German, English, answers and card order come from the JSON as-is.

---

## 4. Learner flow

```
German Practice → Nursing German tile
  → Chapter list (22 chapters, only the next one unlocked)
    → Chapter N
        flashcards (in JSON order)
          └ every 20 cards → Quick check (5 questions on cards seen so far) → back to cards
        last card → Chapter quiz
          ≥ 70% → Chapter complete → "Start Chapter N+1" (next chapter unlocked)
          < 70% → "Try the quiz again" | "Review the cards" (next chapter stays locked)
```

---

## 5. Screens and behaviour

### 5.1 Chapter select
Render with `ChapterSelectTemplate` exactly like A1 Flashcards:
- `title`: "Nursing German", `subtitle`: "German for your first weeks on the ward"
- `headerImage`: `cover.jpg`
- One entry per chapter from `content/index.json` in `chapter_number` order; `chapter_name` = `title_en`, `module_number` = `chapter_number`.
- **Progress** via `getProgress`: `current` = cards reached (saved index + 1), `total` = number of cards, completed when the chapter quiz is passed.
- **Locking** via `isChapterLocked`: chapter 1 is always open; chapter N is locked until chapter N−1's quiz is passed (`unlock.requires_chapter`). Locked chapters show the existing "Locked" badge and lock icon and cannot be opened.
- Tapping an unlocked chapter opens the runner at the saved position.

### 5.2 Flashcards (chapter runner)
Use the existing deck and card components (`A1FlashcardDeck` / `A1FlashcardCard`) and controls (previous, Shuffle, Reset, next/Finish), swipe, tap to flip, header "Flashcards  n/total" and the 20-segment progress bar.

**Front of every card:** image (top half) · German text (`front.german`) · speaker button · "Tap to flip". For phrase/pattern/document/spelling cards, show `front.label` as a small tag on the image (e.g. "PATIENTS ASK", "PATTERN · SHOW THE WAY", "WARD DOCUMENT").

**Back of every card (gold):** always the same 4 parts, in the same positions:

| Slot | Content |
|---|---|
| 1 | Label **"Meaning"** + `back.meaning_en` |
| 2 | divider |
| 3 | Label `back.label` + `back.german` (bold, italic) + `back.english` (small) + speaker button (plays `audio.back`) |
| 4 | `back.note` (small, optional) |

This is the existing card back (Meaning + Example) with the second label taken from `back.label` instead of always "Example". Labels in the content: `Example`, `You answer`, `You note down`, `When`, `Tip`, `Key words`, `Letters`, `Say it`.

**Card types (`type`)**

| type | Front shows | Extra fields | Back label |
|---|---|---|---|
| `word` | the word; colour the article (der/die/das) as the product does, or plain | `word.article`, `word.plural`, `word.false_friend` (show a small "False friend" pill on the back when true) | Example |
| `pattern` | a sentence pattern; the part in `[brackets]` in `front.pattern_de` is the swappable part. Highlight it and remove the brackets. `front.german` is the same sentence without brackets. | `goal_id` | Tip |
| `phrase` | what a patient/colleague/doctor/visitor says (`front.speaker`, `front.speaker_name`), or what *you* say (`front.label` = "You say") | `goal_id`, `replies[]` (all correct replies; the back shows the first) | You answer / You note down / When |
| `document` | the document title (`front.german`) over its image | `document` (§6) | Key words |
| `spelling` | "Wie schreibt man das?" over the image; the tag shows the letters | `spelling.name`, `spelling.letters[]` | Letters |
| `emergency` | the emergency phrase | — | Say it |

**Rules**
- Card order = `order`. Shuffle only reorders the remaining cards; Reset returns to card 1 **and** resets the saved position (A1 behaviour).
- Save progress on every advance the same way `saveFlashcardProgress` does (`currentIndex`, `isCompleted`, `advanced`).
- Reopening a chapter resumes at the saved card.
- Every card has an image; the layout must not shift between cards.

### 5.3 Quick check (every 20 cards)
- Trigger: the existing A1 rule, when advancing to card index 20, 40, … (`shouldOpenTestPrompt`).
- Intro with Maya: "Quick check!" / "Before you forget… answer these!" / Start.
- **5 questions** from `questions` whose `card_id` belongs to a card with `order ≤ checkpoint`. Prefer word and phrase questions; for the emergency chapter use `emergency_translate`.
- No pass mark, no rewards. After the last question, return to the deck.
- If the learner leaves mid-check and returns, show the quick check again (don't skip it).

### 5.4 Chapter quiz
- Starts after the last card (intro with Maya: "Chapter quiz", one line, Start).
- **Question selection per attempt**, from `questions` using `rules.quiz_composition`:

| Chapter kind | Selection |
|---|---|
| Normal | Up to **4 word cards** → one question each (alternate `translate_to_german` / `translate_to_english`); up to **8 phrase cards** → one question each (pick from that card's questions); **2 questions per document card**; **all spelling** questions. Shuffle the result. |
| Emergency (`quiz_composition.emergency_translate`) | **10 random** `emergency_translate` questions, **8-second timer** each. |

  `rules.quiz_questions_per_attempt` gives the expected size. A retry draws a new selection.
- **Answer flow** (reuse the existing A1 quiz UI: option rows, Check button, result feedback):
  1. Select an option → **Check** becomes active.
  2. Correct → green feedback, the correct answer, `feedback_de` if present (play it with the learner voice), **Next**.
  3. Wrong → red feedback, **Try again** on the same question. **Only the first attempt counts toward the score.**
  4. `emergency_translate`: a wrong answer or timeout shows the correct answer and **Next** (no retry).
- **Pass:** first-try score ≥ `rules.quiz_pass_mark` (0.7). Mark the chapter complete and unlock the next chapter. Show "Chapter N complete!", the score, and a single button **Start Chapter N+1** (last chapter: back to the chapter list).
- **Fail:** "Almost there", "x of y right · 70% needed to open the next chapter", buttons **Try the quiz again** and **Review the cards**.
- Rewards (coins/XP) and the quiz-submit call follow whatever the A1 flashcard quiz does today (`submitFlashcardQuiz`). Don't create a separate economy.

### 5.5 Question card: one layout for every question type
Every question renders in the same structure (like the existing MCQ question in the A1 quiz):

```
[ image  (question.image, same image as its flashcard) ]   ← optional context, fixed height
LABEL                                 (question.label, small uppercase)
Question text                         (see table)
[🔊] German line + English line       (only when the type has audio)
(A) option   (B) option   (C) option   (D) option          ← text only
[ Check ]
```

| type | Question text | German line / audio | Options |
|---|---|---|---|
| `translate_to_german` | `question_en` (e.g. How do you say "Ward" in German?) | — | German |
| `translate_to_english` | `question_en` (e.g. What does "die Station" mean?) | `german` + 🔊 `audio` | English |
| `choose_reply`, `choose_reply_sie_du` | `speaker_name`: „`prompt_de`" | 🔊 `audio` + `prompt_en` | German replies |
| `picture_choice` | `speaker_name`: „`prompt_de`" | 🔊 `audio` + `prompt_en` | German key words (text; **no pictures**) |
| `body_part_choice` | `speaker_name`: „`prompt_de`" | 🔊 `audio` + `prompt_en` | German body parts |
| `listen_and_note` | `speaker_name`: „`prompt_de`" | 🔊 `audio` + `prompt_en` | values (e.g. 130/85) |
| `situation_choice` | `question_en` (a situation) | — | German sentences |
| `document_question` | `question_en` | — | English. Show the document from card `document_card_id` in place of the image; tap to open it full size. |
| `spelling` | `question_en` ("Which name is spelled?") + `prompt_de` | 🔊 `audio` (letters, pause 400 ms between letters) | names |
| `emergency_translate` | `question_en` | — | German phrases; show an 8 s countdown (`time_limit_seconds`) |

**Rules:** shuffle options on every display; `answer` is always one of `options`; auto-play the question audio once when it opens (if the type has audio).

### 5.6 States
Loading, error, offline, usage-limit lock and feature-flag-off states behave exactly like A1 Flashcards. If an image fails to load, keep the frame size (no broken-image icon).

### 5.7 Layout requirements
- Flashcard, quiz and result screens must fit a **375×700** screen **without scrolling**. The quiz image height shrinks on short screens; the document opens in an overlay instead of making the page longer.
- Card elements (image, text, speaker, hint) stay in the same position on every card, front and back.
- Images are 3:2 landscape; show them with `object-fit: cover` in their frame.

---

## 6. Documents inside cards

`document` cards (10 in total) carry a structured document to render as a paper-like sheet:

```jsonc
"document": {
  "title_de": "Medikamentenplan",
  "title_en": "Medication plan",
  "blocks": [
    { "type": "heading",  "text": "MEDIKAMENTENPLAN" },
    { "type": "subtitle", "text": "Weber, Erika · geb. 03.05.1944 · Zimmer 1" },
    { "type": "table", "header": ["Medikament","Dosis","mo","mi","ab","na"],
      "rows": [["Metformin","500 mg","1","0","1","0"],
               ["Paracetamol","500 mg",{"text":"bei Bedarf","colspan":4}]],
      "highlight": [] },
    { "type": "fields", "items": ["Yılmaz, Emre","* 12.03.1981","ALLERGIE: Penicillin"], "highlight": ["ALLERGIE: Penicillin"] },
    { "type": "text", "text": "Vor dem Betreten:" },
    { "type": "list", "items": ["Hände desinfizieren","Kittel · Maske · Handschuhe"] }
  ],
  "key_words": [ { "de": "1-0-1-0", "en": "morning and evening" } ]
}
```
- A table cell is a string, or `{text, colspan}` when it spans columns. `header` may be empty.
- Values listed in `highlight` are shown in red/bold (e.g. an abnormal blood pressure).
- On the flashcard, the card image is shown; on `document_question`, show the rendered document so the learner can read it.

---

## 7. Speakers and audio

Every card has `audio.front` and `audio.back`, and every question with sound has `audio`: `{ "text", "voice", "lang": "de-DE" }`. Play them with `useTextToSpeech`. The `voice` values are logical keys; map them to the TTS voices the backend supports (if only one German voice exists, use it for all):

| voice key | Character | Suggested voice |
|---|---|---|
| `patient_old_female` | Frau Weber, 82, patient | older female |
| `patient_old_male` | Herr Schmidt, 67, patient | older male |
| `patient_male` | Herr Yılmaz, 45, patient | male |
| `colleague_female` | Lena, nurse colleague | young female |
| `doctor_male` | Dr. Braun, doctor | male |
| `visitor_female` | Anna Weber, visitor | female |
| `learner_nurse_female` | the learner / model answers / words | clear female, slightly slower |

Spelling audio: read the letters with a short pause between them (`pause_between_items_ms`).

---

## 8. Progress and unlock rules

| Item | Rule |
|---|---|
| Card position | Highest card index reached; saved on every advance; Reset sets it back to 0 |
| Quick checks | Remember which checkpoints (20, 40…) were completed |
| Chapter complete | Chapter quiz passed (first-try score ≥ 0.7) |
| Best score | Keep the best attempt; replaying never un-passes a chapter |
| Unlocked | Chapter 1 always; chapter N when chapter N−1 is complete |
| Current chapter | First chapter that is not complete (shown on the entry tile: "Chapter X of 22") |

Store these the same way A1 flashcard progress (`current_index`, `is_completed`, `final_quiz_passed`) is stored today.

---

## 9. Content rules (if anyone edits content later)
- A1 grammar only: present tense, *Sie*-imperative, modal verbs, *kein/nicht*, accusative, dative only in fixed phrases (*Ich helfe Ihnen*, *mit dem Herzen*), *hatte/war*. No perfect tense, no subordinate clauses, no subjunctive, no passive.
- *Sie* with patients, visitors and doctors; *du* with nurse colleagues.
- *die Pflegekraft* = **Nurse** (gender-neutral). Never translate it as "Sister".
- Every German line has English. Every question's `answer` is in `options`. Every question's `card_id` is a card in the same chapter.
- Images: 3:2, realistic photo style, no text in the image, adults only; the image must show exactly what the card teaches.

---

## 10. Analytics

Use `useFirstPartyAnalytics` like A1 Flashcards, with `module: "a1_nursing"` (or the module key convention the codebase uses):

| Event | When | Properties |
|---|---|---|
| `learning_module_started` | chapter runner opened | chapter_number, resume_index, total_cards |
| `learning_module_submitted` | chapter quiz submitted | chapter_number, score, passed, attempt |
| `flashcard_quiz_submitted` | quick check / chapter quiz submitted (same as A1) | chapter_number, quiz_type (`mini`/`final`), right, total |
| existing card-flip / audio events | as A1 Flashcards emits them | + chapter_number, card_type |

---

## 11. Content package

```
nursing-german-a1/
├── IMPLEMENTATION.md          ← this file
└── content/
    ├── index.json             ← chapter list in order (+ totals)
    ├── cover.jpg              ← header / tile image
    ├── chapter-01-who-i-am-at-work/
    │   ├── chapter.json       ← the chapter (cards + questions)
    │   ├── w-nurse.jpg        ← every image the chapter uses, referenced by filename
    │   └── …
    ├── chapter-02-hospital-places/
    └── … chapter-22-discharge-day/
```

- **One folder = one chapter = one upload.** `chapter.json` references its images by **filename only** (`"image": "w-ward.jpg"`); every referenced file is in the same folder and there are no extra files. If the existing uploader expects a ZIP of images, zip the `.jpg` files of that folder.
- IDs are stable: chapter `nursing-a1-ch05`, cards `ch05-c01…`, goals `ch05-g1…`, questions `ch05-q001…`. Use them for progress and analytics.
- `schema_version: 1`.

### 11.1 `chapter.json`

```jsonc
{
  "schema_version": 1,
  "module": "nursing_german",
  "cefr": "A1",
  "chapter_id": "nursing-a1-ch02",
  "chapter_number": 2,
  "title_en": "Hospital places",
  "title_de": "Im Krankenhaus",
  "unlock": { "requires_chapter": 1, "requires_quiz_pass": true },   // chapter 1: null / false
  "rules": {
    "quick_check_every_cards": 20,
    "quick_check_questions": 5,
    "quiz_pass_mark": 0.7,
    "quiz_questions_per_attempt": 12,
    "quiz_composition": { "word_cards": 4, "phrase_cards": 8, "document_questions_per_document": 2, "spelling": "all" }
    // emergency chapter: { "emergency_translate": 10 }
  },
  "goals": [ { "id": "ch02-g1", "title_en": "Show the way", "pattern_de": "[Die Toilette] ist hier rechts.",
               "pattern_en": "The toilet is here on the right.", "tip_en": "hier = here · dort = over there …" } ],
  "cards": [ /* Card */ ],
  "questions": [ /* Question */ ],
  "images": [ "p-02-01.jpg", "w-ward.jpg" ]
}
```

### 11.2 Card

```jsonc
{
  "id": "ch02-c15",
  "order": 15,
  "type": "phrase",                 // word | pattern | phrase | document | spelling | emergency
  "goal_id": "ch02-g1",             // pattern + phrase cards only
  "image": "p-02-01.jpg",
  "front": {
    "german": "Wo ist die Toilette?",
    "label": "Patients ask",        // tag on the image (null for words)
    "speaker": "weber",             // weber | schmidt | yilmaz | lena | braun | anna | nurse | null
    "speaker_name": "Frau Weber",
    "pattern_de": "…[swappable]…"   // pattern cards only
  },
  "back": {
    "meaning_en": "Where is the toilet?",
    "label": "You answer",
    "german": "Die Toilette ist hier rechts.",
    "english": "The toilet is here on the right.",
    "note": "Key word: die Toilette = the toilet"
  },
  "audio": {
    "front": { "text": "Wo ist die Toilette?", "voice": "patient_old_female", "lang": "de-DE" },
    "back":  { "text": "Die Toilette ist hier rechts.", "voice": "learner_nurse_female", "lang": "de-DE" }
  },
  // type-specific:
  "word":     { "article": "die", "plural": false, "false_friend": false },   // word
  "replies":  [ { "label": "You say", "german": "…", "english": "…" } ],      // phrase
  "document": { … },                                                           // document (§6)
  "spelling": { "name": "Weber", "letters": [ { "letter": "W", "say": "weh" } ] }  // spelling
}
```

### 11.3 Question

```jsonc
{
  "id": "ch02-q027",
  "type": "choose_reply",
  "label": "What do you answer?",
  "card_id": "ch02-c15",            // the flashcard this question tests (same chapter)
  "image": "p-02-01.jpg",           // same image as that flashcard (context only)
  "speaker": "schmidt", "speaker_name": "Herr Schmidt",
  "prompt_de": "Wo ist die Toilette?",
  "prompt_en": "Where is the toilet?",
  "question_en": null,              // used by translate/situation/document/spelling/emergency types
  "german": null,                   // translate_to_english only
  "audio": { "text": "Wo ist die Toilette?", "voice": "patient_old_male", "lang": "de-DE" },
  "options": ["Hier rechts, die zweite Tür.", "Um acht Uhr.", "Ja, bitte."],
  "answer": "Hier rechts, die zweite Tür.",
  "feedback_de": null, "feedback_en": null,   // optional: what the nurse says after a correct answer
  "time_limit_seconds": null,       // 8 for emergency_translate
  "document_card_id": null          // document_question: card holding the document
}
```
Fields that don't apply to a type are absent or `null`.

### 11.4 Chapters

| # | Folder | Title | Cards | Questions |
|---|---|---|---|---|
| 1 | chapter-01-who-i-am-at-work | Who I am at work | 18 | 20 |
| 2 | chapter-02-hospital-places | Hospital places | 25 | 35 |
| 3 | chapter-03-objects-and-equipment | Objects & equipment | 24 | 32 |
| 4 | chapter-04-the-body | The body | 13 | 10 |
| 5 | chapter-05-inside-the-body | Inside the body (organs & glands) | 29 | 42 |
| 6 | chapter-06-emergency-german | Emergency German | 25 | 25 |
| 7 | chapter-07-symptoms-and-pain | Symptoms & pain | 17 | 16 |
| 8 | chapter-08-numbers-and-vital-signs | Numbers & vital signs | 22 | 28 |
| 9 | chapter-09-times-and-shifts | Times & shifts | 16 | 17 |
| 10 | chapter-10-medication-and-food | Medication & food | 31 | 46 |
| 11 | chapter-11-instructions | Instructions | 16 | 15 |
| 12 | chapter-12-basic-care | Basic care | 16 | 16 |
| 13 | chapter-13-talking-to-colleagues | Talking to colleagues | 22 | 28 |
| 14 | chapter-14-comforting-patients | Comforting patients | 14 | 12 |
| 15 | chapter-15-admitting-a-patient | Admitting a patient | 23 | 29 |
| 16 | chapter-16-walking-and-falls | Walking & falls | 14 | 12 |
| 17 | chapter-17-phone-calls | Phone calls | 16 | 14 |
| 18 | chapter-18-hygiene-and-isolation | Hygiene & isolation | 16 | 17 |
| 19 | chapter-19-toilet-and-continence | Toilet & continence | 17 | 18 |
| 20 | chapter-20-visitors-and-relatives | Visitors & relatives | 15 | 14 |
| 21 | chapter-21-the-night-round | The night round | 15 | 13 |
| 22 | chapter-22-discharge-day | Discharge day | 15 | 15 |

(Exact numbers are in `content/index.json`.)

---

## 12. Acceptance checklist

**Flow**
- [ ] Tile visible only when the feature flag is on; opens the chapter list.
- [ ] New user: only chapter 1 unlocked; locked chapters can't be opened.
- [ ] Leaving after 5 cards and returning resumes at card 6; the list shows the progress.
- [ ] Previous, flip, Shuffle (keeps position), Reset (card 1 + saved position reset) work.
- [ ] Quick check appears at card 20 (and 40…), uses only cards already seen, then returns to the deck.
- [ ] Last card → chapter quiz. Wrong → Try again (not scored). < 70% → fail screen; next chapter stays locked. ≥ 70% → chapter complete, next chapter unlocked, "Start Chapter N+1".
- [ ] Emergency chapter: 10 questions with an 8 s countdown; timeout = wrong + correct answer shown.
- [ ] Passing chapter 22 ends the path.

**Content**
- [ ] All 22 chapters upload without missing images.
- [ ] Every card shows its image; every question shows its label, question text and text options.
- [ ] No question uses pictures as options; no question is a picture alone.
- [ ] Every quiz question belongs to a card in the same chapter.
- [ ] Audio plays for card fronts, backs and question prompts.

**Layout**
- [ ] Flashcard, quiz and result screens fit 375×700 without scrolling.
- [ ] Card image, text, speaker and hint positions don't move between cards; every back uses the same 4-slot layout.

---

## 13. Do not
- Don't add a menu of content types (words / phrases / documents…). It is one path.
- Don't use images as answer options or as the only question.
- Don't generate quiz questions from other chapters or from general A1 content.
- Don't change the content text, answers or translations.
- Don't create new architecture, state libraries, API styles or design-system components where an A1 Flashcard equivalent exists.

---

## 14. Decisions to confirm with the product owner (defaults in brackets)
1. Free or Premium, and from which chapter? *(same as other A1 modules via usage limits)*
2. Rewards for chapter completion? *(same as the A1 flashcard quiz today)*
3. Pass mark for the emergency chapter? *(70%, like the others)*
