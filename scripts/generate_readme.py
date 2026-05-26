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

MATRIX_CHARS = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF"
MATRIX_COLORS = ["#ff0000", "#cc0000", "#990000", "#ff3333", "#ff6666"]


def build_matrix_rain():
    rng = random.Random(42)
    count = 35
    width = 800
    height = 80
    drops = []

    for i in range(count):
        x = rng.randint(10, width - 10)
        ch = rng.choice(MATRIX_CHARS)
        dur = round(rng.uniform(2.0, 4.5), 1)
        delay = round(rng.uniform(0, 5.0), 1)
        is_head = rng.random() < 0.25
        color = "#ff2222" if is_head else rng.choice(MATRIX_COLORS)
        weight = "bold" if is_head else "normal"
        start_y = rng.randint(-height - 20, -5)
        drops.append(
            f'<text x="{x}" y="{start_y}" fill="{color}"'
            f' font-weight="{weight}" font-size="13" font-family="monospace">'
            f'<animate attributeName="y" values="{start_y};{height + 20}"'
            f' dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'{ch}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#0d1117"/>
  {"".join(drops)}
</svg>"""


def fetch_json(url: str, token: str | None = None) -> dict | list | None:
    headers = {
        "Accept": "application/json",
        "User-Agent": "ElderEvil-profile-bot/1.0",
    }
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
    user_url = f"https://api.github.com/users/{GITHUB_USER}"
    user = fetch_json(user_url, token=token)
    if not isinstance(user, dict):
        return {}

    pr_count = 0
    issue_count = 0
    if token:
        pr_data = fetch_json(
            f"https://api.github.com/search/issues?q=author:{GITHUB_USER}+type:pr&per_page=1",
            token=token,
        )
        if isinstance(pr_data, dict):
            pr_count = pr_data.get("total_count", 0)

        issue_data = fetch_json(
            f"https://api.github.com/search/issues?q=author:{GITHUB_USER}+type:issue&per_page=1",
            token=token,
        )
        if isinstance(issue_data, dict):
            issue_count = issue_data.get("total_count", 0)

    return {
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "created_at": user.get("created_at", ""),
        "pr_count": pr_count,
        "issue_count": issue_count,
    }


def build_terminal_section(stats: dict):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    years_active = ""
    if stats.get("created_at"):
        joined = datetime.datetime.fromisoformat(stats["created_at"].replace("Z", "+00:00"))
        years_active = str((datetime.datetime.now(datetime.timezone.utc) - joined).days // 365)

    repos = stats.get("public_repos", "?")
    prs = stats.get("pr_count", "?")
    issues = stats.get("issue_count", "?")
    followers = stats.get("followers", "?")
    since = years_active or "?"
    return f"""\x60\x60\x60
╭──────────────────────────────────────────────────────╮
│  ELDEREVIL@evillab.tech                    {now[:10]}  │
├──────────────────────────────────────────────────────┤
│  > whoami                                            │
│  Elder.Evil · 33 · Kharkiv, Ukraine · UTC+3          │
│                                                      │
│  > pwd                                               │
│  /home/elder                                         │
│                                                      │
│  > ls ~/skills/                                      │
│  Python  FastAPI  Pytest  Wagtail  Django  Docker    │
│  Kubernetes  Shell  Bazzite  k3s  Ansible            │
│                                                      │
│  > cat ~/interests.txt                               │
│  Python projects · self-hosting · homelab            │
│  automation · k3s · immutable Linux                  │
│                                                      │
│  > gh stats                                          │
│  repos: {repos:<3}  prs: {prs:<3}  issues: {issues:<3}            │
│  followers: {followers:<3}  github since: {since} years          │
╰──────────────────────────────────────────────────────╯
\x60\x60\x60"""


def build_contribution_section():
    return f"""<div align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username={GITHUB_USER}&theme=github_dark" alt="Contribution Graph" />
</div>"""


def build_footer():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""---
<div align="center">
  <sub><code>~ $ _</code> · last updated: {now}</sub>
</div>"""


def main():
    print("[info] Fetching GitHub data...")
    stats = fetch_user_stats()
    repos = fetch_github_repos()

    sections = [
        f'<div align="center">{build_matrix_rain()}</div>',
        build_terminal_section(stats),
        build_contribution_section(),
        build_footer(),
    ]

    readme_content = "\n\n".join(s for s in sections if s.strip())
    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"[done] README written to {README_PATH}")


if __name__ == "__main__":
    main()
