# Reconnaissance — megacorpone.com

Passive OSINT reconnaissance of **`megacorpone.com`** — Offensive Security's public
reconnaissance training target — using the assignment's web tools (DNSDumpster, GitHub,
Postman, Hunter.io, Have I Been Pwned, Google dorks) and Kali tooling (theHarvester,
dnsrecon), driven by an AI agent (Claude Code). Every result is labelled with the tool
that produced it.

> **Passive only.** Reads public information (DNS, certificate transparency, the target's
> own website, search indexes, public code). No accounts, systems, or private data are
> accessed. See [`docs/00-rules-of-engagement.md`](docs/00-rules-of-engagement.md).

---

## 1. The assignment, and where each part is answered

| Requirement | How it was done | Where |
|---|---|---|
| **DNSDumpster** (DNS/infra map) | Full DNS footprint + **zone transfer** (AXFR) | [`scripts/dns_enum.py`](scripts/dns_enum.py), [`docs/02`](docs/02-manual-recon.md), [`evidence/dns/`](evidence/dns) |
| **Hunter.io** (emails) | Harvested emails + naming convention from the target site (no key used) | [`scripts/email_harvest.py`](scripts/email_harvest.py), [`evidence/web/emails.json`](evidence/web/emails.json) |
| **GitHub** (code exposure) | `gh search` repos + code referencing the domain | [`evidence/github/`](evidence/github), [`docs/02`](docs/02-manual-recon.md) |
| **Google dorks** | Curated 16-dork query set, scoped | [`evidence/dorks/google-dorks.md`](evidence/dorks/google-dorks.md) |
| **Postman** (public APIs) | Public-workspace search — documented negative | [`docs/02`](docs/02-manual-recon.md) |
| **Have I Been Pwned** | Method documented; not run (no key, not domain owner) | [`docs/02`](docs/02-manual-recon.md) |
| **theHarvester** (Kali) | OSINT harvesting; equivalent run + ready Kali command | [`docs/03`](docs/03-kali-tools.md) |
| **dnsrecon** (Kali) | Run locally via a Py3.14 shim; records/AXFR captured via working paths | [`scripts/run_dnsrecon.py`](scripts/run_dnsrecon.py), [`docs/03`](docs/03-kali-tools.md) |
| **Run with an agent on Linux/Kali container** | Agent = Claude Code; Kali/Katoolin container path documented | [`docs/03`](docs/03-kali-tools.md) |
| **Label which tool produced each result** | Per-source attribution in evidence + consolidated report | [`results/recon.json`](results/recon.json), [`docs/04`](docs/04-findings.md) |

---

## 2. Results

Full write-up: [`docs/04-findings.md`](docs/04-findings.md) · machine-readable
[`results/recon.json`](results/recon.json).

- **23 hosts** mapped with IPs (the full internal naming scheme) via **DNS zone transfer**,
  corroborated by crt.sh + resolver brute force — including the VPN estate
  (`vpn/vpn2/vpndev/vpnprod`) and management plane (`admin`, `router`, `siem`, `snmp`, `syslog`).
- **9 emails** and the **`{first-initial}{surname}`** convention (e.g. `msmith` = M. Smith).
- **MX:** hybrid Gandi + self-hosted `mail`/`mail2`. **TXT:** `"Try Harder"` + a Google
  Workspace verification token. Hosting in **OVHcloud** ranges.
- **GitHub:** official source repo is public; 30 code hits reference the domain (mostly OSCP notes).

The **zone transfer is the headline finding** — the target's nameservers are deliberately
misconfigured to allow AXFR, handing over the entire internal host list (including 4 hosts
the wordlist brute force missed) in one request.

---

## 3. Reproduce it

```bash
pip install -r requirements.txt

python scripts/dns_enum.py          # A/MX/NS/TXT/SOA + zone transfer (AXFR)
python scripts/subdomain_enum.py    # crt.sh + resolver brute force
python scripts/email_harvest.py     # emails + naming convention from the site
python scripts/run_dnsrecon.py -d megacorpone.com -t std   # dnsrecon (Py3.14 shim)
python scripts/consolidate.py       # merge everything -> results/recon.json
```

GitHub recon: `gh search repos megacorpone` / `gh search code "megacorpone.com"`.
Kali tools on an unrestricted network: see [`docs/03-kali-tools.md`](docs/03-kali-tools.md).

---

## 4. Environment note (honest disclosure)

Collection ran from a **mobile-hotspot** workstation whose **carrier blocks all direct
outbound port 53** (diagnosed: not the local firewall, not a VPN — upstream). So:
- Direct DNS zone transfer (TCP/53) couldn't leave the machine; it was completed via an
  **HTTPS vantage point** instead (same real zone data).
- `dnsrecon`/`theHarvester` have **Python 3.14** incompatibilities; handled with a shim
  (dnsrecon) and an equivalent HTTPS-based harvest (theHarvester), with ready-to-run Kali
  commands for an unrestricted environment.

No security control on the workstation was disabled — the block is at the carrier. Details
in [`docs/03-kali-tools.md`](docs/03-kali-tools.md).

---

## 5. Repository map

```
.
├── README.md
├── scripts/
│   ├── scope.yaml            ← target allowlist (passive-only rules)
│   ├── dns_enum.py           ← DNS records + zone transfer (HTTPS fallback)
│   ├── subdomain_enum.py     ← crt.sh + resolver brute force
│   ├── email_harvest.py      ← emails + naming convention (target site)
│   ├── run_dnsrecon.py       ← dnsrecon wrapper (Python 3.14 shim)
│   └── consolidate.py        ← merge evidence -> results/recon.json
├── docs/ 00-rules-of-engagement · 01-methodology · 02-manual-recon · 03-kali-tools · 04-findings
├── evidence/ dns · crtsh · web · github · dorks   (raw output, labelled by tool)
└── results/ recon.json
```

## Ethics & authorization

`megacorpone.com` is published by OffSec specifically to be enumerated for training. All
recon here is passive; no credentials were submitted to any third-party service and no real
secrets or private data are published. Using these methods against systems you are not
authorized to test is illegal. See [`docs/00-rules-of-engagement.md`](docs/00-rules-of-engagement.md).

## License

[MIT](LICENSE).
