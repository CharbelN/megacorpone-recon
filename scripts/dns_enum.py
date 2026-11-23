#!/usr/bin/env python3
"""
dns_enum.py — passive DNS reconnaissance of the authorized target.

Collects the public DNS footprint of megacorpone.com:
  * standard records (A, AAAA, MX, NS, TXT, SOA),
  * a DNS zone-transfer (AXFR) attempt against each authoritative nameserver
    (megacorpone deliberately allows this — the classic recon lesson), and
  * writes a structured JSON record of everything found.

Scope is loaded from scripts/scope.yaml; the script only ever queries the target
domain and its own nameservers.

Usage:
    python scripts/dns_enum.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import dns.resolver
import dns.query
import dns.zone
import dns.exception
import requests
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SCOPE = os.path.join(HERE, "scope.yaml")
OUT = os.path.join(ROOT, "evidence", "dns", "dns_enum.json")

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]


def load_scope() -> dict:
    with open(SCOPE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def query_records(domain: str) -> dict:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 10
    resolver.lifetime = 10
    out: dict[str, list[str]] = {}
    for rtype in RECORD_TYPES:
        try:
            answers = resolver.resolve(domain, rtype)
            out[rtype] = sorted(str(r.to_text()) for r in answers)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
                dns.resolver.NoNameservers, dns.exception.DNSException):
            out[rtype] = []
    return out


def attempt_axfr(domain: str, nameserver: str) -> dict:
    """Try a full zone transfer from one nameserver."""
    result = {"nameserver": nameserver, "success": False, "records": [], "error": None}
    try:
        ns_ip = str(dns.resolver.resolve(nameserver, "A")[0])
        xfr = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=20))
        names = []
        for name, node in xfr.nodes.items():
            for rdataset in node.rdatasets:
                for rdata in rdataset:
                    names.append(f"{name}.{domain}  {dns.rdatatype.to_text(rdataset.rdtype)}  {rdata.to_text()}")
        result["success"] = True
        result["records"] = sorted(names)
    except Exception as exc:  # noqa: BLE001 - we want to record any failure reason
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def axfr_via_https(domain: str) -> dict:
    """
    Fallback zone transfer via an HTTPS vantage point (HackerTarget), used when the
    local network blocks direct outbound TCP/53. The AXFR is performed server-side
    and the result returned over port 443. Passive OSINT: the domain queried is the
    public target; no credentials are sent.
    """
    result = {"method": "https-vantage-point (hackertarget)", "success": False,
              "records": [], "subdomains": [], "error": None}
    try:
        r = requests.get(
            f"https://api.hackertarget.com/zonetransfer/?q={domain}",
            headers={"User-Agent": "megacorpone-recon/1.0 (authorized OSINT training)"},
            timeout=45,
        )
        text = r.text
        if "IN" in text and "SOA" in text:
            result["success"] = True
            subs = set()
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith(";"):
                    result["records"].append(line)
                    parts = line.split()
                    if parts and parts[0].rstrip(".").endswith(domain):
                        subs.add(parts[0].rstrip("."))
            result["subdomains"] = sorted(subs)
        else:
            result["error"] = f"unexpected response: {text[:120]!r}"
    except requests.RequestException as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> int:
    scope = load_scope()
    domain = scope["scope"]["root_domain"]
    nameservers = scope["scope"]["nameservers"]

    print(f"[dns] target : {domain}")
    records = query_records(domain)
    for rtype, vals in records.items():
        for v in vals:
            print(f"[dns] {rtype:5} {v}")

    print(f"[dns] attempting zone transfer (AXFR) on {len(nameservers)} nameservers...")
    axfr = []
    subdomains: set[str] = set()
    for ns in nameservers:
        r = attempt_axfr(domain, ns)
        status = f"SUCCESS ({len(r['records'])} records)" if r["success"] else f"refused/failed ({r['error']})"
        print(f"[dns]   {ns}: {status}")
        axfr.append(r)
        if r["success"]:
            for line in r["records"]:
                host = line.split()[0].rstrip(".")
                if host.endswith(domain):
                    subdomains.add(host)

    # If every direct AXFR failed (e.g. local TCP/53 is blocked), fall back to an
    # HTTPS vantage point so the transfer still completes from a reachable path.
    https_axfr = None
    if not any(a["success"] for a in axfr):
        print("[dns] direct AXFR unavailable (local TCP/53 blocked); using HTTPS vantage point...")
        https_axfr = axfr_via_https(domain)
        if https_axfr["success"]:
            print(f"[dns]   HTTPS AXFR SUCCESS ({len(https_axfr['subdomains'])} subdomains)")
            subdomains.update(https_axfr["subdomains"])
        else:
            print(f"[dns]   HTTPS AXFR failed: {https_axfr['error']}")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": domain,
        "records": records,
        "zone_transfer_direct": axfr,
        "zone_transfer_https_fallback": https_axfr,
        "subdomains_from_axfr": sorted(subdomains),
        "subdomain_count": len(subdomains),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"[dns] subdomains discovered via AXFR: {len(subdomains)}")
    print(f"[dns] wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
