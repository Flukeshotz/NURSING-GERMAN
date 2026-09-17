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
        if im.size[0] > 640:
            im.convert("RGB").resize((640, 640), Image.LANCZOS).save(p, "JPEG", quality=78, optimize=True, progressive=True)
            done += 1
print(f"optimized {done} images")
