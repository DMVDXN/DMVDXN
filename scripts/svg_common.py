"""Shared palette and helpers for the Code in Stereo SVG assets."""
from xml.sax.saxutils import escape as _escape

GREEN = "#1ED760"
GREEN_LIGHT = "#78fbb5"
BG_DARK = "#0d1117"
BG_GREEN = "#112921"
STROKE = "#255844"
MUTED = "#99b0a4"
TEXT = "#c9d1d9"
FONT = "Arial, Helvetica, sans-serif"
MONO = "'Courier New', monospace"
HAND = "'Segoe Print', 'Bradley Hand', 'Comic Sans MS', cursive"


def esc(s):
    return _escape(str(s), {'"': "&quot;"})


# Shared CSS: equalizer bars bounce, .spin rotates around its own center.
ANIM_CSS = """
.b{fill:#1ED760;transform-box:fill-box;transform-origin:bottom;animation:eq 1.1s ease-in-out infinite alternate}
@keyframes eq{0%{transform:scaleY(.25)}50%{transform:scaleY(1)}100%{transform:scaleY(.45)}}
.bc{fill:#1ED760;transform-box:fill-box;transform-origin:center;animation:eq 1.1s ease-in-out infinite alternate}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
"""

BG_DEFS = """<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#112921"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#1ED760"/><stop offset="1" stop-color="#78fbb5"/></linearGradient>"""


def eq_bars(x0, base, n, heights, w=5, gap=4, center=None):
    """Animated equalizer bars. Bottom-aligned on `base`, or centered on y=`center` when given."""
    out = []
    for i in range(n):
        h = heights[i % len(heights)]
        y = center - h / 2 if center is not None else base - h
        cls = "bc" if center is not None else "b"
        out.append(
            f'<rect class="{cls}" x="{x0 + i * (w + gap)}" y="{y:g}" width="{w}" height="{h}" rx="2" '
            f'style="animation-delay:-{(i * 0.13) % 1.1:.2f}s"/>'
        )
    return "".join(out)


def svg_doc(w, h, title, body, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">\n'
        f'<title id="t">{esc(title)}</title>\n<style>{ANIM_CSS}{extra_css}</style>\n'
        f"<defs>{BG_DEFS}</defs>\n{body}\n</svg>\n"
    )
