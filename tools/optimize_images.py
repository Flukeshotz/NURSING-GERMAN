#!/usr/bin/env python3
"""Shrink generated images for mobile: 640x640 JPEG, quality 78. Safe to re-run."""
import os
from PIL import Image
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
done = 0
for f in sorted(os.listdir(D)):
    if f.endswith(".jpg"):
        p = os.path.join(D, f)
        im = Image.open(p)
        limit = 640 if im.size[0] == im.size[1] else 1200   # square cards 640, wide header 1200
        if max(im.size) > limit:
            im = im.convert("RGB"); im.thumbnail((limit, limit), Image.LANCZOS)
            im.save(p, "JPEG", quality=78, optimize=True, progressive=True)
            done += 1
print(f"optimized {done} images")
