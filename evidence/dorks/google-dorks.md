# Google Dorks — megacorpone.com

Curated Google search operators for passive reconnaissance of the target. These
read only Google's public index — no interaction with the target's systems. Run
them in a browser (automating Google violates its ToS and triggers CAPTCHAs, so
the deliverable here is the vetted query set + what each surfaces).

> Scope: all queries are constrained to `megacorpone.com`. Record only public info.

## Surface mapping

| # | Dork | What it surfaces |
|---|------|------------------|
| 1 | `site:megacorpone.com` | Every page Google has indexed for the domain |
| 2 | `site:*.megacorpone.com` | Indexed content on **subdomains** (mail, vpn, intranet, …) |
| 3 | `site:megacorpone.com -www` | Non-www hosts (quick subdomain hint) |
| 4 | `site:megacorpone.com inurl:admin OR inurl:login` | Admin / login portals |

## Files & documents (metadata goldmine)

| # | Dork | What it surfaces |
|---|------|------------------|
| 5 | `site:megacorpone.com filetype:pdf` | Public PDFs (authors, software in metadata) |
| 6 | `site:megacorpone.com (filetype:xlsx OR filetype:docx OR filetype:csv)` | Office docs |
| 7 | `site:megacorpone.com filetype:txt` | robots.txt, notes, config dumps |
| 8 | `site:megacorpone.com ext:bak OR ext:old OR ext:log` | Backup / stale / log files |

## People & contact (OSINT pivot)

| # | Dork | What it surfaces |
|---|------|------------------|
| 9 | `site:megacorpone.com "@megacorpone.com"` | Email addresses on indexed pages |
| 10 | `"@megacorpone.com" -site:megacorpone.com` | Staff emails leaked **off-site** (forums, pastes) |
| 11 | `site:linkedin.com "megacorpone"` | Employees / roles on LinkedIn |

## Exposed tech & secrets (what blue-teams hunt for)

| # | Dork | What it surfaces |
|---|------|------------------|
| 12 | `site:megacorpone.com intitle:"index of"` | Open directory listings |
| 13 | `site:megacorpone.com inurl:wp-content OR inurl:wp-admin` | WordPress footprint |
| 14 | `site:megacorpone.com intext:"password" filetype:log` | Passwords in logs (rare but critical) |
| 15 | `site:github.com "megacorpone.com"` | Code / configs referencing the domain (see `../github/`) |
| 16 | `site:pastebin.com "megacorpone"` | Pastes mentioning the org |

## Notes

- Dorks 9–11 and 16 are the highest-value OSINT pivots (people → phishing surface,
  leaked credentials).
- `megacorpone.com` is a training target, so most "secret" dorks return little real
  data — but the **methodology** is identical against a real engagement target.
- Cross-reference hits here with the DNS subdomains in `../dns/zone_transfer_axfr.txt`
  and the GitHub findings in `../github/`.
