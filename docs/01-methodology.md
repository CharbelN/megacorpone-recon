# 01 — Methodology

Passive reconnaissance of `megacorpone.com`, in two tracks the assignment defines:

1. **Manual recon** with web OSINT services — DNSDumpster, GitHub, Postman, Hunter.io,
   Have I Been Pwned, Google dorks. See [`02-manual-recon.md`](02-manual-recon.md).
2. **Kali tooling** — theHarvester and dnsrecon (Katoolin / Kali container). See
   [`03-kali-tools.md`](03-kali-tools.md).

Everything is reproducible: the repo ships small scripts that perform the collection over
paths that work on a restricted network, each labelled with the tool it stands in for.

## Recon flow

```
scope (scripts/scope.yaml)
  ├─ DNS footprint            → scripts/dns_enum.py        (A/MX/NS/TXT/SOA + AXFR)
  ├─ Subdomain discovery      → scripts/subdomain_enum.py  (crt.sh + resolver brute force)
  ├─ Email / staff harvest    → scripts/email_harvest.py   (target website)
  ├─ GitHub exposure          → gh search                  (evidence/github/)
  ├─ Google dorks             → evidence/dorks/             (curated query set)
  ├─ Kali tools               → theHarvester / dnsrecon     (docs/03)
  └─ consolidate              → scripts/consolidate.py      (results/recon.json)
```

## OSINT framework mapping

| Activity | OSINT category | Output |
|----------|----------------|--------|
| DNS records & zone transfer | Infrastructure / DNS | subdomains, IPs, mail & name servers |
| Certificate transparency | Infrastructure | historic/active subdomains |
| Email & staff harvesting | People / social | addresses, naming convention, surnames |
| GitHub & Google dorks | Exposed assets | leaked references, documents, portals |

## Which tool produced which result

Every result is attributed. The consolidated [`results/recon.json`](../results/recon.json)
records a `sources` map and per-subdomain `sources` list; each `evidence/<tool>/` folder
holds that tool's raw output; and [`04-findings.md`](04-findings.md) carries the summary
with attribution. This satisfies the assignment's instruction to *"clearly label which
tool or agent produced each result."*

## The agent

The "favorite agent" running the tools here is **Claude Code** (this assistant), acting as
the recon operator: it drove the scripts, the GitHub search, and the analysis, staying
inside `scope.yaml`. The Kali-container path for running the same agent against an
unrestricted network is documented in [`03-kali-tools.md`](03-kali-tools.md).
