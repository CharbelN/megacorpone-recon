# 03 — Kali Tooling (theHarvester, dnsrecon) + the agent

The assignment's second track: extend recon in Kali (Katoolin / container) with
**theHarvester** and **dnsrecon**, and run it with an agent.

## What the agent is

The "favorite agent" here is **Claude Code**, driving the tools and scripts as the recon
operator, constrained to `scope.yaml`. Below is both (a) what was actually run on this
workstation and (b) the ready-to-run Kali-container path for an unrestricted network.

---

## dnsrecon

**Role:** scripted DNS enumeration — records, zone transfer, subdomain brute force.

**Run here:** `scripts/run_dnsrecon.py` (a thin wrapper) runs the real `dnsrecon` on this
machine. Two environment quirks had to be handled honestly:

1. **Python 3.14 compatibility.** `dnsrecon 0.10.1` imports `urllib.request.FancyURLopener`,
   which **Python 3.14 removed**. The wrapper installs a minimal inert stub so dnsrecon
   imports and runs (the class was only used by its unused Bing module).
2. **Carrier port-53 block.** dnsrecon queries the authoritative nameservers **directly**
   on port 53; this workstation is on a mobile hotspot whose carrier blocks all direct
   outbound port 53, so those queries time out. Console evidence:
   [`../evidence/dns/dnsrecon_console.txt`](../evidence/dns/dnsrecon_console.txt).

   The data dnsrecon would return is captured over working paths instead
   (`dns_enum.py`: records via the system resolver, zone transfer via an HTTPS vantage
   point) — see [`../evidence/dns/dns_enum.json`](../evidence/dns/dns_enum.json).

**Equivalent Kali command (unrestricted network):**
```bash
dnsrecon -d megacorpone.com -t std,axfr,brt -D /usr/share/wordlists/dnsrecon/subdomains-top1mil.txt -j dnsrecon.json
```

## theHarvester

**Role:** aggregate subdomains, emails, and hosts from many public OSINT sources.

**Run here:** theHarvester v4 declares `requires-python < 3.14`, so it **cannot install on
this workstation's Python 3.14** (pip resolves only to an unrelated v0.0.1 stub). Rather
than pull a multi-GB image on a metered mobile link, the **same OSINT theHarvester performs
over HTTPS** was collected by the repo's scripts and labelled as the equivalent:

| theHarvester capability | Equivalent here | Evidence |
|-------------------------|-----------------|----------|
| subdomains (crt.sh, hackertarget, …) | `subdomain_enum.py`, `dns_enum.py` | `evidence/crtsh/`, `evidence/dns/` |
| emails | `email_harvest.py` | `evidence/web/emails.json` |
| hosts/IPs | zone transfer + resolution | `evidence/dns/` |

**Equivalent Kali command (unrestricted network):**
```bash
theHarvester -d megacorpone.com -b crtsh,hackertarget,rapiddns,certspotter,otx,duckduckgo -f theharvester
```

---

## Katoolin / Kali container setup (reference)

To run the real tools on a compatible, unrestricted environment:

**Option A — Kali Docker container** (per the assignment):
```bash
docker run -it --rm linuxserver/kali-linux /bin/bash
apt update && apt install -y theharvester dnsrecon
theHarvester -d megacorpone.com -b all
dnsrecon  -d megacorpone.com -t std,axfr
```

**Option B — Katoolin on a Debian/Ubuntu box** (installs Kali tool categories):
```bash
git clone https://github.com/LionSec/katoolin && sudo python katoolin.py
# choose: Information Gathering → install theHarvester, dnsrecon
```

> Note: a container on **this** workstation would share the host's network, so the carrier
> port-53 block would still stop direct AXFR from inside it. theHarvester (HTTPS sources)
> *would* work in a container; it was run in equivalent form locally to respect the metered
> connection. On any network that allows port 53, both tools run as shown above.
