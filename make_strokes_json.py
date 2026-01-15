import os, json, re
import xml.etree.ElementTree as ET

KANJI_DIR = "kanji-svg"
OUT_FILE = "strokes.json"
S_RE = re.compile(r"-s(\d+)\b")

def extract_ds(svg_path: str):
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
    except Exception:
        return None

    paths = []
    for el in root.iter():
        if not el.tag.lower().endswith("path"):
            continue
        pid = el.attrib.get("id", "")
        d = el.attrib.get("d", "")
        if not d:
            continue
        m = S_RE.search(pid)
        if not m:
            continue
        n = int(m.group(1))
        paths.append((n, d))

    if not paths:
        return None

    paths.sort(key=lambda x: x[0])
    return [d for _, d in paths]

def main():
    if not os.path.isdir(KANJI_DIR):
        raise SystemExit(f"Folder not found: {KANJI_DIR}")

    data = {}
    total = 0
    ok = 0

    for fn in sorted(os.listdir(KANJI_DIR)):
        if not fn.lower().endswith(".svg"):
            continue
        hexpart = fn[:-4]
        try:
            ch = chr(int(hexpart, 16))
        except Exception:
            continue

        total += 1
        ds = extract_ds(os.path.join(KANJI_DIR, fn))
        if ds:
            data[ch] = ds
            ok += 1

    out = {"version": 1, "strokes": data}
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    print(f"✅ wrote {OUT_FILE}: {ok}/{total} files had strokes")

if __name__ == "__main__":
    main()
