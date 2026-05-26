#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import random
import urllib.request
import urllib.error
import datetime
from pathlib import Path


GITHUB_USER = "ElderEvil"
README_PATH = Path(__file__).resolve().parent.parent / "README.md"
OUTER = 54  # total line width including box borders
# format: " │<INNER content> │"  →  prefix 3 + content + suffix 2 = OUTER
INNER = OUTER - 5  # 49 chars between the │ symbols


def build_matrix_banner():
    rng = random.Random(42)
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF"
    streaks = []

    for col in range(16):
        x = 20 + col * 48
        length = rng.randint(3, 6)
        top_bright = rng.choice(["#ff2222", "#ff0000"])
        colors = ["#ff0000", "#cc0000", "#990000", "#660000", "#330000"]
        for i in range(length):
            y = rng.randint(10, 70)
            opacity = max(0.15, 1.0 - i * 0.2)
            color = top_bright if i == 0 else rng.choice(colors[1:])
            ch = rng.choice(chars)
            weight = "bold" if i == 0 else "normal"
            streaks.append(
                f'<text x="{x}" y="{y + i * 16}" fill="{color}"'
                f' font-weight="{weight}" font-size="14" font-family="monospace"'
                f' opacity="{opacity:.1f}">{ch}</text>'
            )

    return f"""<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="780" height="90" viewBox="0 0 780 90">
  <rect width="780" height="90" fill="#0d1117" rx="6"/>
  {"".join(streaks)}
</svg>
</div>"""


def fetch_json(url: str, token: str | None = None) -> dict | list | None:
    headers = {"Accept": "application/json", "User-Agent": "ElderEvil-profile-bot/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token.removeprefix('Bearer ')}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError) as e:
        print(f"[warn] Failed to fetch {url}: {e}")
        return None


def fetch_github_repos():
    token = os.environ.get("GITHUB_TOKEN")
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?sort=updated&per_page=100&type=owner"
    data = fetch_json(url, token=token)
    if not isinstance(data, list):
        return []
    data.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
    return data


def fetch_user_stats():
    token = os.environ.get("GITHUB_TOKEN")
    user = fetch_json(f"https://api.github.com/users/{GITHUB_USER}", token=token)
    if not isinstance(user, dict):
        return {}
    pr_count = issue_count = 0
    if token:
        pr = fetch_json(
            f"https://api.github.com/search/issues?q=author:{GITHUB_USER}+type:pr&per_page=1", token=token
        )
        if isinstance(pr, dict):
            pr_count = pr.get("total_count", 0)
        iss = fetch_json(
            f"https://api.github.com/search/issues?q=author:{GITHUB_USER}+type:issue&per_page=1", token=token
        )
        if isinstance(iss, dict):
            issue_count = iss.get("total_count", 0)
    return {
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "created_at": user.get("created_at", ""),
        "pr_count": pr_count,
        "issue_count": issue_count,
    }


def pad(s: str, w: int) -> str:
    """Left-align string s in field of width w."""
    s = str(s)
    return s + " " * (w - len(s))


def build_fastfetch(stats: dict):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    years = ""
    if stats.get("created_at"):
        joined = datetime.datetime.fromisoformat(stats["created_at"].replace("Z", "+00:00"))
        years = str((datetime.datetime.now(datetime.timezone.utc) - joined).days // 365)

    repos = stats.get("public_repos", "?")
    prs = stats.get("pr_count", "?")
    issues = stats.get("issue_count", "?")
    followers = stats.get("followers", "?")
    since = years or "?"

    dash = "─" * (OUTER - 3)
    l1 = f" OS       {pad('Bazzite Linux 41 (x86_64)', 20)}"
    l2 = f" Location {pad('Kharkiv, Ukraine', 20)}"
    l3 = f" Timezone {pad('UTC+3', 20)}"
    l4 = f" Skills   {pad('Python  FastAPI  Pytest', 20)}"
    l5 = f"          {pad('Wagtail  Django  Docker  K8s', 20)}"
    l6 = f" Blog     {pad('evillab.tech', 20)}"

    repo_line = f" repos {pad(repos, 3)}   PRs {pad(prs, 3)}   issues {pad(issues, 3)}"
    stats_line = f" stars 0     since {pad(since, 2)} years   followers {pad(followers, 2)}"

    box = [
        "```",
        f" ┌{dash}┐",
        f" │ {pad('elderevil@evillab.tech', INNER)} │",
        f" ├{dash}┤",
        f" │ {pad(l1, INNER)} │",
        f" │ {pad(l2, INNER)} │",
        f" │ {pad(l3, INNER)} │",
        f" │ {pad(l4, INNER)} │",
        f" │ {pad(l5, INNER)} │",
        f" │ {pad(l6, INNER)} │",
        f" ├{dash}┤",
        f" │ {pad('GitHub Stats', INNER)} │",
        f" │ {pad('─' * (INNER - 2), INNER)} │",
        f" │ {pad(repo_line, INNER)} │",
        f" │ {pad(stats_line, INNER)} │",
        f" └{dash}┘",
        "```",
    ]
    return "\n".join(box)


def build_contribution():
    return f"""<div align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username={GITHUB_USER}&theme=github_dark" alt="Contribution Graph" />
</div>"""


def build_footer():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""---
<p align="center"><sub><code>~ $ _</code> · {now}</sub></p>"""


def main():
    print("[info] Fetching GitHub data...")
    stats = fetch_user_stats()

    sections = [
        build_matrix_banner(),
        build_fastfetch(stats),
        build_contribution(),
        build_footer(),
    ]

    readme_content = "\n\n".join(s for s in sections if s.strip())
    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"[done] README written to {README_PATH}")


if __name__ == "__main__":
    main()
