#!/usr/bin/env python3
"""Generate the flashcard and quiz pictures with gpt-image-1-mini (Azure OpenAI or OpenAI).

Reads AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY (or OPENAI_API_KEY) from the .env in the NURSING GERMAN folder.
Writes images/<id>.jpg and images/index.json. Existing images are skipped, so it is safe to re-run.

  python3 tools/generate_images.py            # all missing images
  python3 tools/generate_images.py --limit 3  # try a few first
"""
import base64, json, os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)

def load_env():
    for path in (os.path.join(APP, "..", ".env"), os.path.join(APP, ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def generate(item, key, model, quality, url, headers):
    out = os.path.join(APP, item["file"])
    if os.path.exists(out):
        return item["id"], "skipped"
    body = json.dumps({"model": model, "prompt": item["prompt"], "size": item.get("size", "1024x1024"),
                       "quality": quality, "output_format": "jpeg", "output_compression": 82, "n": 1}).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        return item["id"], f"error {e.code}: {e.read().decode()[:200]}"
    b64 = data["data"][0]["b64_json"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(base64.b64decode(b64))
    return item["id"], "created"

def main():
    load_env()
    azure_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip()
    if azure_key:
        key = azure_key
        url = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/images/generations"
        headers = {"api-key": key, "Content-Type": "application/json"}
        model = os.environ.get("AZURE_OPENAI_IMAGE_DEPLOYMENT", "gpt-image-1-mini")
    else:
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            sys.exit("No API key found. Add AZURE_OPENAI_API_KEY or OPENAI_API_KEY to the .env file.")
        url = "https://api.openai.com/v1/images/generations"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1-mini")
    quality = os.environ.get("IMAGE_QUALITY", "medium")
    items = json.load(open(os.path.join(HERE, "image_manifest.json"), encoding="utf-8"))
    if "--limit" in sys.argv:
        items = items[: int(sys.argv[sys.argv.index("--limit") + 1])]
    failed = 0
    with ThreadPoolExecutor(max_workers=int(os.environ.get("IMAGE_WORKERS", "10"))) as pool:
        for fut in as_completed([pool.submit(generate, it, key, model, quality, url, headers) for it in items]):
            iid, status = fut.result()
            failed += status.startswith("error")
            print(f"{iid}: {status}", flush=True)
    done = sorted(f[:-4] for f in os.listdir(os.path.join(APP, "images")) if f.endswith(".jpg"))
    json.dump(done, open(os.path.join(APP, "images", "index.json"), "w"))
    print(f"{len(done)} images ready, {failed} failed")

if __name__ == "__main__":
    main()
