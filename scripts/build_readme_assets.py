#!/usr/bin/env python3
"""Generates the README's animated SVG artwork and badges into docs/readme/ (dark + light variants).

Run from the repo root after changing any text below:  python3 scripts/build_readme_assets.py
Same approach as the AWS-Cloud-Resume and Resume_CV_CoverLetter READMEs: self-contained SVG (no
external fonts, images or services), CSS animations inside the SVG that switch off for viewers with
"reduce motion" enabled, and the same palette as emrecancioglu.com.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "readme"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SPACED = 'letter-spacing="3"'
LINKEDIN = "#0a66c2"

PALETTES = {
    "dark": dict(bg1="#0a0d12", bg2="#0e1a18", card="#11161d", card_border="#1f2a33", grid="#1a2430",
                 text="#ececea", muted="#9aa3ab", accent="#34d399", accent2="#38bdf8", accent3="#fbbf24",
                 accent_soft="#34d39922", line="#2a3540"),
    "light": dict(bg1="#ffffff", bg2="#ecfdf5", card="#ffffff", card_border="#d7e3dd", grid="#e3ece8",
                  text="#17181a", muted="#5b6168", accent="#059669", accent2="#0284c7", accent3="#d97706",
                  accent_soft="#05966914", line="#d4dbd7"),
}

BASE_STYLE = """
    .fade { opacity: 0; animation: fade .7s ease-out forwards; }
    @keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    .pulse { stroke-dasharray: 16 600; stroke-dashoffset: 616; animation: flow 2.4s linear infinite; }
    @keyframes flow { to { stroke-dashoffset: 0; } }
"""
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .fade { opacity: 1; } .write { stroke-dashoffset: 0 !important; } .stamp { opacity: 1; } }"


def svg(width, height, body, style, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<style>text {{ font-family: {FONT}; }} .mono {{ font-family: {MONO}; }} {BASE_STYLE} {style} {REDUCED_MOTION}</style>'
            f'{body}</svg>')


def t(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(s)}</text>'


def backdrop(p, w, h, glow_cx=0.8):
    return f'''
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>
      <radialGradient id="glow" cx="{glow_cx}" cy="0.5" r="0.5"><stop offset="0" stop-color="{p["accent"]}" stop-opacity="0.18"/><stop offset="1" stop-color="{p["accent"]}" stop-opacity="0"/></radialGradient>
      <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="{p["grid"]}" stroke-width="1"/></pattern>
    </defs>
    <rect width="{w}" height="{h}" rx="18" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" rx="18" fill="url(#grid)" opacity="0.5"/>
    <rect width="{w}" height="{h}" rx="18" fill="url(#glow)"/>
    <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="none" stroke="{p["card_border"]}"/>'''


def write_line(p, x, y, length, delay):
    return (f'<path d="M{x} {y}h{length}" stroke="{p["line"]}" stroke-width="6" stroke-linecap="round" class="write" '
            f'style="stroke-dasharray:{length} {length};stroke-dashoffset:{length};animation-delay:{delay:.2f}s"/>')


# ---------------------------------------------------------------- hero banner
def hero(p):
    w, h = 1200, 380
    body = [backdrop(p, w, h),
            f'<g class="fade">{t(64, 96, "n8n · OpenAI · LinkedIn API", 15, p["accent"], 700, extra=SPACED)}</g>',
            f'<g class="fade" style="animation-delay:.15s">{t(62, 154, "LinkedIn Content", 54, p["text"], 700)}</g>',
            f'<g class="fade" style="animation-delay:.25s">{t(62, 212, "Automation", 54, p["text"], 700)}</g>',
            f'<g class="fade" style="animation-delay:.4s">{t(64, 252, "Weekly, evidence-backed Turkish posts: drafted, illustrated,", 19, p["muted"])}</g>',
            f'<g class="fade" style="animation-delay:.45s">{t(64, 278, "reviewed on Telegram and published, all from a local Docker stack.", 19, p["muted"])}</g>',
            f'''<g class="fade" style="animation-delay:.6s">
      <rect x="64" y="302" width="250" height="40" rx="20" fill="{p["accent_soft"]}" stroke="{p["accent"]}" stroke-opacity="0.5"/>
      {t(189, 327, "no claim without evidence", 15, p["accent"], 600, "middle")}
    </g>''']

    # A LinkedIn-style post card that writes itself, gets its visual, then an "Approved" stamp.
    cx, cy, cw, ch = 760, 34, 380, 312
    card = [f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{p["card"]}" stroke="{p["card_border"]}" stroke-width="1.5"/>',
            f'<circle cx="{cx + 36}" cy="{cy + 36}" r="18" fill="{p["accent"]}"/>',
            t(cx + 36, cy + 41, "EÇ", 13, "#ffffff", 800, "middle"),
            t(cx + 64, cy + 32, "Emre Çancıoğlu", 14, p["text"], 700),
            t(cx + 64, cy + 50, "OT · Industrial AI · Digitalization", 11, p["muted"]),
            f'<rect x="{cx + cw - 46}" y="{cy + 22}" width="26" height="26" rx="5" fill="{LINKEDIN}"/>',
            t(cx + cw - 33, cy + 41, "in", 15, "#ffffff", 800, "middle"),
            write_line(p, cx + 20, cy + 84, 330, 0.6), write_line(p, cx + 20, cy + 102, 300, 0.9),
            write_line(p, cx + 20, cy + 120, 250, 1.2)]
    # The generated visual: a tiny data-flow diagram in the post image.
    ix, iy, iw, ih = cx + 20, cy + 138, cw - 40, 120
    nodes = [(ix + 50, iy + 60), (ix + 170, iy + 34), (ix + 170, iy + 86), (ix + 290, iy + 60)]
    diagram = [f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="8" fill="#0b1f33"/>']
    for (x0, y0), (x1, y1), d in [(nodes[0], nodes[1], 0), (nodes[0], nodes[2], .5), (nodes[1], nodes[3], 1), (nodes[2], nodes[3], 1.5)]:
        path = f"M{x0} {y0} L{x1} {y1}"
        diagram.append(f'<path d="{path}" stroke="#1d3b57" stroke-width="2"/>'
                       f'<path d="{path}" stroke="#20c4cb" stroke-width="2.5" stroke-linecap="round" class="pulse" style="animation-delay:{d}s"/>')
    for x, y in nodes:
        diagram.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#0b1f33" stroke="#0099e5" stroke-width="2.5"/>')
    diagram.append(t(ix + iw - 10, iy + ih - 10, "emrecancioglu.com", 10, "#e9eef2", 600, "end"))
    card.append(f'<g class="fade" style="animation-delay:1.6s">{"".join(diagram)}</g>')
    # Reactions row + approval stamp.
    ry = cy + ch - 26
    for i, c in enumerate([LINKEDIN, "#df704d", "#6dae4f"]):
        card.append(f'<circle cx="{cx + 30 + i * 12}" cy="{ry}" r="8" fill="{c}" stroke="{p["card"]}" stroke-width="2"/>')
    card.append(f'<g class="fade" style="animation-delay:2.2s">{t(cx + 64, ry + 4, "Scheduled · Monday", 12, p["muted"], 500)}</g>')
    card.append(f'''<g class="stamp"><rect x="{cx + cw - 132}" y="{ry - 15}" width="112" height="30" rx="15" fill="{p["accent"]}"/>
      {t(cx + cw - 76, ry + 5, "✓ Approved", 13, "#ffffff", 700, "middle")}</g>''')
    body.append(f'<g class="fade" style="animation-delay:.3s"><g class="float">{"".join(card)}</g></g>')
    style = f"""
    .write {{ animation: write .5s ease-out forwards; }}
    @keyframes write {{ to {{ stroke-dashoffset: 0; }} }}
    .float {{ animation: float 6s ease-in-out infinite; }}
    @keyframes float {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
    .stamp {{ opacity: 0; transform-origin: {cx + cw - 76}px {ry}px; animation: stamp .5s cubic-bezier(.2,1.6,.4,1) 2.6s forwards; }}
    @keyframes stamp {{ from {{ opacity: 0; transform: scale(1.8); }} to {{ opacity: 1; transform: scale(1); }} }}
    """
    return svg(w, h, "".join(body), style,
               "LinkedIn Content Automation: weekly evidence-backed Turkish LinkedIn posts drafted, illustrated, "
               "reviewed on Telegram and published by n8n from a local Docker stack")


# ---------------------------------------------------------------- workflow diagram
def node(p, x, y, w, h, title, sub, color, delay, tag=None):
    tag_svg = ""
    if tag:
        tag_svg = (f'<rect x="{x + w - 58}" y="{y + 10}" width="46" height="18" rx="9" fill="{color}" fill-opacity="0.16"/>'
                   + t(x + w - 35, y + 23, tag, 10, color, 700, "middle"))
    return f'''<g class="fade" style="animation-delay:{delay:.2f}s">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{p["card"]}" stroke="{color}" stroke-opacity="0.65" stroke-width="1.5"/>
      <rect x="{x}" y="{y + 14}" width="4" height="{h - 28}" rx="2" fill="{color}"/>
      {tag_svg}
      {t(x + 20, y + h / 2 - 2, title, 16, p["text"], 700)}
      {t(x + 20, y + h / 2 + 18, sub, 12, p["muted"])}
    </g>'''


def edge(p, d, color, delay, label=None, lx=0, ly=0, dashed=False):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    base = f'<path d="{d}" fill="none" stroke="{p["grid"]}" stroke-width="2"{dash}/>'
    out = base + (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" class="pulse" '
                  f'style="animation-delay:{delay:.2f}s"/>')
    if label:
        out += t(lx, ly, label, 11, p["muted"], 600, "middle")
    return out


def workflow(p):
    w, h = 1200, 520
    nw, nh = 236, 76
    xs = [48, 338, 628, 918]
    y_radar, y1, y2 = 70, 200, 380
    c_in, c_ai, c_out = p["accent2"], p["accent"], LINKEDIN
    out = [backdrop(p, w, h, 0.5), t(48, 46, "HOW A POST IS MADE", 14, p["accent"], 700, extra=SPACED)]
    edges = [
        edge(p, f"M{xs[0] + nw} {y_radar + 30} C{xs[1] + 60} {y_radar + 30}, {xs[1] + nw / 2} {y_radar + 60}, {xs[1] + nw / 2} {y1}", p["accent3"], .2,
             "daily signals", xs[1] + 40, y_radar + 22),
        edge(p, f"M{xs[0] + nw} {y1 + nh / 2} H{xs[1]}", c_in, .4, "", 0, 0),
        edge(p, f"M{xs[1] + nw} {y1 + nh / 2} H{xs[2]}", c_ai, .8, "", 0, 0),
        edge(p, f"M{xs[2] + nw} {y1 + nh / 2} H{xs[3]}", c_ai, 1.2, "pass", (xs[2] + nw + xs[3]) / 2, y1 + nh / 2 - 10),
        edge(p, f"M{xs[3] + nw / 2} {y1 + nh} V{y2}", c_ai, 1.6, "", 0, 0),
        edge(p, f"M{xs[3]} {y2 + nh / 2} H{xs[2] + nw}", c_out, 2.0, "approve", (xs[2] + nw + xs[3]) / 2, y2 + nh / 2 - 10),
        edge(p, f"M{xs[2]} {y2 + nh / 2} H{xs[1] + nw}", c_out, 2.4, "", 0, 0),
        edge(p, f"M{xs[1]} {y2 + nh / 2} H{xs[0] + nw}", c_out, 2.8, "", 0, 0),
        # Regenerate loop from the Telegram review back to the draft step.
        edge(p, f"M{xs[3] + 40} {y2} V{y1 + nh + 40} H{xs[1] + nw / 2} V{y1 + nh}", p["accent3"], 3.0,
             "regenerate text / image", (xs[1] + xs[3]) / 2 + 80, y1 + nh + 32, dashed=True),
    ]
    nodes = [
        node(p, xs[0], y_radar, nw, 60, "Technology radar", "CISA · Siemens · OpenAI · AWS feeds", p["accent3"], .1, "WF-08"),
        node(p, xs[0], y1, nw, nh, "Evidence form", "real work · demos · lessons", c_in, .2, "WF-01"),
        node(p, xs[1], y1, nw, nh, "Weekly draft", "OpenAI · structured JSON", c_ai, .3, "WF-02"),
        node(p, xs[2], y1, nw, nh, "Claim & privacy gate", "every claim → evidence id", c_ai, .4),
        node(p, xs[3], y1, nw, nh, "Branded visual", "OpenAI image + renderer", c_ai, .5, "WF-03"),
        node(p, xs[3], y2, nw, nh, "Telegram review", "approve · redo · reject", c_out, .6, "WF-07"),
        node(p, xs[2], y2, nw, nh, "Weekly schedule", "slot picked Monday 09:00", c_out, .7, "WF-05"),
        node(p, xs[1], y2, nw, nh, "Publish", "LinkedIn Images + Posts API", c_out, .8, "WF-06"),
        node(p, xs[0], y2, nw, nh, "Post log", "URN · usage · errors", c_out, .9),
    ]
    out += edges + nodes
    out.append(f'<g class="fade" style="animation-delay:1s">{t(w / 2, h - 24, "Runs in Docker on one Mac · n8n listens on 127.0.0.1 · only OpenAI, LinkedIn and Telegram calls leave the machine", 13, p["muted"], 500, "middle")}</g>')
    return svg(w, h, "".join(out), "",
               "Workflow: technology radar and evidence form → weekly draft (OpenAI) → claim and privacy gate → branded visual → "
               "Telegram review (approve, regenerate or reject) → weekly schedule → publish to LinkedIn → post log")


# ---------------------------------------------------------------- feature cards
FEATURES = [
    ("🧾", "No invented claims", ["Every metric maps to evidence", "Unmapped claim → post blocked", "Reviewer model can't add claims"], "accent"),
    ("📱", "Human in the loop", ["Draft + visual sent to Telegram", "Approve, redo text or image", "Nothing posts without a yes"], "accent2"),
    ("🎨", "On-brand visuals", ["OpenAI image as the base", "Pillow renderer adds title + logo", "Same palette as the website"], "accent3"),
    ("🔒", "Local & private", ["Docker Compose on a Mac", "Secrets in .env / Docker secrets", "Private evidence never leaves"], "accent"),
]


def features(p):
    w, h = 1200, 230
    cw, gap = 286, 16
    out = []
    for i, (emoji, title, lines, key) in enumerate(FEATURES):
        x = i * (cw + gap) + 4
        c = p[key]
        rows = "".join(t(x + 24, 120 + j * 28, "▸ " + s, 14, p["muted"]) for j, s in enumerate(lines))
        out.append(f'''<g class="fade" style="animation-delay:{i * 0.15:.2f}s">
      <rect x="{x}" y="4" width="{cw}" height="{h - 8}" rx="14" fill="{p["card"]}" stroke="{p["card_border"]}" stroke-width="1.5"/>
      <rect x="{x}" y="4" width="{cw}" height="4" rx="2" fill="{c}"/>
      <rect x="{x}" y="4" width="60" height="4" rx="2" fill="#ffffff" opacity="0.6" class="shine" style="animation-delay:{i * 0.5:.1f}s"/>
      {t(x + 24, 56, emoji, 24, p["text"])}
      {t(x + 64, 56, title, 18, p["text"], 700)}
      <line x1="{x + 24}" y1="78" x2="{x + cw - 24}" y2="78" stroke="{p["card_border"]}"/>
      {rows}
    </g>''')
    style = """
    .shine { animation: shine 3s ease-in-out infinite; }
    @keyframes shine { 0% { transform: translateX(0); opacity: 0; } 20% { opacity: .6; } 60%,100% { transform: translateX(226px); opacity: 0; } }
    """
    alt = " · ".join(f"{title}: {', '.join(lines)}" for _, title, lines, _ in FEATURES)
    return svg(w, h, "".join(out), style, alt)


# ---------------------------------------------------------------- weekly schedule
SCHEDULE = [("Tech radar", "daily 07:30"), ("Draft", "Mon 08:30"), ("Visual", "every 2 min"),
            ("Review", "on Telegram"), ("Schedule", "Mon 09:00"), ("Publish", "every 15 min")]


def schedule(p):
    w, h = 1200, 170
    x0, x1, y = 100, 1100, 70
    step = (x1 - x0) / (len(SCHEDULE) - 1)
    period = 7.0
    out = [backdrop(p, w, h, 0.5),
           f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{p["grid"]}" stroke-width="4" stroke-linecap="round"/>',
           f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{p["accent"]}" stroke-width="4" stroke-linecap="round" class="progress"/>']
    for i, (name, when) in enumerate(SCHEDULE):
        x = x0 + i * step
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="14" fill="{p["card"]}" stroke="{p["accent"]}" stroke-width="3"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="8" fill="{p["accent"]}" style="animation: lit{i} {period}s linear infinite"/>')
        out.append(t(f"{x:.1f}", y + 44, name, 15, p["text"], 700, "middle"))
        out.append(t(f"{x:.1f}", y + 64, when, 12, p["muted"], 400, "middle", 'class="mono"'))
    style = f"""
    .progress {{ stroke-dasharray: {x1 - x0}; stroke-dashoffset: {x1 - x0}; animation: run {period}s linear infinite; }}
    @keyframes run {{ 80%, 92% {{ stroke-dashoffset: 0; opacity: 1; }} 100% {{ stroke-dashoffset: 0; opacity: 0; }} }}
    """
    # Each dot lights up when the progress line reaches it (the line covers the track in 80% of the period).
    for i in range(len(SCHEDULE)):
        reach = 80 * i / (len(SCHEDULE) - 1)
        style += (f"@keyframes lit{i} {{ 0%, {max(reach - 0.1, 0):.1f}% {{ fill-opacity: {1 if i == 0 else 0}; }} "
                  f"{reach:.1f}%, 92% {{ fill-opacity: 1; }} 100% {{ fill-opacity: 0; }} }}\n")
    return svg(w, h, "".join(out), style,
               "Schedule: " + " → ".join(f"{n} ({w_})" for n, w_ in SCHEDULE))


# ---------------------------------------------------------------- footer
def footer(p):
    w, h = 1200, 120
    body = f'''<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{p["accent"]}"/><stop offset="1" stop-color="{LINKEDIN}"/></linearGradient></defs>
    <path class="wave" d="M0,60 C200,10 400,110 600,60 C800,10 1000,110 1200,60 L1240,120 L-40,120Z" fill="url(#g)" opacity="0.18"/>
    <path class="wave2" d="M0,80 C200,40 400,120 600,80 C800,40 1000,120 1200,80 L1240,120 L-40,120Z" fill="url(#g)" opacity="0.12"/>
    {t(600, 52, "Automated with n8n · reviewed by a human · emrecancioglu.com", 15, p["muted"], 500, "middle")}'''
    style = """.wave { animation: sway 6s ease-in-out infinite alternate; }
    .wave2 { animation: sway 8s ease-in-out infinite alternate-reverse; }
    @keyframes sway { to { transform: translateX(-40px); } }"""
    return svg(w, h, body, style, "Automated with n8n, reviewed by a human — emrecancioglu.com")



# ---------------------------------------------------------------- badges
# Badges are generated here too instead of linking img.shields.io: GitHub's image proxy (camo)
# regularly times out on shields.io (HTTP 504), which shows up as broken images in the README.
# Brand icon paths are from Simple Icons (CC0, simpleicons.org), 24x24 viewBox.
BADGE_FONT = "Verdana, 'DejaVu Sans', Geneva, sans-serif"


def text_width(s, size=11):
    """Rough Verdana advance widths; the text is then forced to this width with textLength."""
    w = 0.0
    for ch in s:
        if ch in "il.,:;|!'·":
            w += 0.33
        elif ch == " ":
            w += 0.35
        elif ch in "mwMW":
            w += 0.95
        elif ch.isupper() or ch.isdigit():
            w += 0.72
        else:
            w += 0.6
    return w * size


def badge(label, value, color, icon=None, label_color="#24292f"):
    h, pad, size = 28, 10, 11
    icon_w = 20 if icon else 0
    segs = []  # (x, width, fill, text)
    x = 0
    if label:
        lw = pad + icon_w + text_width(label) + pad
        segs.append((x, lw, label_color, label))
        x += lw
    vw = (0 if label else icon_w) + pad + text_width(value) + pad
    segs.append((x, vw, color, value))
    w = x + vw
    parts = []
    for i, (sx, sw, fill, text) in enumerate(segs):
        parts.append(f'<rect x="{sx:.1f}" width="{sw:.1f}" height="{h}" fill="{fill}"/>')
        tx = sx + pad + (icon_w if i == 0 else 0)
        tw = text_width(text)
        parts.append(f'<text x="{tx:.1f}" y="18.5" font-size="{size}" font-weight="600" fill="#ffffff" '
                     f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    if icon:
        parts.append(f'<svg x="{pad}" y="7" width="14" height="14" viewBox="0 0 24 24"><path fill="#ffffff" d="{ICONS[icon]}"/></svg>')
    alt = f"{label}: {value}" if label else value
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.1f} {h}" role="img" aria-label="{escape(alt)}">'
            f'<title>{escape(alt)}</title><style>text {{ font-family: {BADGE_FONT}; letter-spacing: .2px; }}</style>'
            f'<clipPath id="r"><rect width="{w:.1f}" height="{h}" rx="6"/></clipPath><g clip-path="url(#r)">{"".join(parts)}</g></svg>')


ICONS = {
    "n8n": "M21.4737 5.6842c-1.1772 0-2.1663.8051-2.4468 1.8947h-2.8955c-1.235 0-2.289.893-2.492 2.111l-.1038.623a1.263 1.263 0 0 1-1.246 1.0555H11.289c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947s-2.1663.8051-2.4467 1.8947H4.973c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947C1.1311 9.4737 0 10.6047 0 12s1.131 2.5263 2.5263 2.5263c1.1772 0 2.1663-.8051 2.4468-1.8947h1.4223c.2804 1.0896 1.2696 1.8947 2.4467 1.8947 1.1772 0 2.1663-.8051 2.4468-1.8947h1.0008a1.263 1.263 0 0 1 1.2459 1.0555l.1038.623c.203 1.218 1.257 2.111 2.492 2.111h.3692c.2804 1.0895 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263c-1.1772 0-2.1664.805-2.4468 1.8947h-.3692a1.263 1.263 0 0 1-1.246-1.0555l-.1037-.623A2.52 2.52 0 0 0 13.9607 12a2.52 2.52 0 0 0 .821-1.4794l.1038-.623a1.263 1.263 0 0 1 1.2459-1.0555h2.8955c.2805 1.0896 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263m0 1.2632a1.263 1.263 0 0 1 1.2631 1.2631 1.263 1.263 0 0 1-1.2631 1.2632 1.263 1.263 0 0 1-1.2632-1.2632 1.263 1.263 0 0 1 1.2632-1.2631M2.5263 10.7368A1.263 1.263 0 0 1 3.7895 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 1.2632 12a1.263 1.263 0 0 1 1.2631-1.2632m6.3158 0A1.263 1.263 0 0 1 10.1053 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 7.579 12a1.263 1.263 0 0 1 1.2632-1.2632m10.1053 3.7895a1.263 1.263 0 0 1 1.2631 1.2632 1.263 1.263 0 0 1-1.2631 1.2631 1.263 1.263 0 0 1-1.2632-1.2631 1.263 1.263 0 0 1 1.2632-1.2632",
    "openai": "M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z",
    "postgresql": "M23.5594 14.7228a.5269.5269 0 0 0-.0563-.1191c-.139-.2632-.4768-.3418-1.0074-.2321-1.6533.3411-2.2935.1312-2.5256-.0191 1.342-2.0482 2.445-4.522 3.0411-6.8297.2714-1.0507.7982-3.5237.1222-4.7316a1.5641 1.5641 0 0 0-.1509-.235C21.6931.9086 19.8007.0248 17.5099.0005c-1.4947-.0158-2.7705.3461-3.1161.4794a9.449 9.449 0 0 0-.5159-.0816 8.044 8.044 0 0 0-1.3114-.1278c-1.1822-.0184-2.2038.2642-3.0498.8406-.8573-.3211-4.7888-1.645-7.2219.0788C.9359 2.1526.3086 3.8733.4302 6.3043c.0409.818.5069 3.334 1.2423 5.7436.4598 1.5065.9387 2.7019 1.4334 3.582.553.9942 1.1259 1.5933 1.7143 1.7895.4474.1491 1.1327.1441 1.8581-.7279.8012-.9635 1.5903-1.8258 1.9446-2.2069.4351.2355.9064.3625 1.39.3772a.0569.0569 0 0 0 .0004.0041 11.0312 11.0312 0 0 0-.2472.3054c-.3389.4302-.4094.5197-1.5002.7443-.3102.064-1.1344.2339-1.1464.8115-.0025.1224.0329.2309.0919.3268.2269.4231.9216.6097 1.015.6331 1.3345.3335 2.5044.092 3.3714-.6787-.017 2.231.0775 4.4174.3454 5.0874.2212.5529.7618 1.9045 2.4692 1.9043.2505 0 .5263-.0291.8296-.0941 1.7819-.3821 2.5557-1.1696 2.855-2.9059.1503-.8707.4016-2.8753.5388-4.1012.0169-.0703.0357-.1207.057-.1362.0007-.0005.0697-.0471.4272.0307a.3673.3673 0 0 0 .0443.0068l.2539.0223.0149.001c.8468.0384 1.9114-.1426 2.5312-.4308.6438-.2988 1.8057-1.0323 1.5951-1.6698zM2.371 11.8765c-.7435-2.4358-1.1779-4.8851-1.2123-5.5719-.1086-2.1714.4171-3.6829 1.5623-4.4927 1.8367-1.2986 4.8398-.5408 6.108-.13-.0032.0032-.0066.0061-.0098.0094-2.0238 2.044-1.9758 5.536-1.9708 5.7495-.0002.0823.0066.1989.0162.3593.0348.5873.0996 1.6804-.0735 2.9184-.1609 1.1504.1937 2.2764.9728 3.0892.0806.0841.1648.1631.2518.2374-.3468.3714-1.1004 1.1926-1.9025 2.1576-.5677.6825-.9597.5517-1.0886.5087-.3919-.1307-.813-.5871-1.2381-1.3223-.4796-.839-.9635-2.0317-1.4155-3.5126zm6.0072 5.0871c-.1711-.0428-.3271-.1132-.4322-.1772.0889-.0394.2374-.0902.4833-.1409 1.2833-.2641 1.4815-.4506 1.9143-1.0002.0992-.126.2116-.2687.3673-.4426a.3549.3549 0 0 0 .0737-.1298c.1708-.1513.2724-.1099.4369-.0417.156.0646.3078.26.3695.4752.0291.1016.0619.2945-.0452.4444-.9043 1.2658-2.2216 1.2494-3.1676 1.0128zm2.094-3.988-.0525.141c-.133.3566-.2567.6881-.3334 1.003-.6674-.0021-1.3168-.2872-1.8105-.8024-.6279-.6551-.9131-1.5664-.7825-2.5004.1828-1.3079.1153-2.4468.079-3.0586-.005-.0857-.0095-.1607-.0122-.2199.2957-.2621 1.6659-.9962 2.6429-.7724.4459.1022.7176.4057.8305.928.5846 2.7038.0774 3.8307-.3302 4.7363-.084.1866-.1633.3629-.2311.5454zm7.3637 4.5725c-.0169.1768-.0358.376-.0618.5959l-.146.4383a.3547.3547 0 0 0-.0182.1077c-.0059.4747-.054.6489-.115.8693-.0634.2292-.1353.4891-.1794 1.0575-.11 1.4143-.8782 2.2267-2.4172 2.5565-1.5155.3251-1.7843-.4968-2.0212-1.2217a6.5824 6.5824 0 0 0-.0769-.2266c-.2154-.5858-.1911-1.4119-.1574-2.5551.0165-.5612-.0249-1.9013-.3302-2.6462.0044-.2932.0106-.5909.019-.8918a.3529.3529 0 0 0-.0153-.1126 1.4927 1.4927 0 0 0-.0439-.208c-.1226-.4283-.4213-.7866-.7797-.9351-.1424-.059-.4038-.1672-.7178-.0869.067-.276.1831-.5875.309-.9249l.0529-.142c.0595-.16.134-.3257.213-.5012.4265-.9476 1.0106-2.2453.3766-5.1772-.2374-1.0981-1.0304-1.6343-2.2324-1.5098-.7207.0746-1.3799.3654-1.7088.5321a5.6716 5.6716 0 0 0-.1958.1041c.0918-1.1064.4386-3.1741 1.7357-4.4823a4.0306 4.0306 0 0 1 .3033-.276.3532.3532 0 0 0 .1447-.0644c.7524-.5706 1.6945-.8506 2.802-.8325.4091.0067.8017.0339 1.1742.081 1.939.3544 3.2439 1.4468 4.0359 2.3827.8143.9623 1.2552 1.9315 1.4312 2.4543-1.3232-.1346-2.2234.1268-2.6797.779-.9926 1.4189.543 4.1729 1.2811 5.4964.1353.2426.2522.4522.2889.5413.2403.5825.5515.9713.7787 1.2552.0696.087.1372.1714.1885.245-.4008.1155-1.1208.3825-1.0552 1.717-.0123.1563-.0423.4469-.0834.8148-.0461.2077-.0702.4603-.0994.7662zm.8905-1.6211c-.0405-.8316.2691-.9185.5967-1.0105a2.8566 2.8566 0 0 0 .135-.0406 1.202 1.202 0 0 0 .1342.103c.5703.3765 1.5823.4213 3.0068.1344-.2016.1769-.5189.3994-.9533.6011-.4098.1903-1.0957.333-1.7473.3636-.7197.0336-1.0859-.0807-1.1721-.151zm.5695-9.2712c-.0059.3508-.0542.6692-.1054 1.0017-.055.3576-.112.7274-.1264 1.1762-.0142.4368.0404.8909.0932 1.3301.1066.887.216 1.8003-.2075 2.7014a3.5272 3.5272 0 0 1-.1876-.3856c-.0527-.1276-.1669-.3326-.3251-.6162-.6156-1.1041-2.0574-3.6896-1.3193-4.7446.3795-.5427 1.3408-.5661 2.1781-.463zm.2284 7.0137a12.3762 12.3762 0 0 0-.0853-.1074l-.0355-.0444c.7262-1.1995.5842-2.3862.4578-3.4385-.0519-.4318-.1009-.8396-.0885-1.2226.0129-.4061.0666-.7543.1185-1.0911.0639-.415.1288-.8443.1109-1.3505.0134-.0531.0188-.1158.0118-.1902-.0457-.4855-.5999-1.938-1.7294-3.253-.6076-.7073-1.4896-1.4972-2.6889-2.0395.5251-.1066 1.2328-.2035 2.0244-.1859 2.0515.0456 3.6746.8135 4.8242 2.2824a.908.908 0 0 1 .0667.1002c.7231 1.3556-.2762 6.2751-2.9867 10.5405zm-8.8166-6.1162c-.025.1794-.3089.4225-.6211.4225a.5821.5821 0 0 1-.0809-.0056c-.1873-.026-.3765-.144-.5059-.3156-.0458-.0605-.1203-.178-.1055-.2844.0055-.0401.0261-.0985.0925-.1488.1182-.0894.3518-.1226.6096-.0867.3163.0441.6426.1938.6113.4186zm7.9305-.4114c.0111.0792-.049.201-.1531.3102-.0683.0717-.212.1961-.4079.2232a.5456.5456 0 0 1-.075.0052c-.2935 0-.5414-.2344-.5607-.3717-.024-.1765.2641-.3106.5611-.352.297-.0414.6111.0088.6356.1851z",
    "docker": "M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186m-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186m-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186m5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185m-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185m-2.92 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.082.185.185.185M23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 00-.75.748 11.376 11.376 0 00.692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 003.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288Z",
    "telegram": "M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z",
    "python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z",
    "nodedotjs": "M11.998,24c-0.321,0-0.641-0.084-0.922-0.247l-2.936-1.737c-0.438-0.245-0.224-0.332-0.08-0.383 c0.585-0.203,0.703-0.25,1.328-0.604c0.065-0.037,0.151-0.023,0.218,0.017l2.256,1.339c0.082,0.045,0.197,0.045,0.272,0l8.795-5.076 c0.082-0.047,0.134-0.141,0.134-0.238V6.921c0-0.099-0.053-0.192-0.137-0.242l-8.791-5.072c-0.081-0.047-0.189-0.047-0.271,0 L3.075,6.68C2.99,6.729,2.936,6.825,2.936,6.921v10.15c0,0.097,0.054,0.189,0.139,0.235l2.409,1.392 c1.307,0.654,2.108-0.116,2.108-0.89V7.787c0-0.142,0.114-0.253,0.256-0.253h1.115c0.139,0,0.255,0.112,0.255,0.253v10.021 c0,1.745-0.95,2.745-2.604,2.745c-0.508,0-0.909,0-2.026-0.551L2.28,18.675c-0.57-0.329-0.922-0.945-0.922-1.604V6.921 c0-0.659,0.353-1.275,0.922-1.603l8.795-5.082c0.557-0.315,1.296-0.315,1.848,0l8.794,5.082c0.57,0.329,0.924,0.944,0.924,1.603 v10.15c0,0.659-0.354,1.273-0.924,1.604l-8.794,5.078C12.643,23.916,12.324,24,11.998,24z M19.099,13.993 c0-1.9-1.284-2.406-3.987-2.763c-2.731-0.361-3.009-0.548-3.009-1.187c0-0.528,0.235-1.233,2.258-1.233 c1.807,0,2.473,0.389,2.747,1.607c0.024,0.115,0.129,0.199,0.247,0.199h1.141c0.071,0,0.138-0.031,0.186-0.081 c0.048-0.054,0.074-0.123,0.067-0.196c-0.177-2.098-1.571-3.076-4.388-3.076c-2.508,0-4.004,1.058-4.004,2.833 c0,1.925,1.488,2.457,3.895,2.695c2.88,0.282,3.103,0.703,3.103,1.269c0,0.983-0.789,1.402-2.642,1.402 c-2.327,0-2.839-0.584-3.011-1.742c-0.02-0.124-0.126-0.215-0.253-0.215h-1.137c-0.141,0-0.254,0.112-0.254,0.253 c0,1.482,0.806,3.248,4.655,3.248C17.501,17.007,19.099,15.91,19.099,13.993z",
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z",
}

BADGES = [  # file name, label, value, color, icon
    ("workflows", "n8n workflows", "8", "#ea4b71", "n8n"),
    ("language", "posts", "Türkçe · weekly", "#059669", None),
    ("review", "approval", "human in the loop", "#0a66c2", "telegram"),
    ("n8n", None, "n8n 2.3", "#ea4b71", "n8n"),
    ("openai", None, "OpenAI API", "#10a37f", "openai"),
    ("postgres", None, "PostgreSQL 16", "#336791", "postgresql"),
    ("docker", None, "Docker Compose", "#1d63ed", "docker"),
    ("telegram", None, "Telegram bot", "#229ed9", "telegram"),
    ("linkedin", None, "LinkedIn API", "#0a66c2", "linkedin"),
    ("python", None, "Python · Pillow", "#3776ab", "python"),
    ("node", None, "Node.js", "#339933", "nodedotjs"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("hero", hero), ("workflow", workflow), ("features", features),
                     ("schedule", schedule), ("footer", footer)]:
        for mode, p in PALETTES.items():
            (OUT / f"{name}-{mode}.svg").write_text(fn(p), encoding="utf-8")
    badge_dir = OUT / "badges"
    badge_dir.mkdir(exist_ok=True)
    for name, label, value, color, icon in BADGES:
        (badge_dir / f"{name}.svg").write_text(badge(label, value, color, icon), encoding="utf-8")
    print(f"wrote {len(PALETTES) * 5} files to {OUT} and {len(BADGES)} badges to {badge_dir}")


if __name__ == "__main__":
    main()
