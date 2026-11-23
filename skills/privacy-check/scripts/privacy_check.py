#!/usr/bin/env python3
"""Find personal data in design sources (HTML, MD, TXT, SVG, captions) before content is published.

Usage:
  python3 privacy_check.py <folder or file> [...] [--allow-domain example.org ...]

Looks for Indonesian civil-servant IDs (NIP, 18 digits with a birth-date structure), national IDs (NIK,
16 digits), mobile numbers, personal emails, licence plates, and labels like "Name:/ID:" that come along
with app screenshots. Images referenced by HTML are listed too: stock photos are licensed, but screenshots
and event photos must be looked at by a person (names on screen, faces of non-models).
Exit code 1 if anything FAILS.
"""
import argparse, os, re, sys
from urllib.parse import unquote

ap = argparse.ArgumentParser()
ap.add_argument("paths", nargs="*", default=["."])
ap.add_argument("--allow-domain", nargs="*", default=[], help="email domains that are fine to show (e.g. the organisation's own)")
ap.add_argument("--stock-hint", nargs="*", default=["stock", "logo", "cutout"], help="path fragments of images that need no manual review")
a = ap.parse_args()

TEXT = (".html", ".htm", ".md", ".txt", ".svg")
allow = "|".join(re.escape(d) for d in a.allow_domain) or r"(?!)"
PAT = [
    ("FAIL", "NIP (civil-servant ID)", re.compile(r"(?<!\d)(19|20)\d{6}\s?(19|20)\d{4}\s?[12]\s?\d{3}(?!\d)")),
    ("FAIL", "NIK (national ID)", re.compile(r"(?<!\d)\d{16}(?!\d)")),
    ("FAIL", "phone number", re.compile(r"(?<![\d\w])(\+62|62|0)8\d{1,2}[-\s]?\d{3,4}[-\s]?\d{3,5}(?!\d)")),
    ("CHECK", "email", re.compile(rf"[\w.+-]+@(?!(?:{allow})\b)[\w-]+\.[\w.]+")),
    ("CHECK", "licence plate", re.compile(r"\b[A-Z]{1,2}\s\d{1,4}\s[A-Z]{1,3}\b")),
    ("CHECK", "identity label", re.compile(r"\b(NIP|NIK|ID No\.?|Phone|Date of Birth|Address|Tanggal Lahir|Alamat)\s*[:：]", re.I)),
]
IMG = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+\.(?:png|jpe?g|webp))["']|url\(\s*["']?([^"')]+\.(?:png|jpe?g|webp))""", re.I)

def files(args):
    for p in args:
        if os.path.isdir(p):
            for d, subs, fs in os.walk(p):
                subs[:] = [s for s in subs if not s.startswith(".") and s != "node_modules"]
                yield from (os.path.join(d, f) for f in fs if f.lower().endswith(TEXT))
        elif os.path.exists(p):
            yield p

found = {"FAIL": [], "CHECK": []}
images = set()
for path in files(a.paths):
    text = open(path, encoding="utf-8", errors="ignore").read()
    if path.endswith((".html", ".htm")):
        images.update(unquote(m.group(1) or m.group(2)).replace("file://", "") for m in IMG.finditer(text))
        text = re.sub(r"data:[^\"')]+", "", text)  # skip embedded base64
    for lvl, name, rx in PAT:
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            found[lvl].append(f"{name} \"{m.group(0)[:40]}\" in {os.path.basename(path)}:{line}")

print("# Privacy check")
for lvl in ("FAIL", "CHECK"):
    items = list(dict.fromkeys(found[lvl]))
    print(f"## {lvl} ({len(items)})")
    for i in items[:40]:
        print(f"- {i}")
review = sorted({os.path.basename(i): i for i in images if not any(s.lower() in i.lower() for s in a.stock_hint)}.values())
print(f"## Images to look at yourself ({len(review)})")
print("Screenshots: no staff names, IDs, emails or other personal data. Event photos: faces of people who are not models need consent or blurring.")
for i in review:
    print(f"- {i}")
print(f"\nVerdict: {'FAIL' if found['FAIL'] else 'CHECK' if found['CHECK'] or review else 'PASS'}")
sys.exit(1 if found["FAIL"] else 0)
