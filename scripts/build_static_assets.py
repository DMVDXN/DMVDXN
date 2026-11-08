"""Build the static Code in Stereo graphics into assets/.

Usage:  python scripts/build_static_assets.py
Edit the data lists below (TRACKS, RELEASES, TOUR, MIXTAPE) and re-run.
"""
import os

from svg_common import (BG_DARK, FONT, GREEN, HAND, MONO, MUTED, STROKE, TEXT,
                        eq_bars, esc, svg_doc)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ------------------------------------------------------------------ data
TRACKS = [
    ("01", "Behind the Headphones", "Intro", "01:26", 0.30),
    ("02", "Current Rotation", "Playlist", "02:58", 0.40),
    ("03", "Studio Equipment", "Mixing Board", "03:14", 0.50),
    ("04", "Featured Releases", "The Discography", "04:07", 0.58),
    ("05", "Platinum Records", "Certifications", "02:41", 0.66),
    ("06", "Tour Dates", "On the Road", "03:05", 0.75),
    ("07", "On Repeat", "Listening Stats", "03:33", 0.86),
    ("08", "Let's Collaborate", "Outro", "03:42", 0.97),
]

RELEASES = [
    # slug, line1, line2, tag, catalog, bg1, bg2, accent
    ("socialsense-ai", "SOCIALSENSE", "AI", "AI · VR · WELLBEING", "DMV-001", "#0f3d2a", "#06140e", "#1ED760"),
    ("icon-history", "ICON", "HISTORY", "AI · EDUCATION", "DMV-002", "#3a2a10", "#120c05", "#F5B942"),
    ("guard", "GUARD", "", "RESPONSIBLE AI", "DMV-003", "#13294a", "#060c17", "#5AA9FF"),
    ("collision-course", "COLLISION", "COURSE", "UNITY · VR", "DMV-004", "#3d1420", "#14060a", "#FF5C7A"),
    ("lyris", "LYRIS", "", "AI · LYRICS · POETRY", "BONUS-01", "#2a1745", "#0c0716", "#B98CFF"),
    ("cover-crazy", "COVER", "CRAZY", "ALBUM ART · BINGO", "BONUS-02", "#0f3d2a", "#06140e", "#1ED760"),
    ("roar-and-rhythm", "ROAR &", "RHYTHM", "POETRY · MUSIC · ART", "BONUS-03", "#14306b", "#070f22", "#F47B20"),
]

TOUR = [
    # stop, city, venue lines, set lines, status, accent
    ("01", "BALTIMORE, MD", ["MORGAN STATE", "UNIVERSITY"], ["B.S. Computer Science", "Magna Cum Laude"], "PLAYED", "#5AA9FF"),
    ("02", "ATLANTA, GA", ["EMORY", "UNIVERSITY"], ["M.S. Computer Science", "Graduate program"], "NOW PLAYING", GREEN),
    ("03", "ATLANTA, GA", ["EMORY CENTER FOR", "DIGITAL SCHOLARSHIP"], ["Digital Scholarship", "Assistant"], "NOW PLAYING", GREEN),
    ("04", "CITY TBA", ["NEXT STOP", "TBA"], ["Your team?", "Booking open"], "TICKETS OPEN", "#F5B942"),
]

MIXTAPE = {
    "title": "CURRENTLY LEARNING",
    "vol": "VOL. 1",
    "side_a": ["Algorithms", "AI Systems", "Thoughtful Software Design"],
    "side_b": ["Human-Centered AI", "Accessibility", "Immersive Interaction"],
}


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ------------------------------------------------------------------ track headers
def track_header(num, title, sub, dur, frac):
    m, s = map(int, dur.split(":"))
    el = int((m * 60 + s) * frac)
    css = (".p{transform-origin:left;animation:prog 6s linear infinite}"
           "@keyframes prog{from{transform:scaleX(.02)}to{transform:scaleX(1)}}")
    body = f"""<rect x="1" y="1" width="1098" height="90" rx="16" fill="url(#bg)" stroke="{STROKE}"/>
<circle cx="52" cy="46" r="24" fill="{GREEN}"/><path d="M45 34 L62 46 L45 58 Z" fill="{BG_DARK}"/>
<text x="94" y="35" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">TRACK {num}  ·  {esc(sub.upper())}</text>
<text x="94" y="66" fill="#fff" font-family="{FONT}" font-weight="700" font-size="28">{esc(title)}</text>
<rect x="560" y="44" width="330" height="4" rx="2" fill="#284839"/>
<g transform="translate(560 44)"><rect class="p" width="330" height="4" rx="2" fill="url(#ln)" style="animation-delay:-{frac * 6:.2f}s"/></g>
<text x="560" y="68" fill="{MUTED}" font-family="{MONO}" font-size="12">{el // 60:02d}:{el % 60:02d}</text>
<text x="890" y="68" fill="{MUTED}" font-family="{MONO}" font-size="12" text-anchor="end">{dur}</text>
{eq_bars(935, 66, 15, [30, 18, 38, 24, 34, 14, 28, 40, 20, 32])}"""
    return svg_doc(1100, 92, f"Track {num}: {title}", body, css)


# ------------------------------------------------------------------ album covers
def album_cover(l1, l2, tag, cat, bg1, bg2, acc):
    longest = max(len(l1), len(l2))
    fs = 34 if longest <= 6 else (26 if longest <= 9 else 19)
    y1 = 150 if l2 else 168
    l2el = (f'<text x="22" y="{y1 + fs + 4}" fill="#fff" font-family="{FONT}" font-weight="800" '
            f'font-size="{fs}">{esc(l2)}</text>') if l2 else ""
    ry = (y1 + fs + 4 if l2 else y1) + 20
    body = f"""<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<clipPath id="c"><rect width="300" height="300" rx="18"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="300" height="300" fill="url(#g)"/>
<g class="spin" style="animation-duration:8s">
<circle cx="228" cy="150" r="118" fill="#050807"/>
<circle cx="228" cy="150" r="104" fill="none" stroke="#1b1f1d" stroke-width="2"/>
<circle cx="228" cy="150" r="88" fill="none" stroke="#1b1f1d" stroke-width="2"/>
<circle cx="228" cy="150" r="72" fill="none" stroke="#1b1f1d" stroke-width="2"/>
<circle cx="228" cy="150" r="40" fill="{acc}"/>
<path d="M228 118 A32 32 0 0 1 260 150" fill="none" stroke="{bg2}" stroke-width="3" opacity=".5"/>
<circle cx="228" cy="150" r="5" fill="{bg2}"/></g>
<rect width="168" height="300" fill="url(#g)" opacity=".92"/>
<text x="22" y="40" fill="{acc}" font-family="{MONO}" font-size="12" letter-spacing="2">{cat}</text>
<text x="22" y="{y1}" fill="#fff" font-family="{FONT}" font-weight="800" font-size="{fs}">{esc(l1)}</text>
{l2el}<rect x="22" y="{ry}" width="40" height="4" rx="2" fill="{acc}"/>
<text x="22" y="270" fill="{TEXT}" font-family="{MONO}" font-size="11" letter-spacing="1.5">{esc(tag)}</text></g>
<rect x=".5" y=".5" width="299" height="299" rx="18" fill="none" stroke="{acc}" stroke-opacity=".35"/>"""
    return svg_doc(300, 300, f"Album cover for {(l1 + ' ' + l2).strip().title()}", body)


# ------------------------------------------------------------------ outro player bar
def outro():
    body = f"""<rect x="1" y="1" width="1098" height="118" rx="18" fill="url(#bg)" stroke="{STROKE}"/>
<rect x="24" y="22" width="76" height="76" rx="10" fill="{GREEN}"/>
<text x="62" y="70" fill="{BG_DARK}" font-family="{FONT}" font-weight="800" font-size="30" text-anchor="middle">+</text>
<text x="120" y="48" fill="#fff" font-family="{FONT}" font-weight="700" font-size="22">Your Idea (feat. Daniel Onyejiekwe)</text>
<text x="120" y="76" fill="{MUTED}" font-family="{MONO}" font-size="13" letter-spacing="2">UP NEXT  ·  UNRELEASED  ·  OPEN TO COLLABS</text>
<g fill="{TEXT}"><path d="M640 48 h4 v24 h-4z M666 48 L648 60 L666 72z"/>
<circle cx="710" cy="60" r="22" fill="{GREEN}"/>
<rect x="702" y="50" width="5" height="20" rx="1" fill="{BG_DARK}"/><rect x="713" y="50" width="5" height="20" rx="1" fill="{BG_DARK}"/>
<path d="M754 48 L772 60 L754 72z M776 48 h4 v24 h-4z"/></g>
{eq_bars(840, 82, 26, [30, 18, 44, 24, 38, 14, 28, 46, 20, 34, 40, 16])}"""
    return svg_doc(1100, 120, "Now playing: Your Idea (feat. Daniel Onyejiekwe). Up next, open to collabs.", body)


# ------------------------------------------------------------------ tour dates
def tour_dates():
    W, H = 1100, 330
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#bg)" stroke="{STROKE}"/>',
             f'<text x="550" y="50" fill="#fff" font-family="{FONT}" font-weight="800" font-size="26" '
             f'text-anchor="middle" letter-spacing="4">THE CODE IN STEREO TOUR</text>',
             f'<text x="550" y="74" fill="{GREEN}" font-family="{MONO}" font-size="12" text-anchor="middle" '
             f'letter-spacing="3">EDUCATION · RESEARCH · ENGINEERING · LIVE ON STAGE</text>']
    tw, th, gap, y0 = 245, 215, 18, 96
    x0 = (W - (4 * tw + 3 * gap)) / 2
    for i, (stop, city, venue, setl, status, acc) in enumerate(TOUR):
        x = x0 + i * (tw + gap)
        live = status == "NOW PLAYING"
        cut = y0 + 150
        parts.append(f'<g transform="translate({x} {y0})">')
        parts.append(f'<rect width="{tw}" height="{th}" rx="12" fill="#0b1712" stroke="{acc}" stroke-opacity=".7"/>')
        parts.append(f'<rect width="{tw}" height="30" rx="12" fill="{acc}" fill-opacity=".14"/>')
        parts.append(f'<text x="16" y="20" fill="{acc}" font-family="{MONO}" font-size="11" letter-spacing="2">'
                     f'STOP {stop} · {esc(city)}</text>')
        for j, line in enumerate(venue):
            fs = 19 if len(line) <= 13 else 15
            parts.append(f'<text x="16" y="{62 + j * 23}" fill="#fff" font-family="{FONT}" font-weight="800" '
                         f'font-size="{fs}">{esc(line)}</text>')
        for j, line in enumerate(setl):
            parts.append(f'<text x="16" y="{118 + j * 17}" fill="{TEXT}" font-family="{FONT}" font-size="13">'
                         f'{esc(line)}</text>')
        dy = cut - y0
        parts.append(f'<line x1="14" y1="{dy}" x2="{tw - 14}" y2="{dy}" stroke="{acc}" stroke-opacity=".5" '
                     f'stroke-dasharray="5 5"/>')
        pill_w = len(status) * 8 + 24
        parts.append(f'<rect x="16" y="{dy + 20}" width="{pill_w}" height="24" rx="12" fill="{acc}" '
                     f'fill-opacity="{1 if live else .18}"/>')
        if live:
            parts.append(f'<circle cx="28" cy="{dy + 32}" r="4" fill="{BG_DARK}">'
                         f'<animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
        parts.append(f'<text x="{38 if live else 28}" y="{dy + 36}" fill="{BG_DARK if live else acc}" '
                     f'font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1">{status}</text>')
        bx = tw - 80
        widths = [2, 1, 3, 1, 2, 1, 1, 3, 2, 1, 2, 3, 1, 2, 1]
        cx = bx
        for k, bw in enumerate(widths):
            if k % 2 == 0:
                parts.append(f'<rect x="{cx}" y="{dy + 18}" width="{bw}" height="28" fill="{TEXT}" opacity=".55"/>')
            cx += bw + 1.6
        parts.append("</g>")
    return svg_doc(W, H, "Tour dates: Morgan State University (B.S. CS, magna cum laude), Emory University (M.S. CS), "
                         "Emory Center for Digital Scholarship, next stop TBA", "\n".join(parts))


# ------------------------------------------------------------------ mixtape cassette
def reel(cx, cy):
    spokes = "".join(
        f'<rect x="{cx - 3}" y="{cy - 22}" width="6" height="12" rx="2" fill="#1a1a1a" '
        f'transform="rotate({a} {cx} {cy})"/>' for a in (0, 60, 120, 180, 240, 300))
    return (f'<circle cx="{cx}" cy="{cy}" r="34" fill="#2b1d12"/>'
            f'<g class="spin" style="animation-duration:3s"><circle cx="{cx}" cy="{cy}" r="24" fill="#f2f2f2"/>'
            f'{spokes}<circle cx="{cx}" cy="{cy}" r="7" fill="#1a1a1a"/></g>')


def mixtape():
    W, H = 1100, 330
    m = MIXTAPE
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#bg)" stroke="{STROKE}"/>']
    # cassette body
    cx, cy, cw, ch = 40, 35, 470, 260
    p.append(f'<g transform="translate({cx} {cy})">')
    p.append(f'<rect width="{cw}" height="{ch}" rx="18" fill="#1b1f24" stroke="#3a4048" stroke-width="2"/>')
    for sx, sy in ((14, 14), (cw - 14, 14), (14, ch - 14), (cw - 14, ch - 14)):
        p.append(f'<circle cx="{sx}" cy="{sy}" r="5" fill="#3a4048"/>')
    # label
    p.append(f'<rect x="28" y="22" width="{cw - 56}" height="168" rx="10" fill="#f4ecd8"/>')
    p.append(f'<rect x="28" y="22" width="{cw - 56}" height="30" rx="10" fill="{GREEN}"/>')
    p.append(f'<rect x="28" y="40" width="{cw - 56}" height="12" fill="{GREEN}"/>')
    p.append(f'<text x="44" y="43" fill="{BG_DARK}" font-family="{MONO}" font-weight="700" font-size="13" '
             f'letter-spacing="2">A  ·  C-90  ·  CODE IN STEREO</text>')
    p.append(f'<text x="{cw / 2}" y="82" fill="#222" font-family="{HAND}" font-size="24" '
             f'text-anchor="middle">{esc(m["title"])}  {esc(m["vol"])}</text>')
    # tape window
    p.append(f'<rect x="90" y="96" width="{cw - 180}" height="80" rx="40" fill="#0e1013"/>')
    p.append(f'<rect x="185" y="112" width="{cw - 370}" height="48" rx="4" fill="#3b2a1d" opacity=".8"/>')
    p.append(reel(150, 136))
    p.append(reel(cw - 150, 136))
    # bottom trapezoid
    p.append(f'<path d="M95 {ch} L120 {ch - 52} L{cw - 120} {ch - 52} L{cw - 95} {ch} Z" fill="#262b31" stroke="#3a4048"/>')
    for hx in (165, cw / 2, cw - 165):
        p.append(f'<circle cx="{hx}" cy="{ch - 26}" r="7" fill="#0e1013"/>')
    p.append("</g>")
    # j-card tracklist
    jx = 560
    p.append(f'<text x="{jx}" y="70" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">'
             f'MIXTAPE · {esc(m["vol"])}</text>')
    p.append(f'<text x="{jx}" y="104" fill="#fff" font-family="{FONT}" font-weight="800" font-size="30">'
             f'{esc(m["title"].title())}</text>')
    y = 138
    n = 1
    for side, tracks in (("SIDE A", m["side_a"]), ("SIDE B", m["side_b"])):
        p.append(f'<text x="{jx}" y="{y}" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="3">{side}</text>')
        y += 20
        for t in tracks:
            p.append(f'<text x="{jx}" y="{y}" fill="{GREEN}" font-family="{MONO}" font-size="14">{n:02d}</text>')
            p.append(f'<text x="{jx + 36}" y="{y}" fill="#fff" font-family="{FONT}" font-size="17">{esc(t)}</text>')
            p.append(f'<line x1="{jx + 36}" y1="{y + 8}" x2="{W - 50}" y2="{y + 8}" stroke="#203a2e"/>')
            y += 22
            n += 1
        y += 6
    return svg_doc(W, H, f"Mixtape: {m['title'].title()} {m['vol']}. Side A: {', '.join(m['side_a'])}. "
                         f"Side B: {', '.join(m['side_b'])}.", "\n".join(p))


# ------------------------------------------------------------------ turntable
def turntable():
    W = H = 320
    grooves = "".join(f'<circle cx="140" cy="165" r="{r}" fill="none" stroke="#1d2420" stroke-width="1.5"/>'
                      for r in range(48, 112, 9))
    body = f"""<rect x="6" y="20" width="308" height="282" rx="22" fill="#18201c" stroke="{STROKE}" stroke-width="2"/>
<rect x="6" y="20" width="308" height="282" rx="22" fill="url(#bg)" opacity=".6"/>
<circle cx="140" cy="165" r="122" fill="#0b0f0d" stroke="#2c3a33" stroke-width="3"/>
<g class="spin" style="animation-duration:1.8s">
<circle cx="140" cy="165" r="114" fill="#080a09"/>{grooves}
<path d="M140 65 A100 100 0 0 1 235 140" fill="none" stroke="#2a3330" stroke-width="5" opacity=".7"/>
<circle cx="140" cy="165" r="36" fill="{GREEN}"/>
<text x="140" y="160" fill="{BG_DARK}" font-family="{FONT}" font-weight="800" font-size="9" text-anchor="middle">DMVDXN</text>
<text x="140" y="176" fill="{BG_DARK}" font-family="{MONO}" font-size="7" text-anchor="middle">33⅓ RPM</text>
<circle cx="140" cy="165" r="4" fill="#ddd"/></g>
<circle cx="276" cy="58" r="20" fill="#2c3a33" stroke="#3f5248" stroke-width="2"/><circle cx="276" cy="58" r="7" fill="#9fb3a8"/>
<path d="M276 58 L282 200 L232 252" fill="none" stroke="#c9d1d9" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="216" y="244" width="26" height="16" rx="3" fill="{GREEN}" transform="rotate(-45 229 252)"/>
<circle cx="290" cy="280" r="9" fill="{GREEN}"><animate attributeName="opacity" values="1;.35;1" dur="1.6s" repeatCount="indefinite"/></circle>
<rect x="28" y="276" width="44" height="8" rx="4" fill="#2c3a33"/><rect x="28" y="276" width="28" height="8" rx="4" fill="{GREEN}"/>"""
    return svg_doc(W, H, "Animated turntable spinning a DMVDXN record", body)


# ------------------------------------------------------------------ ticket stub contact
def ticket():
    W, H = 1100, 210
    stub_x = 850
    body = f"""<defs><mask id="m"><rect width="{W}" height="{H}" fill="#fff"/>
<circle cx="{stub_x}" cy="8" r="16" fill="#000"/><circle cx="{stub_x}" cy="{H - 8}" r="16" fill="#000"/>
<circle cx="8" cy="{H / 2}" r="16" fill="#000"/><circle cx="{W - 8}" cy="{H / 2}" r="16" fill="#000"/></mask></defs>
<g mask="url(#m)">
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="14" fill="url(#bg)" stroke="{GREEN}" stroke-width="2"/>
<clipPath id="sc"><rect x="{stub_x}" y="0" width="{W - stub_x}" height="{H}"/></clipPath>
<rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="14" fill="{GREEN}" clip-path="url(#sc)"/></g>
<line x1="{stub_x}" y1="30" x2="{stub_x}" y2="{H - 30}" stroke="{BG_DARK}" stroke-width="2" stroke-dasharray="6 6"/>
<text x="56" y="56" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="4">CODE IN STEREO PRESENTS</text>
<text x="56" y="100" fill="#fff" font-family="{FONT}" font-weight="800" font-size="38">A COLLAB SESSION</text>
<text x="56" y="130" fill="{TEXT}" font-family="{FONT}" font-size="17">feat. Daniel Onyejiekwe &amp; You</text>
<text x="56" y="168" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="2">VENUE: DANIELONYEJIEKWE.COM   ·   DOORS: ANYTIME   ·   ALL GENRES WELCOME</text>
<text x="{(stub_x + W - 8) / 2}" y="78" fill="{BG_DARK}" font-family="{FONT}" font-weight="800" font-size="30" text-anchor="middle">ADMIT</text>
<text x="{(stub_x + W - 8) / 2}" y="112" fill="{BG_DARK}" font-family="{FONT}" font-weight="800" font-size="30" text-anchor="middle">ONE</text>
<text x="{(stub_x + W - 8) / 2}" y="150" fill="{BG_DARK}" font-family="{MONO}" font-size="12" text-anchor="middle" letter-spacing="2">NO. 0001</text>"""
    return svg_doc(W, H, "Ticket: Code in Stereo presents a collab session, featuring Daniel Onyejiekwe and you. "
                         "Admit one.", body)


# ------------------------------------------------------------------ advisory label
def advisory():
    W, H = 240, 150
    body = f"""<rect width="{W}" height="{H}" fill="#000"/>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" fill="none" stroke="#fff" stroke-width="3"/>
<text x="{W / 2}" y="44" fill="#fff" font-family="{FONT}" font-weight="900" font-size="26" text-anchor="middle" letter-spacing="1">CODE</text>
<text x="{W / 2}" y="70" fill="#fff" font-family="{FONT}" font-weight="900" font-size="22" text-anchor="middle">ADVISORY</text>
<rect x="16" y="82" width="{W - 32}" height="56" fill="#fff"/>
<text x="{W / 2}" y="106" fill="#000" font-family="{FONT}" font-weight="900" font-size="17" text-anchor="middle">EXPLICIT CONTENT</text>
<text x="{W / 2}" y="128" fill="#000" font-family="{FONT}" font-weight="700" font-size="13" text-anchor="middle">CONTAINS CODE</text>"""
    return svg_doc(W, H, "Code advisory: explicit content, contains code", body)


def main():
    for num, title, sub, dur, frac in TRACKS:
        slug = title.lower().replace("'", "").replace(" ", "-")
        write(f"tracks/{num}-{slug}.svg", track_header(num, title, sub, dur, frac))
    for slug, *rest in RELEASES:
        write(f"releases/{slug}.svg", album_cover(*rest))
    write("outro.svg", outro())
    write("tour-dates.svg", tour_dates())
    write("mixtape.svg", mixtape())
    write("turntable.svg", turntable())
    write("ticket.svg", ticket())
    write("advisory.svg", advisory())
    print("static assets written to", os.path.normpath(ROOT))


if __name__ == "__main__":
    main()
