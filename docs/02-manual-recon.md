# 02 — Manual Recon (web OSINT tools)

The assignment's manual phase: DNSDumpster, GitHub, Postman, Hunter.io, Have I Been
Pwned, and Google dorks. Several of these are account- or API-key-gated; per the rules of
engagement, **no credentials were submitted** to any of them. Where a tool is gated, the
method is documented and the same data is collected over a free, passive path and
labelled as the equivalent.

---

## DNSDumpster — DNS/infrastructure mapping

**Role:** maps a domain's DNS — subdomains, A/MX/NS records, hosting IPs.
**What we collected (equivalent, passive):** the full DNS footprint via `dns_enum.py`
plus the **zone transfer** (the richest possible DNSDumpster-style result). Raw:
[`../evidence/dns/`](../evidence/dns).

| Record | Value |
|--------|-------|
| A (apex) | `149.56.244.87` |
| NS | `ns1 / ns2 / ns3 .megacorpone.com` |
| MX | `mail`, `mail2` .megacorpone.com + Gandi (`fb.mail.gandi.net`, `spool.mail.gandi.net`) |
| TXT | `"Try Harder"` · `google-site-verification=U7B_b0HNeBtY4qYGQZNsEYXfCJ32hMNV3GtC0wWq5pA` |

**Hosting insight:** apex + `www`/`www2`/`ai` on `149.56.244.87`; most internal hosts on
`167.114.21.64–79`; nameservers spread across `51.79.37.18`, `51.222.39.63`,
`66.70.207.180` (all OVH/OVHcloud ranges). 23 hosts total — see [`04-findings.md`](04-findings.md).

---

## Hunter.io — email addresses & naming convention

**Role:** finds a company's email addresses and the pattern they follow.
**Gated:** Hunter.io needs an account/API key → **not used**.
**Equivalent (passive):** harvested emails directly from the target's **own public
website** (`email_harvest.py`). Raw: [`../evidence/web/emails.json`](../evidence/web/emails.json).

- **Role addresses:** `hr@`, `sales@`, `shipping@` megacorpone.com
- **Personal:** `joe@`, `mcarlow@`, `msmith@`, `thudson@`, `trivera@`, `agrofield@`
- **Naming convention:** `{first-initial}{surname}` → e.g. `msmith` = *M. Smith*,
  `thudson` = *T. Hudson*, `trivera` = *T. Rivera*, `mcarlow` = *M. Carlow*.

This convention is the key OSINT pivot: given any employee's name, their likely email is
predictable (phishing-surface mapping).

---

## GitHub — code & reference exposure

**Role:** find code, configs, or secrets referencing the org.
**What we collected (real, via `gh search`):** raw in [`../evidence/github/`](../evidence/github).

- **20 repositories** mention *megacorpone*, including the **official source**
  `megacorpone/megacorpone.com` ("dev backup for main site") — the actual site code is public.
- **30 code hits across 18 repos** reference `megacorpone.com`, overwhelmingly OSCP / pentest
  study notes and cheat sheets (`OSCP-Cheatsheet`, `Penetration-Testing-Study-Notes`, …) —
  consistent with its status as a training target.
- No real secrets were found or published (it is a training domain).

---

## Google Dorks — indexed-content discovery

**Role:** mine Google's public index for pages, files, emails, and exposed assets.
**Deliverable:** a vetted 16-dork query set scoped to the domain, with what each surfaces —
[`../evidence/dorks/google-dorks.md`](../evidence/dorks/google-dorks.md). (Automating
Google breaches its ToS and triggers CAPTCHAs, so the query set is the artifact; run them
in a browser.)

---

## Postman — public API recon

**Role:** search Postman's **public** workspaces/collections for the org's APIs.
**Method (passive):** search the Postman public API network for `megacorpone` /
`megacorpone.com`. **Result:** no public Postman collections are published for this target
(expected — it is a static training site with no real API). Documented as a negative; the
method is the deliverable.

---

## Have I Been Pwned — breach exposure

**Role:** check whether the domain's email addresses appear in known breaches.
**Gated:** HIBP's domain search requires a verified-owner API key; individual-account
lookups require an API key → **not used** (and we do not own the domain).
**Method (documented, not executed):** with authorization, submit the domain to HIBP's
*Domain Search* (owner-verified) or query individual harvested addresses via the HIBP API.
**Result for this lab:** the harvested addresses are fictional training data, so no
legitimate breach exposure applies. Method recorded for completeness.
