# TransWeb Skills

**Open-source Agent Skills for [transweb.cn](https://transweb.cn/) — use and create browser-native AI workers.**

This repository contains two installable skills and a beginner-friendly manual. They work with any client that supports the `SKILL.md` convention, including Claude Code, OpenClaw, DSH, Codex, Cursor, and other Agent Skills-compatible tools.

[中文使用说明书](docs/transweb-ai-manual.html) · [PDF](docs/transweb-ai-manual.pdf) · [Quick start](docs/quickstart.md)

---

## Skills

| Skill | Version | What it does |
| --- | --- | --- |
| [`transweb-ai`](skills/transweb-ai/SKILL.md) | `1.2.3` | Browse, run, and chain AI apps in a transweb.cn account; generate web PPT, visual charts, 3D figure modeling, 3D animation, and mini-games |
| [`transweb-create`](skills/transweb-create/SKILL.md) | `1.0.0` | Turn source material into a transweb.cn Agent, or a requirement into a browser AI Skill |

`transweb-ai` is for **using** existing apps. `transweb-create` is for **creating** new Agent/Skill apps. They can be installed together or independently.

## Features

- **Browser-native**: no client install for the generated apps; every result is a web link.
- **Agent / Skill aware**: `run` reads `documentType` and returns a string for Agent apps or a result link for Skill apps.
- **PPT routing**: requests for slides/decks go directly to the official presentation app.
- **Offline preview**: `demo` and `--dry-run` let you inspect workflows without an API key, network, or credits.
- **Private by default**: creating an app does not publish it globally; opt in with `--publish`.
- **Creator identity**: new apps store the API-key owner's display name as `creator`.
- **Bilingual metadata**: `display_name`, `display_name_en`, `description_zh`, `description_en` are present for marketplaces.
- **No bundled secrets**: this repository contains no default API key.

## Install

### skills.sh

```bash
npx skills add liuwenjin/transweb-skills --skill transweb-ai
npx skills add liuwenjin/transweb-skills --skill transweb-create
```

### ClawHub / OpenClaw

```bash
clawhub install transweb-ai
clawhub install transweb-create
```

### Manual

Copy the skill folders into the skills directory used by your client:

```text
<client-skills>/transweb-ai/
<client-skills>/transweb-create/
```

The folder must contain `SKILL.md` at its root. Do not add an extra wrapper directory when packaging a skill.

## Configuration

Both skills share the same API-key configuration.

### 1. Get an API key

1. Sign in at [transweb.cn](https://transweb.cn/).
2. Open the account menu → **API Key** → **Manage**.
3. Enter a name, click **Add**, and copy the key immediately.
4. The full key (`ak_live_...`) is shown **only once**.

The web UI creates a key with `doc:read` + `ai:chat` by default. It may not include `account:read`; `whoami` can therefore warn about a missing scope, which does not block listing apps, running skills, or generating PPT.

### 2. Configure locally

```bash
cd skills/transweb-ai
python3 scripts/transweb_ai.py configure --api-key-stdin
# paste the key, then Ctrl-D (macOS/Linux) or Ctrl-Z Enter (Windows PowerShell)
```

Or use an environment variable for one-off use:

```bash
export TRANSWEB_API_KEY=ak_live_...
python3 scripts/transweb_ai.py list --limit 5
```

Config lookup order:

1. `--config <path>` / `TRANSWEB_CONFIG`
2. `<project>/.transweb-ai.json`
3. `<project>/.transweb/transweb-ai.json`
4. `<project>/.dsh/transweb-ai.json` (legacy)
5. `~/.config/transweb-ai/config.json`
6. `~/.dsh/transweb-ai.json` (legacy)

The file is written with `0600` permissions. Never commit it.

### 3. Verify without spending credits

```bash
python3 scripts/transweb_ai.py selftest --json
python3 scripts/transweb_ai.py demo --json
```

`selftest` checks the package, frontmatter, dependencies, and key leakage without network access. `demo` previews a workflow without calling the API.

## Usage

```bash
# List account apps
python3 scripts/transweb_ai.py list --limit 10 --json

# Run one app
python3 scripts/transweb_ai.py run --ids <appId> --input "your request" --json

# Chain apps
python3 scripts/transweb_ai.py run --ids <id1>,<id2> --input "your request" --json

# Generate a web PPT
python3 scripts/transweb_ai.py ppt --input "topic, sections, key points" --json

# Preview without calling the API
python3 scripts/transweb_ai.py ppt --input "quarterly review" --dry-run --json
```

**Agent apps** return a string result. **Skill apps** return an archived result link. Legacy apps without `documentType` are treated as Skill-compatible.

### Create an Agent or Skill

```bash
cd skills/transweb-create

python3 scripts/transweb_create.py agent --file material.md --json
python3 scripts/transweb_create.py skill --input "turn three paragraphs into one conclusion" --json
```

New apps are **private by default** (`publishStatus=false`). Add `--publish` only when global visibility is intended.

## Documentation

- **Beginner manual (web/print)**: [HTML](docs/transweb-ai-manual.html) · [PDF](docs/transweb-ai-manual.pdf)
- **Developer quick start**: [docs/quickstart.md](docs/quickstart.md)
- **Digital-labor knowledge base**: [docs/knowledge-base.md](docs/knowledge-base.md)
- **API reference**: [skills/transweb-ai/references/api.md](skills/transweb-ai/references/api.md)

The beginner manual is designed for A4 printing and avoids terminal commands: it shows how to ask an AI assistant to configure and use the skill.

## Security

- No API key is bundled. Do not add one to this repository, issues, screenshots, or logs.
- Keep the local config at `0600`; use `configure --api-key-stdin` instead of shell history.
- Generated links may be publicly accessible; check content before sharing.
- `publishStatus=false` hides an app from the public marketplace but is not an absolute confidentiality boundary.
- See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

```bash
python3 -m unittest discover -s skills/transweb-ai/tests -v
python3 -m unittest discover -s skills/transweb-create/tests -v
python3 skills/transweb-ai/scripts/transweb_ai.py selftest --json
python3 skills/transweb-create/scripts/transweb_create.py selftest --json
```

## License

ISC. See [LICENSE](LICENSE).

## Acknowledgements

TransWeb Skills are independent open-source integrations for the transweb.cn platform. TransWeb and its app templates are operated by their respective owners.
