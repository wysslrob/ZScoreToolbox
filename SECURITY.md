# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ Yes    |
| < 1.1   | ❌ No     |

Only the latest release receives security fixes. Please update to the most recent
version before reporting an issue.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it via
**[GitHub Issues](https://github.com/wysslrob/ZScoreToolbox/issues)** and
**mark the issue as private / confidential** when creating it (use the
"Report a security vulnerability" option on the Issues page).

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- The version of ZScoreToolbox you tested against
- Your suggested fix, if you have one

We will acknowledge reports within **7 days** and aim to release a patch within
**30 days** for confirmed issues.

## Scope & Threat Model

ZScoreToolbox is a **local Windows desktop tool** with no server component and
no network communication of its own.  The relevant attack surface is:

| Area | Notes |
|------|-------|
| **Python dependencies** | Pillow, keyboard, mss, pystray — automatically scanned weekly via `pip-audit` in CI |
| **Screenshot data** | The app captures a single screenshot per measurement and discards it immediately; no data is stored or transmitted |
| **Hotkey listener** | Uses the `keyboard` library to listen for Ctrl+Alt+S globally; no keylogging or data retention |
| **Clipboard** | The user explicitly clicks "Copy" to write a Z-score value; no automatic clipboard access |
| **Network** | No inbound or outbound network connections except `pip install` during setup/build |

## Automated Security Scanning

Every push to `main` and every week on Monday, the CI pipeline runs:

- **[Bandit](https://bandit.readthedocs.io/)** — static analysis of Python source code
- **[pip-audit](https://pypi.org/project/pip-audit/)** — CVE scanning of Python dependencies

Reports are uploaded as GitHub Actions artifacts.  The workflow fails if Bandit
finds any **HIGH** severity issue.
