---
name: transweb-create
description: "Use when the user wants to create browser-based Agent apps or AI Skill apps from documents/materials or requirements, and get an agent.html?id=... / skill.html?id=... link. 需要 transweb.cn API Key（ak_live_...）。"
whenToUse: "当用户说“把这些资料做成 Agent”“把这份文档变成智能体”“根据这个需求生成一个 AI Skill/网页应用”“创建一个技能并给我链接”等，需要调用 transweb.cn 创建 Agent/Skill 应用时。"
display_name: "TransWeb 应用创建器"
display_name_en: "TransWeb App Creator"
description_zh: "把资料或需求转换成浏览器上可运行的 Agent 应用或 AI Skill 应用。"
description_en: "Turn source material or requirements into browser-based Agent apps or AI Skill apps."
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - curl
    primaryEnv: TRANSWEB_API_KEY
    envVars:
      - name: TRANSWEB_API_KEY
        required: false
        description: transweb.cn API Key（ak_live_...）；也可用 config 文件保存。
      - name: TRANSWEB_CONFIG
        required: false
        description: 自定义配置文件路径（默认复用 transweb-ai.json）。
      - name: TRANSWEB_PROFILE
        required: false
        description: 选择 API Key profile。
      - name: TRANSWEB_BASE_URL
        required: false
        description: 覆盖 transweb.cn 服务地址。
      - name: TRANSWEB_API_NAME
        required: false
        description: 覆盖模型供应方 apiName。
      - name: TRANSWEB_MODEL
        required: false
        description: 覆盖模型名。
    emoji: "🏗️"
    homepage: https://github.com/liuwenjin/transweb
---

# TransWeb 应用创建器

适用于任何支持 `SKILL.md` 的 Agent Skills 客户端；只依赖 `python3` + `curl`，不绑定特定宿主。

把资料或需求转换成浏览器上可运行的 **Agent 应用**或 **AI Skill 应用**，返回：

```text
Agent: https://transweb.cn/agent.html?id=<documentId>
Skill: https://transweb.cn/skill.html?id=<documentId>
```

本技能只负责**创建**；列出/运行已有应用、生成 PPT 请用 `transweb-ai`。

## 配置

API Key 与 `transweb-ai` 共用同一份配置。按以下顺序查找：`--config` / `TRANSWEB_CONFIG` → 项目 `.transweb-ai.json` / `.transweb/transweb-ai.json` → 旧版项目 `.dsh/transweb-ai.json` → `~/.config/transweb-ai/config.json` → 旧版 `~/.dsh/transweb-ai.json`。

```bash
python3 scripts/transweb_create.py configure --verify
python3 scripts/transweb_create.py config show
python3 scripts/transweb_create.py whoami --json
```

推荐 scope：`doc:read` + `ai:chat`；`account:read` 可选。

实际校验范围：`ai:chat` 只拦 `/gpt/aiGatewayRequest`，`doc:read` 只拦 `getLoginedData` 等标注接口；`publishPptItem`、`setDocumentStatus`、bucket 上传、`getDocumentData` 等不校验 scope，`doc:write` 当前没有接口使用。scope 不能替代账号隔离。

### 离线自检（审核/沙箱）

不需要 API Key，不发起网络请求：

```bash
python3 scripts/transweb_create.py selftest --json
python3 scripts/transweb_create.py --version
```

检查 Python/curl、包内文件、frontmatter 必需字段、依赖与密钥泄漏；沙箱/平台审核可先运行这一条。

### 切换服务地址

```bash
# 永久切换（写入共享 profile，transweb-ai 也会生效）
python3 scripts/transweb_create.py config base http://localhost
python3 scripts/transweb_create.py config base

# 单次命令
python3 scripts/transweb_create.py agent --file material.md --base-url http://localhost

# 环境变量
TRANSWEB_BASE_URL=http://localhost python3 scripts/transweb_create.py skill --input "..."
```

恢复：`config base https://transweb.cn`。目标服务需提供相同的 `/admin/getAppConfig`、`/user/getAgentData`、`/user/getDocumentData`、`/gpt/aiGatewayRequest`、bucket 上传等接口。

## 创建 Agent

输入资料正文、文件或 stdin：

```bash
python3 scripts/transweb_create.py agent --file material.md --json
python3 scripts/transweb_create.py agent --input "资料正文..." --json
cat material.txt | python3 scripts/transweb_create.py agent --stdin --json
```

支持文件：

- txt / md 直接读取；
- PDF 需 `pypdf` 或 `PyPDF2`；
- docx 需 `python-docx`；
- 旧版 .doc 请先转 txt/docx。

输出示例：

```json
{
  "ok": true,
  "link": "https://transweb.cn/agent.html?id=...",
  "id": "...",
  "type": "agent",
  "title": "Kubernetes 运维工程师",
  "description": "面向 ... 的助手",
  "promptChars": 605,
  "pointsCost": 90,
  "published": false
}
```

创建流程：

1. `GET /admin/getAppConfig` → `publishInfo.folderName` / `appName` / `user` / `avatar`；
2. `GET /user/getAgentData?agent=<publishInfo.folderName>&lang=zh` → 解析 `agentList_zh`，按创建类型精确选模板：Agent 选 `agentGenerator`，Skill 选 `appGenerator`；
3. `knowledgeApp` 压缩资料 → `characterProfile` 生成 `roleProfile`；
4. 写入 Agent 模板的 title / subtitle / introduce / exampleList；
5. 上传应用代码 → `publishPptItem`，写入 `documentType:"agent"`；
6. 把 knowledgeApp 存档 `_id` 写入 `knowledges`，关联知识库；
7. 默认 `publishStatus=false`，返回直接链接。

## 创建 Skill

```bash
python3 scripts/transweb_create.py skill \
  --input "把用户输入的三段话总结成一句不超过 40 字的结论，并说明依据" \
  --json
```

创建流程（与 `aigcPlugin.createAigcApp` 对齐的四步工作流）：

1. 先取 `publishInfo` 与 `agentList_zh` 模板（Agent：`agentGenerator`；Skill：`appGenerator`）；
2. 需求分析（`requirement`）→ 质量约束（`contentQuality`）→ 模板生成（`pageTemplate`，输入需求示例）→ 模板润色（`improveTemplate`）；
3. 用四步结果生成 system prompt 与自定义 HTML/CSS 页面；
4. 绑定 `appTemplate.vue`，写入 title / introduce / defaultTemplate / inputPlaceholder / icon / exampleList；
5. 上传应用代码 → `publishPptItem`，写入 `documentType:"skill"`；
6. 默认 `publishStatus=false`，返回 `skill.html?id=...` 直接链接。

输出示例：

```json
{
  "ok": true,
  "link": "https://transweb.cn/skill.html?id=...",
  "id": "...",
  "type": "skill",
  "title": "会议待办卡片",
  "description": "...",
  "promptChars": 2566,
  "pointsCost": 96,
  "published": false
}
```

## 通用选项

| 选项 | 说明 |
| --- | --- |
| `--input` | 资料/需求正文 |
| `--file` | 从文件读取 |
| `--stdin` | 从 stdin 读取 |
| `--title` | 覆盖生成标题 |
| `--description` | 覆盖描述 |
| `--publish` | **显式**发布到全局市场；默认不发布 |
| `--json` | JSON 输出 |
| `--quiet` | 不输出进度 |
| `--timeout` | 生成超时秒数 |

## 重要行为

- **documentType**：Agent 写 `agent`，Skill 写 `skill`；`transweb-ai` 的 `run` 据此决定输出字符串还是链接。
- **默认私有**：`publishStatus=false`，不会出现在 `getPublishedList`；直接链接仍可打开。
- 需要全局可见时才加 `--publish`。
- 会消耗 transweb.cn AI 积分。
- 上传代码需要系统 `curl` 与 API Key 会话（脚本自动建立 cookie）。
- 应用 `creator` 自动取 API Key 所有者名称（`getAgentData` 当前账号的 `name_zh`），appEditor 的“创作者”会显示该名称。
- 文档包装会对所有字符串做 JavaScript `escape()`，标题/描述中的 `(` `)` 不会破坏 `WebTool.extractContentInBrackets` 解析。
- 找不到目标模板（`agentGenerator` / `appGenerator`）时直接报错，不会静默换模板。

## 交付

1. 优先给直接链接：

```text
[打开 Agent](https://transweb.cn/agent.html?id=...)
[打开 Skill](https://transweb.cn/skill.html?id=...)
```

2. 说明标题、类型、消耗积分。
3. `published:false`：私有，需要公开时加 `--publish` 重新创建/更新。

## 排障

| 现象 | 处理 |
| --- | --- |
| 缺少 API Key | `configure --api-key-stdin` 或设置 `TRANSWEB_API_KEY` |
| `doc:read`/`ai:chat` 不足 | 仅对应标注接口会报；按错误补 scope，写接口不靠 scope 拦截 |
| 上传失败 | 确认系统有 `curl`，重新运行 |
| PDF/Word 读取失败 | 安装 `pypdf` / `python-docx`，或先转 txt |
| `getAppConfig`/`agentList_zh` 失败 | 检查平台可访问；确认 `agentGenerator` / `appGenerator` 模板存在 |
| 生成结果不是 JSON | 重试；四步工作流会返回原始输出开头用于排查 |

## 资源

- `scripts/transweb_create.py`：configure / config / whoami / agent / skill
- `references/api.md`：接口细节
- `README.md`：安装与示例

配套的 `transweb-ai` 负责使用已有应用；本技能负责创建。两个技能可独立安装、独立配置。
