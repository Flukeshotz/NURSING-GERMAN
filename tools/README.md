# Tools

Content lives in `index.html` (the prototype). These scripts turn it into developer-ready files.

| Script | What it does |
|---|---|
| `lib_load.js` | Loads the content and level logic from `index.html` into Node. Used by the other JS tools. |
| `build_scene_manifest.js` | Builds `image_manifest.json`: one exact prompt for every picture a card or question needs. |
| `generate_images.py` | Generates the missing pictures with **gpt-image-1-mini** (Azure OpenAI or OpenAI). Skips existing files. |
| `optimize_images.py` | Resizes pictures to 640×640 JPEG for mobile. |
| `sync_image_list.py` | Writes the list of available pictures into `index.html`. |
| `export_levels.js` | Writes `content/levels/level-XX.json` and `content/levels/index.json`. |
| `zip_levels.py` | Writes `content/levels/level-XX-images.zip` with exactly the pictures that level uses. |

## Full rebuild

```bash
node tools/build_scene_manifest.js
python3 tools/generate_images.py        # needs a .env, see below
python3 tools/optimize_images.py
python3 tools/sync_image_list.py
node tools/export_levels.js
python3 tools/zip_levels.py
```

## .env (never commit)

Put it in the folder **above** this repo, or in the repo root (it is git-ignored):

```
AZURE_OPENAI_ENDPOINT=https://<resource>.services.ai.azure.com/openai/v1
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_IMAGE_DEPLOYMENT=gpt-image-1-mini
IMAGE_QUALITY=medium
IMAGE_WORKERS=10
```

Or set `OPENAI_API_KEY` to use OpenAI directly.

## Picture naming

| Prefix | Used for | Example |
|---|---|---|
| `w-` | Word flashcards and picture quiz questions | `w-bp.jpg` (der Blutdruck) |
| `i-` | Picture answer options in ward situations | `i-rollstuhl.jpg` (der Rollstuhl) |
| `p-SS-NN` | Phrase and pattern flashcards (situation SS, exchange NN) | `p-02-01.jpg` (Wo ist die Toilette?) |
| `e-NN` | Emergency flashcards | `e-01.jpg` (Hilfe!) |
| `d-<doc>` | Document flashcards | `d-med.jpg` (Medikamentenplan) |
| `s-<name>` | Spelling flashcards | `s-weber.jpg` |
