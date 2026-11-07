#!/usr/bin/env python3
"""Render the living red hero SVG for github.com/Zlee12.

ASCII portrait (red theme) + ZLEE12 LED name + live stats strip.
Stats come from env vars (set by the GitHub Action); sensible
fallbacks keep it working when run by hand.

    REPOS, STARS, CONTRIB, FOLLOWERS  (integers)

Usage:  python assets/gen_hero.py  ->  writes assets/hero.svg
"""
import os
import html
import pyfiglet
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
AVATAR = os.path.join(HERE, "avatar.jpg")
OUT = os.path.join(HERE, "hero.svg")

# ---- live stats (env, with fallbacks) --------------------------------------
def stat(name, default):
    try:
        return f"{int(os.environ.get(name, default)):,}"
    except ValueError:
        return str(default)

REPOS = stat("REPOS", 2)
STARS = stat("STARS", 0)
CONTRIB = stat("CONTRIB", 12)
FOLLOWERS = stat("FOLLOWERS", 2)

# ---- red ASCII portrait ----------------------------------------------------
P_COLS = 86                               # square mosaic resolution
CELL = 7.0                                # natural grid step
GLYPHS = "+*oX#%@"                         # dense set, bright -> denser
DARK = 0.19                               # below this = empty (figure silhouette)

def pixel_color(r, g, b):
    """Red theme: brightness drives red; only genuinely white pixels (the moon)
    lift green/blue toward white-hot. Saturated bright sky stays red."""
    L = (0.2126*r + 0.7152*g + 0.0722*b)/255
    # pure red duotone: dark -> deep red, bright -> hot pink-red. No grey/white.
    rr = int(max(0, min(255, 95 + L*160)))
    gb = int(max(0, min(rr, (L**2.2)*150)))
    return rr, gb, gb, L

def build_portrait():
    """Square crop of the avatar as a high-contrast RED ASCII mosaic.
    Figure -> empty silhouette, sky -> red, moon -> white-hot. (group, W, H)."""
    im = Image.open(AVATAR).convert("RGB")
    w, h = im.size
    # crop tight around the moon + figure (head/torso) so the subject reads
    cx, cy, frac = 0.50, 0.33, 0.52
    side = int(frac*min(w, h))
    left = int(cx*w - side/2); top = int(cy*h - side/2)
    left = max(0, min(w-side, left)); top = max(0, min(h-side, top))
    im = im.crop((left, top, left+side, top+side))
    n = P_COLS
    small = im.resize((n, n), Image.LANCZOS)
    small = ImageEnhance.Color(small).enhance(1.6)
    small = ImageEnhance.Contrast(small).enhance(1.6)
    small = ImageEnhance.Brightness(small).enhance(1.12)
    px = small.load()
    fs = CELL*1.5                          # oversize so glyphs tile into a solid mosaic
    out = [f'<g class="mono" font-size="{fs:.2f}" xml:space="preserve">']
    for j in range(n):
        y = j*CELL + CELL*0.85
        spans, run, rf = [], "", None
        def flush():
            if run: spans.append(f'<tspan fill="{rf}">{html.escape(run)}</tspan>')
        for i in range(n):
            r, g, b = px[i, j]
            rr, gg, bb, L = pixel_color(r, g, b)
            t = max(0.0, min(1.0, (L-0.10)/0.82))
            if t < DARK:
                flush(); run=""; rf=None; spans.append(" "); continue
            g2 = GLYPHS[min(len(GLYPHS)-1, int(((t-DARK)/(1-DARK))*(len(GLYPHS)-1)))]
            col = f"#{rr:02x}{gg:02x}{bb:02x}"
            if col == rf: run += g2
            else: flush(); rf=col; run=g2
        flush()
        out.append(f'<text x="0" y="{y:.1f}">{"".join(spans)}</text>')
    out.append('</g>')
    return "\n".join(out), n*CELL, n*CELL

# ---- ZLEE12 LED blocks -----------------------------------------------------
def build_name(x0, y0, cell=13):
    grid = [r for r in pyfiglet.figlet_format("ZLEE12", font="ansi_regular").split("\n") if r.strip()][:5]
    rects = []
    for j, row in enumerate(grid):
        for i, c in enumerate(row):
            if c == "█":
                rects.append(f'<rect x="{x0+i*cell}" y="{y0+j*cell}" width="{cell-2}" height="{cell-2}" rx="2"/>')
    cols = max(len(r) for r in grid)
    return "\n".join(rects), cols*cell, len(grid)*cell

# ---- compose ---------------------------------------------------------------
W, H = 1000, 430
PANEL = 372                      # portrait column width
_port, natW, natH = build_portrait()
bx, by, bw, bh = 24, 60, PANEL-48, H-136
s = min(bw/natW, bh/natH)
ox = bx + (bw - natW*s)/2
oy = by + (bh - natH*s)/2
port = f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.4f})">{_port}</g>'
blocks, nw, nh = build_name(PANEL+34, 92, cell=12)

RX = PANEL + 34                  # right column x
stats = [("REPOS", REPOS), ("STARS", STARS), ("CONTRIB", CONTRIB), ("FOLLOWERS", FOLLOWERS)]
sx = RX; sw = (W-30-RX)//4
stat_svg = []
for k, (lab, val) in enumerate(stats):
    cx = sx + k*sw
    stat_svg.append(
        f'<g><rect x="{cx}" y="330" width="{sw-12}" height="64" rx="8" fill="#0d0609" '
        f'stroke="#2a1016" stroke-width="1"/>'
        f'<text class="mono" x="{cx+14}" y="358" font-size="20" fill="#ff5b5b" font-weight="700">{val}</text>'
        f'<text class="mono" x="{cx+14}" y="380" font-size="9.5" letter-spacing="1.5" fill="#7a6a6e">{lab}</text></g>')
stat_svg = "\n".join(stat_svg)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" role="img" aria-label="ZLEE12 — threat hunter, systems and security engineer">
  <title>Zlee12 — living identity (red)</title>
  <desc>Animated red ASCII portrait and name. REPOS {REPOS} · STARS {STARS} · CONTRIBUTIONS {CONTRIB} · FOLLOWERS {FOLLOWERS}</desc>
  <defs>
    <radialGradient id="halo" cx="30%" cy="42%" r="75%">
      <stop offset="0%" stop-color="#ff2a2a" stop-opacity="0.18"/>
      <stop offset="55%" stop-color="#7a0f0f" stop-opacity="0.07"/>
      <stop offset="100%" stop-color="#07070a" stop-opacity="0"/></radialGradient>
    <linearGradient id="name" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#ffb0b0"/><stop offset="50%" stop-color="#ff2f2f"/><stop offset="100%" stop-color="#e01414"/></linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ff2a2a" stop-opacity="0"/><stop offset="50%" stop-color="#ff2a2a"/><stop offset="100%" stop-color="#ff2a2a" stop-opacity="0"/></linearGradient>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5.5"/></filter>
    <clipPath id="scr"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <clipPath id="pan"><rect x="16" y="52" width="{PANEL-32}" height="{H-120}" rx="12"/></clipPath>
    <style>
      :root{{color-scheme:dark}}
      .mono{{font-family:"SFMono-Regular","Consolas","Liberation Mono","Menlo",monospace}}
      text{{dominant-baseline:middle}}
      @keyframes flick{{0%,100%{{opacity:1}}93%{{opacity:1}}94%{{opacity:.6}}95%{{opacity:1}}97%{{opacity:.8}}98%{{opacity:1}}}}
      @keyframes pulse{{0%,100%{{opacity:.8}}50%{{opacity:1}}}}
      @keyframes scan{{0%{{transform:translateY(-24px)}}100%{{transform:translateY(430px)}}}}
      @keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
      @keyframes draw{{0%{{stroke-dashoffset:620}}100%{{stroke-dashoffset:0}}}}
      .glyphs{{animation:flick 6s steps(60) infinite}}
      .halo{{animation:pulse 3.4s ease-in-out infinite}}
      .line{{stroke-dasharray:620;animation:draw 2.2s ease-out forwards}}
      .cur{{animation:blink 1.05s steps(1) infinite}}
      .scan{{animation:scan 6s linear infinite}}
      @media (prefers-reduced-motion:reduce){{.glyphs,.halo,.line,.cur,.scan{{animation:none}}.line{{stroke-dashoffset:0}}}}
    </style>
  </defs>
  <g clip-path="url(#scr)">
    <rect width="{W}" height="{H}" fill="#07070a"/>
    <rect width="{W}" height="{H}" fill="url(#halo)"/>
    <g stroke="#ff2a2a" stroke-opacity="0.05">
      <path d="M0 86H1000M0 172H1000M0 258H1000M0 344H1000"/>
      <path d="M420 0V430M560 0V430M700 0V430M840 0V430"/></g>

    <!-- portrait panel -->
    <rect x="16" y="52" width="{PANEL-32}" height="{H-120}" rx="12" fill="#09070a" stroke="#2a1016" stroke-width="1.5"/>
    <g clip-path="url(#pan)" class="glyphs">{port}</g>
    <rect class="scan" x="16" y="52" width="{PANEL-32}" height="16" fill="#ff2a2a" fill-opacity="0.06" clip-path="url(#pan)"/>

    <!-- status row -->
    <g class="mono halo" font-size="11.5" letter-spacing="3" fill="#ff6b6b">
      <circle cx="{RX+5}" cy="40" r="4" fill="#ff2a2a"/>
      <text x="{RX+18}" y="41">LIVE // SIGNAL</text>
      <text x="{W-26}" y="41" text-anchor="end" fill="#6a5a5e">THREAT HUNTING · HARDWARE · AI RED-TEAM</text>
    </g>

    <!-- name -->
    <g class="glyphs">
      <g filter="url(#soft)" fill="#ff3a3a" opacity="0.95">{blocks}</g>
      <g fill="url(#name)">{blocks}</g>
    </g>

    <path class="line" d="M{RX} 184H{W-26}" stroke="url(#rule)" stroke-width="2"/>

    <!-- subtitle + precept -->
    <g class="mono">
      <text x="{RX}" y="210" font-size="15" letter-spacing="1" fill="#e7e7ea">threat hunter · systems &amp; security engineer</text>
      <text x="{RX+412}" y="210" font-size="15" fill="#ff2a2a" class="cur">▋</text>
      <text x="{RX}" y="236" font-size="12.5" letter-spacing="1.5" fill="#8a7a7e">SECURITY · MICROCONTROLLERS · DIY &amp; HARDWARE HACKING</text>
    </g>

    <!-- the way: three precepts -->
    <g class="mono" font-size="12" fill="#c4b4b8">
      <text x="{RX}" y="272"><tspan fill="#ff4b4b">λ</tspan>  protect what lives — tools that give people agency, not take it</text>
      <text x="{RX}" y="294"><tspan fill="#ff4b4b">λ</tspan>  small, sharp, local-first — own the stack, trust what you can read</text>
      <text x="{RX}" y="316"><tspan fill="#ff4b4b">λ</tspan>  do nothing of no use — discipline over noise, the long way is the way</text>
    </g>

    {stat_svg}

    <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="#ff2a2a" stroke-opacity="0.32" stroke-width="2"/>
  </g>
</svg>'''
open(OUT, "w").write(svg)
print("wrote", OUT, "| REPOS", REPOS, "STARS", STARS, "CONTRIB", CONTRIB, "FOLLOWERS", FOLLOWERS)
