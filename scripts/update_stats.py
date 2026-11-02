"""Renders assets/stats.svg from live GitHub data. Runs daily in GitHub Actions.

    GH_TOKEN=... python scripts/update_stats.py               # fetch + render
    python scripts/update_stats.py --from-json data.json      # render saved data

Uses only the standard library (plus fonttools, if installed, to embed the font).
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

from svgkit import (CHAR, FAINT, GREEN, MUTED, NEON, SOFT, SVG, TEXT, prompt_segments, vivid, width)

ROOT = Path(__file__).resolve().parent.parent
LOGIN = os.environ.get("GITHUB_REPOSITORY_OWNER", "HarshParmar321")
TOP_N = 6
# Markup and config languages say little about what you build, so they are left out.
EXCLUDE = {"HTML", "CSS", "SCSS", "Less", "Blade", "Dockerfile", "Shell", "PLpgSQL",
           "Makefile", "Procfile", "Batchfile", "PowerShell", "Jupyter Notebook"}

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    createdAt
    contributionsCollection { contributionCalendar { totalContributions } }
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, privacy: PUBLIC,
                 isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        pushedAt
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def graphql(token, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "User-Agent": f"{LOGIN}-profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def fetch():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("Set GH_TOKEN (GitHub Actions provides one automatically).")
    after, repos, user = None, [], None
    while True:
        user = graphql(token, {"login": LOGIN, "after": after})
        page = user["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    langs = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            entry = langs.setdefault(name, {"bytes": 0, "color": edge["node"]["color"] or "#8b949e"})
            entry["bytes"] += edge["size"]
    latest = repos[0] if repos else {"name": "-", "pushedAt": user["createdAt"]}
    return {
        "login": LOGIN,
        "repos": user["repositories"]["totalCount"],
        "contributions": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "created_at": user["createdAt"],
        "last_push": {"repo": latest["name"], "at": latest["pushedAt"]},
        "languages": langs,
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def nice_date(iso, fmt="%d %b %Y"):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime(fmt)


def render(d):
    W, x0, size = 880, 30, 15
    langs = sorted(((k, v) for k, v in d["languages"].items() if k not in EXCLUDE),
                   key=lambda kv: -kv[1]["bytes"])[:TOP_N]
    total = sum(v["bytes"] for _, v in langs) or 1

    top = 38 + 30
    tiles_y = top + 26
    tile_h = 76
    langs_y = tiles_y + tile_h + 44
    row_h = 26
    H = langs_y + 30 + len(langs) * row_h + 40

    svg = SVG(W, H, f"GitHub stats for {d['login']}")
    svg.window("stats.txt — auto-updated daily")
    svg.text(x0, top + 4, prompt_segments() + [(f"gh stats --user {d['login']}", TEXT)], size=size)

    tiles = [
        (f"{d['repos']}", "public repos"),
        (f"{d['contributions']:,}", "contributions (1y)"),
        (nice_date(d["created_at"], "%b %Y"), "on github since"),
        (nice_date(d["last_push"]["at"], "%d %b"), f"last push: {d['last_push']['repo']}"),
    ]
    gap = 12
    tw = (W - 2 * x0 - gap * (len(tiles) - 1)) / len(tiles)
    for i, (value, label) in enumerate(tiles):
        tx = x0 + i * (tw + gap)
        max_chars = int((tw - 32) / (11.5 * CHAR))
        if len(label) > max_chars:
            label = label[:max_chars - 1] + "…"
        svg.add(f'<rect x="{tx:.1f}" y="{tiles_y}" width="{tw:.1f}" height="{tile_h}" rx="10" fill="{FAINT}" fill-opacity=".6" stroke="#30363d"/>')
        svg.add(f'<rect x="{tx:.1f}" y="{tiles_y + 16}" width="3" height="{tile_h - 32}" rx="1.5" fill="{NEON}"/>')
        svg.text(tx + 18, tiles_y + 38, value, size=24, weight=800, fill=NEON)
        svg.text(tx + 18, tiles_y + 60, label, size=11.5, fill=MUTED)

    svg.text(x0, langs_y, prompt_segments() + [(f"gh langs --top {len(langs)}", TEXT)], size=size)
    cells, cell_w, cell_gap = 40, 9, 3
    label_w = width("TypeScript    ", 14)
    for r, (name, info) in enumerate(langs):
        y = langs_y + 26 + r * row_h
        pct = info["bytes"] / total * 100
        filled = max(1, round(pct / 100 * cells))
        color = vivid(info["color"])
        svg.text(x0 + 2, y + 11, name, size=14, fill=SOFT)
        bx = x0 + label_w
        for c in range(cells):
            cx = bx + c * (cell_w + cell_gap)
            if c < filled:
                # Fades in left to right; viewers without SMIL simply see the full bar.
                k = min(0.95, (0.25 + r * 0.12 + c * 0.025) / 2.6)
                svg.add(f'<rect x="{cx:.1f}" y="{y}" width="{cell_w}" height="14" rx="2" fill="{color}">'
                        f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="2.6s" fill="freeze"/></rect>')
            else:
                svg.add(f'<rect x="{cx:.1f}" y="{y}" width="{cell_w}" height="14" rx="2" fill="{FAINT}"/>')
        svg.text(bx + cells * (cell_w + cell_gap) + 14, y + 11, f"{pct:5.1f}%", size=14, weight=700, fill=TEXT)

    svg.text(x0, H - 22, [("↻ ", GREEN, 700), (f"refreshed {nice_date(d['updated'])} by GitHub Actions", MUTED)], size=12)
    return svg.save(ROOT / "assets" / "stats.svg")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--from-json":
        data = json.loads(Path(sys.argv[2]).read_text())
    else:
        data = fetch()
    print(render(data))
