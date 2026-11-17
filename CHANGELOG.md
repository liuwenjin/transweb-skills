# Changelog

## transweb-ai 1.2.3

- Based on the `1.2.2-wb` package.
- Updated capability description: web PPT, visual charts, 3D figure modeling, 3D animation, mini-games; `transweb-create` for extensions.
- Kept offline `demo` / `--dry-run`, `selftest`, 10 unit tests, and bilingual metadata.
- Package layout keeps `SKILL.md` at ZIP root.

## transweb-ai 1.2.2-wb

- Added offline preview (`demo`, `--dry-run`) for sandbox and training.
- Expanded selftest and tests.
- Added `author` and bilingual examples.

## transweb-ai 1.2.0

- Split usage and creation into `transweb-ai` and `transweb-create`.
- Added `documentType` handling: Agent returns a string; Skill returns a link.
- Added default-private creation and creator identity.
- Added bracket-safe document serialization.

## transweb-ai 1.1.0

- Added Agent/Skill creation.
- Added `admin/getAppConfig` → `publishInfo` → `getAgentData` template flow.
- Added `agentGenerator` / `appGenerator` template selection.

## transweb-ai 1.0.0

- Initial release: list, run, chain, and PPT generation.
