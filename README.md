# Nursing German (A1)

A nursing-only German practice mode for the Skillcase app, for nurses moving to Germany. It covers CEFR A1 only.

**Live prototype:** https://nursing-german.vercel.app
**Product spec:** [`docs/PRD.md`](docs/PRD.md) · **Final audit:** [`docs/AUDIT.md`](docs/AUDIT.md)

## How it works

It uses the same teaching method as the existing A1 practice modes: **teach first, then ask**.

German Practice → **Nursing German** → 21 levels unlocked in order → each level: flashcards → quick check every 20 cards → level quiz (70% to pass) → the next level opens.

## Repository layout

```
.
├── index.html              Clickable prototype (single file, no build step). Deployed on Vercel.
├── images/                 Generated pictures (640×640 JPEG) used by the prototype
├── content/
│   ├── SCHEMA.md           JSON format for levels, flashcards and quiz questions
│   └── levels/
│       ├── index.json      All levels in order
│       ├── level-01.json   Flashcards + quiz pool for level 1
│       ├── level-01-images.zip   Exactly the pictures level 1 uses
│       └── …               (21 levels)
├── tools/                  Picture generation and content export (see tools/README.md)
└── docs/
    ├── PRD.md              Product requirements
    └── AUDIT.md            Final audit results and open items
```

## For developers

- **Content to import:** `content/levels/*.json`. Format: `content/SCHEMA.md`.
- **Pictures:** each level's zip contains every file named in that level's JSON (`front.image`, `quiz_pool[].image`, option images).
- **UI:** reuse the existing A1 components. Level list = `ChapterSelectTemplate`; cards = `A1FlashcardDeck` / `A1FlashcardCard`; quiz = the A1 quiz flow. See PRD §6.
- **Run the prototype locally:** `python3 -m http.server` in this folder, then open http://localhost:8000.
- **Rebuild content after editing `index.html`:** see `tools/README.md`.

## Placeholders

- Audio uses the browser's German text-to-speech. Production should use recorded or neural TTS audio (PRD §9).
- Pictures are AI-generated and need a human review before launch.
