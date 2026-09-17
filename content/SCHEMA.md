# Level content format

Each level is one JSON file, `content/levels/level-XX.json`, and one picture archive, `content/levels/level-XX-images.zip`. `content/levels/index.json` lists all levels in order.

Every picture filename in a level JSON is inside that level's zip, at the zip root.

## Level

```jsonc
{
  "level": 2,
  "cefr": "A1",
  "title_en": "Hospital places",
  "title_de": "Im Krankenhaus",
  "unlock": { "requires_level": 1, "pass_mark": 0.7 },   // null for level 1
  "flow": ["flashcards", "quick_check_every_20_cards", "level_quiz", "next_level"],
  "rules": { "quick_check_every_cards": 20, "quiz_pass_mark": 0.7, "quiz_questions_per_attempt": 11 },
  "goals": [ { "title": "Show the way", "pattern": "[Die Toilette] ist hier rechts.", "pattern_en": "…", "tip": "…" } ],
  "flashcards": [ /* Flashcard, taught in this order */ ],
  "quiz_pool": [ /* Question: the app draws questions_per_attempt from here */ ],
  "images_zip": "level-02-images.zip",
  "images": ["i-aufzug.jpg", "p-02-01.jpg", "w-ward.jpg"]
}
```

`[brackets]` in a pattern mark the word the learner can swap. Highlight it in the UI.

## Flashcard

Every card has the same front and back shape, so the UI uses one component.

```jsonc
{
  "order": 1,
  "type": "word | phrase | pattern | document | spelling | emergency",
  "front": { "german": "die Station", "speaker": null, "label": null, "image": "w-ward.jpg" },
  "back":  { "meaning_en": "Ward", "label": "Example", "german": "Hier ist die Station.", "english": "Here is the Ward.", "note": "…or null" },

  // only on some types:
  "article_word": "die Station", "false_friend": false,          // word
  "replies": [ { "label": "You say", "german": "…", "english": "…" } ], // phrase
  "pattern": "Ich bin [Priya], Ihre Pflegekraft.",               // pattern
  "document": { "title_de": "…", "title_en": "…", "html": "…", "key_words": [ { "de": "RR", "en": "blood pressure" } ] },
  "spelling": { "name": "Weber", "letters": [ { "letter": "W", "say": "weh" } ] }
}
```

- `speaker` is one of: `weber`, `schmidt`, `yilmaz` (patients), `lena` (nurse colleague), `braun` (doctor), `anna` (visitor), `nurse` (the learner), or `null`.
- `german` values with `der/die/das` should show the article in its colour: der blue, die pink, das teal, plural purple.

## Question types in `quiz_pool`

**Every question is asked in words.** Pictures are never the question and never an option. `supporting_image` is a small thumbnail next to the question text, optional to show.

| type | Question (text) | Options | answer |
|---|---|---|---|
| `translate_to_german` | `question_en`, e.g. How do you say "Lab" in German? | German | German |
| `translate_to_english` | `question_en`, e.g. What does "das Labor" mean? | English | English |
| `choose_reply` / `choose_reply_sie_du` | `prompt_de` (with audio) + `prompt_en` | German replies | German |
| `situation_choice` | `prompt_en` | German sentences | German |
| `picture_choice` | `prompt_de` + `prompt_en`: what the person needs | German key words | German |
| `body_part_choice` | `prompt_de` + `prompt_en`: where it hurts | German body parts | German |
| `listen_and_note` | `prompt_de` (audio) | values, e.g. `130/85` | value |
| `document_question` | `question_en` + `document_html` | English | English |
| `spelling` | letters read aloud (`audio_letters`) | names | name |
| `emergency_translate` | `question_en`, `time_limit_seconds` = 8 | German | German |

`answer` is always one of `options`; shuffle options at runtime. `feedback_de`/`feedback_en` (optional) is what the nurse says after a correct answer. Every question has `from_card`: the German text of the flashcard it tests.
