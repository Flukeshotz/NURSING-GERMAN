# Complete audit: Nursing German (A1)

| | |
|---|---|
| Date | 17 Sep 2026 |
| Scope | Prototype (`index.html`), level content (`content/levels`), pictures, tools, docs, live site |
| Live | https://nursing-german.vercel.app |
| Verdict | **Ready for developer handoff.** No blockers. 13 findings: 0 high, 5 medium, 8 low. All are listed below with owner and fix. |

---

## 1. Summary

| Area | Result |
|---|---|
| Learner path (21 levels, fresh start → end) | ✅ Passed |
| Edge cases (wrong answers, fail/retry, resume, back mid-quiz, locked levels, shuffle/reset) | ✅ Passed, 2 behaviour notes (F-06, F-07) |
| Content: German quality and A1 scope | ✅ Passed after fixes; 1 low finding (F-12) |
| Content integrity (JSON, zips, pictures, translations) | ✅ 0 problems |
| Screen fit (no scrolling) | ✅ Passed at 375×700 and 375×812 |
| Accessibility | ⚠️ 4 findings (F-01 … F-04) |
| Performance | ⚠️ 2 findings (F-05, F-08) |
| Security and privacy | ✅ No secrets in git history; 1 action (F-09) |
| Code quality (prototype only) | ℹ️ 1 finding (F-10); production is rebuilt in React |
| Docs | ✅ PRD rewritten as a developer PRD; schema up to date |

---

## 2. What was tested and how

### 2.1 Full learner path
Automated run in a 375×700 viewport with `?audit` (marks the correct option). Result: all 21 levels completed in order; every pass unlocked the next level; the last screen shows "All levels done!".

| Level | Cards | Questions answered (incl. quick checks) | Result |
|---|---|---|---|
| 1 Who I am at work | 18 | 12 | 12/12 ✅ |
| 2 Hospital places | 25 | 17 | 12/12 ✅ |
| 3 Objects & equipment | 24 | 17 | 12/12 ✅ |
| 4 The body | 13 | 8 | 8/8 ✅ |
| 5 Emergency German | 25 | 15 | 10/10 ✅ |
| 6 Symptoms & pain | 15 | 10 | 10/10 ✅ |
| 7 Numbers & vital signs | 21 | 19 | 14/14 ✅ |
| 8 Times & shifts | 16 | 16 | 12/12 ✅ |
| 9 Medication & food | 28 | 21 | 16/16 ✅ |
| 10 Instructions | 14 | 9 | 9/9 ✅ |
| 11 Basic care | 16 | 11 | 11/11 ✅ |
| 12 Talking to colleagues | 21 | 19 | 14/14 ✅ |
| 13 Comforting patients | 14 | 9 | 9/9 ✅ |
| 14 Admitting a patient | 22 | 23 | 18/18 ✅ |
| 15 Walking & falls | 14 | 9 | 9/9 ✅ |
| 16 Phone calls | 16 | 11 | 11/11 ✅ |
| 17 Hygiene & isolation | 16 | 12 | 12/12 ✅ |
| 18 Toilet & continence | 16 | 12 | 12/12 ✅ |
| 19 Visitors & relatives | 15 | 10 | 10/10 ✅ |
| 20 The night round | 14 | 9 | 9/9 ✅ |
| 21 Discharge day | 15 | 11 | 11/11 ✅ |

During the run: 0 JavaScript errors, 0 screens that scrolled, 0 cards or questions without a picture.

### 2.2 Edge cases

| # | Test | Result |
|---|---|---|
| 1 | Fresh start: only Level 1 unlocked | ✅ |
| 2 | Tapping a locked level does nothing | ✅ |
| 3 | Leave after 5 cards → list shows "Continue" and "5/18 done" | ✅ |
| 4 | Continue reopens at card 6 | ✅ |
| 5 | Previous-card button | ✅ |
| 6 | Tap to flip shows the back | ✅ |
| 7 | Shuffle keeps the current position | ✅ |
| 8 | Reset goes back to card 1 | ✅ (see F-07) |
| 9 | Last card → "Level quiz" intro | ✅ |
| 10 | Wrong answer → red result + "Try again" | ✅ |
| 11 | Retry after wrong → green result, does not count toward the score | ✅ |
| 12 | 0% on first tries → "Almost there", next level stays locked | ✅ |
| 13 | Fail screen offers "Try the quiz again" and "Review the cards" | ✅ |
| 14 | Results screen has Back | ✅ |
| 15 | Retry and pass → "Level 1 complete", "Start Level 2", Level 2 unlocked, badge green | ✅ |
| 16 | Quick check appears after 20 cards | ✅ |
| 17 | Leave during a quick check → resume at card 21, quick check not repeated | ✅ (see F-06) |
| 18 | Leave during the level quiz → resume on the last card, quiz restarts | ✅ (see F-06) |

### 2.3 Content

| Check | Result |
|---|---|
| German lines linted (prompts, options, feedback, patterns) | 873 |
| Duplicate options in a question | 0 |
| *du* used towards patients, visitors or the doctor in a correct answer | 0 |
| Reply lines without English | 0 |
| Word taught in two levels / not taught in any level | 0 / 0 |
| Pattern brackets unbalanced | 0 |
| Grammar above A1 (perfect tense, subordinate clauses, subjunctive, passive) | 0 after fix |
| Every card: picture + English meaning + back line with English | 378/378 |
| Every quiz answer is in its options | 419/419 |
| Every question's `from_card` is a card in the same level | 419/419 |
| Pictures named in JSON present in the level zip / unused picture files | all / 0 |

**Fixed during this audit:**
- All 80 word-card example sentences were rewritten by hand. The generated ones were often wrong: „Hier ist die Angehörigen" (grammar), „Hier ist der Stuhlgang", "Here is the Tab..".
- „Hilfe! Ich bin gefallen!" (perfect tense, A2) → „Hilfe! Ich liege auf dem Boden!"
- Two example sentences with dative beyond fixed phrases were simplified.

### 2.4 Accessibility (WCAG 2.1 AA, automated + manual)

| Check | Result |
|---|---|
| Buttons without an accessible name | 0 ✅ |
| Visible keyboard focus style | Present ✅ |
| `prefers-reduced-motion` respected | Present ✅ |
| Flashcard operable by keyboard (Enter/Space flips, ←/→ navigate) | ✅ |
| German text marked `lang="de"` | ❌ F-01 |
| Touch targets ≥ 44×44 px | ❌ F-02 |
| Text contrast ≥ 4.5:1 (small text) | ❌ F-03 |
| Pictures have text alternatives where they carry meaning | ⚠️ F-04 |

### 2.5 Performance

| Metric | Value |
|---|---|
| `index.html` (prototype, includes Maya, coin and UI images inline) | 369 KB |
| Pictures (319 JPEG, 960×640 q78) | 18 MB total, ~40–70 KB each |
| Pictures per level | 0.8–1.3 MB |
| Level zips (all 21) | 18 MB (a duplicate of `images/`, by design) |
| Live page response | ~0.2 s |

### 2.6 Security and privacy

| Check | Result |
|---|---|
| API keys in any commit (whole git history) | None ✅ |
| `.env` tracked | No ✅ (git-ignored, lives outside the repo) |
| Personal data stored | Progress and coins only, in `localStorage` (prototype) ✅ |
| Azure key exposure | Shared once in a chat session → rotate (F-09) |

---

## 3. Findings

| ID | Severity | Area | Finding | Fix | Owner | Status |
|---|---|---|---|---|---|---|
| F-01 | Medium | Accessibility | German text is not marked `lang="de"`, so screen readers read German with English pronunciation. | Add `lang="de"` to every element that renders German (card front, back line, prompts, German options). | Dev | **Fixed 2026-09-18** |
| F-02 | Medium | Accessibility | Tap targets below 44 px: Back link (57×21), Shuffle/Reset/Next (≈39 px tall), small speaker buttons (30–36 px). | Minimum 44×44 hit area (padding or `::after` hit zone). | Dev / Design | **Fixed 2026-09-18** |
| F-03 | Medium | Accessibility | Low contrast: in-progress level badge text on gold (3.0:1); 10 px uppercase labels on the gold card back (≈4.4:1); grey header titles (4.2:1). Some come from existing design-system tokens. | Darken badge text to ≥ 4.5:1 (e.g. `#8a6414`); raise card-back labels to ≥ 11 px and `#5a4a1a` at full opacity. | Design | **Fixed 2026-09-18** |
| F-04 | Low | Accessibility | Pictures use `alt=""`. That is fine on flashcards (the word is shown), but quiz pictures give context. | On quiz cards set `alt` to the card's English meaning. | Dev | **Fixed 2026-09-18** |
| F-05 | Medium | Performance | Pictures are JPEG at 40–70 KB each. | Serve WebP/AVIF from a CDN with `srcset` (≈30–50% smaller); preload the next 3 cards like `A1Flashcard` does. | Dev | Open — needs a CDN, out of scope for the static prototype |
| F-06 | Low | Behaviour | Quiz progress is not saved: leaving mid-quiz restarts it. Quick check is skipped when resuming past card 20. | Production: persist `quiz_state` per level (§8 of PRD), or accept and document. Show the quick check on resume if it was not completed. | Dev / Product | **Partially fixed 2026-09-18**: the quick check now fires on resume too (`s.miniSeen` persisted per level, checked in `openLevel`). Losing progress on an in-progress quiz itself is still accepted, per the fix note. |
| F-07 | Low | Behaviour | "Reset" returns the deck to card 1, but the saved position stays at the furthest card, so "Continue" jumps forward again. | Reset should also reset `current_index` (as A1 Flashcards does). | Dev | **Fixed 2026-09-18** |
| F-08 | Low | Performance | Level zips duplicate `images/` in the repo (18 MB twice). | Keep zips as release artefacts (GitHub Release or storage bucket) instead of committing them, if repo size matters. | Dev | Open — repo-hosting decision, not a code change |
| F-09 | Medium | Security | The Azure OpenAI key was pasted in a chat session. | Rotate the key in Azure; store in the backend secret manager only. | Harsh | Open — needs Harsh to rotate the key in Azure |
| F-10 | Low | Code | Prototype is a single 1,230-line script with some dead code (`bodySvg`, `COUNTRIES`, `DRILL_SECONDS`, `P`, `personal`). | None for the prototype. Production is a React rebuild (PRD §6). | — | Won't fix (by design) |
| F-11 | Low | UX | Level badge says "25/25 done" once all cards are seen, even if the quiz is not passed yet. | Show "Quiz left" until passed, "Done" after. | Design / Dev | **Fixed 2026-09-18** |
| F-12 | Low | Content | Two "write it down" questions have English options ("tomorrow 10:00", "every 2 hours") while others use values. | Use German/neutral values: "morgen, 10 Uhr", "alle 2 Stunden". | Content | **Fixed 2026-09-18** |
| F-13 | Low | Content | 319 AI photos have been spot-checked (≈30), not fully reviewed. | Human review of all photos against their card before launch; regenerate any mismatch from `tools/image_manifest.json`. | Content | Open — needs a full manual review pass |

---

## 4. Not in scope of this audit
- Real device testing on Android (Capacitor build) and iOS.
- Audio quality (the prototype uses browser text-to-speech).
- Load testing of backend APIs (not built yet).
- Native German speaker review of all 873 lines. **Recommended before launch.**

## 5. How to re-run
- **Full path:** open `index.html?audit` locally; audit mode marks the correct option with `data-audit-ok`.
- **Content integrity:** `node tools/export_levels.js && python3 tools/zip_levels.py`, then the checks in this file (§2.3) can be scripted from `content/levels/*.json`.
