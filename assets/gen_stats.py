#!/usr/bin/env python3
"""Render red-theme GitHub stat SVGs into the repo so they never depend on a
rate-limited external service. The GitHub Action fills the numbers via env and
writes a contribution calendar to assets/cal.json; run by hand it falls back to
whatever is already there.

Writes:  assets/stats.svg   assets/graph.svg
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))

def n(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return int(default)

CONTRIB   = n("CONTRIB", 473)
COMMITS   = n("COMMITS", 0)
PRS       = n("PRS", 1)
ISSUES    = n("ISSUES", 0)
STARS     = n("STARS", 0)
FOLLOWERS = n("FOLLOWERS", 2)
REPOS     = n("REPOS", 2)

RED="#ff2a2a"; RED2="#ff5b5b"; BG="#0a0a0d"; BD="#2a1016"; TX="#c9c9d1"; MUT="#7a6a6e"
FONT='font-family="SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"'

def fmt(x): return f"{x:,}"

# ---- stats card -----------------------------------------------------------
def stats_card():
    rows = [
        ("Contributions (last year)", CONTRIB),
        ("Commits (last year)", COMMITS),
        ("Pull requests", PRS),
        ("Stars earned", STARS),
        ("Followers", FOLLOWERS),
        ("Public repositories", REPOS),
    ]
    W, H = 460, 232
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats">']
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{BG}" stroke="{BD}"/>')
    out.append(f'<text x="24" y="38" {FONT} font-size="17" font-weight="700" fill="{RED}">Zlee12 · signal</text>')
    out.append(f'<line x1="24" y1="52" x2="{W-24}" y2="52" stroke="{BD}"/>')
    y = 80
    for label, val in rows:
        out.append(f'<text x="24" y="{y}" {FONT} font-size="13" fill="{TX}">{label}</text>')
        out.append(f'<text x="{W-24}" y="{y}" {FONT} font-size="15" font-weight="700" fill="{RED2}" text-anchor="end">{fmt(val)}</text>')
        y += 25
    open(os.path.join(HERE, "stats.svg"), "w").write("\n".join(out)+"\n</svg>\n")

# ---- contribution heatmap -------------------------------------------------
def heat_color(c, mx):
    if c <= 0: return "#15090c"
    t = (c / mx) ** 0.6
    stops = [(0.0,(74,15,18)),(0.4,(143,17,20)),(0.7,(216,31,31)),(1.0,(255,91,91))]
    for k in range(len(stops)-1):
        a,(ar,ag,ab)=stops[k]; b,(br,bg,bb)=stops[k+1]
        if t<=b:
            f=(t-a)/(b-a) if b>a else 0
            return f"#{int(ar+f*(br-ar)):02x}{int(ag+f*(bg-ag)):02x}{int(ab+f*(bb-ab)):02x}"
    return "#ff5b5b"

def graph_card():
    path = os.path.join(HERE, "cal.json")
    weeks = []
    total = CONTRIB
    if os.path.exists(path):
        try:
            data = json.load(open(path))
            weeks = data.get("weeks", []); total = data.get("total", total)
        except Exception:
            weeks = []
    if not weeks:
        weeks = [[0]*7 for _ in range(53)]        # empty grid until the Action fills it
    mx = max((max(w) for w in weeks if w), default=1) or 1
    cell, gap, pad = 11, 3, 24
    gw = len(weeks)*(cell+gap)
    W = pad*2 + gw; H = pad*2 + 7*(cell+gap) + 24
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution graph">']
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{BG}" stroke="{BD}"/>')
    out.append(f'<text x="{pad}" y="34" {FONT} font-size="14" fill="{RED}">{fmt(total)} contributions in the last year</text>')
    y0 = 48
    for wi, wk in enumerate(weeks):
        x = pad + wi*(cell+gap)
        for di in range(7):
            c = wk[di] if di < len(wk) else 0
            out.append(f'<rect x="{x}" y="{y0+di*(cell+gap)}" width="{cell}" height="{cell}" rx="2" fill="{heat_color(c,mx)}"/>')
    # legend
    lx = W - pad - 5*(cell+gap) - 60
    ly = H - 16
    out.append(f'<text x="{lx-30}" y="{ly+9}" {FONT} font-size="10" fill="{MUT}">less</text>')
    for i,c in enumerate([0, mx*0.25, mx*0.5, mx*0.75, mx]):
        out.append(f'<rect x="{lx+i*(cell+gap)}" y="{ly}" width="{cell}" height="{cell}" rx="2" fill="{heat_color(c,mx)}"/>')
    out.append(f'<text x="{lx+5*(cell+gap)+4}" y="{ly+9}" {FONT} font-size="10" fill="{MUT}">more</text>')
    open(os.path.join(HERE, "graph.svg"), "w").write("\n".join(out)+"\n</svg>\n")

stats_card()
graph_card()
print("stats.svg + graph.svg written | CONTRIB", CONTRIB, "weeks", "cal.json" if os.path.exists(os.path.join(HERE,"cal.json")) else "empty")
