# Security Policy

## Reporting a vulnerability

Please report security problems privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue for anything an attacker could use before it is fixed.

Useful reports include:

- the API, webhooks or job queue (authentication, SSRF, injection, denial of service)
- prompt injection through analysed claims that changes a verdict, a veto or the audit
- ways around the scope scrubber, field suppression or the regulated response envelope
- anything that makes the tool profile or build a dossier on a person, in breach of the [Anti-Weaponization Charter](ANTI-WEAPONIZATION-CHARTER.md)

Errors of fact in published scenarios or research are not security issues. Please use [CORRECTIONS.md](CORRECTIONS.md) for those.

## What to expect

This is a single-maintainer project, so responses are best effort. You will get an acknowledgement, a fix or a reasoned decision, and credit in the CHANGELOG if you want it.

## Supported versions

Only the latest release on `main` receives fixes.

## Deployment note

The API has no built-in authentication. Run it on localhost (the default compose file binds to `127.0.0.1`) or behind your own access control. Never expose it directly to the internet.
