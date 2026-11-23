#!/usr/bin/env python3
"""
subdomain_enum.py — discover megacorpone.com subdomains from sources that work
without a DNS zone transfer:

  1. crt.sh certificate-transparency logs (HTTPS, passive, no auth), and
  2. UDP-based resolution of a common-subdomain wordlist (confirms which names
     actually resolve, and to which IP).

Both are passive OSINT. Output: evidence/crtsh/subdomains.json.

Usage:
    python scripts/subdomain_enum.py
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

import requests
import dns.resolver
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "evidence", "crtsh", "subdomains.json")

# A compact, common-subdomain wordlist for confirmation by resolution.
WORDLIST = [
    "www", "www2", "mail", "mail2", "smtp", "pop", "imap", "webmail", "ns1", "ns2",
    "ns3", "admin", "intranet", "vpn", "remote", "portal", "beta", "dev", "test",
    "staging", "router", "fw", "firewall", "siem", "snmp", "syslog", "support",
    "help", "secret", "internal", "ftp", "git", "gitlab", "jira", "wiki", "blog",
    "shop", "store", "api", "app", "dashboard", "monitor", "nagios", "proxy",
]


def load_scope() -> dict:
    with open(os.path.join(HERE, "scope.yaml"), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def from_crtsh(domain: str) -> list[str]:
    """Certificate-transparency subdomains via crt.sh (with retries — it is flaky)."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    headers = {"User-Agent": "megacorpone-recon/1.0 (authorized OSINT training)"}
    for attempt in range(4):
        try:
            r = requests.get(url, headers=headers, timeout=45)
            if r.status_code == 200 and r.text.strip().startswith("["):
                data = r.json()
                names = set()
                for entry in data:
                    for n in entry.get("name_value", "").split("\n"):
                        n = n.strip().lower().lstrip("*.")
                        if n.endswith(domain):
                            names.add(n)
                return sorted(names)
        except (requests.RequestException, ValueError):
            pass
        time.sleep(3 * (attempt + 1))
    return []


def resolve_wordlist(domain: str) -> dict:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5
    found = {}
    for word in WORDLIST:
        host = f"{word}.{domain}"
        try:
            answers = resolver.resolve(host, "A")
            found[host] = sorted(str(a) for a in answers)
        except dns.exception.DNSException:
            continue
    return found


def main() -> int:
    scope = load_scope()
    domain = scope["scope"]["root_domain"]

    print(f"[subenum] crt.sh certificate transparency for {domain} ...")
    crt = from_crtsh(domain)
    print(f"[subenum] crt.sh unique names: {len(crt)}")
    for s in crt:
        print(f"[subenum]   crt.sh  {s}")

    print(f"[subenum] resolving {len(WORDLIST)} common subdomains (UDP) ...")
    resolved = resolve_wordlist(domain)
    for host, ips in sorted(resolved.items()):
        print(f"[subenum]   resolve {host} -> {', '.join(ips)}")

    all_subs = sorted(set(crt) | set(resolved.keys()))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": domain,
        "crtsh_subdomains": crt,
        "resolved_subdomains": resolved,
        "all_subdomains": all_subs,
        "counts": {
            "crtsh": len(crt),
            "resolved_bruteforce": len(resolved),
            "combined_unique": len(all_subs),
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"[subenum] combined unique subdomains: {len(all_subs)}")
    print(f"[subenum] wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
