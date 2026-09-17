# PRD: Nursing German (A1)

| | |
|---|---|
| Product | Skillcase learning app |
| Feature | Nursing German, a nursing-only practice mode |
| Scope | V1 = CEFR A1 only |
| Status | Prototype ready for build · [live prototype](https://nursing-german.vercel.app) |
| Content | `content/levels/` (21 level JSON files, one picture zip per level) |

---

## 1. Problem

Skillcase learners are internationally trained nurses, mostly from India, preparing to work in Germany. The app already teaches general A1 German: Flashcards, Grammar, Listening, Speaking, Reading and Tests.

General A1 German does not cover the language a nurse needs on the ward from day one:

- Hospital words and chart abbreviations. Nurses say *BP*, *drip*, *OT*; German charts say *RR*, *Infusion*, *OP*.
- Short exchanges with patients, colleagues, doctors and relatives.
- Reading ward documents such as medication plans (`1-0-1-0`), vital signs charts and handover notes.
- Emergency phrases that must come out instantly.

Every one of these fits A1 grammar, but none of it is in a general A1 course.

## 2. Goal

Give A1 learners a **nursing-only practice mode** that works exactly like the practice modes they already know, so there is nothing new to learn about how to use it.

### Success metrics

| Metric | Target (first 90 days) |
|---|---|
| A1 learners who open Nursing German | ≥ 40% |
| Learners who finish Level 1 after starting it | ≥ 70% |
| Learners who reach Level 5 (Emergency German) | ≥ 35% |
| Level quiz pass rate on the first attempt | 60–80% (below 60% = too hard, above 90% = too easy) |
| Median session length | 6–10 minutes |

## 3. Users

- **Primary:** nurses at A1 level preparing for Germany. Often working shifts, studying on a phone in short sessions.
- **English only.** Learners come from many regions and languages, so all explanations are in English. No regional languages.

## 4. Scope

### In scope (V1)
- A1 only. Present tense, formal imperative (*Setzen Sie sich bitte*), modal verbs, *kein/nicht*, accusative. Dative only in fixed phrases (*Ich helfe Ihnen*).
- 21 levels unlocked one after another.
- Flashcards, then a quick check every 20 cards, then a level quiz.
- Audio for every German line.
- A realistic photo on every flashcard. Quiz questions reuse the card's photo; **answer options are always text**.

### Out of scope (V1)
- A2, B1, B2 nursing content
- General A1 grammar or vocabulary already taught elsewhere in the app
- Ward culture content (removed from V1)
- Free speaking or pronunciation scoring
- Choice menus. Learners never pick a content type; the path decides.

## 5. Teaching method

Same as the other A1 practice modes: **teach first, then ask.**

```
German Practice → Nursing German → Level list → Level N
   Level N:  flashcards ──(every 20 cards)──> quick check ──> more flashcards
             last card ──> level quiz ──> pass (≥ 70%) ──> Level N+1 unlocks
                                       └─> fail ──> retry quiz or review cards
```

Rules:
1. **Never ask before teaching.** Every quiz question tests something taught on a card in that level. Documents and spelling have their own teaching cards.
2. **One path, no choices.** The only decisions: continue, retry, or review.
3. **Each level teaches in a fixed order:** words → (for each goal) pattern card → phrase cards → document cards → spelling cards.

## 6. User experience

### 6.1 Entry
A **Nursing German** card at the top of *German Practice*, marked "NEW" and showing "Level X of 21".

### 6.2 Level list
Same component as the A1 chapter list (`ChapterSelectTemplate`):
- Header image, "A1 · Nursing German", one-line subtitle
- A row of progress bars, one per level (gold while in progress, green when done)
- One row per level: "Level N: Title", a badge "x/y done" or "Locked", and a lock icon
- A sticky button: **Start / Continue Level N: Title**

### 6.3 Flashcards
Same component as A1 Flashcards (`A1FlashcardDeck` / `A1FlashcardCard`):
- A stacked deck of 3 cards (purple, light blue, white, slightly rotated)
- **Fixed positions on every card:** photo on the top half; German text centred in a fixed 2-line slot; speaker button and "Tap to flip" always in the same place
- **Front:** picture on the top half; German text, a speaker button and "Tap to flip" on the bottom half
- **Back (gold):** always the same layout:
  1. `Meaning` (English)
  2. divider
  3. one labelled German line and its English: *Example / You answer / You note down / When / Tip / Key words / Letters / Say it*
  4. an optional short note
- Swipe left for the next card, right for the previous one. Buttons: ‹ · Shuffle · Reset · › / Finish.
- Progress: "Flashcards n/total" and a bar split into 20-card segments.

| Card type | Front | Back label |
|---|---|---|
| word | picture + word with article colour | Example (*Hier ist die Station.*) |
| pattern | photo + sentence pattern with the swappable word highlighted | Tip |
| phrase | scene + what the patient, colleague or doctor says | You answer / You note down |
| phrase (you speak first) | scene + what you say | When (the situation) |
| document | photo of the document in use | Key words |
| spelling | photo + letters of a name | Letters (how each letter sounds) |
| emergency | scene + phrase | Say it |

### 6.4 Quick check
After every 20 cards: 5 multiple-choice meaning questions on cards already seen. No pass mark; it continues automatically.

### 6.5 Level quiz
- **Every question is built from a flashcard of the same level, with the same picture and the same German.** Nothing is asked that the level did not teach.
- Drawn from the level's `quiz_pool`: 4 word questions (picture → German, German → meaning), 8 phrase questions (card photo + what the person says → the right reply), 2 questions per document, and spelling questions if the level has them.
- Emergency level: 10 emergency cards as photo → "What do you say?", **8 seconds each**.
- Flow per question: select → **Check** → result card (green "Richtig!" / red "Incorrect!").
  - Wrong answers can be retried; only the first attempt counts toward the score.
  - True/false and drill questions move on straight away.
- **Pass mark 70%.** Pass: stars, coins, **Start Level N+1**. Fail: **Try the quiz again** or **Review the cards**.

### 6.6 Rewards
Coins use the existing economy: +10 per first-try correct quiz answer, +20 for passing a level. There are no separate nursing coins.

## 7. Content

### 7.1 Inventory

| | Count |
|---|---|
| Levels | 21 |
| Flashcards | 378 |
| Hospital words (incl. chart abbreviations, roles, places, false friends) | 80 |
| Ward situations | 20 (200 exchanges, 60 sentence patterns) |
| Ward documents | 10 |
| Emergency phrases / drill situations | 25 / 25 |
| Pictures | 319 (one photo per flashcard; answer options are text only) |

### 7.2 Levels

| # | Level | Words | Phrases + patterns | Documents | Spelling | Emergency | Cards |
|---|---|---|---|---|---|---|---|
| 1 | Who I am at work | 5 | 13 | 0 | 0 | 0 | 18 |
| 2 | Hospital places | 13 | 12 | 0 | 0 | 0 | 25 |
| 3 | Objects & equipment | 11 | 13 | 0 | 0 | 0 | 24 |
| 4 | The body | 0 | 13 | 0 | 0 | 0 | 13 |
| 5 | Emergency German | 0 | 0 | 0 | 0 | 25 | 25 |
| 6 | Symptoms & pain | 2 | 13 | 0 | 0 | 0 | 15 |
| 7 | Numbers & vital signs | 7 | 13 | 1 | 0 | 0 | 21 |
| 8 | Times & shifts | 2 | 13 | 1 | 0 | 0 | 16 |
| 9 | Medication & food | 13 | 13 | 2 | 0 | 0 | 28 |
| 10 | Instructions | 1 | 13 | 0 | 0 | 0 | 14 |
| 11 | Basic care | 3 | 13 | 0 | 0 | 0 | 16 |
| 12 | Talking to colleagues | 7 | 13 | 1 | 0 | 0 | 21 |
| 13 | Comforting patients | 1 | 13 | 0 | 0 | 0 | 14 |
| 14 | Admitting a patient | 5 | 13 | 2 | 2 | 0 | 22 |
| 15 | Walking & falls | 1 | 13 | 0 | 0 | 0 | 14 |
| 16 | Phone calls | 1 | 13 | 0 | 2 | 0 | 16 |
| 17 | Hygiene & isolation | 2 | 13 | 1 | 0 | 0 | 16 |
| 18 | Toilet & continence | 2 | 13 | 1 | 0 | 0 | 16 |
| 19 | Visitors & relatives | 2 | 13 | 0 | 0 | 0 | 15 |
| 20 | The night round | 1 | 13 | 0 | 0 | 0 | 14 |
| 21 | Discharge day | 1 | 13 | 1 | 0 | 0 | 15 |

### 7.3 Content rules
- Every German sentence uses A1 grammar only (see §4).
- Always *Sie* with patients and doctors, *du* with colleagues.
- Say *Pflegekraft / Pflegefachfrau / Pflegefachmann*, not *Schwester*. Teach *Schwester* only as something patients say.
- Every German line has an English translation.
- Articles are colour-coded: der blue, die pink, das teal, plural purple. **Design system gap:** green and red are already used for correct/incorrect, so these colours need design sign-off.

## 8. Data and delivery

- Content format: `content/SCHEMA.md`.
- One JSON file per level, plus one zip with exactly the pictures that level uses. This allows level-by-level download and caching.
- Suggested backend tables mirror the existing A1 flashcard tables: `nursing_levels`, `nursing_cards`, `nursing_quiz_questions`, `nursing_progress (user_id, level, current_index, quiz_passed, best_score)`.
- Progress to store: current card index per level, whether the quiz was passed, best score. Unlock = previous level passed.

## 9. Media

| | Prototype | Production |
|---|---|---|
| Pictures | gpt-image-1-mini, **realistic healthcare-photo style**, adults only, no text (`tools/generate_images.py`) | Review every picture; replace any that don't show exactly the card's meaning |
| Audio | Browser text-to-speech | Pre-generated neural TTS (e.g. Azure Speech, de-DE) with one voice per character: older woman, older man, colleague, doctor, visitor, learner |

## 10. Analytics events

| Event | Properties |
|---|---|
| `nursing_opened` | source |
| `nursing_level_started` | level, resumed_from_index |
| `nursing_card_flipped` | level, card_type, order |
| `nursing_card_audio_played` | level, card_type, side |
| `nursing_quick_check_completed` | level, correct, total |
| `nursing_quiz_submitted` | level, correct, total, passed, attempt |
| `nursing_level_completed` | level, stars, time_spent_s |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Cards look inconsistent | One fixed card layout: photo 50%, text slot, speaker and hint in fixed positions; one fixed back layout |
| A generated picture shows the wrong thing | Human review of all 368 pictures before launch; regenerate from the manifest |
| Robotic browser audio | Replace with recorded or neural TTS files before launch |
| 21 levels feels long | Levels are 13–25 cards; show "Level X of 21" and the next level on every results screen |
| Overlap with general A1 content | Content rule: nursing-specific only. Body parts and numbers appear only in ward context |
| New colours conflict with the design system | Article colours need design sign-off (§7.3) |

## 12. Open questions

1. Is Nursing German free or Premium? And from which level?
2. Should passing Level 21 unlock anything, e.g. a certificate or a jobs-screen badge?
3. Pass mark: 70% for every level, or higher for Emergency German?
4. Should spaced review of missed cards feed into the existing Flashcards review?

## 13. Where things are in the repo

| Path | What |
|---|---|
| `index.html` | Clickable prototype (single file, no build) |
| `images/` | Generated pictures used by the prototype |
| `content/levels/` | Level JSON + image zips for the app |
| `content/SCHEMA.md` | JSON format |
| `tools/` | Picture generation and export scripts |
