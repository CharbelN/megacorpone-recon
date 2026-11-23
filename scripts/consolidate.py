#!/usr/bin/env python3
"""
consolidate.py — merge every tool's evidence into one report: results/recon.json
and a short results/summary.md. Each data point keeps its source so you can see
which tool/agent produced it.

Usage:
    python scripts/consolidate.py
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
EV = os.path.join(ROOT, "evidence")


def load(path, default=None):
    full = os.path.join(EV, path)
    if not os.path.exists(full):
        return default
    with open(full, "r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_axfr_hosts(txt_path):
    hosts = {}
    full = os.path.join(EV, txt_path)
    if not os.path.exists(full):
        return hosts
    for line in open(full, "r", encoding="utf-8"):
        m = re.match(r"(\S+megacorpone\.com)\.\s+\d+\s+IN\s+A\s+(\d+\.\d+\.\d+\.\d+)", line.strip())
        if m:
            hosts[m.group(1)] = m.group(2)
    return hosts


def main() -> int:
    dns = load("dns/dns_enum.json", {})
    subs = load("crtsh/subdomains.json", {})
    emails = load("web/emails.json", {})
    axfr_hosts = parse_axfr_hosts("dns/zone_transfer_axfr.txt")

    # merge subdomains from every source, tracking provenance
    provenance: dict[str, set] = {}
    for h in axfr_hosts:
        provenance.setdefault(h, set()).add("zone-transfer")
    for h in dns.get("subdomains_from_axfr", []):
        provenance.setdefault(h, set()).add("zone-transfer")
    for h in subs.get("crtsh_subdomains", []):
        provenance.setdefault(h, set()).add("crt.sh")
    for h in subs.get("resolved_subdomains", {}):
        provenance.setdefault(h, set()).add("resolver-bruteforce")

    subdomains = []
    for host in sorted(provenance):
        subdomains.append({
            "host": host,
            "ip": axfr_hosts.get(host),
            "sources": sorted(provenance[host]),
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": "megacorpone.com",
        "dns_records": dns.get("records", {}),
        "nameservers": dns.get("records", {}).get("NS", []),
        "mail_servers": dns.get("records", {}).get("MX", []),
        "zone_transfer": {
            "allowed_by_target": bool(axfr_hosts),
            "obtained_via": "https vantage point (local TCP/53 blocked by carrier)",
            "host_count": len(axfr_hosts),
        },
        "subdomains": subdomains,
        "subdomain_count": len(subdomains),
        "emails": emails.get("emails_found", []),
        "email_convention": emails.get("naming_convention"),
        "sources": {
            "dns_records": "scripts/dns_enum.py (dnspython via system resolver)",
            "zone_transfer": "scripts/dns_enum.py HTTPS fallback (hackertarget)",
            "subdomains": "scripts/subdomain_enum.py (crt.sh + resolver brute force)",
            "emails": "scripts/email_harvest.py (target website HTTPS crawl)",
            "github": "evidence/github/ (gh search)",
            "google_dorks": "evidence/dorks/google-dorks.md",
        },
    }

    out = os.path.join(ROOT, "results", "recon.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"[consolidate] subdomains: {report['subdomain_count']}")
    print(f"[consolidate] emails    : {len(report['emails'])}")
    print(f"[consolidate] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
