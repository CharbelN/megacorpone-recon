#!/usr/bin/env python3
"""
run_dnsrecon.py — run dnsrecon on Python 3.14.

Why this wrapper exists
-----------------------
dnsrecon 0.10.1 imports `urllib.request.FancyURLopener` (for its legacy Bing
scraper). Python 3.14 **removed** `FancyURLopener`/`URLopener`, so importing
dnsrecon crashes before it does anything. Those classes were only used for the
optional Bing module (which needs an API key we are not using), so a minimal,
inert stub restores import-compatibility without changing dnsrecon's DNS logic.

This lets us run the real dnsrecon tool locally (no Kali container download) for
the standard DNS enumeration the assignment asks for. The AXFR dnsrecon attempts
will still fail from this host because outbound TCP/53 is blocked upstream (see
docs/00-rules-of-engagement.md); the zone transfer itself is captured separately
via an HTTPS vantage point in scripts/dns_enum.py.

Usage:
    python scripts/run_dnsrecon.py -d megacorpone.com -t std -j evidence/dns/dnsrecon_std.json
"""

import sys
import urllib.request


class _InertURLopener:
    """Minimal stand-in for the removed urllib FancyURLopener/URLopener."""

    def __init__(self, *args, **kwargs):
        pass

    def open(self, *args, **kwargs):
        raise RuntimeError("legacy URLopener disabled on Python 3.14 (Bing module not used)")


# Restore the names dnsrecon expects, if the running Python removed them.
for _name in ("FancyURLopener", "URLopener"):
    if not hasattr(urllib.request, _name):
        setattr(urllib.request, _name, _InertURLopener)

# Now dnsrecon imports cleanly; hand off to its CLI.
from dnsrecon.__main__ import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
