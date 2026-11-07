#!/usr/bin/env python3
"""Render red monospace 'console tag' strips as SVGs so the tech labels are
red (like the hero) and one consistent font/size — something GitHub's grey
<code> spans and the mismatched shields badges couldn't both do.

Writes: assets/focus.svg  assets/work.svg  assets/stack.svg
Static content, so this runs once (not in the daily Action).
"""
import os, html

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = 'font-family="SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace"'
CW = 7.8            # monospace advance at 13px
FS = 13
H = 27             # chip height
GAP = 8
PADX = 11

CHIP_BG = "#140406"
CHIP_BD = "#ff2a2a"
CHIP_TX = "#ff6b6b"
DESC_TX = "#9a8a8e"

def esc(s): return html.escape(s)

def chip(x, y, text):
    w = len(text)*CW + PADX*2
    svg = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{H}" rx="7" '
           f'fill="{CHIP_BG}" stroke="{CHIP_BD}" stroke-opacity="0.75"/>'
           f'<text x="{x+PADX:.1f}" y="{y+H/2+0.5:.1f}" {FONT} font-size="{FS}" '
           f'fill="{CHIP_TX}" dominant-baseline="central">{esc(text)}</text>')
    return svg, w

def write(name, inner, W, Ht):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{Ht}" '
           f'viewBox="0 0 {W:.0f} {Ht}" role="img">\n{inner}\n</svg>\n')
    open(os.path.join(HERE, name), "w").write(svg)

def strip(name, tags):
    """One wrapping row of chips."""
    x, y = 1, 2
    maxw = 1
    parts = []
    for t in tags:
        c, w = chip(x, y, t)
        parts.append(c)
        x += w + GAP
        maxw = max(maxw, x)
    write(name, "\n".join(parts), maxw, H+4)

def rows(name, items):
    """Rows of [chip] + description text."""
    y = 2
    chipw = max(len(lbl)*CW + PADX*2 for lbl, _ in items)
    descx = chipw + 14
    maxw = 1
    parts = []
    for lbl, desc in items:
        c, _ = chip(1, y, lbl)
        # pad chip to common width by drawing it then the description aligned
        parts.append(c)
        parts.append(f'<text x="{descx:.1f}" y="{y+H/2+0.5:.1f}" {FONT} font-size="{FS}" '
                     f'fill="{DESC_TX}" dominant-baseline="central">{esc(desc)}</text>')
        maxw = max(maxw, descx + len(desc)*CW + 6)
        y += H + GAP
    write(name, "\n".join(parts), maxw, y)

strip("focus.svg", ["offense to defend", "build-in-the-open", "local-first"])
strip("stack.svg", ["Python", "Go", "Bash", "Docker", "KVM / Proxmox",
                    "Arduino", "Arch Linux", "Hyprland"])
strip("m913.svg", ["Python", "GTK4", "HID"])
rows("work.svg", [
    ("threat hunting", "finding what hides in the noise"),
    ("AI red-team", "adversarial LLM security"),
    ("hardware", "prototyping, firmware, PCBs, rigs"),
])
print("wrote focus.svg, stack.svg, m913.svg, work.svg")
