"""Roots for the whole page: one root system from the top of the hero down to the footer, with gold impulses.

Writes inputs/radici-pagina.svg, an animated SVG (CSS inside, no script) laid behind the page at its full width
(style.css). Every root starts at the top of the page, or branches off one that does: nothing sprouts out of nowhere.
  - the hero: roots come down at the top right, clear of the copy on the left, and draw themselves in on load;
  - one root crosses under the hero's buttons to the left margin, others carry on down the right: guided trunks
    that run the length of the page, giving off branches into the margins;
  - below the hero the roots keep to the margins and fade towards the middle, under the content.
The page uncovers the roots below the first screen as you scroll (style.css). Change SEED for another set.

Each root is a filled shape, not a stroke: it tapers smoothly from its base to a pointed tip, a branch starts as
thick as its parent is where it leaves it, and the thick roots get a lighter streak down one side for volume.

    python tools/radici.py
"""
import math
import random
from pathlib import Path

INPUTS = Path(__file__).resolve().parent.parent / "inputs"
HERO = True            # set by build(): the home page's roots, or the margins' alone
SEED = 46
W, H = 1600, 7300       # 1600 units = the page's width; at 1440 x 900 the page is ~6550 px tall = ~7300 units
HERO_END = 1000         # the hero's bottom edge, in units (at 1440 x 900)

INK = "#4a3220"
LIGHT = "#8b6a49"       # the streak of light along the thick roots
GOLD = "#e9a92a"
GROW_SPEED = 520        # units/s while the first screen's roots draw themselves in
GROW_UNTIL = 1300       # roots below this are uncovered by scrolling instead
PULSE_SPEED = 300       # units/s along a root
PULSES = 30
TIP = 0.35              # width at a tip

rnd = random.Random(SEED)
branches = []           # {"pts", "ws", "shrink", "w0", "depth", "parent", "at"}


def zone(x, y):
    """The x range roots may use at height y: right of the hero's copy, free under its buttons, then the margins."""
    if not HERO:
        return (-40, 380) if x < W / 2 else (1220, W + 40)
    if y < 760:
        return 430, W + 40
    if y < HERO_END:
        return -40, W + 40
    return (-40, 380) if x < W / 2 else (1220, W + 40)


def taper(w0, t, k=0.8):
    """Width at fraction t (0 base, 1 tip) of a root that starts w0 wide; a smaller k keeps it thick for longer."""
    return TIP + (w0 - TIP) * (1 - t) ** k


def angle_to(a, b):
    return (b - a + math.pi) % (2 * math.pi) - math.pi


def grow(x, y, ang, w0, depth, parent=None, at=0, guide=None):
    me = len(branches)
    b = {"pts": [(x, y)], "shrink": [1.0], "w0": w0, "depth": depth, "parent": parent, "at": at}
    branches.append(b)
    steps = int(rnd.uniform(26, 46) * 0.8 ** depth) + 8
    if guide:
        route = [(x, y)] + guide
        steps = int(sum(math.dist(p, q) for p, q in zip(route, route[1:])) / 11) + 20
    turn, shrink, g = 0.0, 1.0, 0
    kids = []
    for i in range(steps):
        turn = turn * 0.8 + rnd.gauss(0, 0.05)             # bends carry on for a while: smooth meanders, no zigzag
        ang += turn
        if guide and g < len(guide):                        # a trunk heads for its next waypoint
            gx, gy = guide[g]
            ang += angle_to(ang, math.atan2(gy - y, gx - x)) * 0.12
            if math.dist((x, y), (gx, gy)) < 90:
                g += 1
        else:
            ang += (math.pi / 2 - ang) * 0.05               # gravity: roots go down, they don't loop back up
            lo, hi = zone(x, y)
            if x - lo < 140 and lo > -40:
                ang += (math.pi / 2 - ang) * 0.12 - 0.03    # keep clear of the copy / the middle of the page
            if hi - x < 140 and hi < W + 40:
                ang += (math.pi / 2 - ang) * 0.12 + 0.03
        step = rnd.uniform(10, 13)
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        b["pts"].append((x, y))
        b["shrink"].append(shrink)
        lo, hi = zone(x, y)
        if y > H + 20 or x < -40 or x > W + 40 or (not guide and (x < lo - 10 or x > hi + 10)):
            break
        chance = 0.04 if guide else 0.1 if depth < 2 else 0.06   # trunks give off branches all the way down
        if depth < 3 and i > 2 and rnd.random() < chance:
            turn_to = rnd.choice((-1, 1))
            kids.append((x, y, ang + turn_to * rnd.uniform(0.35, 0.9), rnd.uniform(0.45, 0.7), len(b["pts"]) - 1))
            shrink *= 0.97 if guide else 0.86                # a root thins where it gives off a branch
    # Widths over the length the root actually grew, so a root that stopped early still ends in a fine point.
    n = len(b["pts"])
    k = 0.45 if guide else 0.8                              # trunks stay strong down the page
    b["ws"] = [max(TIP, taper(w0, j / (n - 1), k) * b["shrink"][j]) for j in range(n)]
    for kx, ky, ka, kf, kat in kids:
        if b["ws"][kat] > 1.2:
            grow(kx, ky, ka, b["ws"][kat] * kf, depth + 1, me, kat)
    return me


def build(out, hero):
    """Grow one root system and write it: with the hero's roots (the home page) or the margins' alone (the other
    pages, whose opening copy is not on the left)."""
    global HERO
    HERO = hero
    rnd.seed(SEED)
    branches.clear()
    # The hero's own roots, from the top right.
    if hero:
        for x in (1060, 1190, 1310):
            grow(x + rnd.uniform(-30, 30), -16, math.pi / 2 + rnd.uniform(-0.35, 0.35), rnd.uniform(10, 14), 1)
    # Trunks: down the right margin from the top, in from the right edge, and across under the hero to the left margin.
    grow(1480, -16, math.pi / 2, 18, 0, guide=[(1450, 900), (1480, 1900), (1420, 3000), (1490, 4200), (1430, 5400), (1480, 6600), (1450, H + 60)])
    grow(W + 18, 420, math.pi * 0.85, 12, 0, guide=[(1330, 1150), (1300, 2300), (1360, 3500), (1290, 4700), (1340, 5800)])
    left = [(150, 2000), (220, 3200), (160, 4400), (210, 5600), (170, 6900), (180, H + 60)]
    if hero:   # across under the hero's buttons, then down the left margin
        grow(930, -16, math.pi / 2, 17, 0, guide=[(900, 520), (760, 810), (430, 920), (180, 1050)] + left)
    else:      # straight down the left margin
        grow(160, -16, math.pi / 2, 17, 0, guide=[(200, 900)] + left)


    def length(pts):
        return sum(math.dist(p, q) for p, q in zip(pts, pts[1:]))


    def lineage(i, upto=None):
        """Points from the root's start down to point `upto` of branch i (all of it when None)."""
        b = branches[i]
        own = b["pts"] if upto is None else b["pts"][:upto + 1]
        return own if b["parent"] is None else lineage(b["parent"], b["at"]) + own[1:]


    def mid(p, q):
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


    def f(p):
        return f"{p[0]:.0f} {p[1]:.0f}"


    def line(pts):
        """A smooth open curve through the points' midpoints (quadratic Béziers with the points as controls)."""
        if len(pts) < 3:
            return "M" + " L".join(f(p) for p in pts)
        out = [f"M{f(pts[0])}"]
        for p, q in zip(pts[1:-1], pts[2:]):
            out.append(f"Q{f(p)} {f(mid(p, q))}")
        out.append(f"L{f(pts[-1])}")
        return " ".join(out)


    def outline(pts, ws, shift=0.0, scale=1.0):
        """A closed, smooth shape around the centre line, ws wide at each point, ending in a point at the tip.
        shift moves it sideways (in widths), scale narrows it: a streak of light down one side."""
        left, right = [], []
        for k, p in enumerate(pts):
            a, b = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            n = math.hypot(tx, ty) or 1
            nx, ny = -ty / n, tx / n
            c = (p[0] + nx * ws[k] * shift, p[1] + ny * ws[k] * shift)
            h = ws[k] * scale / 2
            left.append((c[0] + nx * h, c[1] + ny * h))
            right.append((c[0] - nx * h, c[1] - ny * h))
        a, b = pts[-2], pts[-1]
        n = math.dist(a, b) or 1
        tip = (b[0] + (b[0] - a[0]) / n * ws[-1] * 4, b[1] + (b[1] - a[1]) / n * ws[-1] * 4)
        ring = left + [tip] + right[::-1]
        out = [f"M{f(ring[0])}"]
        for p, q in zip(ring[1:-1], ring[2:]):
            out.append(f"Q{f(p)} {f(mid(p, q))}")
        out.append(f"L{f(ring[-1])}Z")
        return " ".join(out)


    # Roots: a tapered shape per branch. A mask draws the first screen's roots in on load, piece by piece as the growth
    # reaches them; further down the mask is open (the page uncovers those roots as you scroll).
    shapes, light, reveal = [], [], []
    for b in branches:
        pts = b["pts"]
        if len(pts) < 3:
            continue
        op = min(0.92, 0.45 + b["w0"] * 0.04)
        shapes.append(f'<path d="{outline(pts, b["ws"])}" opacity="{op:.2f}"/>')
        if b["w0"] > 6:
            light.append(f'<path d="{outline(pts, b["ws"], shift=-0.18, scale=0.26)}"/>')
        t = length(lineage(b["parent"], b["at"])) / GROW_SPEED if b["parent"] is not None else 0
        for c in range(0, len(pts) - 1, 20):
            part = pts[c:c + 21]
            if len(part) < 2:
                continue
            wide = f'stroke-width="{max(b["ws"][c:c + 21]) + 8:.0f}"'
            if part[0][1] < GROW_UNTIL:
                dur = length(part) / GROW_SPEED
                reveal.append(f'<path class="a" d="{line(part)}" pathLength="1" {wide} style="animation-duration:{dur:.2f}s;animation-delay:{t:.2f}s"/>')
                t += dur
    grow_end = max(length(lineage(i)) for i, b in enumerate(branches) if b["pts"][0][1] < GROW_UNTIL) / GROW_SPEED
    grow_end = min(grow_end, 3.0)

    # Impulses: on stretches of root spread down the whole page, each ending at a tip, each on its own beat.
    tips = [i for i, b in enumerate(branches) if b["depth"] >= 1 and len(b["pts"]) > 4]
    bands = {}
    for i in tips:
        bands.setdefault(int(branches[i]["pts"][-1][1] // 240), []).append(i)
    chosen = [rnd.choice(v) for _, v in sorted(bands.items())]
    chosen = rnd.sample(chosen, min(PULSES, len(chosen)))
    pulses, lines = [], []
    for k, i in enumerate(chosen):
        pts = lineage(i)
        keep, run = rnd.uniform(900, 1600), 0.0             # the last stretch of the line up to the tip
        for j in range(len(pts) - 1, 0, -1):
            run += math.dist(pts[j], pts[j - 1])
            if run > keep:
                pts = pts[j - 1:]
                break
        dur = length(pts) / PULSE_SPEED * rnd.uniform(0.85, 1.25)
        delay = (grow_end * 0.6 if pts[0][1] < GROW_UNTIL else 0) + rnd.uniform(0, 5)
        style = f'animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s'
        lines.append(f'<path id="l{k}" d="{line(pts)}" pathLength="1"/>')
        # One line, three strokes: a wide faint halo, a glow and a bright core, all running together.
        pulses.append(f'<use href="#l{k}" stroke-width="16" opacity=".16" style="{style}"/>'
                      f'<use href="#l{k}" stroke-width="7" opacity=".4" style="{style}"/>'
                      f'<use href="#l{k}" stroke-width="3" stroke="#fff1c4" style="{style}"/>')

    nl = "\n"
    if hero:
        masks = (f'<rect width="{W}" height="800" fill="url(#hero)"/>{nl}'
                 f'        <rect y="740" width="{W}" height="410" fill="url(#under)"/>{nl}'
                 f'        <rect y="1080" width="{W}" height="{H - 1080}" fill="url(#margins)"/>')
    else:
        masks = f'<rect width="{W}" height="{H}" fill="url(#margins)"/>'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
    <!-- Generated by tools/radici.py (seed {SEED}). -->
    <defs>
      <!-- Where the roots show: right of the hero's copy, everywhere under its buttons, then the margins. -->
      <linearGradient id="hero" gradientUnits="userSpaceOnUse" x1="430" y1="0" x2="850" y2="0">
        <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/>
      </linearGradient>
      <linearGradient id="under" gradientUnits="userSpaceOnUse" x1="0" y1="740" x2="0" y2="1150">
        <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff"/>
        <stop offset=".83" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="margins" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="0">
        <stop offset="0" stop-color="#fff"/><stop offset=".19" stop-color="#fff"/><stop offset=".33" stop-color="#fff" stop-opacity="0"/>
        <stop offset=".67" stop-color="#fff" stop-opacity="0"/><stop offset=".81" stop-color="#fff"/><stop offset="1" stop-color="#fff"/>
      </linearGradient>
      <mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
        {masks}
      </mask>
      <mask id="g" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
        <g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round">
    {nl.join(reveal)}
        </g>
        <rect y="{GROW_UNTIL}" width="{W}" height="{H - GROW_UNTIL}" fill="#fff"/>
      </mask>
    {nl.join(lines)}
    </defs>
    <style>
      .a {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation-name: grow; animation-timing-function: linear; animation-fill-mode: forwards; }}
      @keyframes grow {{ to {{ stroke-dashoffset: 0; }} }}
      .p use {{ stroke-dasharray: .05 1.2; stroke-dashoffset: .05; animation-name: run; animation-timing-function: cubic-bezier(.45,.05,.55,.95); animation-iteration-count: infinite; }}
      @keyframes run {{ to {{ stroke-dashoffset: -1.1; }} }}
      @media (prefers-reduced-motion: reduce) {{ .a {{ animation: none; stroke-dashoffset: 0; }} .p use {{ display: none; }} }}
    </style>
    <g mask="url(#m)">
      <g mask="url(#g)">
        <g fill="{INK}">
    {nl.join(shapes)}
        </g>
        <g fill="{LIGHT}" opacity=".5">
    {nl.join(light)}
        </g>
      </g>
      <g class="p" fill="none" stroke="{GOLD}" stroke-linecap="round" stroke-linejoin="round">
    {nl.join(pulses)}
      </g>
    </g>
    </svg>
    """
    out.write_text(svg, encoding="utf-8")
    print(f"{out.name}: {len(branches)} branches, {len(pulses)} impulses, {len(svg) // 1024} KB")


build(INPUTS / "radici-pagina.svg", hero=True)
build(INPUTS / "radici-margini.svg", hero=False)
