import os, json
from PIL import Image
BASE = "/workspace/pixel_art"
rows = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
    for f in sorted(files):
        if f.endswith(".png"):
            p = os.path.join(root, f)
            im = Image.open(p)
            rows.append((os.path.relpath(p, BASE), im.size[0], im.size[1]))
with open(os.path.join(BASE, "MANIFEST.txt"), "w") as fh:
    fh.write(f"{'FILE':70s} {'W':>5s} {'H':>5s}\n")
    fh.write("-" * 82 + "\n")
    for r in rows:
        fh.write(f"{r[0]:70s} {r[1]:5d} {r[2]:5d}\n")
print(len(rows), "PNGs catalogued")
