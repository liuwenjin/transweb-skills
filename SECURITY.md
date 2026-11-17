# Security Policy

## Supported versions

| Skill | Supported |
| --- | --- |
| `transweb-ai` | 1.2.x |
| `transweb-create` | 1.0.x |

## Reporting a vulnerability

Please use the repository's **private security advisory** feature, or contact the maintainer privately. Do not open a public issue for:

- exposed API keys or cookies;
- authentication/authorization bypasses;
- secret leakage in packages or screenshots;
- command injection or unsafe file handling.

Include:

- affected skill and version;
- reproduction steps;
- impact;
- a redacted log or screenshot.

## Secrets and generated data

- This repository contains no default API key.
- Runtime keys must live in a local `0600` config or an environment variable.
- Never commit `.transweb-ai.json`, `.dsh/transweb-ai.json`, `cookies.txt`, or `.env`.
- Generated app/result links may be publicly accessible. Review content before sharing.
- `publishStatus=false` hides an app from the public marketplace, but it is not an absolute confidentiality boundary.

## Dependency and network behavior

`transweb-ai` uses Python's standard library and, when available, the system `curl` binary for HTTP. `transweb-create` requires `curl` for code uploads. Both send requests only to the configured TransWeb base URL; `selftest` performs no network calls.
