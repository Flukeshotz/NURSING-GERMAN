# PRD: Nursing German (A1): developer specification

| | |
|---|---|
| Product | Skillcase learning app |
| Feature | Nursing German, a nursing-only practice mode |
| Level | CEFR A1 (V1) |
| Status | Ready for build |
| Prototype | https://nursing-german.vercel.app (open with `?audit` to see correct answers marked) |
| Repo | https://github.com/Flukeshotz/NURSING-GERMAN |
| Content | `content/levels/level-01.json` … `level-21.json` + one picture zip per level |
| Content format | [`content/SCHEMA.md`](../content/SCHEMA.md) |
| Audit | [`docs/AUDIT.md`](AUDIT.md) |
| Frontend target | `SkillCase-Frontend` (React 19, Vite, Tailwind v4, Redux Toolkit, Capacitor Android) |

---

## 1. TL;DR for developers

Build a new practice mode that **reuses the A1 Flashcards architecture**:

1. **Entry:** a *Nursing German* card at the top of *German Practice*.
2. **Level list:** 21 levels unlocked in order. Reuse `ChapterSelectTemplate`.
3. **Level runner:** flashcards (reuse `A1FlashcardDeck` / `A1FlashcardCard`) → a quick check every 20 cards → level quiz → pass at 70% → the next level unlocks.
4. **Every quiz question is built from the level's own cards.** Questions are asked in words; options are always text; the card's photo is supporting context.
5. **Backend:** mirror the `/a1/flashcard/*` endpoints under `/nursing/*` (§10). Content is imported from the level JSON files (§9).
6. **Audio:** existing `/tts/speak` with one German voice per character (§12). Pictures: CDN (§13).

---

## 2. Problem

Skillcase learners are internationally trained nurses, mostly from India, preparing to work in Germany. The app teaches general A1 German, but not the language nurses need on the ward from day one:

- Hospital words and chart abbreviations (nurses say *BP*, *drip*, *OT*; German charts say *RR*, *Infusion*, *OP*)
- Short exchanges with patients, colleagues, doctors and relatives
- Reading ward documents (medication plans `1-0-1-0`, vital signs charts, handover notes)
- Emergency phrases that must come out instantly

All of it fits A1 grammar; none of it is in a general A1 course.

## 3. Goals and success metrics

**Goal:** A1 learners master nursing-specific German through a practice mode that works exactly like the modes they already use.

| Metric | Definition | Target (90 days after launch) |
|---|---|---|
| Adoption | A1 users who open Nursing German ÷ A1 active users | ≥ 40% |
| Level 1 completion | Users who pass Level 1 ÷ users who start it | ≥ 70% |
| Depth | Users who pass Level 5 ÷ users who start Level 1 | ≥ 35% |
| First-attempt pass rate | Level quizzes passed on attempt 1 | 60–80% |
| Session length | Median minutes per session in the mode | 6–10 |
| Quality | Crash-free sessions in the mode | ≥ 99.5% |

## 4. Users and constraints

- A1 learners, mostly on Android phones (Capacitor app), often on shift, studying in short sessions.
- **Explanations in English only.** Learners come from many regions; no regional languages.
- Small screens: every screen must fit on a 375×700 viewport without scrolling (§15).

## 5. Scope

### In scope (V1)
- 21 levels, 378 flashcards, 419 quiz questions in the pool, 319 photos (§9, Appendix A)
- Level list, flashcard runner, quick check, level quiz, results
- Server-side progress, unlock, coins, streak integration, analytics
- Audio for every German line
- Feature flag and usage limits (same as other A1 modules)

### Out of scope (V1)
- A2 / B1 / B2 nursing content
- Speaking or pronunciation scoring
- Ward culture content (removed)
- Spaced repetition across levels (open question §20)
- Content management UI (content is imported from JSON)

---

## 6. Teaching method (non-negotiable rules)

| # | Rule | How it shows in the product |
|---|---|---|
| P1 | **Teach first, then ask.** | Every level: flashcards → quiz. Quick check after every 20 cards only asks about cards already seen. |
| P2 | **Only ask what the level taught.** | Every question has `from_card`; it must point to a card in the same level. |
| P3 | **Questions in words, options in text.** | Pictures never replace the question and are never options (they are ambiguous). The card photo is shown as context. |
| P4 | **One path, no choices.** | No content-type menu. The only decisions: Continue, Try again, Review the cards. |
| P5 | **A1 only.** | Present tense, *Sie* imperative, modal verbs, *kein/nicht*, accusative; dative only as fixed phrases; *hatte/war* allowed. No perfect tense, subordinate clauses, subjunctive or passive. |
| P6 | **Formal with patients, informal with colleagues.** | *Sie* with patients, visitors, doctors; *du* with nurse colleagues. |

---

## 7. Screens and acceptance criteria

The frontend reuses existing components wherever possible:

| Screen / part | Reuse | New |
|---|---|---|
| Entry card | German Practice grid card | Card content, "NEW" badge, "Level X of 21" |
| Level list | `ChapterSelectTemplate` | Header photo `h-nursing-german.jpg`, "Level N: Title" names |
| Flashcard deck | `A1FlashcardDeck` (stack, swipe, flip, prev/shuffle/reset/next) | — |
| Flashcard faces | `A1FlashcardCard` (front photo + German + speaker; gold back) | Back layout variants (§7.3) |
| Progress bar | `components/a2/ProgressBar` (20-card segments) | — |
| Quiz intro | Existing Maya intro pattern | Copy |
| Question card | — | `NursingQuestionCard` (§7.5) |
| Option rows | Lesson `OptionRow` (lettered, selected/correct/incorrect) | — |
| Result modal | `LessonResultModal` | — |
| Level results | Lesson result/summary pattern + coin | Copy |
| Streak | `FloatingStreakCounter`, `StreakCelebrationModal` | — |
| Audio | `useTextToSpeech` (`/tts/speak` → browser fallback) | `voice` per speaker (§12) |
| Analytics | `useFirstPartyAnalytics` | Events (§14) |
| Limits | `useUsageLimitModule("A1", "nursing")` | Module key |

### 7.1 Entry card (German Practice)
- Full-width card above the existing mode tiles: navy gradient, cross icon, title **Nursing German**, subtitle **Level {current} of 21 · ward words and phrases**, "NEW" pill for 30 days.
- Tap → `/a1/nursing`.

**Acceptance**
- [ ] Card shows the user's current level (first level not passed; "21 of 21" when all passed).
- [ ] Hidden when feature flag `nursing_german_a1` is off.

### 7.2 Level list: `/a1/nursing`
- Back → German Practice. Title "Nursing German".
- Header photo (150 px, gradient to white), "A1 · Nursing German", subtitle "German for your first weeks on the ward. Levels open one after another."
- Carousel: one progress bar per level (gold in progress, green passed), label "Lv. N".
- Rows: "Level N: {title_en}" + badge + chevron/lock.
  - Locked: grey "Locked" + lock icon, 60% opacity, not tappable.
  - In progress: gold badge "{current}/{total}" (see audit F-11: show "Quiz left" when all cards are seen but the quiz is not passed).
  - Passed: green "Done".
- Sticky button: **Start Level N: Title** or **Continue Level N: Title** (N = first not-passed level).

**Acceptance**
- [ ] New user: only Level 1 unlocked; button "Start Level 1: Who I am at work".
- [ ] After passing Level N, Level N+1 unlocks immediately (optimistic), confirmed by the server.
- [ ] Current level row highlighted and scrolled into view.
- [ ] Loading: 6 skeleton rows (same as `ChapterSelectTemplate`). Error: retry message.

### 7.3 Flashcard runner: `/a1/nursing/:levelId`
Layout top to bottom, fixed: back row (Back · "Level N: Title") → "Flashcards" + "n/total" → segmented progress bar → deck → controls (‹ · Shuffle · Reset · › / Finish).

**Card front (all types):** photo 3:2 on top (tag chip for phrase/pattern/document/spelling cards), German text centred in a 2-line slot, speaker button, "Tap to flip". Positions do not move between cards.

**Card back (gold, all types):** `MEANING` label + English → divider → one labelled block (label, German line, English line, speaker) → optional note → "Tap for German".

| Card type | Front German | Back label | Back German | Back English | Note |
|---|---|---|---|---|---|
| `word` | word with article colour | Example | example sentence | its English | chart hint or tip (e.g. "On charts: RR") |
| `pattern` | sentence with the swappable part highlighted | Tip | pattern sentence | tip | — |
| `phrase` (someone speaks) | what the patient/colleague/doctor says | You answer / You note down | correct reply | its English | key word, if any |
| `phrase` (you speak first) | what you say | When | what you say | the situation | — |
| `document` | document name | Key words | key words joined | meanings joined | — |
| `spelling` | "Wie schreibt man das?" | Letters | W · E · B · E · R | weh · eh · beh · eh · err | — |
| `emergency` | phrase | Say it | phrase | "Short and loud. Say it twice." | — |

**Interactions**
- Tap card → flip. Swipe left / › → next. Swipe right / ‹ → previous. Enter/Space flips; ←/→ navigate.
- Speaker buttons play audio without flipping.
- Shuffle reorders the remaining cards only. Reset → card 1 **and** resets saved position (audit F-07).
- Every 20 cards (20, 40…) → Quick check (§7.4), then continue.
- After the last card → Level quiz intro (§7.5).

**Acceptance**
- [ ] Deck order follows the level JSON `flashcards[].order`.
- [ ] Position saved on every advance (debounced, like `saveFlashcardProgress`).
- [ ] Reopening a level resumes at the saved card.
- [ ] Every card shows its photo; the photo fills the 3:2 frame (no letterboxing).
- [ ] German text never overflows its slot (2-line clamp); back never overflows.
- [ ] Screen fits 375×700 without scrolling.

### 7.4 Quick check
- Trigger: advancing past card index 20, 40, … when not yet completed for that checkpoint.
- Intro: Maya, "Quick check!", "Before you forget… answer these!", **Start**.
- 5 questions from cards seen so far (§8.3). No pass mark; no coins; then back to the deck.

**Acceptance**
- [ ] Only uses cards with `order` ≤ checkpoint.
- [ ] Completing it records the checkpoint; resuming later does not skip an uncompleted checkpoint (audit F-06).

### 7.5 Level quiz and question card
- Intro: Maya, "Level quiz" / "Emergency drill", one-line explanation, **Start**.
- Header: "Quiz" + "n/total" + segmented progress bar.

**`NursingQuestionCard`**, one layout for every question type:

```
┌──────────────────────────────┐
│  photo (3:2 frame, height     │  ← card photo, or the document for document questions
│  clamps to screen) [timer]    │    (tap document → full-size overlay)
├──────────────────────────────┤
│  LABEL (uppercase, 11px)      │
│  Question text (16–17px bold) │
│  [🔊] German line / English   │  ← only when there is audio or a German prompt
└──────────────────────────────┘
 (A) option          ← text only, OptionRow
 (B) option
 (C) option
 [ Check ]           ← sticky bottom
```

| Question type | Label | Question text | Sub line | Options |
|---|---|---|---|---|
| `translate_to_german` | Translate into German | How do you say "{english}" in German? | — | German words (article colours) |
| `translate_to_english` | Translate into English | What does „{german}" mean? | 🔊 | English |
| `choose_reply` / `choose_reply_sie_du` | What do you answer? | {Name}: „{prompt_de}" | 🔊 + prompt_en | German replies |
| `situation_choice` | What do you say? | {prompt_en} | — | German sentences |
| `picture_choice` | What does this person need? | {Name}: „{prompt_de}" | 🔊 + prompt_en | German key words |
| `body_part_choice` | Where is the problem? | {Name}: „{prompt_de}" | 🔊 + prompt_en | German body parts |
| `listen_and_note` | What do you write down? | {Name}: „{prompt_de}" | 🔊 + prompt_en | values |
| `document_question` | Read the document · tap to zoom | {question_en} | — | English |
| `spelling` | Listen to the spelling | Which name is spelled? | 🔊 letters + „Wie schreibt man das?" | names |
| `emergency_translate` | Emergency · translate into German | How do you say "{english}" in German? | — | German phrases; **8 s timer** |

**Answer flow**
1. Select an option (blue selected state) → **Check** enabled.
2. Check → `LessonResultModal`:
   - Correct: green "Richtig!", correct answer, optional `feedback_de`, "+10 coins" on first try, **Next**. The nurse's line is spoken.
   - Wrong: red "Incorrect!", chosen answer, **Try again** (question stays; the retry does not count toward the score).
   - `emergency_translate`: a wrong answer or time-out shows the right answer and **Next** (no retry).
3. Auto-play `prompt_de` audio when a question opens (spelling: the letters).

**Acceptance**
- [ ] Every question shows a label, question text and text options; never a picture as an option.
- [ ] Options are shuffled per attempt; `answer` is always among them.
- [ ] Timer counts down visibly (ring) for emergency questions; at 0 the question is marked wrong.
- [ ] Screen fits 375×700 without scrolling (document opens in an overlay).

### 7.6 Level results
- Back row. Maya (thumbs up on pass), stars, title, score line.
- **Pass (≥ 70%)**: "Level N complete!", "{right} of {total} right", coins earned, "Next up: Level N+1: Title", button **Start Level N+1** (last level: **All levels done!** → level list).
- **Fail**: "Almost there", "{right} of {total} right · 70% needed to open the next level", buttons **Try the quiz again** and **Review the cards** (opens the deck at card 1).

**Acceptance**
- [ ] Pass unlocks the next level, awards coins once per level (idempotent server-side).
- [ ] Retry draws a new set of questions (§8.3).

### 7.7 States for every screen
| State | Behaviour |
|---|---|
| Loading | Skeletons (list), `ExerciseLayoutSkeleton` (runner/quiz) |
| Offline / request failed | Keep the local state; retry progress saves in the background; show a toast only if the user leaves |
| Usage limit reached | Same lock UI as other A1 modules (`useUsageLimitModule`) |
| Feature flag off | Entry card hidden; routes redirect to `/` |
| Audio unavailable | Speaker buttons stay; `useTextToSpeech` falls back to browser speech |
| Picture fails | Frame keeps its size with a neutral background; no broken-image icon |

---

## 8. Logic

### 8.1 Deck composition (already materialised in the JSON)
Order inside a level:
1. Word cards (level's hospital words)
2. For each goal (3): the pattern card, then that goal's phrase cards
3. Document cards
4. Spelling cards

Emergency level (5): 25 emergency cards.

### 8.2 Progress and unlock
| Field | Rule |
|---|---|
| `current_index` | Highest card index reached; updated on advance; reset to 0 by Reset |
| `quick_checks_done` | Set of checkpoints (20, 40…) completed |
| `cards_completed` | `current_index + 1 >= total_cards` |
| `quiz_passed` | Any attempt with score ≥ 0.7 |
| `best_score` | Max of attempt scores |
| `stars` | ≥ 0.95 → 3; ≥ 0.85 → 2; ≥ 0.7 → 1 (best attempt) |
| Unlocked | Level 1 always; Level N if Level N−1 `quiz_passed` |
| Current level | First level with `quiz_passed = false` |

### 8.3 Question selection (server-side, like `generateFinalQuiz`)
**Level quiz**, drawn from `quiz_pool`:

| Source | Count |
|---|---|
| Word questions | Up to 4 distinct word cards, alternating `translate_to_german` / `translate_to_english` |
| Phrase questions | Up to 8 distinct phrase cards (one question per card) |
| Document questions | 2 per document card |
| Spelling questions | All spelling questions |
| Emergency level | 10 random `emergency_translate` |

Shuffle the final list. `rules.quiz_questions_per_attempt` in each level JSON gives the expected size.

**Quick check**: up to 2 word + 3 phrase questions (emergency level: 5 emergency) from cards with `order ≤ checkpoint`; shuffle; take 5.

### 8.4 Scoring and rewards
| Event | Rule |
|---|---|
| First-try correct (level quiz) | +1 score, +10 coins |
| Retry after wrong | No score, no coins |
| Quick check | No score, no coins |
| Level passed | +20 coins, once per level |
| Streak | Card advances count toward the daily goal, same as A1 Flashcards |

---

## 9. Content and data model

### 9.1 Source files
- `content/levels/index.json`: level order and file names
- `content/levels/level-XX.json`: `flashcards[]` and `quiz_pool[]` (format: `content/SCHEMA.md`)
- `content/levels/level-XX-images.zip`: exactly the photos the level uses

### 9.2 Tables (suggested; mirror the A1 flashcard tables)

```sql
nursing_levels (
  id            serial primary key,
  level_number  int unique not null,        -- 1..21
  title_en      text not null,
  title_de      text not null,
  pass_mark     numeric not null default 0.7,
  quiz_size     int not null,
  content_version text not null,            -- e.g. "2026-09-17"
  is_active     boolean default true
);

nursing_cards (
  id            serial primary key,
  level_id      int references nursing_levels(id),
  sort_order    int not null,
  type          text check (type in ('word','pattern','phrase','document','spelling','emergency')),
  front_german  text not null,
  front_label   text,
  speaker       text,                        -- weber|schmidt|yilmaz|lena|braun|anna|nurse|null
  image_key     text not null,               -- e.g. w-bp.jpg
  back_meaning_en text not null,
  back_label    text not null,
  back_german   text,
  back_english  text,
  back_note     text,
  extra         jsonb                        -- article_word, false_friend, replies, pattern, document, spelling
);

nursing_questions (
  id            serial primary key,
  level_id      int references nursing_levels(id),
  card_id       int references nursing_cards(id),   -- resolved from from_card
  type          text not null,
  payload       jsonb not null,             -- question fields exactly as in quiz_pool
  answer        text not null
);

nursing_progress (
  user_id       uuid,
  level_id      int references nursing_levels(id),
  current_index int default 0,
  quick_checks_done int[] default '{}',
  quiz_passed   boolean default false,
  best_score    numeric default 0,
  stars         int default 0,
  coins_awarded boolean default false,
  updated_at    timestamptz default now(),
  primary key (user_id, level_id)
);

nursing_quiz_attempts (
  id            bigserial primary key,
  user_id       uuid,
  level_id      int,
  kind          text check (kind in ('quick_check','level_quiz')),
  question_ids  int[] not null,
  answers       jsonb,                      -- [{question_id, chosen, correct, first_try}]
  score         numeric,
  passed        boolean,
  created_at    timestamptz default now()
);
```

### 9.3 Import script
1. For each `level-XX.json`: upsert `nursing_levels`, replace its cards and questions in one transaction.
2. Resolve `from_card` → `card_id` by matching `front.german` (or `article_word`) within the level. Fail the import if any question does not resolve (rule P2).
3. Upload photos from the zip to the CDN under `nursing/a1/{content_version}/{image_key}`.
4. Validate: answer ∈ options; every `image_key` exists on the CDN; no duplicate options.

---

## 10. API (mirror `/a1/flashcard/*`)

All endpoints authenticated. `GET`s use `api.cachedGet` with cache tag `a1:nursing`; `POST`s invalidate it.

### `GET /a1/nursing/levels`
```json
{
  "current_level": 2,
  "levels": [
    { "id": 1, "level_number": 1, "title_en": "Who I am at work", "total_cards": 18,
      "current_index": 17, "quiz_passed": true, "stars": 3, "is_locked": false },
    { "id": 2, "level_number": 2, "title_en": "Hospital places", "total_cards": 25,
      "current_index": 4, "quiz_passed": false, "stars": 0, "is_locked": false },
    { "id": 3, "level_number": 3, "title_en": "Objects & equipment", "total_cards": 24,
      "current_index": 0, "quiz_passed": false, "stars": 0, "is_locked": true }
  ]
}
```

### `GET /a1/nursing/levels/:levelId/cards`
```json
{
  "level": { "id": 2, "level_number": 2, "title_en": "Hospital places", "pass_mark": 0.7 },
  "progress": { "current_index": 4, "quick_checks_done": [], "quiz_passed": false },
  "cards": [
    { "id": 101, "order": 1, "type": "word",
      "front": { "german": "die Station", "speaker": null, "label": null,
                 "image_url": "https://cdn…/nursing/a1/2026-09-17/w-ward.jpg" },
      "back": { "meaning_en": "Ward", "label": "Example", "german": "Ich arbeite auf Station 3.",
                "english": "I work on ward 3.", "note": null },
      "extra": { "article_word": "die Station", "false_friend": false } }
  ]
}
```
Returns 403 `LEVEL_LOCKED` if the level is locked.

### `POST /a1/nursing/progress`
```json
{ "level_id": 2, "current_index": 5, "advanced": true }
```
- `advanced: true` counts toward usage limits and streak (same as A1).
- `current_index` only increases, unless `"reset": true`.

### `GET /a1/nursing/levels/:levelId/quiz?kind=quick_check&checkpoint=20`
### `GET /a1/nursing/levels/:levelId/quiz?kind=level_quiz`
```json
{
  "attempt_id": 9001,
  "questions": [
    { "id": 555, "type": "choose_reply", "card_id": 114,
      "label": "What do you answer?", "speaker": "weber",
      "prompt_de": "Wo ist die Toilette?", "prompt_en": "Where is the toilet?",
      "image_url": "https://cdn…/p-02-01.jpg",
      "options": ["Hier rechts, die zweite Tür.", "Um acht Uhr.", "Ja, bitte."],
      "time_limit_seconds": null }
  ]
}
```
Options are shuffled server-side. **Answers are not sent** to the client.

### `POST /a1/nursing/quiz/check`
```json
// request
{ "attempt_id": 9001, "question_id": 555, "chosen": "Um acht Uhr.", "first_try": true }
// response
{ "correct": false, "answer": null, "feedback_de": null }
```
`answer` is returned only when correct, or for `emergency_translate` (no retry).

### `POST /a1/nursing/quiz/submit`
```json
// request
{ "attempt_id": 9001 }
// response
{ "kind": "level_quiz", "score": 0.83, "right": 10, "total": 12, "passed": true, "stars": 1,
  "coins_awarded": 140, "next_level": { "id": 3, "level_number": 3, "title_en": "Objects & equipment" } }
```
The server computes the score from `nursing_quiz_attempts.answers` (first tries only). Passing sets `quiz_passed`, unlocks the next level, and awards level coins once.

---

## 11. Content pipeline

| Step | Tool | Output |
|---|---|---|
| Edit content | `index.html` data (prototype) | — |
| Generate photo prompts | `tools/build_scene_manifest.js` | `tools/image_manifest.json` |
| Generate photos | `tools/generate_images.py` (gpt-image-1-mini, 1536×1024) | `images/*.jpg` |
| Optimise | `tools/optimize_images.py` (960×640 JPEG) | `images/*.jpg` |
| Export levels | `tools/export_levels.js` | `content/levels/*.json` |
| Package photos | `tools/zip_levels.py` | `content/levels/*-images.zip` |
| Import | backend import script (§9.3) | DB + CDN |

Content changes after V1 should move to the DB with an admin review step (out of scope for V1).

## 12. Audio

| Speaker key | Character | Voice (Azure Speech, de-DE, suggestion) |
|---|---|---|
| `weber` | Frau Weber, 82, patient | older female |
| `schmidt` | Herr Schmidt, 67, patient | older male |
| `yilmaz` | Herr Yılmaz, 45, patient | male |
| `lena` | Lena, nurse colleague | young female |
| `braun` | Dr. Braun, doctor | male |
| `anna` | Anna, visitor | female |
| `nurse` / null | the learner (model answers, words) | female, clear, slightly slower |

- Pre-generate audio for every German string in the level JSON (card fronts, back lines, prompts, feedback, correct replies). Key the files by a hash of `text + voice`; serve from the CDN.
- Spelling: letters with 400 ms pauses ("W … E … B …").
- Rate: 0.9 for patients over 65 and for the learner voice; 1.0 otherwise.
- The client uses `useTextToSpeech`: play the pre-generated URL if present, else `/tts/speak`, else browser speech.

## 13. Pictures

| | Spec |
|---|---|
| Count | 318 card photos + 1 header |
| Format | 3:2 landscape; source 1536×1024; delivery WebP/AVIF with JPEG fallback, 960 and 480 px widths (`srcset`) |
| Frames | Flashcard front and question card use 3:2 frames with `object-fit: cover` |
| Naming | `w-*` word, `p-SS-NN` phrase/pattern scene, `e-NN` emergency, `d-*` document, `s-*` spelling, `h-*` header |
| Alt text | Flashcards: `alt=""` (word shown). Question card: `alt` = card's English meaning |
| Preload | Next 3 cards' photos (as in `A1Flashcard`) |
| Review | Human review of all photos before launch (audit F-13) |

## 14. Analytics

Use `useFirstPartyAnalytics` with `module: "a1_nursing"`, keeping the existing event names where they exist.

| Event | When | Properties |
|---|---|---|
| `nursing_entry_opened` | Entry card tapped | `current_level` |
| `learning_module_started` | Level runner opened | `module`, `level`, `resume_index`, `total_cards` |
| `nursing_card_flipped` | First flip per card per session | `level`, `card_id`, `card_type`, `order` |
| `nursing_audio_played` | Speaker tapped | `level`, `card_id`/`question_id`, `side`, `source` (pregenerated/tts/browser) |
| `nursing_deck_shuffled` / `nursing_deck_reset` | Button | `level`, `index` |
| `nursing_quick_check_completed` | Quick check done | `level`, `checkpoint`, `right`, `total` |
| `nursing_question_answered` | Each check | `level`, `question_type`, `first_try`, `correct`, `ms_to_answer` |
| `learning_module_submitted` | Level quiz submitted | `module`, `level`, `score`, `passed`, `attempt` |
| `nursing_level_completed` | First pass | `level`, `stars`, `attempts`, `time_spent_s` |

## 15. Non-functional requirements

### Accessibility (WCAG 2.1 AA)
- `lang="de"` on all German text (audit F-01).
- Touch targets ≥ 44×44 px (F-02).
- Text contrast ≥ 4.5:1; large text ≥ 3:1 (F-03).
- Flashcard: role="button", Enter/Space flip, ←/→ navigation; focus visible.
- `prefers-reduced-motion`: no swipe/flip animation, instant state change.
- Result modal traps focus and returns it to the Check button.

### Layout
- No vertical scrolling on flashcard, quiz and result screens at 375×700 and above. The quiz photo height clamps with the screen height (92–190 px).
- Fixed element positions on cards and question cards (no layout shift between cards).

### Performance
- Level list interactive < 1.5 s on a mid-range Android device over 4G.
- Card advance < 100 ms; no image pop-in for the next card (preload).
- Per-level media download ≤ 1.5 MB (WebP).

### Reliability
- Progress saves are idempotent and debounced; failed saves retry with backoff; the server never lowers `current_index` except on Reset.
- Quiz scoring is server-authoritative; the client never receives answers before checking.

## 16. Feature flag, limits and rollout
| Step | Audience |
|---|---|
| Internal | Staff accounts (`nursing_german_a1` flag) |
| Beta | 10% of A1 users, 2 weeks; watch metrics §3 and crash-free sessions |
| GA | 100% of A1 users |

Usage limits: register module `nursing` under A1 in `useUsageLimitModule` (free vs Premium: open question §20).

## 17. QA test plan

### Functional (must pass)
| # | Scenario | Expected |
|---|---|---|
| T1 | New user opens Nursing German | Only Level 1 unlocked; "Start Level 1" |
| T2 | Tap locked level | Nothing opens |
| T3 | Advance 5 cards, leave, return | "Continue", "5/18", resumes at card 6 |
| T4 | Previous, flip, audio (front/back) | Work; audio does not flip the card |
| T5 | Shuffle | Remaining cards reorder; position kept |
| T6 | Reset | Card 1; saved position reset |
| T7 | Advance past card 20 | Quick check with 5 questions on seen cards |
| T8 | Leave during quick check, return | Quick check shown again (not skipped) |
| T9 | Finish cards | Level quiz intro |
| T10 | Wrong answer | Red result, Try again; retry doesn't count |
| T11 | Score < 70% | "Almost there", Try again / Review; next level locked |
| T12 | Score ≥ 70% | Level complete, coins once, next level unlocked |
| T13 | Emergency question time-out | Marked wrong, right answer shown, Next |
| T14 | Document question | Document visible in frame; tap opens full size |
| T15 | Pass Level 21 | "All levels done!" |
| T16 | Full path levels 1→21 (automation) | All unlock in order |
| T17 | Replay a passed level with a lower score | Stays passed; best score kept; no extra level coins |

### Content (automated in CI on import)
- Every card has image, meaning and back English; every question resolves `card_id`; answer ∈ options; no duplicate options; all image keys exist.

### Visual / device
- Pixel 6a, Samsung A-series (small), 375×700 web: no scrolling, no layout shift, photos fill frames.

## 18. Milestones (estimate)

| # | Milestone | Scope | Estimate |
|---|---|---|---|
| M1 | Backend | Tables, import script, 6 endpoints, scoring | 5–6 dev days |
| M2 | Media | CDN upload, WebP conversion, audio pre-generation job | 2–3 dev days |
| M3 | Frontend: list + runner | Entry card, level list, deck with new back variants, progress | 4–5 dev days |
| M4 | Frontend: quiz | Question card, quick check, level quiz, results, timer | 4–5 dev days |
| M5 | Analytics, flag, limits, a11y fixes | §14–16 | 2 dev days |
| M6 | QA + content review | Test plan, native-speaker review, photo review | 3–4 days |

## 19. Risks

| Risk | Mitigation |
|---|---|
| A photo does not show exactly the card | Human review; regenerate from manifest; questions never rely on the photo alone (P3) |
| Robotic audio | Pre-generated neural voices per character |
| German errors | Native-speaker review of all 873 lines before GA |
| Learners feel 21 levels is long | Short levels (13–28 cards), "Next up" on results, streak integration |
| Cheating via client | Server-side scoring, answers never sent before check |

## 20. Open questions

| # | Question | Owner |
|---|---|---|
| Q1 | Free or Premium? From which level? | Product |
| Q2 | Reward for finishing Level 21 (certificate, jobs badge)? | Product |
| Q3 | Higher pass mark for Emergency German? | Product |
| Q4 | Feed missed cards into spaced review in A1 Flashcards? | Product |
| Q5 | Article colours der/die/das/plural into the design system? | Design |

---

## Appendix A: levels

| # | Title | German title | Words | Patterns | Phrases | Documents | Spelling | Emergency | Cards | Question pool | Questions per quiz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Who I am at work | Ich bin Ihre Pflegekraft | 5 | 3 | 10 | 0 | 0 | 0 | 18 | 20 | 12 |
| 2 | Hospital places | Im Krankenhaus | 13 | 3 | 9 | 0 | 0 | 0 | 25 | 35 | 12 |
| 3 | Objects & equipment | Dinge auf Station | 11 | 3 | 10 | 0 | 0 | 0 | 24 | 32 | 12 |
| 4 | The body | Der Körper | 0 | 3 | 10 | 0 | 0 | 0 | 13 | 10 | 10 |
| 5 | Emergency German | Notfall-Deutsch | 0 | 0 | 0 | 0 | 0 | 25 | 25 | 25 | 10 |
| 6 | Symptoms & pain | Schmerzen | 2 | 3 | 10 | 0 | 0 | 0 | 15 | 14 | 12 |
| 7 | Numbers & vital signs | Vitalwerte | 7 | 3 | 10 | 1 | 0 | 0 | 21 | 27 | 14 |
| 8 | Times & shifts | Dienst & Uhrzeit | 2 | 3 | 10 | 1 | 0 | 0 | 16 | 17 | 14 |
| 9 | Medication & food | Medikamente & Essen | 13 | 3 | 10 | 2 | 0 | 0 | 28 | 42 | 16 |
| 10 | Instructions | Bitte …! | 1 | 3 | 10 | 0 | 0 | 0 | 14 | 12 | 12 |
| 11 | Basic care | Grundpflege | 3 | 3 | 10 | 0 | 0 | 0 | 16 | 16 | 12 |
| 12 | Talking to colleagues | Mit Kollegen | 7 | 3 | 10 | 1 | 0 | 0 | 21 | 27 | 14 |
| 13 | Comforting patients | Keine Angst | 1 | 3 | 10 | 0 | 0 | 0 | 14 | 12 | 12 |
| 14 | Admitting a patient | Aufnahme | 5 | 3 | 10 | 2 | 2 | 0 | 22 | 28 | 18 |
| 15 | Walking & falls | Mobilisation & Sturz | 1 | 3 | 10 | 0 | 0 | 0 | 14 | 12 | 12 |
| 16 | Phone calls | Am Telefon | 1 | 3 | 10 | 0 | 2 | 0 | 16 | 14 | 14 |
| 17 | Hygiene & isolation | Hygiene | 2 | 3 | 10 | 1 | 0 | 0 | 16 | 17 | 14 |
| 18 | Toilet & continence | Toilette & Ausscheidung | 2 | 3 | 10 | 1 | 0 | 0 | 16 | 17 | 14 |
| 19 | Visitors & relatives | Besuch & Angehörige | 2 | 3 | 10 | 0 | 0 | 0 | 15 | 14 | 12 |
| 20 | The night round | Nachtdienst | 1 | 3 | 10 | 0 | 0 | 0 | 14 | 12 | 12 |
| 21 | Discharge day | Entlassung | 1 | 3 | 10 | 1 | 0 | 0 | 15 | 15 | 14 |

Totals: 378 cards · 419 questions in the pool · 318 card photos.

## Appendix B: question pool by type

| Type | Count |
|---|---|
| `translate_to_german` | 80 |
| `translate_to_english` | 80 |
| `choose_reply` | 76 |
| `choose_reply_sie_du` | 5 |
| `situation_choice` | 40 |
| `picture_choice` | 44 |
| `body_part_choice` | 10 |
| `listen_and_note` | 24 |
| `document_question` | 30 |
| `emergency_translate` | 25 |
| `spelling` | 4 |

## Appendix C: frontend file map (suggested)

```
src/api/nursingApi.js                      getNursingLevels, getNursingCards, saveNursingProgress,
                                           getNursingQuiz, checkNursingAnswer, submitNursingQuiz
src/pages/a1/nursing/NursingLevelSelect.jsx   uses ChapterSelectTemplate
src/pages/a1/nursing/NursingLevel.jsx         deck + quick check + quiz + results state machine
src/components/a1/nursing/NursingCardBack.jsx back variants (§7.3)
src/components/a1/nursing/NursingQuestionCard.jsx
src/components/a1/nursing/QuestionTimer.jsx
App.jsx                                     routes /a1/nursing, /a1/nursing/:levelId (lazyScreen)
German Practice grid                        entry card behind feature flag
```
