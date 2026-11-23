#!/usr/bin/env python3
"""
email_harvest.py — passive email / staff harvesting from the target's own public
website (the OSINT theHarvester performs against web sources, done over HTTPS,
which works on this network).

Crawls a small, bounded set of in-scope pages on megacorpone.com and extracts:
  * email addresses (@megacorpone.com), and
  * the email naming convention (e.g. first-initial + surname).

Passive: reads only public web pages on the authorized target; no login, no
submission of data to third parties.

Usage:
    python scripts/email_harvest.py
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import OrderedDict
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "evidence", "web", "emails.json")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@megacorpone\.com", re.IGNORECASE)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

SEED_PAGES = [
    "https://www.megacorpone.com/",
    "https://www.megacorpone.com/contact.html",
    "https://www.megacorpone.com/about.html",
]


def load_scope() -> dict:
    with open(os.path.join(HERE, "scope.yaml"), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def in_scope(url: str, root_domain: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == root_domain or host.endswith("." + root_domain)


def crawl(root_domain: str, max_pages: int = 25) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent": "megacorpone-recon/1.0 (authorized OSINT training)"})
    seen: set[str] = set()
    queue = list(SEED_PAGES)
    emails: "OrderedDict[str, None]" = OrderedDict()
    pages_fetched = []

    while queue and len(pages_fetched) < max_pages:
        url = queue.pop(0)
        if url in seen or not in_scope(url, root_domain):
            continue
        seen.add(url)
        try:
            r = session.get(url, timeout=20)
        except requests.RequestException:
            continue
        pages_fetched.append({"url": url, "status": r.status_code})
        if "html" not in r.headers.get("Content-Type", "").lower():
            continue
        body = r.text
        for m in EMAIL_RE.findall(body):
            emails.setdefault(m.lower(), None)
        # enqueue in-scope same-site links (bounded)
        for href in HREF_RE.findall(body):
            nxt = urljoin(url, href)
            if nxt.split("#")[0] not in seen and in_scope(nxt, root_domain) and nxt.endswith((".html", "/")):
                queue.append(nxt.split("#")[0])
        time.sleep(0.2)

    return {"emails": list(emails.keys()), "pages": pages_fetched}


def infer_convention(emails: list[str]) -> str:
    locals_ = [e.split("@")[0] for e in emails]
    if not locals_:
        return "unknown"
    # Heuristic: mostly short (<=8) lowercase local parts with no separators
    if all("." not in l and "_" not in l for l in locals_) and all(len(l) <= 9 for l in locals_):
        return "likely {first-initial}{surname} (e.g. jdoe@megacorpone.com)"
    if any("." in l for l in locals_):
        return "likely {first}.{surname}@megacorpone.com"
    return "mixed / see samples"


def main() -> int:
    scope = load_scope()
    root = scope["scope"]["root_domain"]
    print(f"[emails] crawling public pages on {root} ...")
    data = crawl(root)
    emails = sorted(data["emails"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": root,
        "source": "target public website (HTTPS crawl)",
        "pages_fetched": len(data["pages"]),
        "emails_found": emails,
        "email_count": len(emails),
        "naming_convention": infer_convention(emails),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"[emails] pages fetched: {len(data['pages'])}")
    print(f"[emails] emails found : {len(emails)}")
    for e in emails:
        print(f"[emails]   {e}")
    print(f"[emails] convention   : {report['naming_convention']}")
    print(f"[emails] wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
