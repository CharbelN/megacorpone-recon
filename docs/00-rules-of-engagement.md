# 00 — Rules of Engagement

> Read this first. This engagement is **passive OSINT reconnaissance only**.

## Target & authorization

| Item | Value |
|------|-------|
| **Target** | `megacorpone.com` |
| **Nature** | Offensive Security's **public, intentional reconnaissance training target** (used in PEN-200 / OSCP) |
| **Authorization** | The domain is published by OffSec expressly to be enumerated for training. Also the target assigned by the course. |
| **Engagement type** | Passive OSINT / footprinting |
| **Operator** | CharbelN |

## What this engagement does and does not do

**Does (passive OSINT — reading public information):**
- DNS records, DNS zone transfer (AXFR) — the target deliberately allows it
- Certificate-transparency logs (crt.sh), subdomain resolution
- The target's **own public website** (emails, staff names)
- Public search indexes (Google dorks), public code (GitHub)

**Does NOT:**
- Authenticate to, or access, any account, system, or private data
- Submit credentials or personal data to Hunter.io / Have I Been Pwned / DNSDumpster / Postman
- Run exploits, intrusive active scans, or port scans of third-party hosts
- Publish any real secret, credential, or private personal data

This mirrors the assignment's instruction: *"Record only information you are allowed to
collect. Do not attempt to access accounts, systems, or data without permission."*

## Scope control

Scope is defined once in [`../scripts/scope.yaml`](../scripts/scope.yaml) (same guardrail
idea as a real engagement): the tooling only ever queries `megacorpone.com` and its own
nameservers.

## A note on the zone transfer

A DNS zone transfer (AXFR) is attempted against the target's authoritative nameservers.
On megacorpone this is the canonical lesson — the servers are **deliberately
misconfigured** to allow it. AXFR reads public DNS data; it is not an intrusion.

## Environment note (honest disclosure)

Testing ran from a workstation on a **mobile-hotspot** connection whose carrier **blocks
all direct outbound port 53** (TCP and UDP). This is disclosed throughout because it
shaped *how* some data was collected (e.g., the zone transfer was completed via an HTTPS
vantage point instead of a direct AXFR). No security control on the workstation was
disabled — the block is upstream at the carrier. See [`03-kali-tools.md`](03-kali-tools.md).
