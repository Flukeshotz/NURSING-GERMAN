#!/usr/bin/env python3
"""Write the list of available pictures into index.html (window.IMGSET), so the prototype never shows half a set."""
import json, os, re
APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = sorted(f[:-4] for f in os.listdir(os.path.join(APP, "images")) if f.endswith(".jpg"))
p = os.path.join(APP, "index.html"); t = open(p, encoding="utf-8").read()
t, n = re.subn(r"window\.IMGSET=new Set\(\[.*?\]\);", "window.IMGSET=new Set(" + json.dumps(ids) + ");", t, count=1, flags=re.S)
assert n == 1
open(p, "w", encoding="utf-8").write(t)
json.dump(ids, open(os.path.join(APP, "images", "index.json"), "w"))
print(f"{len(ids)} pictures listed in index.html")
