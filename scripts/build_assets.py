"""Builds the static SVGs in assets/: the animated terminal header, project cards,
stack card, contact buttons and the snake placeholder.

Edit the CONTENT section below, then run:

    pip install fonttools brotli
    python scripts/build_assets.py
"""
from pathlib import Path

from svgkit import (BG, BLUE, BORDER, CHAR, CYAN, FAINT, GREEN, MUTED, NEON, ORANGE, PANEL,
                    PURPLE, RED, SOFT, SVG, TEXT, YELLOW, esc, prompt_segments, vivid, width, wrap)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ───────────────────────────── CONTENT ─────────────────────────────

NAME = "Harsh Parmar"
ROLE = "AI & Full-Stack Developer"
PLACE = "Mumbai, India"
MISSION = "I build AI systems for people with a real problem, not a tech wishlist."
MISSION_2 = "RAG assistants · agents · automation · full products, end to end"
SHIPPED = ["claimsathi/", "clipmaker/", "flowdesk/", "figma-to-code/", "pdf-buddy/", "shippingmath/"]
STATUS = "open to freelance projects and full-time roles"

TAG_COLORS = {
    "python": "#3572A5", "fastapi": "#009688", "claude": "#D97757", "sse": "#8b949e",
    "whisper": "#10a37f", "ffmpeg": "#5cb85c", "opencv": "#5C3EE8", "next.js": "#e6edf3",
    "express": "#c9d1d9", "socket.io": "#c9d1d9", "postgres": "#4169E1", "prisma": "#5a67d8",
    "typescript": "#3178c6", "playwright": "#2EAD33", "react": "#61dafb", "groq": "#f55036",
    "supabase": "#3ecf8e", "astro": "#ff5a03", "cloudflare": "#f38020", "figma api": "#a259ff",
}

PROJECTS = [
    dict(slug="claimsathi", name="ClaimSathi", badge=("BUILD DAY", YELLOW),
         desc="Claim rejected? Upload 3 PDFs and get an honest verdict in ~30s, checked "
              "against your policy and 9 IRDAI rules, plus an appeal letter.",
         stat="4/4 on the expert answer key · EN / HI / MR letters",
         tags=["python", "fastapi", "claude", "sse"]),
    dict(slug="clipmaker", name="Clipmaker", badge=("214 TESTS", GREEN),
         desc="Long video in, scroll-stopping clips out. Transcribes, ranks the best moments, "
              "reframes to 9:16 on the speaker and burns in captions.",
         stat="editable studio: trim · reframe · retime · re-render",
         tags=["python", "whisper", "ffmpeg", "opencv"]),
    dict(slug="flowdesk", name="FlowDesk", badge=("MONOREPO", BLUE),
         desc="Tasks, chat and docs for small teams in one workspace: a Kanban board, "
              "Slack-style channels and a docs space on one database.",
         stat="realtime presence · ⌘K palette · Razorpay + Stripe",
         tags=["next.js", "socket.io", "postgres", "prisma"]),
    dict(slug="figma-to-code", name="Figma to Code", badge=("v0.5", PURPLE),
         desc="Figma plugin + engine that turns designs into clean, responsive HTML/CSS, "
              "then checks it against Figma pixel by pixel in a real browser.",
         stat="fidelity + code-quality scores · 10k layers in ~15s",
         tags=["python", "fastapi", "typescript", "playwright"]),
    dict(slug="pdf-buddy", name="PDF Buddy", badge=("LIVE", NEON),
         desc="RAG chatbot: upload a PDF, ask anything, and get answers grounded in the "
              "document instead of the model's guesses.",
         stat="LLaMA 3.3 70B on Groq · pgvector · 3-tier retrieval",
         tags=["fastapi", "react", "groq", "supabase"]),
    dict(slug="shippingmath", name="ShippingMath", badge=("LIVE", NEON),
         desc="Free shipping calculator for online sellers: dimensional weight with 2026 UPS, "
              "FedEx and USPS rules, box comparison and margin.",
         stat="shippingmath.com · no sign-up · runs in the browser",
         tags=["astro", "typescript", "cloudflare"]),
]

STACK_ROWS = [
    ("ai", [("Claude", "#D97757"), ("OpenAI", "#10a37f"), ("Groq · LLaMA", "#f55036"),
            ("Whisper", "#74aa9c"), ("RAG", NEON), ("pgvector", "#4169E1"), ("Hugging Face", "#FFD21E")]),
    ("backend", [("Python", "#3572A5"), ("FastAPI", "#009688"), ("Node.js", "#5FA04E"),
                 ("Express", "#c9d1d9"), ("Socket.io", "#c9d1d9"), ("PHP", "#777BB4"), ("Laravel", "#FF2D20")]),
    ("frontend", [("TypeScript", "#3178c6"), ("React", "#61dafb"), ("Next.js", "#e6edf3"),
                  ("Astro", "#ff5a03"), ("Tailwind", "#38bdf8"), ("GSAP", "#88CE02")]),
    ("data", [("PostgreSQL", "#4169E1"), ("Prisma", "#5a67d8"), ("Supabase", "#3ecf8e"),
              ("Redis · BullMQ", "#FF4438"), ("MySQL", "#4479A1")]),
    ("ship", [("Vercel", "#e6edf3"), ("Cloudflare", "#f38020"), ("Docker", "#2496ED"),
              ("Playwright", "#2EAD33"), ("Figma plugins", "#a259ff")]),
]

BUTTONS = [
    ("linkedin", "open linkedin", "#0A66C2"),
    ("email", "mail harsh", "#EA4335"),
]

# ───────────────────────────── HEADER ─────────────────────────────


def header():
    W, size, lh, x0 = 880, 15, 27, 30
    cw = size * CHAR
    type_speed, pause = 0.07, 0.32
    script = [
        ("cmd", "whoami"),
        ("name", NAME),
        ("out", [(ROLE, TEXT, 700), ("  ·  " + PLACE, MUTED)]),
        ("gap",),
        ("cmd", "cat mission.txt"),
        ("out", [(MISSION, SOFT)]),
        ("out", [(MISSION_2, MUTED)]),
        ("gap",),
        ("cmd", "ls ~/shipped"),
        ("out", sum(([(d, BLUE, 700), ("  ", TEXT)] for d in SHIPPED), [])[:-1]),
        ("gap",),
        ("cmd", "echo $STATUS"),
        ("status", STATUS),
        ("gap",),
        ("prompt",),
    ]
    heights = {"name": 52, "gap": 12}
    top = 38 + 24
    H = top + sum(heights.get(item[0], lh) for item in script) + 8
    svg = SVG(W, H, f"{NAME}: {ROLE}, {PLACE}")
    svg.window("harsh@mumbai: ~ — zsh")

    p_w = width("harsh@mumbai:~$ ", size)
    t, y = 0.6, top

    def appear(at, fade=0.0):
        if fade:
            return (f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" '
                    f'begin="{at:.2f}s" dur="{fade}s" fill="freeze"/>')
        return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s" fill="freeze"/>'

    for item in script:
        kind = item[0]
        if kind == "gap":
            y += heights["gap"]
            t += 0.3
            continue
        base = y + 18 if kind != "name" else y + 38
        if kind in ("cmd", "prompt"):
            svg.add(appear(t))
            svg.text(x0, base, prompt_segments(), size=size)
            svg.add("</g>")
            cx = x0 + p_w
            if kind == "prompt":
                svg.add(f'<rect x="{cx:.1f}" y="{base - 14}" width="{cw:.1f}" height="18" fill="{NEON}" opacity="0">'
                        f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
                        f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.06s" '
                        f'begin="{t + 0.01:.2f}s" repeatCount="indefinite"/></rect>')
                y += lh
                continue
            cmd = item[1]
            n = len(cmd)
            start, dur = t + 0.3, n * type_speed
            vals = ";".join(f"{i * cw:.1f}" for i in range(n + 1))
            xs = ";".join(f"{cx + i * cw:.1f}" for i in range(n + 1))
            cid = svg.uid("type")
            svg.defs.append(
                f'<clipPath id="{cid}"><rect x="{cx:.1f}" y="{base - 16}" width="0" height="22">'
                f'<animate attributeName="width" values="{vals}" calcMode="discrete" begin="{start:.2f}s" '
                f'dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
            svg.add(f'<g clip-path="url(#{cid})">')
            svg.text(cx, base, [(cmd, TEXT)], size=size)
            svg.add("</g>")
            end = start + dur
            svg.add(f'<rect x="{cx:.1f}" y="{base - 14}" width="{cw:.1f}" height="18" fill="{NEON}" opacity="0">'
                    f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
                    f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{start:.2f}s" '
                    f'dur="{dur:.2f}s" fill="freeze"/>'
                    f'<set attributeName="opacity" to="0" begin="{end + pause:.2f}s"/></rect>')
            t = end + pause
            y += lh
        elif kind == "name":
            svg.add(appear(t, fade=0.45))
            gid = svg.uid("blur")
            svg.defs.append(f'<filter id="{gid}" x="-10%" y="-60%" width="120%" height="220%">'
                            f'<feGaussianBlur stdDeviation="7"/></filter>')
            svg.text(x0, base, item[1], size=38, weight=800, fill=NEON,
                     attrs=f'filter="url(#{gid})" opacity=".55"')
            svg.text(x0, base, item[1], size=38, weight=800, fill=NEON)
            svg.add("</g>")
            t += 0.15
            y += heights["name"]
        elif kind == "out":
            svg.add(appear(t))
            svg.text(x0, base, item[1], size=size)
            svg.add("</g>")
            t += 0.12
            y += lh
        elif kind == "status":
            svg.add(appear(t))
            svg.add('<g><animate attributeName="opacity" values="1;.25;1" dur="1.8s" repeatCount="indefinite"/>')
            svg.text(x0, base, [("●", NEON)], size=size)
            svg.add("</g>")
            svg.text(x0 + 2 * cw, base, [(item[1], TEXT)], size=size)
            svg.add("</g>")
            t += 0.12
            y += lh
    return svg.save(ASSETS / "header.svg")


# ───────────────────────────── PROJECT CARDS ─────────────────────────────


def pill(svg, x, y, label, color, size=11.5, h=22, dot=True):
    pad = 9
    tw = width(label, size)
    w = pad * 2 + tw + (12 if dot else 0)
    svg.add(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{FAINT}" stroke="{BORDER}"/>')
    tx = x + pad
    if dot:
        svg.add(f'<circle cx="{tx + 3.5:.1f}" cy="{y + h / 2}" r="3.5" fill="{vivid(color)}"/>')
        tx += 12
    svg.text(tx, y + h / 2 + size * 0.36, label, size=size, fill=SOFT)
    return w


def card(p):
    W, H, pad = 440, 210, 24
    svg = SVG(W, H, f"{p['name']}: {p['desc']}")
    bar = svg.window("", bar=30, radius=10)
    svg.text(68, 19.5, f"~/{p['slug']}", size=12, fill=MUTED)

    label, color = p["badge"]
    bsize, bh = 10.5, 18
    bw = width(label, bsize) + 18 + (11 if label == "LIVE" else 0)
    bx, by = W - 14 - bw, (bar - bh) / 2
    svg.add(f'<rect x="{bx:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="{bh / 2}" fill="{color}" '
            f'fill-opacity=".12" stroke="{color}" stroke-opacity=".6"/>')
    tx = bx + 9
    if label == "LIVE":
        svg.add(f'<circle cx="{tx + 3:.1f}" cy="{bar / 2}" r="3" fill="{color}">'
                f'<animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>')
        tx += 11
    svg.text(tx, bar / 2 + 3.8, label, size=bsize, weight=700, fill=color)

    ty = bar + 36
    tw = svg.text(pad, ty, [("❯ ", NEON, 700), (p["name"], TEXT, 800)], size=20)
    svg.add(f'<rect x="{pad + tw + 4:.1f}" y="{ty - 16}" width="10" height="19" fill="{NEON}">'
            f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" '
            f'repeatCount="indefinite"/></rect>')

    dsize = 13
    lines = wrap(p["desc"], int((W - pad * 2) / (dsize * CHAR)))
    assert len(lines) <= 3, f"{p['name']}: description needs {len(lines)} lines, max is 3"
    for i, line in enumerate(lines):
        svg.text(pad, ty + 27 + i * 19.5, line, size=dsize, fill=SOFT)
    sy = ty + 27 + 3 * 19.5 + 4
    svg.text(pad, sy, [("→ ", NEON, 700), (p["stat"], GREEN)], size=12)

    x, y = pad, H - 22 - 18
    for tag in p["tags"]:
        x += pill(svg, x, y, tag, TAG_COLORS.get(tag, MUTED)) + 7
    assert x <= W - pad + 7, f"{p['name']}: tags overflow the card"
    return svg.save(ASSETS / "projects" / f"{p['slug']}.svg")


# ───────────────────────────── STACK ─────────────────────────────


def stack():
    W, x0, size = 880, 30, 15
    label_w = width("frontend   ", 14)
    rows, y = [], 0
    # lay out pills first to know the height
    max_x = W - x0
    for label, items in STACK_ROWS:
        x, line, placed = x0 + label_w, 0, []
        for name, color in items:
            w = 18 + width(name, 12.5) + 12
            if x + w > max_x:
                line += 1
                x = x0 + label_w
            placed.append((x, line, name, color))
            x += w + 8
        rows.append((label, placed, line + 1))
    top = 38 + 30
    H = top + 34 + sum(n * 36 for _, _, n in rows) + 14
    svg = SVG(W, H, "Tech stack: " + "; ".join(f"{l}: " + ", ".join(n for n, _ in it) for l, it in STACK_ROWS))
    svg.window("stack.txt — harsh@mumbai")
    svg.text(x0, top + 4, prompt_segments() + [("cat stack.txt", TEXT)], size=size)
    y = top + 34
    for label, placed, nlines in rows:
        svg.text(x0, y + 17.5, label, size=14, weight=700, fill=NEON)
        for x, line, name, color in placed:
            pill(svg, x, y + line * 36, name, color, size=12.5, h=26)
        y += nlines * 36
    return svg.save(ASSETS / "stack.svg")


# ───────────────────────────── BUTTONS + SNAKE PLACEHOLDER ─────────────────────────────


def buttons():
    size, h = 14, 44
    w = max(width(f"$ {label} ↗", size) for _, label, _ in BUTTONS) + 52
    out = []
    for slug, label, color in BUTTONS:
        svg = SVG(int(w), h, label)
        svg.add(f'<rect x=".5" y=".5" width="{w - 1:.1f}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>')
        svg.add(f'<rect x="1" y="12" width="3" height="20" rx="1.5" fill="{vivid(color)}"/>')
        svg.text(22, h / 2 + 5, [("$ ", NEON, 700), (label, TEXT, 700), (" ↗", MUTED)], size=size)
        out.append(svg.save(ASSETS / "buttons" / f"{slug}.svg"))
    return out


def snake_placeholder():
    for mode, bg, fg, sub in (("dark", BG, TEXT, MUTED), ("light", "#ffffff", "#1f2328", "#59636e")):
        svg = SVG(880, 120, "Contribution snake placeholder")
        svg.add(f'<rect x=".5" y=".5" width="879" height="119" rx="12" fill="{bg}" stroke="{BORDER}" stroke-dasharray="6 6"/>')
        svg.text(440, 56, [("$ ", NEON, 700), ("./hatch-snake.sh", fg, 700)], size=15, anchor="middle")
        svg.text(440, 84, "run Actions › Update profile › Run workflow once and the snake appears here",
                 size=12.5, fill=sub, anchor="middle")
        p = ASSETS / f"snake-{mode}.svg"
        if not p.exists() or "placeholder" in p.read_text(encoding="utf-8"):
            svg.save(p)


if __name__ == "__main__":
    print(header())
    for p in PROJECTS:
        print(card(p))
    print(stack())
    print(*buttons(), sep="\n")
    snake_placeholder()
    print("done")
