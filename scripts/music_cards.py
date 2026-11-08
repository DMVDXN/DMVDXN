"""Generate the live Code in Stereo cards (run by .github/workflows/music-cards.yml).

Outputs into the folder given as the first argument (default: dist/):
  now-playing.svg   Spotify "now playing" / "last spin" card
  wrapped.svg       Spotify-Wrapped-style summary of the past 12 months on GitHub
  waveform.svg      Past year of contributions drawn as an audio waveform
  sequencer.svg     Contribution calendar as a drum machine step sequencer

Environment:
  GITHUB_TOKEN, GITHUB_USER (default DMVDXN)
  SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN  (optional; "off air" card without them)

Local preview with fake data:  python scripts/music_cards.py dist --demo
Standard library only, so the workflow needs no pip install.
"""
import base64
import calendar
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

from svg_common import (BG_DARK, FONT, GREEN, MONO, MUTED, STROKE, TEXT,
                        eq_bars, esc, svg_doc)

UA = {"User-Agent": "code-in-stereo-cards"}
# Markup/styling languages inflate the language mix on static sites, so leave them out.
HIDDEN_LANGS = {"HTML", "CSS", "SCSS", "Sass", "Less"}


# ================================================================== HTTP helpers
def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})}, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()


def http_json(url, **kw):
    status, body = http(url, **kw)
    return status, (json.loads(body) if body else None)


# ================================================================== GitHub data
GQL = """
query($login:String!){
  user(login:$login){
    followers{ totalCount }
    contributionsCollection{
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions restrictedContributionsCount
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
      commitContributionsByRepository(maxRepositories:10){ repository{ name } contributions{ totalCount } }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{ name stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
    }
  }
}"""


def fetch_github(user, token):
    payload = json.dumps({"query": GQL, "variables": {"login": user}}).encode()
    _, res = http_json("https://api.github.com/graphql", data=payload,
                       headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    if res.get("errors"):
        raise RuntimeError(res["errors"])
    u = res["data"]["user"]
    cc = u["contributionsCollection"]
    days = [(d["date"], d["contributionCount"])
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    repos = [(r["repository"]["name"], r["contributions"]["totalCount"])
             for r in cc["commitContributionsByRepository"]]
    langs, colors = Counter(), {}
    for node in u["repositories"]["nodes"]:
        for e in node["languages"]["edges"]:
            if e["node"]["name"] in HIDDEN_LANGS:
                continue
            langs[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or GREEN
    stats = {"stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
             "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
             "prs": cc["totalPullRequestContributions"], "issues": cc["totalIssueContributions"],
             "reviews": cc["totalPullRequestReviewContributions"],
             "repos": u["repositories"]["totalCount"], "followers": u["followers"]["totalCount"]}
    return {"total": cc["contributionCalendar"]["totalContributions"], "days": days,
            "repos": repos, "langs": langs, "colors": colors, "stats": stats}


def demo_github():
    rnd = random.Random(7)
    today = dt.date.today()
    days = []
    for i in range(364, -1, -1):
        d = today - dt.timedelta(days=i)
        base = 2 + 3 * math.sin(i / 40) ** 2
        days.append((d.isoformat(), max(0, int(rnd.gauss(base, 3))) if rnd.random() > .25 else 0))
    return {"total": sum(c for _, c in days), "days": days,
            "repos": [("AudioVista", 120), ("Lyris", 80), ("Nexum", 40)],
            "langs": Counter({"TypeScript": 900, "Python": 400, "Kotlin": 100}),
            "colors": {"TypeScript": "#3178c6", "Python": "#3572A5", "Kotlin": "#A97BFF"},
            "stats": {"stars": 12, "commits": 640, "prs": 25, "issues": 8, "reviews": 4, "repos": 21, "followers": 3}}


def summarize(gh):
    days = gh["days"]
    # longest streak
    best = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    # current streak (today may still be empty, so allow it)
    cs = 0
    for i, (_, c) in enumerate(reversed(days)):
        if c > 0:
            cs += 1
        elif i == 0:
            continue
        else:
            break
    months, weekdays = defaultdict(int), defaultdict(int)
    for d, c in days:
        y, m, dd = map(int, d.split("-"))
        months[(y, m)] += c
        weekdays[dt.date(y, m, dd).weekday()] += c
    pm = max(months, key=months.get) if any(months.values()) else None
    pw = max(weekdays, key=weekdays.get) if any(weekdays.values()) else None
    top_repo = max(gh["repos"], key=lambda r: r[1]) if gh["repos"] else None
    top_lang = gh["langs"].most_common(1)[0][0] if gh["langs"] else None
    return {
        "total": gh["total"],
        "longest": best,
        "current": cs,
        "peak_month": f"{calendar.month_abbr[pm[1]]} {pm[0]}" if pm else "—",
        "peak_month_n": months[pm] if pm else 0,
        "fav_day": calendar.day_name[pw] if pw is not None else "—",
        "top_repo": top_repo[0] if top_repo else "—",
        "top_repo_n": top_repo[1] if top_repo else 0,
        "top_lang": top_lang or "—",
        "top_lang_color": gh["colors"].get(top_lang, GREEN),
        "langs": gh["langs"].most_common(5),
        "colors": gh["colors"],
        "active_days": sum(1 for _, c in days if c > 0),
    }


# ================================================================== Wrapped card
def fit(text, max_chars):
    text = str(text)
    return text if len(text) <= max_chars else text[: max_chars - 1] + "…"


def wrapped_svg(s, user):
    W, H = 1100, 440
    year = dt.date.today().year
    tiles = [
        ("TOTAL PLAYS", f"{s['total']:,}", "contributions, past 12 months", GREEN),
        ("TOP GENRE", fit(s["top_lang"], 13), "most-written language", s["top_lang_color"]),
        ("MOST PLAYED", fit(s["top_repo"].replace("_", " ").replace("-", " "), 15), f"{s['top_repo_n']} commits", "#B98CFF"),
        ("LONGEST STREAK", f"{s['longest']} days", f"current: {s['current']} days", "#F5B942"),
        ("PEAK MONTH", s["peak_month"], f"{s['peak_month_n']} contributions", "#FF5C7A"),
        ("FAVORITE DAY", s["fav_day"], f"{s['active_days']} active days", "#5AA9FF"),
    ]
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22" fill="url(#bg)" stroke="{STROKE}"/>',
         # decorative blobs
         f'<circle cx="120" cy="400" r="150" fill="{GREEN}" opacity=".12"/>',
         f'<circle cx="330" cy="40" r="90" fill="#B98CFF" opacity=".10"/>',
         f'<text x="48" y="80" fill="{GREEN}" font-family="{MONO}" font-size="14" letter-spacing="4">PAST 12 MONTHS</text>',
         f'<text x="44" y="150" fill="#fff" font-family="{FONT}" font-weight="900" font-size="62">{esc(fit(user, 10))}</text>',
         f'<text x="44" y="216" fill="#fff" font-family="{FONT}" font-weight="900" font-size="62">WRAPPED</text>',
         f'<text x="44" y="282" fill="{GREEN}" font-family="{FONT}" font-weight="900" font-size="62">{year}</text>']
    # language "genre" bar
    tot = sum(v for _, v in s["langs"]) or 1
    x = 48
    p.append(f'<text x="48" y="336" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="2">GENRE MIX</text>')
    for name, v in s["langs"]:
        w = 300 * v / tot
        p.append(f'<rect x="{x:.1f}" y="348" width="{max(w - 2, 1):.1f}" height="12" rx="3" fill="{s["colors"].get(name, GREEN)}"/>')
        x += w
    # legend: fixed 2x2 grid that stays left of the tiles (which start at x=404)
    for i, (name, v) in enumerate(s["langs"][:4]):
        lx = 48 + (i % 2) * 160
        ly = 386 + (i // 2) * 22
        label = f"{fit(name, 14)} {100 * v / tot:.0f}%"
        p.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{s["colors"].get(name, GREEN)}"/>')
        p.append(f'<text x="{lx + 15}" y="{ly}" fill="{TEXT}" font-family="{FONT}" font-size="12">{esc(label)}</text>')
    # tiles 3x2
    tw, th, gx, gy, x0, y0 = 220, 170, 16, 16, 404, 40
    for i, (label, value, sub, acc) in enumerate(tiles):
        tx = x0 + (i % 3) * (tw + gx)
        ty = y0 + (i // 3) * (th + gy)
        fs = 34 if len(value) <= 8 else (28 if len(value) <= 10 else (23 if len(value) <= 12 else 18))
        p.append(f'<g transform="translate({tx} {ty})">'
                 f'<rect width="{tw}" height="{th}" rx="16" fill="{acc}" fill-opacity=".13" stroke="{acc}" stroke-opacity=".45"/>'
                 f'<rect x="18" y="20" width="28" height="4" rx="2" fill="{acc}"/>'
                 f'<text x="18" y="50" fill="{acc}" font-family="{MONO}" font-size="13" letter-spacing="2">{label}</text>'
                 f'<text x="18" y="{98 + (34 - fs) // 3}" fill="#fff" font-family="{FONT}" font-weight="800" font-size="{fs}">{esc(value)}</text>'
                 f'<text x="18" y="140" fill="{MUTED}" font-family="{FONT}" font-size="14">{esc(sub)}</text></g>')
    return svg_doc(W, H, f"{user} Wrapped {year}: {s['total']} contributions, top language {s['top_lang']}, "
                         f"most active repo {s['top_repo']}, longest streak {s['longest']} days", "\n".join(p))


# ================================================================== Waveform card
def waveform_svg(gh, s):
    W, H = 1100, 230
    days = gh["days"][-364:]
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    sums = [sum(c for _, c in w) for w in weeks]
    mx = max(sums) or 1
    cy, amp = 120, 62
    x0, x1 = 50, W - 50
    step = (x1 - x0) / len(sums)
    bw = max(step * 0.62, 2)
    css = (".ph{animation:ph 12s linear infinite}"
           f"@keyframes ph{{from{{transform:translateX(0)}}to{{transform:translateX({x1 - x0}px)}}}}")
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#bg)" stroke="{STROKE}"/>',
         '<defs><linearGradient id="wv" x1="0" y1="1" x2="0" y2="0"><stop stop-color="#0E4429"/>'
         f'<stop offset=".5" stop-color="#26A641"/><stop offset="1" stop-color="{GREEN}"/></linearGradient></defs>',
         f'<text x="50" y="36" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">CONTRIBUTION WAVEFORM</text>',
         f'<text x="{W - 50}" y="36" fill="{MUTED}" font-family="{MONO}" font-size="12" text-anchor="end" '
         f'letter-spacing="1">{s["total"]:,} PLAYS · 52 WEEKS · 1 BAR = 1 WEEK</text>',
         f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="#1e3b2d"/>']
    for i, v in enumerate(sums):
        h = max(2, amp * math.sqrt(v / mx))
        x = x0 + i * step + (step - bw) / 2
        p.append(f'<rect x="{x:.1f}" y="{cy - h:.1f}" width="{bw:.1f}" height="{2 * h:.1f}" rx="{bw / 2:.1f}" '
                 f'fill="url(#wv)" opacity="{0.45 + 0.55 * v / mx:.2f}"/>')
    # month labels at the first week of each month
    last = None
    for i, w in enumerate(weeks):
        m = int(w[0][0][5:7])
        if m != last:
            if last is not None:
                p.append(f'<text x="{x0 + i * step:.1f}" y="{H - 22}" fill="{MUTED}" font-family="{MONO}" '
                         f'font-size="11">{calendar.month_abbr[m].upper()}</text>')
            last = m
    p.append(f'<g class="ph"><line x1="{x0}" y1="{cy - amp - 8}" x2="{x0}" y2="{cy + amp + 8}" stroke="#fff" '
             f'stroke-width="2" opacity=".8"/><circle cx="{x0}" cy="{cy - amp - 8}" r="4" fill="#fff"/></g>')
    return svg_doc(W, H, f"Past year of GitHub contributions drawn as an audio waveform, {s['total']} total",
                   "\n".join(p), css)


# ================================================================== Beat machine (contribution calendar)
INSTRUMENTS = ["KICK", "SNARE", "HI-HAT", "CLAP", "TOM", "RIDE", "CRASH"]
DAY_ABBR = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
PAD_COLORS = ["#161b22", "#0E4429", "#006D32", "#26A641", GREEN]


def sequencer_svg(gh, s):
    days = gh["days"][-371:]
    first = dt.date.fromisoformat(days[0][0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # back up to Sunday
    cells = []
    for d, c in days:
        date = dt.date.fromisoformat(d)
        cells.append(((date - start).days // 7, (date.weekday() + 1) % 7, c, date))
    ncols = max(col for col, *_ in cells) + 1
    nz = sorted(c for *_, c, _ in cells if c > 0)
    cuts = [nz[int(len(nz) * q)] for q in (.25, .5, .75)] if nz else [1, 2, 3]

    def level(c):
        return 0 if c == 0 else 1 + sum(c > t for t in cuts)

    W, T = 1100, 12
    lx, top, gap = 112, 94, 3
    pad = (W - lx - 30 - gap * (ncols - 1)) / ncols
    H = int(top + 7 * (pad + gap) + 52)
    css = (f".ph{{animation:ph {T}s linear infinite}}"
           f"@keyframes ph{{from{{transform:translateX(0)}}to{{transform:translateX({ncols * (pad + gap):.1f}px)}}}}"
           f".f{{opacity:0;animation:hit {T}s linear infinite}}"
           "@keyframes hit{0%{opacity:.85}6%{opacity:0}100%{opacity:0}}")
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="url(#bg)" stroke="{STROKE}"/>',
         # transport controls
         f'<rect x="28" y="22" width="30" height="30" rx="6" fill="{GREEN}"/><path d="M38 29 L50 37 L38 45Z" fill="{BG_DARK}"/>',
         f'<rect x="64" y="22" width="30" height="30" rx="6" fill="#1b2a23"/><rect x="73" y="31" width="12" height="12" rx="1" fill="{MUTED}"/>',
         f'<text x="112" y="36" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">BEAT MACHINE · CONTRIBUTIONS</text>',
         f'<text x="112" y="54" fill="{MUTED}" font-family="{MONO}" font-size="11" letter-spacing="1">'
         f'{s["total"]:,} HITS · {s["active_days"]} ACTIVE DAYS · 1 COLUMN = 1 WEEK</text>']
    for r in range(7):
        y = top + r * (pad + gap) + pad * .75
        p.append(f'<text x="28" y="{y:.1f}" fill="{TEXT}" font-family="{MONO}" font-size="10" font-weight="700">{INSTRUMENTS[r]}</text>')
        p.append(f'<text x="80" y="{y:.1f}" fill="#5f7a6d" font-family="{MONO}" font-size="9">{DAY_ABBR[r]}</text>')
    for col, row, c, date in cells:
        x = lx + col * (pad + gap)
        y = top + row * (pad + gap)
        lv = level(c)
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{pad:.1f}" height="{pad:.1f}" rx="3" fill="{PAD_COLORS[lv]}"/>')
        if lv:
            p.append(f'<rect class="f" x="{x:.1f}" y="{y:.1f}" width="{pad:.1f}" height="{pad:.1f}" rx="3" fill="#fff" '
                     f'style="animation-delay:{col / ncols * T:.2f}s"/>')
    # month labels
    last = None
    for col, row, c, date in cells:
        if row == 0 and date.month != last:
            if last is not None:
                p.append(f'<text x="{lx + col * (pad + gap):.1f}" y="{top - 8}" fill="{MUTED}" font-family="{MONO}" '
                         f'font-size="10">{calendar.month_abbr[date.month].upper()}</text>')
            last = date.month
    # playhead
    gh_h = 7 * (pad + gap)
    p.append(f'<g class="ph"><rect x="{lx - 2:.1f}" y="{top - 4}" width="{pad + 4:.1f}" height="{gh_h + 5:.1f}" rx="4" '
             f'fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.5"/></g>')
    # legend
    ly = H - 22
    p.append(f'<text x="{W - 210}" y="{ly + 9}" fill="{MUTED}" font-family="{MONO}" font-size="10">QUIET</text>')
    for i, col in enumerate(PAD_COLORS):
        p.append(f'<rect x="{W - 166 + i * 17}" y="{ly}" width="12" height="12" rx="2" fill="{col}"/>')
    p.append(f'<text x="{W - 76}" y="{ly + 9}" fill="{MUTED}" font-family="{MONO}" font-size="10">LOUD</text>')
    p.append(f'<text x="28" y="{ly + 9}" fill="#5f7a6d" font-family="{MONO}" font-size="10">'
             f'longest groove: {s["longest"]} days · current groove: {s["current"]} days</text>')
    return svg_doc(W, H, f"Past year of GitHub contributions shown as a drum machine step sequencer, "
                         f"{s['total']} contributions", "\n".join(p), css)


# ================================================================== Listening stats + top genres
def stats_svg(gh, s):
    st = gh["stats"]
    W, H = 540, 250
    rows = [("COMMITS", "Tracks laid down, past year", st["commits"]),
            ("ACTIVE DAYS", "Days in the studio, past year", s["active_days"]),
            ("LONGEST STREAK", "Days in a row on the mic", s["longest"]),
            ("PULL REQUESTS", "Collabs submitted", st["prs"]),
            ("REPOSITORIES", "Albums in the catalog", st["repos"])]
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{STROKE}"/>',
         f'<text x="26" y="40" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">LISTENING STATS</text>',
         eq_bars(W - 96, 0, 8, [18, 10, 22, 12, 20, 8, 16, 24], center=35)]
    mx = max(r[2] for r in rows) or 1
    for i, (label, sub, val) in enumerate(rows):
        y = 80 + i * 36
        p.append(f'<text x="26" y="{y}" fill="#fff" font-family="{FONT}" font-weight="700" font-size="14">{label}</text>')
        p.append(f'<text x="26" y="{y + 15}" fill="#5f7a6d" font-family="{FONT}" font-size="12">{esc(sub)}</text>')
        p.append(f'<rect x="250" y="{y - 6}" width="190" height="6" rx="3" fill="#1b2a23"/>')
        p.append(f'<rect x="250" y="{y - 6}" width="{max(6, 190 * math.sqrt(val / mx)):.0f}" height="6" rx="3" fill="url(#ln)"/>')
        p.append(f'<text x="{W - 26}" y="{y}" fill="#fff" font-family="{MONO}" font-weight="700" font-size="16" '
                 f'text-anchor="end">{val:,}</text>')
    return svg_doc(W, H, "Listening stats: " + ", ".join(f"{r[2]} {r[0].lower()}" for r in rows), "\n".join(p))


def langs_svg(gh):
    W, H = 540, 250
    top = gh["langs"].most_common(6)
    tot = sum(gh["langs"].values()) or 1
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{STROKE}"/>',
         f'<text x="26" y="40" fill="{GREEN}" font-family="{MONO}" font-size="13" letter-spacing="3">TOP GENRES</text>',
         f'<text x="{W - 26}" y="40" fill="#5f7a6d" font-family="{MONO}" font-size="11" text-anchor="end">LANGUAGES · BY CODE SIZE</text>']
    # one stacked "mix" bar
    x = 26
    for name, v in top:
        w = (W - 52) * v / tot
        p.append(f'<rect x="{x:.1f}" y="56" width="{max(w - 2, 1):.1f}" height="10" rx="3" fill="{gh["colors"].get(name, GREEN)}"/>')
        x += w
    # faders, two columns
    for i, (name, v) in enumerate(top):
        col, row = i % 2, i // 2
        fx = 26 + col * 252
        y = 100 + row * 44
        pct = 100 * v / tot
        color = gh["colors"].get(name, GREEN)
        p.append(f'<circle cx="{fx + 6}" cy="{y - 5}" r="6" fill="{color}"/>')
        p.append(f'<text x="{fx + 20}" y="{y}" fill="#fff" font-family="{FONT}" font-weight="700" font-size="14">{esc(fit(name, 16))}</text>')
        p.append(f'<text x="{fx + 230}" y="{y}" fill="{TEXT}" font-family="{MONO}" font-size="13" text-anchor="end">{pct:.1f}%</text>')
        p.append(f'<rect x="{fx}" y="{y + 10}" width="230" height="5" rx="2.5" fill="#1b2a23"/>')
        p.append(f'<rect x="{fx}" y="{y + 10}" width="{max(4, 230 * v / top[0][1]):.0f}" height="5" rx="2.5" fill="{color}"/>')
    return svg_doc(W, H, "Top languages: " + ", ".join(f"{n} {100 * v / tot:.0f}%" for n, v in top), "\n".join(p))


# ================================================================== Spotify
def spotify_now():
    cid, secret, refresh = (os.environ.get(k) for k in
                            ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "SPOTIFY_REFRESH_TOKEN"))
    if not (cid and secret and refresh):
        return None
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    _, tok = http_json("https://accounts.spotify.com/api/token",
                       data=urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode(),
                       headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"})
    h = {"Authorization": f"Bearer {tok['access_token']}"}
    status, cur = http_json("https://api.spotify.com/v1/me/player/currently-playing?additional_types=episode", headers=h)
    if status == 200 and cur and cur.get("item") and cur.get("is_playing"):
        item, live = cur["item"], True
        progress = cur.get("progress_ms", 0) / max(item.get("duration_ms", 1), 1)
    else:
        _, rec = http_json("https://api.spotify.com/v1/me/player/recently-played?limit=1", headers=h)
        if not rec or not rec.get("items"):
            return None
        item, live, progress = rec["items"][0]["track"], False, 1.0
    album = item.get("album") or {}
    images = album.get("images") or item.get("images") or []
    art = None
    if images:
        url = sorted(images, key=lambda i: i.get("width") or 0)[min(1, len(images) - 1)]["url"]
        try:
            _, raw = http(url)
            art = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
        except urllib.error.URLError:
            art = None
    artists = ", ".join(a["name"] for a in item.get("artists", [])) or (item.get("show") or {}).get("name", "")
    return {"title": item.get("name", ""), "artist": artists, "album": album.get("name", ""),
            "art": art, "live": live, "progress": progress}


def now_playing_svg(np):
    W, H = 640, 170
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%b %d, %H:%M UTC")
    p = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{STROKE}"/>',
         '<defs><clipPath id="art"><rect x="24" y="24" width="122" height="122" rx="10"/></clipPath></defs>']
    if np is None:
        p += [f'<rect x="24" y="24" width="122" height="122" rx="10" fill="#0a1512"/>',
              f'<g class="spin" style="animation-duration:4s"><circle cx="85" cy="85" r="52" fill="#050807"/>'
              f'<circle cx="85" cy="85" r="38" fill="none" stroke="#1b1f1d" stroke-width="2"/>'
              f'<circle cx="85" cy="85" r="18" fill="{GREEN}"/><circle cx="85" cy="85" r="4" fill="{BG_DARK}"/>'
              f'<path d="M85 47 A38 38 0 0 1 123 85" fill="none" stroke="#2a3330" stroke-width="3"/></g>',
              f'<text x="172" y="50" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="3">● OFF AIR</text>',
              f'<text x="172" y="88" fill="#fff" font-family="{FONT}" font-weight="700" font-size="24">Between sessions</text>',
              f'<text x="172" y="116" fill="{MUTED}" font-family="{FONT}" font-size="15">Nothing spinning right now. Check back soon.</text>']
        title = "Spotify: off air"
    else:
        label = "NOW PLAYING" if np["live"] else "LAST SPIN"
        if np["art"]:
            p.append(f'<image x="24" y="24" width="122" height="122" clip-path="url(#art)" '
                     f'preserveAspectRatio="xMidYMid slice" href="{np["art"]}" xlink:href="{np["art"]}"/>')
        else:
            p.append(f'<rect x="24" y="24" width="122" height="122" rx="10" fill="#0a1512"/>')
        dot = (f'<circle cx="177" cy="45" r="5" fill="{GREEN}"><animate attributeName="opacity" values="1;.25;1" '
               f'dur="1.4s" repeatCount="indefinite"/></circle>') if np["live"] else \
              f'<circle cx="177" cy="45" r="5" fill="{MUTED}"/>'
        p += [dot,
              f'<text x="190" y="50" fill="{GREEN if np["live"] else MUTED}" font-family="{MONO}" font-size="12" '
              f'letter-spacing="3">{label}</text>',
              f'<text x="172" y="86" fill="#fff" font-family="{FONT}" font-weight="700" font-size="22">{esc(fit(np["title"], 34))}</text>',
              f'<text x="172" y="111" fill="{TEXT}" font-family="{FONT}" font-size="15">{esc(fit(np["artist"], 44))}</text>',
              f'<rect x="172" y="128" width="300" height="4" rx="2" fill="#284839"/>',
              f'<rect x="172" y="128" width="{300 * min(max(np["progress"], .02), 1):.0f}" height="4" rx="2" fill="url(#ln)"/>']
        if np["live"]:
            p.append(eq_bars(500, 136, 11, [22, 12, 30, 16, 26, 10, 20, 32]))
        title = f"{label.title()} on Spotify: {np['title']} by {np['artist']}"
    p.append(f'<text x="{W - 22}" y="{H - 14}" fill="#5f7a6d" font-family="{MONO}" font-size="10" '
             f'text-anchor="end">via Spotify · updated {stamp}</text>')
    return svg_doc(W, H, title, "\n".join(p))


def demo_spotify():
    return {"title": "Midnight Build", "artist": "The Refactors", "album": "Demo", "art": None,
            "live": True, "progress": 0.42}


# ================================================================== main
def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "dist"
    demo = "--demo" in sys.argv
    user = os.environ.get("GITHUB_USER", "DMVDXN")
    os.makedirs(out, exist_ok=True)

    def save(name, svg):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)

    # Spotify first: a failure here must not block the GitHub cards.
    try:
        np = demo_spotify() if demo else spotify_now()
    except Exception as e:  # noqa: BLE001 - keep the card "off air" on any API problem
        print("spotify error:", e)
        np = None
    save("now-playing.svg", now_playing_svg(np))

    gh = demo_github() if demo else fetch_github(user, os.environ["GITHUB_TOKEN"])
    s = summarize(gh)
    save("wrapped.svg", wrapped_svg(s, user))
    save("waveform.svg", waveform_svg(gh, s))
    save("sequencer.svg", sequencer_svg(gh, s))
    save("stats.svg", stats_svg(gh, s))
    save("top-langs.svg", langs_svg(gh))


if __name__ == "__main__":
    main()
