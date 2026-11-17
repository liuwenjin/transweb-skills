# Quick start (developers)

## Requirements

- Python 3.9+
- `curl` (recommended; required by `transweb-create` uploads)
- A transweb.cn API key with `doc:read` + `ai:chat`

## 1. Configure

```bash
cd skills/transweb-ai
python3 scripts/transweb_ai.py configure --api-key-stdin
```

Paste `ak_live_...` and end input with Ctrl-D (macOS/Linux) or Ctrl-Z Enter (Windows PowerShell).

## 2. Verify offline

```bash
python3 scripts/transweb_ai.py selftest --json
python3 scripts/transweb_ai.py demo --json
python3 scripts/transweb_ai.py --version
```

No network or key is required for `selftest` / `demo`.

## 3. List and run

```bash
python3 scripts/transweb_ai.py list --limit 10 --json
python3 scripts/transweb_ai.py list --source published --query "PPT" --limit 10
python3 scripts/transweb_ai.py run --ids <appId> --input "your request" --json
```

`run` reads `/user/getDocumentData`:

- `documentType=agent` → returns a string result;
- `documentType=skill` → returns an archived result link;
- missing/unknown → treated as Skill-compatible.

## 4. Generate a PPT

```bash
python3 scripts/transweb_ai.py ppt \
  --input "topic, sections, key points" \
  --json
```

Offline preview:

```bash
python3 scripts/transweb_ai.py ppt --input "quarterly review" --dry-run --json
```

## 5. Configure another account (profile)

```bash
python3 scripts/transweb_ai.py configure --profile work --api-key-stdin
python3 scripts/transweb_ai.py config list
python3 scripts/transweb_ai.py config use work
python3 scripts/transweb_ai.py config use default
```

## 6. Switch base URL

```bash
python3 scripts/transweb_ai.py list --base-url http://localhost
python3 scripts/transweb_ai.py config base http://localhost
python3 scripts/transweb_ai.py config base https://transweb.cn
```

## 7. Create an Agent or Skill

```bash
cd skills/transweb-create

python3 scripts/transweb_create.py agent --file material.md --json
python3 scripts/transweb_create.py skill --input "requirement" --json
```

Creation is private by default. Add `--publish` only when global visibility is intended.

## 8. Test

```bash
python3 -m unittest discover -s skills/transweb-ai/tests -v
python3 -m unittest discover -s skills/transweb-create/tests -v
python3 skills/transweb-ai/scripts/transweb_ai.py selftest --json
python3 skills/transweb-create/scripts/transweb_create.py selftest --json
```

## Config locations

1. `--config` / `TRANSWEB_CONFIG`
2. `<project>/.transweb-ai.json`
3. `<project>/.transweb/transweb-ai.json`
4. `<project>/.dsh/transweb-ai.json` (legacy)
5. `~/.config/transweb-ai/config.json`
6. `~/.dsh/transweb-ai.json` (legacy)

The file is written with `0600` permissions. Never commit it.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `请先登录账号` | Recreate the API key and configure again |
| `缺少 scope` on `whoami` | Expected when the key lacks `account:read`; use `selftest` / `list` |
| `archive_not_found` | Retry with `--wait 30`; do not duplicate paid requests |
| Points exhausted | Top up; reduce chained steps |
| Config not found | `config path`; use `--config` if needed |
| API 404 | `config base https://transweb.cn` |
