# Contributing

Thanks for helping improve TransWeb Skills.

## Before you start

- Do not include API keys, local config files, cookies, generated archives, or screenshots containing account data.
- Keep changes focused: one skill or one documentation topic per pull request.
- Use English or Chinese consistently within the file you edit.

## Development setup

The skills use only the Python standard library. `curl` is optional for `transweb-ai` and required for `transweb-create` uploads.

```bash
python3 --version
python3 -m unittest discover -s skills/transweb-ai/tests -v
python3 -m unittest discover -s skills/transweb-create/tests -v
python3 skills/transweb-ai/scripts/transweb_ai.py selftest --json
python3 skills/transweb-create/scripts/transweb_create.py selftest --json
```

No network or API key is needed for the tests above.

## Adding a skill

Create:

```text
skills/<skill-name>/
├── SKILL.md          # required frontmatter + instructions
├── README.md
├── scripts/
├── references/
└── tests/
```

Frontmatter must include:

```yaml
name: <skill-name>
description: "<selection-oriented English description>"
display_name: "<Chinese display name>"
display_name_en: "<English display name>"
description_zh: "<Chinese description>"
description_en: "<English description>"
```

Package the **contents** of the skill folder so `SKILL.md` is at the ZIP root. Do not add an outer wrapper directory.

## Pull request checklist

- [ ] `py_compile` passes
- [ ] unit tests pass
- [ ] `selftest --json` returns `ok: true`
- [ ] no `ak_live_...` values, config files, or cookies
- [ ] docs updated (manual/quick start/API reference)
- [ ] package layout checked with `unzip -l`
- [ ] generated archives are not committed

## Security

Never paste a real API key into an issue, pull request, test, screenshot, or log. Report security issues through [SECURITY.md](SECURITY.md), not a public issue.
