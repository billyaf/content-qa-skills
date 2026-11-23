#!/usr/bin/env python3
"""Technical check of a social-media design (PNG/JPG) against a brand file: canvas size, palette share,
vertical rhythm (gaps between blocks), large dead areas, and elements touching the side margins.

Usage: python3 tech_check.py --brand brand.json IMAGE.png [IMAGE2.png ...]
Needs Pillow (pip install pillow) or, on macOS, nothing: it falls back to `sips`.
"""
import argparse, json, os, struct, subprocess, sys, tempfile, statistics as st


def load(path):
    """Returns (w, h, px) where px(x, y) -> (r, g, b)."""
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        data = im.load()
        return im.width, im.height, lambda x, y: data[x, y]
    except ImportError:
        tmp = tempfile.mkdtemp()
        bmp = os.path.join(tmp, "x.bmp")
        subprocess.run(["sips", "-s", "format", "bmp", path, "--out", bmp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        b = open(bmp, "rb").read()
        off = struct.unpack_from("<I", b, 10)[0]
        w, h = struct.unpack_from("<ii", b, 18)
        bpp = struct.unpack_from("<H", b, 28)[0]
        topdown, h, bp = h < 0, abs(h), bpp // 8
        row = ((w * bpp + 31) // 32) * 4
        def px(x, y):
            i = off + (y if topdown else h - 1 - y) * row + x * bp
            return b[i + 2], b[i + 1], b[i]
        return w, h, px


hexrgb = lambda s: tuple(int(s.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
lum = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
dist = lambda a, b: sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def check(path, brand):
    w, h, px = load(path)
    sizes = {tuple(map(int, k.split("x"))): v for k, v in brand["sizes"].items()}
    palette = {k: hexrgb(v) for k, v in brand["palette"].items()}
    bg = [hexrgb(c) for c in brand.get("background", [])]
    accent = [hexrgb(c) for c in brand.get("edgeColors", [])]
    QUIET = brand.get("quietStdDev", 10.0)  # luminance std-dev below which a row counts as empty background

    def is_bg(cs):
        if st.pstdev([lum(c) for c in cs]) >= QUIET:
            return False
        mean = tuple(sum(c[i] for c in cs) / len(cs) for i in range(3))
        return any(dist(mean, b) < 60 for b in bg) if bg else True

    print(f"\n=== {os.path.basename(path)} ===")
    kind = sizes.get((w, h))
    print(f"[{'OK' if kind else 'FAIL'}] Size {w}×{h}" + (f" ({kind})" if kind else f" — expected one of {', '.join(brand['sizes'])}"))
    sx = w / 1080.0
    story = h / w > 1.5
    gap_floor = (180 if story else 45) * sx
    dead_limit = 0.15 if story else 0.06

    # Palette share on a sampling grid
    hit, total, wild = {k: 0 for k in palette}, 0, {}
    for y in range(0, h, 12):
        for x in range(0, w, 12):
            c = px(x, y); total += 1
            name, d = min(((k, dist(c, v)) for k, v in palette.items()), key=lambda t: t[1])
            if d < 40:
                hit[name] += 1
            else:
                key = tuple(v // 32 * 32 for v in c)
                wild[key] = wild.get(key, 0) + 1
    share = sum(hit.values()) / total
    # Photo-heavy designs legitimately score low; what really breaks a brand is ONE off-palette colour
    # taking over the canvas (e.g. a background colour copied from the brief). Black is ignored (photo shadows).
    dominant = max((v for k, v in wild.items() if k != (0, 0, 0)), default=0) / total
    if dominant >= 0.25:
        status, note = "FAIL", f" — one off-palette colour covers {dominant:.0%} of the canvas"
    elif share > 0.55:
        status, note = "OK", ""
    else:
        status, note = "CHECK", " — fine if a photo fills the canvas; make sure background, highlights and accents use the palette"
    print(f"[{status}] {share:.0%} of pixels are close to a palette token" + note)
    print("      " + ", ".join(f"{k} {v / total:.0%}" for k, v in sorted(hit.items(), key=lambda t: -t[1]) if v / total >= 0.01))

    # Vertical rhythm: empty rows inside the content column
    m = brand.get("contentColumn", [108, 972])
    x0, x1 = int(m[0] * sx), int(m[1] * sx)
    top, bottom = int(brand.get("skipTop", 200) * sx), h - int(brand.get("skipBottom", 130) * sx)
    quiet = [is_bg([px(x, y) for x in range(x0, x1, 6)]) for y in range(top, bottom)]
    gaps, start = [], None
    for i, s in enumerate(quiet + [False]):
        if s and start is None:
            start = i
        elif not s and start is not None:
            if i - start >= 8:
                gaps.append((top + start, i - start))
            start = None
    gaps = [(y, t) for y, t in gaps if y > top and y + t < bottom]
    if not gaps:
        print("[OK] No empty gaps ≥ 8 px between blocks in the content column")
    else:
        hs = [t for _, t in gaps]
        med = st.median(hs)
        print(f"[INFO] {len(gaps)} gaps between blocks; median {med:.0f}px, largest {max(hs)}px")
        big = [g for g in gaps if g[1] > max(2.2 * med, gap_floor)]
        for y, t in gaps:
            print(f"      y={y:>4}–{y + t:<4} {t:>3}px" + ("  ← much larger than the rhythm" if (y, t) in big else ""))
        print(f"[{'CHECK' if big else 'OK'}] Spacing rhythm " + ("is uneven: one gap stands out" if big else "is even"))

    # Dead area: connected empty 54 px cells
    cell = int(54 * sx)
    cols, rows = (x1 - x0) // cell, (bottom - top) // cell
    empty = {(i, j) for j in range(rows) for i in range(cols)
             if is_bg([px(x0 + i * cell + dx, top + j * cell + dy) for dy in range(0, cell, 9) for dx in range(0, cell, 9)])}
    best, seen = [], set()
    for c in empty:
        if c in seen:
            continue
        stack, group = [c], []
        seen.add(c)
        while stack:
            i, j = stack.pop(); group.append((i, j))
            for n in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if n in empty and n not in seen:
                    seen.add(n); stack.append(n)
        if len(group) > len(best):
            best = group
    area = len(best) * cell * cell / max(1, (x1 - x0) * (bottom - top))
    where = f" around x={x0 + min(i for i, _ in best) * cell}–{x0 + (max(i for i, _ in best) + 1) * cell}, y={top + min(j for _, j in best) * cell}–{top + (max(j for _, j in best) + 1) * cell}" if best else ""
    print(f"[{'CHECK' if area > dead_limit else 'OK'}] Largest connected empty area {area:.0%} of the content area{where}")

    # Side margins: text-coloured pixels in the outer 60 px of the text area
    stray = 0
    for y in range(top, int(h * 0.62), 4):
        for x in list(range(0, int(60 * sx), 6)) + list(range(w - int(60 * sx), w, 6)):
            if any(dist(px(x, y), c) < 40 for c in accent):
                stray += 1
    print(f"[{'OK' if stray < 5 else 'CHECK'}] Outer 60 px margins " + ("are clear" if stray < 5 else f"contain {stray} text-coloured points — is an element outside the column?"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("images", nargs="+")
    a = ap.parse_args()
    brand = json.load(open(a.brand, encoding="utf-8"))
    for p in a.images:
        check(p, brand)
