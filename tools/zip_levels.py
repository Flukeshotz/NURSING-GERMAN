#!/usr/bin/env python3
"""Zip the images each level uses (listed in content/levels/level-XX.json) into level-XX-images.zip."""
import json, os, zipfile
APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LV = os.path.join(APP, "content", "levels")
for f in sorted(os.listdir(LV)):
    if not (f.startswith("level-") and f.endswith(".json")):
        continue
    data = json.load(open(os.path.join(LV, f), encoding="utf-8"))
    out = os.path.join(LV, data["images_zip"])
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as z:
        for name in data["images"]:
            z.write(os.path.join(APP, "images", name), arcname=name)
    print(f"{data['images_zip']}: {len(data['images'])} images, {os.path.getsize(out)//1024} KB")
