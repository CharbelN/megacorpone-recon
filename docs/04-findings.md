# 04 — Findings (consolidated)

Passive recon of `megacorpone.com`, 2026-11-23. Machine-readable:
[`../results/recon.json`](../results/recon.json). Every row is attributed to the tool that
produced it.

## Headline

- **23 hosts** mapped (22 subdomains + apex), with IPs — via **DNS zone transfer** (the
  target allows AXFR), corroborated by crt.sh and resolver brute force.
- **9 email addresses** + the **`{first-initial}{surname}`** naming convention.
- Hosting concentrated in **OVHcloud** ranges (`167.114.21.64–79`, `149.56.244.87`,
  `51.x`/`66.x` for nameservers).
- Notable attack-surface hosts: `vpn`, `vpn2`, `vpndev`, `vpnprod`, `intranet`, `admin`,
  `router`, `siem`, `snmp`, `syslog`, `test`, `beta`.

## DNS footprint — `dns_enum.py`

| Type | Value |
|------|-------|
| A | `149.56.244.87` |
| NS | `ns1 / ns2 / ns3 .megacorpone.com` |
| MX | `10 fb.mail.gandi.net` · `20 spool.mail.gandi.net` · `50 mail.megacorpone.com` · `60 mail2.megacorpone.com` |
| TXT | `"Try Harder"` · `google-site-verification=U7B_b0HNeBtY4qYGQZNsEYXfCJ32hMNV3GtC0wWq5pA` |
| SOA | `ns1.megacorpone.com admin.megacorpone.com` (serial `202508051`) |

**Mail:** hybrid — Gandi handles primary MX, with self-hosted `mail`/`mail2` as lower
priority. **TXT** reveals a Google Workspace site-verification token (Google services in use).

## Hosts / subdomains (23) — zone transfer + crt.sh + resolver

| Host | IP | Sources |
|------|----|---------|
| admin.megacorpone.com | 167.114.21.64 | resolver-bruteforce, zone-transfer |
| ai.megacorpone.com | 149.56.244.87 | crt.sh, zone-transfer |
| beta.megacorpone.com | 167.114.21.65 | resolver-bruteforce, zone-transfer |
| fs1.megacorpone.com | 167.114.21.66 | zone-transfer |
| intranet.megacorpone.com | 167.114.21.67 | resolver-bruteforce, zone-transfer |
| mail.megacorpone.com | 167.114.21.68 | resolver-bruteforce, zone-transfer |
| mail2.megacorpone.com | 167.114.21.69 | resolver-bruteforce, zone-transfer |
| ns1.megacorpone.com | 51.79.37.18 | resolver-bruteforce, zone-transfer |
| ns2.megacorpone.com | 51.222.39.63 | resolver-bruteforce, zone-transfer |
| ns3.megacorpone.com | 66.70.207.180 | resolver-bruteforce, zone-transfer |
| router.megacorpone.com | 167.114.21.70 | resolver-bruteforce, zone-transfer |
| siem.megacorpone.com | 167.114.21.71 | resolver-bruteforce, zone-transfer |
| snmp.megacorpone.com | 167.114.21.72 | resolver-bruteforce, zone-transfer |
| support.megacorpone.com | 167.114.21.74 | resolver-bruteforce, zone-transfer |
| syslog.megacorpone.com | 167.114.21.73 | resolver-bruteforce, zone-transfer |
| test.megacorpone.com | 167.114.21.75 | resolver-bruteforce, zone-transfer |
| vpn.megacorpone.com | 167.114.21.76 | resolver-bruteforce, zone-transfer |
| vpn2.megacorpone.com | 167.114.21.77 | zone-transfer |
| vpndev.megacorpone.com | 167.114.21.78 | zone-transfer |
| vpnprod.megacorpone.com | 167.114.21.79 | zone-transfer |
| www.megacorpone.com | 149.56.244.87 | crt.sh, resolver-bruteforce, zone-transfer |
| www2.megacorpone.com | 149.56.244.87 | crt.sh, resolver-bruteforce, zone-transfer |

> **Why the zone transfer matters:** it returned 4 hosts the wordlist brute force missed
> (`fs1`, `vpn2`, `vpndev`, `vpnprod`) — the full internal naming scheme, including the
> dev/prod VPN split, in a single request. Raw:
> [`../evidence/dns/zone_transfer_axfr.txt`](../evidence/dns/zone_transfer_axfr.txt).

## People / emails — `email_harvest.py`

| Email | Likely identity |
|-------|-----------------|
| `mcarlow@megacorpone.com` | M. Carlow |
| `msmith@megacorpone.com` | M. Smith |
| `thudson@megacorpone.com` | T. Hudson |
| `trivera@megacorpone.com` | T. Rivera |
| `joe@`, `agrofield@` | staff |
| `hr@`, `sales@`, `shipping@` | role / department |

**Convention:** `{first-initial}{surname}@megacorpone.com` — predictable for any named
employee (phishing-surface mapping).

## Exposed references — GitHub (`gh search`)

- Official source repo `megacorpone/megacorpone.com` is public ("dev backup for main site").
- 20 repos + 30 code hits reference the domain — almost all OSCP/pentest study material.
- No real secrets (training target).

## Interpretation (if this were real)

High-value next steps a defender should note: the **VPN estate** (`vpn/vpn2/vpndev/vpnprod`)
and management plane (`admin`, `router`, `siem`, `snmp`, `syslog`) are exposed in DNS; the
**AXFR misconfiguration** hands an attacker the entire internal naming scheme for free; and
the **predictable email convention** plus named staff enables targeted phishing. Remediation
(for a real target): disable zone transfers to untrusted hosts, split internal/external DNS,
and avoid descriptive hostnames in public DNS.
