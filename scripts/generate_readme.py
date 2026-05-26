#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
import datetime
from pathlib import Path


GITHUB_USER = "ElderEvil"
README_PATH = Path(__file__).resolve().parent.parent / "README.md"

HEADER = """<div align="center">
  <a href="https://evillab.tech">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=28&pause=1000&color=58A6FF&center=true&vCenter=true&width=500&lines=Elder.Evil;Python+Developer;FastAPI+%26+Pytest+Learner;Homelab+Enthusiast;blog.evillab.tech" alt="Typing SVG" />
  </a>
  <br/>
  <a href="https://evillab.tech"><sup>evillab.tech</sup></a>
  <br/><br/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" />
</div>
"""

ABOUT_SECTION = """
```yaml
location: Kharkiv, Ukraine
timezone: UTC+3
learning: FastAPI, Pytest, Wagtail
interests: Python, self-hosting, homelab, k3s, automation
site: https://evillab.tech
```
"""


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


def build_repos_section(repos):
    top = [r for r in repos if not r.get("fork") and r.get("stargazers_count", 0) > 0][:6]
    if not top:
        return ""

    lines = [
        "## Popular Repositories",
        "",
        '<div align="center">',
    ]
    for repo in top:
        name = repo.get("name", "")
        lines.append(
            f'<a href="https://github.com/{GITHUB_USER}/{name}">'
            f'<img src="https://github-readme-stats.vercel.app/api/pin/?username={GITHUB_USER}&repo={name}&theme=github_dark&hide_border=true" '
            f'alt="{name}" /></a>'
        )
    lines.append("</div>")
    lines.append("")
    return "\n".join(lines)


def build_stats_section():
    return f"""## GitHub Analytics

<div align="center">
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/stats?username={GITHUB_USER}&theme=github_dark" alt="Stats" />
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username={GITHUB_USER}&theme=github_dark" alt="Languages by Repo" />
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/most-commit-language?username={GITHUB_USER}&theme=github_dark" alt="Languages by Commit" />
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username={GITHUB_USER}&theme=github_dark" alt="Profile Details" />
</div>

<div align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user={GITHUB_USER}&theme=github_dark&hide_border=true" alt="GitHub Streak" />
</div>
"""


def build_footer():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""---

<details>
<summary><b>Activity Graph</b></summary>
<br/>
<img src="https://github-readme-activity-graph.vercel.app/graph?username={GITHUB_USER}&theme=github-dark&hide_border=true&area=true" alt="Activity Graph" />
</details>

<div align="center">
  <sub>Last updated: {now}</sub>
</div>
"""


def main():
    print("[info] Fetching GitHub data...")
    repos = fetch_github_repos()

    sections = [
        HEADER,
        ABOUT_SECTION,
        build_stats_section(),
        build_repos_section(repos),
        build_footer(),
    ]

    readme_content = "\n\n".join(s for s in sections if s.strip())
    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"[done] README written to {README_PATH}")


if __name__ == "__main__":
    main()
