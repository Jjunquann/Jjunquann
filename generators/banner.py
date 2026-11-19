"""README art generator (stdlib only). Edit the constants, then run: python3 generators/banner.py
No argument: writes every asset into assets/.  "auto": writes assets/banner.svg for the current Singapore time
of day (day 07-17, sunset 17-20, night 20-07); the banner workflow publishes it."""
import base64, json, random, sys
from datetime import datetime, timedelta, timezone

NAME, ROLE, W, H = "Jjunquan", "Computer Science Student at the University of Wollongong", 1200, 340
FACTS = [("LOCATION", "Singapore"), ("LEARNING", "C++"), ("HOBBIES", "Darts, gym, anime"), ("LANGUAGE", "English")]
INK, CREAM, MUTED, GOLD, LINE = "#0f0d1f", "#f3f1ff", "#b9b4d8", "#ffc94a", "#2a2450"
FONT = base64.b64encode(open("assets/fredoka-600.ttf", "rb").read()).decode()  # Fredoka (OFL), Basic Latin only
FONTFACE = "@font-face{font-family:Fredoka;src:url(data:font/ttf;base64," + FONT + ")}"
FAMILY = "Fredoka,'Arial Rounded MT Bold',ui-rounded,'Varela Round',sans-serif"
# One calm scene per time of day: sky gradient, skyline tones, window colour, sun/moon colour, label
THEMES = {
    "night": dict(sky=("#0f0d1f", "#241c55"), bld=("#1a1544", "#221b52"), win="#ffd36a", orb="#fff2c4", moon=True, stars=16, label="NIGHT"),
    "sunset": dict(sky=("#2b2060", "#d9648f", "#f6b27a"), bld=("#2a1f5c", "#1d1747"), win="#ffd36a", orb="#f08a3c", moon=False, stars=5, label="SUNSET"),
    "day": dict(sky=("#6cc3f2", "#cfeaf7"), bld=("#7b73c4", "#6a62b0"), win="#fff2c4", orb="#ffc94a", moon=False, stars=0, label="DAY"),
}
SUN = [(x, y) for x in range(7) for y in range(7) if (x - 3) ** 2 + (y - 3) ** 2 <= 9]
MOON = [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (2, 4), (0, 5), (1, 5), (2, 5), (1, 6), (2, 6), (3, 6)]


def banner(t):
    """Hero: quiet pixel skyline, eyebrow, name, role."""
    P = 12
    r = random.Random(11)
    k = len(t["sky"]) - 1
    stops = "".join(f'<stop offset="{i/k}" stop-color="{c}"/>' for i, c in enumerate(t["sky"]))
    dark = t["label"] != "DAY"
    name_c, role_c, eye_c = (CREAM, MUTED, GOLD) if dark else ("#18161f", "#3d3860", "#8a5a00")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">',
         f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
         '<style>' + FONTFACE + '.w{animation:w 5s ease-in-out infinite alternate}@keyframes w{from{opacity:.45}to{opacity:1}}'
         '.s{animation:s 3.4s ease-in-out infinite alternate}@keyframes s{from{opacity:.2}to{opacity:.9}}'
         '.cl{animation:cl 100s linear infinite}@keyframes cl{from{transform:translateX(-260px)}to{transform:translateX(1280px)}}'
         '.sh{opacity:0;animation:sh 12s linear infinite}@keyframes sh{0%,72%{opacity:0;transform:translate(0,0)}74%{opacity:1}84%{opacity:0;transform:translate(-240px,120px)}100%{opacity:0}}'
         '.tl{transform-box:fill-box;transform-origin:0% 100%;animation:tl 3s ease-in-out infinite alternate}@keyframes tl{from{transform:rotate(-12deg)}to{transform:rotate(16deg)}}'
         '.bk{transform-box:fill-box;transform-origin:center;animation:bk 7s infinite}@keyframes bk{0%,93%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}'
         '@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style></defs>',
         f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>']
    for _ in range(t["stars"]):
        o.append(f'<rect class="s" x="{r.randrange(600,1180,6)}" y="{r.randrange(18,150,6)}" width="6" height="6" fill="{t["orb"]}" style="animation-delay:{r.random()*3.4:.1f}s"/>')
    for x, y in (MOON if t["moon"] else SUN):
        o.append(f'<rect x="{1020+x*12}" y="{(150 if t["label"] == "SUNSET" else 40)+y*12}" width="12" height="12" fill="{t["orb"]}"/>')
    cc, co = {"NIGHT": ("#ffffff", .07), "SUNSET": ("#ffd6c0", .4), "DAY": ("#ffffff", .9)}[t["label"]]
    for cy, sc, dur, delay in ((24, 1.0, 100, -20), (52, 0.7, 130, -75), (30, 0.85, 115, -50)):
        cells = "".join(f'<rect x="{cx*10}" y="{ry*10}" width="10" height="10"/>' for ry, (a, b) in enumerate(((2, 5), (1, 7), (0, 8))) for cx in range(a, b + 1))
        o.append(f'<g class="cl" style="animation-duration:{dur}s;animation-delay:{delay}s" fill="{cc}" opacity="{co}"><g transform="translate(0 {cy}) scale({sc})">{cells}</g></g>')
    if t["label"] == "NIGHT":  # an occasional shooting star
        o.append(f'<g class="sh" fill="{t["orb"]}"><rect x="900" y="30" width="6" height="6"/><rect x="912" y="26" width="6" height="6" opacity=".6"/><rect x="924" y="22" width="6" height="6" opacity=".3"/></g>')
    roofs = []
    x = 0
    while x < W:
        w, h = r.choice([5, 6, 7, 8]) * P, r.randrange(3, 7) * P
        o.append(f'<rect x="{x}" y="{H-h}" width="{w}" height="{h}" fill="{r.choice(t["bld"])}"/>')
        roofs.append((x, w, H - h))
        for wx in range(x + P, x + w - P, 2 * P):
            for wy in range(H - h + P, H - P, 2 * P):
                if r.random() < .3:
                    o.append(f'<rect class="w" x="{wx}" y="{wy}" width="{P}" height="{P}" fill="{t["win"]}" style="animation-delay:{r.random()*5:.1f}s"/>')
        x += w
    C = 10  # cat pixel size
    bx, bw, top = next((b for b in roofs if b[0] >= 860 and b[1] >= 72), roofs[-1])
    cx0, cy0, ink = bx + 16, top - 7 * C, ("#2d2760" if t["label"] == "DAY" else "#0a0720")
    body = {(0, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)}
    cell = lambda a, b: f'<rect x="{cx0+a*C}" y="{cy0+b*C}" width="{C}" height="{C}"/>'
    o.append(f'<g fill="{ink}" stroke="{ink}" stroke-width="1">' + "".join(cell(a, b) for a, b in sorted(body)) + '</g>')
    o.append(f'<g fill="{ink}" class="tl">' + "".join(cell(a, b) for a, b in ((7, 6), (8, 6), (9, 5), (9, 4))) + '</g>')
    o.append(f'<g fill="{GOLD}" class="bk">{cell(1, 2)}{cell(3, 2)}</g>')
    o += [f'<text x="68" y="104" font-family="{FAMILY}" font-size="20" letter-spacing="6" fill="{eye_c}">{t["label"]} IN SINGAPORE</text>',
          f'<text x="62" y="196" font-family="{FAMILY}" font-size="104" fill="{name_c}">{NAME}</text>',
          f'<text x="68" y="244" font-family="{FAMILY}" font-size="26" fill="{role_c}">{ROLE}</text></svg>']
    return "\n".join(o)


def facts():
    """Four-column fact bar under the hero."""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 120" width="{W}" height="120">',
         f'<style>{FONTFACE}</style><rect width="{W}" height="120" rx="14" fill="{INK}"/>']
    widths, x = [300, 230, 410, 260], 0  # column widths follow content length
    for i, ((k, v), w) in enumerate(zip(FACTS, widths)):
        if i:
            o.append(f'<rect x="{x}" y="28" width="2" height="64" fill="{LINE}"/>')
        o.append(f'<text x="{x+44}" y="44" font-family="{FAMILY}" font-size="17" letter-spacing="5" fill="{GOLD}">{k}</text>')
        o.append(f'<text x="{x+44}" y="86" font-family="{FAMILY}" font-size="30" fill="{CREAM}">{v}</text>')
        x += w
    return "\n".join(o) + "</svg>"


TECH = [("LANGUAGES", ["Python", "Java", "C++", "JavaScript"]), ("WEB", ["HTML", "CSS", "Cloudflare"]), ("TOOLS", ["Git", "GitHub"])]


def tech():
    """Skill panel: one row per group, a pixel-cornered chip per item (same panel style as the fact bar)."""
    row, H = 64, 40 + 64 * len(TECH)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<style>{FONTFACE}</style><rect width="{W}" height="{H}" rx="14" fill="{INK}"/>']
    for i, (label, items) in enumerate(TECH):
        y = 20 + i * row
        if i:
            o.append(f'<rect x="44" y="{y-2}" width="{W-88}" height="2" fill="{LINE}"/>')
        o.append(f'<text x="44" y="{y+38}" font-family="{FAMILY}" font-size="17" letter-spacing="5" fill="{GOLD}">{label}</text>')
        x = 250
        for t in items:
            w = int(len(t) * 13.5 + 52)
            o.append(f'<rect x="{x}" y="{y+8}" width="{w}" height="44" rx="6" fill="#1a1544" stroke="{LINE}" stroke-width="2"/>'
                     f'<rect x="{x+14}" y="{y+26}" width="8" height="8" fill="{GOLD}"/>'
                     f'<text x="{x+32}" y="{y+38}" font-family="{FAMILY}" font-size="22" fill="{CREAM}">{t}</text>')
            x += w + 14
    return "\n".join(o) + "</svg>"


SPRITES = json.load(open("assets/sprites/meta-small.json"))  # one chibi pose per digit 0-9, blank card box in each
DIGIT_FONT = base64.b64encode(open("assets/silkscreen-digits.ttf", "rb").read()).decode()  # Silkscreen Bold (OFL), digits only


def counter(n, digits=5):
    """Visitor counter: digit d is pose d of the sprite sheet, with the digit written on its blank card."""
    slot, H = 200, 320
    num = str(n).zfill(digits)[-digits:]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {slot*digits} {H}" width="{slot*digits}" height="{H}">',
         '<style>@font-face{font-family:Silk;src:url(data:font/ttf;base64,' + DIGIT_FONT + ')}</style><defs>']
    for d in sorted(set(num)):
        img = base64.b64encode(open(f"assets/sprites/small/s{d}.png", "rb").read()).decode()
        m = SPRITES[int(d)]
        o.append(f'<image id="p{d}" width="{m["w"]}" height="{m["h"]}" href="data:image/png;base64,{img}"/>')
    o.append('</defs>')
    for i, d in enumerate(num):
        m = SPRITES[int(d)]
        sx, sy = i * slot + (slot - m["w"]) // 2, H - m["h"] - 8
        cx, cy, cw, ch = m["card"]
        o.append(f'<use href="#p{d}" x="{sx}" y="{sy}"/>')
        o.append(f'<text x="{sx+cx+cw/2}" y="{sy+cy+ch/2+14}" text-anchor="middle" font-family="Silk" font-weight="700" font-size="40" fill="#2a2236">{d}</text>')
    return "\n".join(o) + "</svg>"


CAT = ["X......X", "XX....XX", "XXXXXXXX", "XXXXXXXX", "XSSXXSSX", "XXXXXXXX", "XXXNNXXX", ".XXXXXX."]
PROJECT = dict(tag="BUILT BY ME", name="Digital Biz Card", lines=["Gamified business card with pixel scenes", "and collectible card packs"],
               chips=["JAVASCRIPT", "CLOUDFLARE", "NFC + QR"], cta="OPEN LIVE CARD")


def project(d=PROJECT):
    """450x219 project card, the same size as the stat cards so they pair up."""
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 219" width="450" height="219">',
         f'<style>{FONTFACE}</style><rect width="450" height="219" rx="10" fill="{INK}"/>',
         f'<text x="24" y="38" font-family="{FAMILY}" font-size="14" letter-spacing="4" fill="{GOLD}">{d["tag"]}</text>',
         f'<text x="24" y="80" font-family="{FAMILY}" font-size="36" fill="{CREAM}">{d["name"]}</text>']
    for i, l in enumerate(d["lines"]):
        o.append(f'<text x="24" y="{110+i*22}" font-family="{FAMILY}" font-size="16" fill="{MUTED}">{l}</text>')
    x = 24
    for c in d["chips"]:
        w = len(c) * 9 + 20
        o.append(f'<rect x="{x}" y="152" width="{w}" height="24" rx="6" fill="#1d1747"/><text x="{x+w/2}" y="169" text-anchor="middle" font-family="{FAMILY}" font-size="12" letter-spacing="1" fill="{GOLD}">{c}</text>')
        x += w + 8
    o.append(f'<text x="24" y="204" font-family="{FAMILY}" font-size="15" letter-spacing="3" fill="{CREAM}">{d["cta"]}  &#8594;</text>')
    return "\n".join(o) + "</svg>"


GLYPHS = {  # 5x7 pixel font for the button
    "C": [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"], "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "N": ["X...X", "XX..X", "XX..X", "X.X.X", "X..XX", "X..XX", "X...X"], "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"], "M": ["X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
}


def button(text="CONTACT ME", k=2):
    """Pixel-art pill button (blue, plum outline, glossy top) linking to the digital card; the README wraps it in a link."""
    tw = sum((5 if ch != " " else 3) + 1 for ch in text) * k - k
    W, H = tw + 16, 26
    L = [8, 5, 3, 2, 1, 1]
    inset = lambda y: L[min(y, H - 1 - y)] if min(y, H - 1 - y) < len(L) else 0
    inside = lambda x, y: 0 <= y < H and inset(y) <= x < W - inset(y)
    px = {}
    for y in range(H):
        for x in range(W):
            if inside(x, y):
                edge = not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                px[(x, y)] = "#5b2a4e" if edge else "#54d8d8" if y in (1, 2) else "#0668c0" if y in (H - 3, H - 2) else "#07a0e0"
    for x, y in ((4, 3), (5, 3), (6, 3), (4, 4), (4, 5)):
        px[(x, y)] = "#ffffff"
    x0, y0 = (W - tw) // 2, (H - 7 * k) // 2
    for ch in text:
        if ch == " ":
            x0 += 4 * k
            continue
        for gy, row in enumerate(GLYPHS[ch]):
            for gx, c in enumerate(row):
                if c == "X":
                    for dx in range(k):
                        for dy in range(k):
                            px[(x0 + gx * k + dx, y0 + gy * k + dy)] = "#5b2a4e"
        x0 += 6 * k
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {W+2} {H+3}" width="{(W+2)*4}" height="{(H+3)*4}" shape-rendering="crispEdges">',
         '<style>.b{animation:b 1.6s ease-in-out infinite}@keyframes b{50%{transform:translateY(1px)}}</style><g class="b">']
    for y in range(H):  # merge horizontal runs of one colour into a single rect
        x = 0
        while x < W:
            c = px.get((x, y))
            if c is None:
                x += 1
                continue
            n = 1
            while px.get((x + n, y)) == c:
                n += 1
            o.append(f'<rect x="{x}" y="{y}" width="{n+.02}" height="1.02" fill="{c}"/>')
            x += n
    return "".join(o) + "</g></svg>"


if __name__ == "__main__":
    if sys.argv[1:2] == ["counter"]:
        open("assets/counter.svg", "w").write(counter(int(sys.argv[2])))
    elif sys.argv[1:] == ["auto"]:
        h = (datetime.now(timezone.utc) + timedelta(hours=8)).hour
        open("assets/banner.svg", "w").write(banner(THEMES["day" if 7 <= h < 17 else "sunset" if 17 <= h < 20 else "night"]))
    else:
        for k, t in THEMES.items():
            open(f"assets/banner-{k}.svg", "w").write(banner(t))
        open("assets/facts.svg", "w").write(facts())
        open("assets/tech.svg", "w").write(tech())
        open("assets/project-biz-card.svg", "w").write(project())
        open("assets/reach-out.svg", "w").write(button())
