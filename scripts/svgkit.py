"""Tiny helpers for drawing terminal-style SVGs with an embedded, subset font.

Every glyph in JetBrains Mono is 0.6em wide, so text layout is plain arithmetic.
Only the characters actually used are embedded, which keeps each SVG small.
"""
import base64
import html
import io
from pathlib import Path

FONT_DIR = Path(__file__).parent / "fonts"
FONT_FILES = {
    400: "JetBrainsMono-Regular.ttf",
    700: "JetBrainsMono-Bold.ttf",
    800: "JetBrainsMono-ExtraBold.ttf",
}
CHAR = 0.6  # advance width of every glyph, in em

# GitHub dark palette + terminal green
BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
FAINT = "#21262d"
TEXT = "#e6edf3"
SOFT = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#3fb950"
NEON = "#39d353"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
YELLOW = "#e3b341"
ORANGE = "#f0883e"
RED = "#ff7b72"
CYAN = "#39c5cf"

STACK = "'JBM', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def width(text, size):
    return len(text) * size * CHAR


def vivid(hex_color, min_lum=0.2):
    """Lighten a colour until it reads well on the dark background."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))

    def lum(r, g, b):
        def ch(c):
            c /= 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

    while lum(r, g, b) < min_lum:
        r, g, b = (min(255, int(c + (255 - c) * 0.12)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _subset_font(weight, chars):
    path = FONT_DIR / FONT_FILES[weight]
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:  # no fonttools: fall back to system monospace fonts
        return None
    font = TTFont(path)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = []  # no ligatures: "->" stays two characters
    options.name_IDs = []
    options.notdef_outline = True
    sub = subset.Subsetter(options)
    sub.populate(text="".join(sorted(chars)) + " ")
    sub.subset(font)
    buf = io.BytesIO()
    try:
        font.flavor = "woff2"
        font.save(buf)
        mime = "font/woff2"
    except Exception:  # brotli missing: plain TTF still works
        buf = io.BytesIO()
        font.flavor = None
        font.save(buf)
        mime = "font/ttf"
    return mime, base64.b64encode(buf.getvalue()).decode()


class SVG:
    def __init__(self, w, h, title=""):
        self.w, self.h, self.title = w, h, title
        self.defs, self.parts, self.css = [], [], []
        self.chars = {400: set(), 700: set(), 800: set()}
        self._id = 0

    def uid(self, prefix="e"):
        self._id += 1
        return f"{prefix}{self._id}"

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, segments, size=14, weight=400, fill=TEXT, anchor="start",
             attrs="", inner=""):
        """segments: a string, or a list of (text, fill[, weight]) tuples."""
        if isinstance(segments, str):
            segments = [(segments, fill, weight)]
        spans, total = [], ""
        for seg in segments:
            t, f = seg[0], seg[1]
            wgt = seg[2] if len(seg) > 2 else weight
            self.chars[wgt].update(t)
            total += t
            spans.append(f'<tspan fill="{f}" font-weight="{wgt}">{esc(t)}</tspan>')
        tl = ""
        if len(total) > 1:
            tl = f' textLength="{width(total, size):.2f}" lengthAdjust="spacingAndGlyphs"'
        self.parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}"{tl} {attrs}>'
            f'{"".join(spans)}{inner}</text>'
        )
        return width(total, size)

    def window(self, title, bar=38, radius=12, glow=True):
        """Draw a terminal window frame. Returns the y where content starts."""
        w, h = self.w, self.h
        if glow:
            gid = self.uid("glow")
            self.defs.append(
                f'<radialGradient id="{gid}" cx="88%" cy="0%" r="70%">'
                f'<stop offset="0" stop-color="{NEON}" stop-opacity=".13"/>'
                f'<stop offset="1" stop-color="{NEON}" stop-opacity="0"/></radialGradient>'
            )
        clip = self.uid("win")
        self.defs.append(f'<clipPath id="{clip}"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>')
        self.add(f'<g clip-path="url(#{clip})">')
        self.add(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
        if glow:
            self.add(f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>')
        self.add(f'<rect width="{w}" height="{bar}" fill="{PANEL}"/>')
        self.add(f'<rect y="{bar - 1}" width="{w}" height="1" fill="{BORDER}"/>')
        self.add('</g>')
        self.add(f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{radius}" fill="none" stroke="{BORDER}"/>')
        r = 6 if bar >= 34 else 5
        for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            self.add(f'<circle cx="{20 + i * (r * 3.2):.1f}" cy="{bar / 2}" r="{r}" fill="{c}"/>')
        if title:
            self.text(w / 2, bar / 2 + 4.5, title, size=12.5, fill=MUTED, anchor="middle")
        return bar

    def render(self):
        rules = []
        for wgt, chars in self.chars.items():
            if not chars:
                continue
            font = _subset_font(wgt, chars)
            if font:
                mime, data = font
                fmt = "woff2" if mime.endswith("woff2") else "truetype"
                rules.append(
                    f"@font-face{{font-family:'JBM';font-weight:{wgt};"
                    f"src:url(data:{mime};base64,{data}) format('{fmt}');}}"
                )
        rules.append(
            f"text{{font-family:{STACK};font-variant-ligatures:none;"
            f"font-feature-settings:'liga' 0,'calt' 0;white-space:pre}}"
        )
        rules.extend(self.css)
        title = f"<title>{esc(self.title)}</title>" if self.title else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" xml:space="preserve" role="img">{title}'
            f'<style>{"".join(rules)}</style><defs>{"".join(self.defs)}</defs>'
            f'{"".join(self.parts)}</svg>'
        )

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self.render(), encoding="utf-8")
        return path


def prompt_segments(user="harsh", host="mumbai", cwd="~"):
    return [(f"{user}@{host}", NEON, 700), (":", TEXT), (cwd, BLUE, 700), ("$ ", TEXT)]


def wrap(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + (1 if cur else 0) <= max_chars:
            cur = f"{cur} {wd}" if cur else wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines
