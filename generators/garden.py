"""Commit tree SVG: one limb per active season-year, oldest at the roots. Stdlib only.
Usage: GITHUB_TOKEN=... python generators/garden.py <login> <outdir>"""
import base64, json, math, os, random, sys, urllib.request
from datetime import date

SEASONS = ["winter", "spring", "summer", "autumn"]
# shortcut: season by calendar month (Dec belongs to next year's winter), activity = all public contributions
# Sakura: pink blossom in spring, leafy in summer, rose-gold in autumn, frosted white in winter
PALETTE = {
    "winter": ["#ffffff", "#dbeafe", "#f5e1ee"],
    "spring": ["#ffb7c5", "#ffc9d6", "#ff9fb5", "#ffe1e8"],
    "summer": ["#b7e4a0", "#ffc0cf", "#9fd68a"],
    "autumn": ["#e8836b", "#f2a65a", "#d96c8c"],
}


def season_of(d):
    y, m = d.year, d.month
    if m == 12:
        return y + 1, "winter"
    return y, SEASONS[(m % 12) // 3]


def fetch(login, token):
    q = """query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){createdAt
      contributionsCollection(from:$f,to:$t){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""
    created = None
    counts = {}
    today = date.today()
    y = today.year - 5
    while y <= today.year:
        v = {"l": login, "f": f"{y}-01-01T00:00:00Z", "t": f"{y}-12-31T23:59:59Z"}
        req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q, "variables": v}).encode(),
                                     {"Authorization": f"bearer {token}"})
        u = json.load(urllib.request.urlopen(req))["data"]["user"]
        created = created or int(u["createdAt"][:4])
        for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                k = season_of(date.fromisoformat(d["date"]))
                counts[k] = counts.get(k, 0) + d["contributionCount"]
        y += 1
    return created, counts


ABBR = {"winter": "WIN", "spring": "SPR", "summer": "SUM", "autumn": "AUT"}
W, H, G, GY = 1200, 520, 6, 468  # canvas, pixel grid, ground line
WOOD, INK, CREAM, MUTED, GOLD = "#7a5a70", "#0f0d1f", "#f3f1ff", "#b9b4d8", "#ffc94a"
FONT = base64.b64encode(open("assets/fredoka-600.ttf", "rb").read()).decode()  # Fredoka (OFL), Basic Latin only
FAMILY = "Fredoka,'Arial Rounded MT Bold',ui-rounded,'Varela Round',sans-serif"
# (light, mid, dark): top-lit, so blossoms lower in a cloud use the darker tones
SHADES = {
    "winter": ("#ffffff", "#e6eefb", "#c3d1ec"), "spring": ("#ffd9e3", "#ffb7c5", "#ee8fab"),
    "summer": ("#d3f0bf", "#a8dc8f", "#72b862"), "autumn": ("#f6b98a", "#e8836b", "#c4553f"),
}
# The tree never changes shape: trunk and boughs as (start, control, end, thickness), plus where each bough starts on its parent.
TRUNK = [((600, GY), (588, 400), (598, 345), 5), ((598, 345), (604, 325), (606, 310), 4)]
BOUGHS = [
    ((606, 310), (500, 292), (400, 212), 3), ((400, 212), (352, 200), (292, 156), 2), ((470, 262), (452, 205), (452, 135), 2),
    ((606, 310), (712, 292), (812, 214), 3), ((812, 214), (862, 204), (912, 150), 2), ((728, 262), (746, 200), (748, 128), 2),
    ((606, 310), (598, 236), (620, 140), 3), ((612, 232), (560, 196), (540, 128), 2), ((616, 214), (668, 186), (690, 120), 2),
    ((600, 372), (540, 360), (470, 332), 2), ((602, 360), (668, 350), (742, 326), 2),
]


def qpt(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])


def line_cells(p0, c, p1, thick):
    """Grid cells along a quadratic curve, thick cells wide."""
    cells = set()
    for i in range(81):
        x, y = qpt(p0, c, p1, i / 80)
        gx, gy = int(x // G), int(y // G)
        for dx in range(thick):
            for dy in range(thick):
                cells.add((gx - thick // 2 + dx, gy - thick // 2 + dy))
    return cells


def runs(cells, fill):
    """Merge horizontal runs of grid cells into rects."""
    out = []
    for gy in sorted({c[1] for c in cells}):
        xs = sorted(c[0] for c in cells if c[1] == gy)
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
                j += 1
            out.append(f'<rect x="{xs[i]*G}" y="{gy*G}" width="{(xs[j]-xs[i]+1)*G}" height="{G}"/>')
            i = j + 1
    return f'<g fill="{fill}">' + "".join(out) + "</g>"


TINT = {"winter": .4, "spring": 0, "summer": .32, "autumn": .32}  # share of a cloud tinted by its season; the rest stays sakura pink


def cloud(rnd, cx, cy, radius, season):
    """A blossom cloud: dense square 'petal' blocks in a squashed disc, pink with a seasonal tint, darker toward the bottom."""
    pink, tint = SHADES["spring"], SHADES[season]
    seen, out = set(), []
    for _ in range(int(1.5 * radius * radius / 100)):
        a, d = rnd.uniform(0, 6.283), radius * math.sqrt(rnd.random())
        x, y = int((cx + d * math.cos(a)) // G) * G, int((cy + d * math.sin(a) * .78) // G) * G
        if (x, y) in seen:
            continue
        seen.add((x, y))
        low = (y - cy) / radius  # -0.8 (top) .. +0.8 (bottom)
        light, mid, dark = tint if rnd.random() < TINT[season] else pink
        col = rnd.choices([light, mid, dark], [max(.1, .5 - low), .5, max(.05, .1 + low)])[0]
        sz = 2 * G if rnd.random() < .6 else G
        tw = f' class="tw" style="animation-delay:{rnd.random()*4:.1f}s"' if rnd.random() < .12 else ""
        out.append(f'<rect{tw} x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}"/>')
    return "".join(out)


def render(login, created, counts, today=None):
    today = today or date.today()
    rnd = random.Random(login)
    active = sorted(k for k, c in counts.items() if c > 0 and k[0] >= created)
    m, total = len(active), sum(counts[k] for k in active)
    cur = season_of(today)[1]
    css = ("@font-face{font-family:Fredoka;src:url(data:font/ttf;base64," + FONT + ")}"
           ".sw{animation:sw 6s ease-in-out infinite alternate}@keyframes sw{from{transform:rotate(-1.2deg)}to{transform:rotate(1.4deg)}}"
           ".tw{animation:tw 3.6s ease-in-out infinite alternate}@keyframes tw{from{opacity:.4}to{opacity:1}}"
           ".st{animation:tw 4s ease-in-out infinite alternate}"
           ".f{opacity:0;animation:f var(--d) linear infinite}"
           "@keyframes f{0%{opacity:0;transform:translate(0,0) rotate(0)}8%{opacity:1}85%{opacity:.9}100%{opacity:0;transform:translate(var(--dx),330px) rotate(300deg)}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">',
         f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f0d1f"/><stop offset="1" stop-color="#241c55"/></linearGradient><style>{css}</style></defs>',
         f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>']
    for _ in range(18):
        o.append(f'<rect class="st" x="{rnd.randrange(24,1176,6)}" y="{rnd.randrange(96,330,6)}" width="6" height="6" fill="#fff2c4" style="animation-delay:{rnd.random()*4:.1f}s"/>')
    o.append(f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="#150f33"/>')
    o.append('<g fill="#2b2260">' + "".join(f'<rect x="{x}" y="{GY-6}" width="6" height="6"/>' for x in range(0, W, 18) if rnd.random() < .6) + "</g>")
    # skeleton
    cells, joints = set(), [(606, 310)]
    for p0, c, p1, th in TRUNK + BOUGHS:
        cells |= line_cells(p0, c, p1, th)
    for p0, c, p1, th in BOUGHS:
        joints += [qpt(p0, c, p1, t) for t in (.4, .7, 1.0)]
    o.append(runs(cells, WOOD))
    # one blossom cloud per active season: oldest near the middle, newest spreading outward over the canopy
    cx, cy, rx, ry = 600, 214, 360, 96
    for i, (y, sea) in enumerate(active):
        r = math.sqrt((i + .5) / m) if m > 1 else 0.0
        ang = i * 2.39996 + 0.6
        px, py = cx + rx * r * math.cos(ang), cy + ry * r * math.sin(ang) * .95 - 6
        radius = 42 + 26 * min(1, 8 / m) + 8 * math.log10(1 + counts[(y, sea)])
        jx, jy = min(joints, key=lambda j: (j[0] - px) ** 2 + (j[1] - py) ** 2)
        twig = runs(line_cells((jx, jy), ((jx + px) / 2 + 8, (jy + py) / 2 + 10), (px, py), 1), WOOD)
        o.append(f'<g class="sw" style="transform-origin:{jx:.0f}px {jy:.0f}px;animation-duration:{rnd.uniform(5,8):.1f}s;animation-delay:{-rnd.uniform(0,6):.1f}s">{twig}{cloud(rnd, px, py, radius, sea)}</g>')
    # falling particles in the current season's colours
    pal = SHADES[cur]
    for _ in range(26):
        sz = 6 if cur == "winter" else rnd.choice([6, 6, 12])
        o.append(f'<rect class="f" x="{rnd.randrange(300,900,6)}" y="{rnd.randrange(100,250,6)}" width="{sz}" height="6" fill="{rnd.choice(pal)}" '
                 f'style="--d:{rnd.uniform(9,15):.1f}s;--dx:{rnd.randrange(-160,40)}px;animation-delay:{-rnd.uniform(0,12):.1f}s"/>')
    # header, legend, footer
    o.append(f'<text x="36" y="48" font-family="{FAMILY}" font-size="18" letter-spacing="6" fill="{GOLD}">COMMIT GARDEN</text>')
    o.append(f'<text x="36" y="86" font-family="{FAMILY}" font-size="32" fill="{CREAM}">{total} contributions in {m} {"season" if m == 1 else "seasons"}</text>')
    for i, sea in enumerate(SEASONS):
        x = 770 + i * 108
        o.append(f'<rect x="{x}" y="40" width="14" height="14" fill="{SHADES[sea][1]}"/><text x="{x+22}" y="53" font-family="{FAMILY}" font-size="16" letter-spacing="2" fill="{MUTED}">{ABBR[sea]}</text>')
    o.append(f'<text x="36" y="{H-20}" font-family="{FAMILY}" font-size="16" fill="{MUTED}">One blossom cloud per season of contributions, tinted by season. Oldest in the middle, newest outside.</text>')
    o.append(f'<text x="{W-36}" y="{H-20}" text-anchor="end" font-family="{FAMILY}" font-size="16" fill="{MUTED}">Updated {today:%d %b %Y}</text></svg>')
    return "\n".join(o)


if __name__ == "__main__":
    login, outdir = sys.argv[1], sys.argv[2]
    created, counts = fetch(login, os.environ["GITHUB_TOKEN"])
    os.makedirs(outdir, exist_ok=True)
    open(f"{outdir}/garden-dark.svg", "w").write(render(login, created, counts))
