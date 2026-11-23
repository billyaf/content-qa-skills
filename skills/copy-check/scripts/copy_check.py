#!/usr/bin/env python3
"""Check a carousel copy file (copy.md) before design: house terms, hashtags, common spelling, phrases
repeated on one slide, numbers with no source, title length, caption length, leftover placeholders.

Usage:
  python3 copy_check.py path/to/copy.md [--rules rules.json] [--sources brief.md facts.md ...]

Default --sources: brief.md and facts.md next to copy.md.
Exit code 1 if anything FAILS. Findings are hints, not verdicts: read each one in context.
"""
import argparse, json, os, re, sys

STOP = set("a an the and or of to in on for with by is are be as at this that it from your our dan di ke dari untuk yang dengan pada ini itu atau dalam oleh sebagai juga akan".split())

ap = argparse.ArgumentParser()
ap.add_argument("copy")
ap.add_argument("--rules", help="JSON with terms, spelling, hashtags, limits (see examples/carousel/rules.json)")
ap.add_argument("--sources", nargs="*")
a = ap.parse_args()

text = open(a.copy, encoding="utf-8").read()
base = os.path.dirname(os.path.abspath(a.copy))
src_files = a.sources if a.sources is not None else [os.path.join(base, f) for f in ("brief.md", "facts.md")]
sources = "\n".join(open(f, encoding="utf-8").read() for f in src_files if os.path.exists(f))
rules = json.load(open(a.rules, encoding="utf-8")) if a.rules and os.path.exists(a.rules) else {}
lim = {"title_lines": 3, "caption_chars": 2200, "max_hashtags": 8, "repeat_ngram": 2, **rules.get("limits", {})}

out = {"FAIL": [], "CHECK": [], "INFO": []}
add = lambda lvl, where, msg: out[lvl].append(f"{where}: {msg}")
strip_ph = lambda s: re.sub(r"\[[^\]]*\]", " ", s)
clean = lambda s: re.sub(r"[*`_>]|HIGHLIGHT:", "", s).strip()

# ---- split slides and caption ----
slides, caption = [], ""
for sec in re.split(r"^## ", text, flags=re.M):
    head, _, body = sec.partition("\n")
    if re.match(r"slide\s*\d+", head, re.I):
        rows = []
        for line in body.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else []
            if len(cells) >= 2 and not re.match(r"^-+$", cells[0].replace(":", "")) and cells[0].lower() not in ("element", "elemen"):
                rows.append((clean(cells[0]), clean(cells[1])))
        slides.append((head.strip(), rows))
    elif head.lower().startswith("caption"):
        caption = body
cap_text = "\n".join(l.lstrip("> ").rstrip() for l in caption.splitlines() if l.startswith(">"))

# ---- per slide ----
for name, rows in slides:
    where = name.split(":")[0]
    titles = [r for r in rows if re.match(r"(title line|judul baris)", r[0], re.I)]
    if len(titles) > lim["title_lines"]:
        add("CHECK", where, f"title has {len(titles)} lines (limit {lim['title_lines']})")
    # The same phrase twice on one slide, e.g. an eyebrow "In 2026," and a title line "IN 2026".
    seen = {}
    for el, val in rows:
        if re.search(r"note|hint|slot|logo", el, re.I):
            continue
        words = re.findall(r"[a-z0-9]+", strip_ph(val).lower())
        n = lim["repeat_ngram"]
        for i in range(len(words) - n + 1):
            gram = tuple(words[i:i + n])
            if not all(w in STOP for w in gram):
                seen.setdefault(gram, set()).add(el)
    for gram, els in seen.items():
        if len(els) > 1:
            add("CHECK", where, f"phrase \"{' '.join(gram)}\" appears in {len(els)} elements ({', '.join(sorted(els))})")
    ph = sum(len(re.findall(r"\[[^\]]+\]", v)) for _, v in rows)
    if ph:
        add("INFO", where, f"{ph} [placeholder] left (fine for a template; a final design must fill them)")

# ---- terms, spelling, numbers ----
body_text = "\n".join(v for _, rows in slides for _, v in rows) + "\n" + cap_text
for t in rules.get("terms", []):
    for wrong in t.get("wrong", []):
        if re.search(rf"(?<![\w#@]){re.escape(wrong)}(?!\w)", body_text):
            add("FAIL", "terms", f"\"{wrong}\" → use \"{t['right']}\" ({t.get('source', '')})")
for wrong, right in rules.get("spelling", []):
    if re.search(rf"(?<!\w){re.escape(wrong)}(?!\w)", body_text, re.I):
        add("CHECK", "spelling", f"\"{wrong}\" → \"{right}\"")

norm = lambda s: re.sub(r"[\s.,]", "", s)
src_norm = norm(sources)
for m in sorted(set(re.findall(r"\d[\d.,:]*\d|\d", strip_ph(body_text)))):
    v = m.strip(".,:")
    if len(v) < 2 or re.fullmatch(r"0\d", v):
        continue  # single digits and slide labels like 01
    if norm(v) not in src_norm:
        add("FAIL" if sources else "CHECK", "numbers", f"\"{v}\" is not in the brief/facts: cite a source or use a placeholder")

# ---- hashtags and caption ----
tags = list(dict.fromkeys(re.findall(r"#\w+", cap_text)))
h = rules.get("hashtags", {})
if len(tags) > lim["max_hashtags"]:
    add("CHECK", "hashtags", f"{len(tags)} hashtags (suggested max {lim['max_hashtags']})")
for t in tags:
    if h.get("official") and t not in h["official"] and t not in h.get("undecided", []):
        add("CHECK", "hashtags", f"{t} is not in the official list {h['official']}")
    if t in h.get("undecided", []):
        add("CHECK", "hashtags", f"{t} has not been decided by the owner; ask at the checkpoint")
if len(cap_text) > lim["caption_chars"]:
    add("CHECK", "caption", f"{len(cap_text)} characters (limit {lim['caption_chars']})")
if not cap_text:
    add("CHECK", "caption", "no caption block (lines starting with '>') under ## Caption")

# ---- report ----
print(f"# Copy check: {a.copy}")
print(f"{len(slides)} slides, caption {len(cap_text)} characters, {len(tags)} hashtags. Sources: {', '.join(os.path.basename(f) for f in src_files if os.path.exists(f)) or '-'}\n")
for lvl in ("FAIL", "CHECK", "INFO"):
    items = list(dict.fromkeys(out[lvl]))
    print(f"## {lvl} ({len(items)})")
    for i in items:
        print(f"- {i}")
    print()
print(f"Verdict: {'FAIL' if out['FAIL'] else 'CHECK' if out['CHECK'] else 'PASS'}")
sys.exit(1 if out["FAIL"] else 0)
