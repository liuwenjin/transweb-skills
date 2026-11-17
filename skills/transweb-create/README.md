# TransWeb 应用创建器

一个跨客户端的 Agent Skill：把资料或需求转换成浏览器上可运行的 **Agent 应用**或 **AI Skill 应用**。适用于任何支持 `SKILL.md` 的 Agent Skills 客户端。

- 资料 → Agent 应用：知识压缩 + 人设生成 + 知识库关联，返回 `agent.html?id=...`
- 需求 → AI Skill 应用：四步工作流 + 自定义 HTML/CSS 页面，返回 `skill.html?id=...`
- 默认**不发布到全局市场**；需要公开时显式加 `--publish`
- `creator` 自动取 API Key 所有者名称
- 只负责创建；列出/运行已有应用、生成 PPT 请用 `transweb-ai`

## 安装

把 `transweb-create/` 整个目录放到客户端扫描的 skills 目录。常见位置：

```text
Claude Code:   ~/.claude/skills/transweb-create/
OpenClaw:      ~/.openclaw/skills/transweb-create/
其他客户端:    <客户端 skills 目录>/transweb-create/
```

只要客户端支持 `SKILL.md` 约定即可，不依赖特定运行时。

## 配置

与 `transweb-ai` 共用同一份 `transweb-ai.json` 配置；不包含默认 API Key。

```bash
python3 scripts/transweb_create.py config show
python3 scripts/transweb_create.py configure --verify
```

推荐 scope：`doc:read` + `ai:chat`。

实际只有标注 `requiredScope` 的接口校验 scope；创建/发布/上传接口大多不校验，`doc:write` 当前未接入。scope 不能替代账号隔离。

### 离线自检

```bash
python3 scripts/transweb_create.py selftest --json
python3 scripts/transweb_create.py --version
python3 -m unittest discover -s tests -v
```

不需要 API Key，不会发起网络请求。

### 切换服务地址

```bash
python3 scripts/transweb_create.py config base http://localhost
python3 scripts/transweb_create.py config base
python3 scripts/transweb_create.py agent --file material.md --base-url http://localhost
TRANSWEB_BASE_URL=http://localhost python3 scripts/transweb_create.py skill --input "..."
```

恢复：`config base https://transweb.cn`。

## 使用

### 资料转 Agent

```bash
python3 scripts/transweb_create.py agent --file material.md --json
python3 scripts/transweb_create.py agent --input "资料正文..." --json
cat material.txt | python3 scripts/transweb_create.py agent --stdin --json
```

输出：

```json
{
  "ok": true,
  "link": "https://transweb.cn/agent.html?id=...",
  "type": "agent",
  "title": "...",
  "published": false
}
```

### 需求转 Skill

```bash
python3 scripts/transweb_create.py skill \
  --input "把用户输入的三段话总结成一句不超过 40 字的结论" \
  --json
```

输出：

```json
{
  "ok": true,
  "link": "https://transweb.cn/skill.html?id=...",
  "type": "skill",
  "title": "...",
  "published": false
}
```

### 选项

| 选项 | 说明 |
| --- | --- |
| `--input` / `--file` / `--stdin` | 输入方式 |
| `--title` / `--description` | 覆盖生成结果 |
| `--publish` | 显式发布到全局市场；默认不发布 |
| `--json` / `--quiet` | 输出控制 |
| `--timeout` | 生成超时 |

## 工作方式

```text
agent:
  getAppConfig → publishInfo
  → getAgentData?agent=<publishInfo.folderName> → agentList_zh
  → 按 appName 选模板
  → knowledgeApp → characterProfile
  → agentTemplate.vue + title/subtitle/introduce/exampleList
  → 上传代码 → publishPptItem → knowledges
  → agent.html?id=...

skill:
  getAppConfig → publishInfo
  → getAgentData?agent=<publishInfo.folderName> → agentList_zh
  → 需求分析 → 质量约束 → 模板生成 → 模板润色
  → system prompt + 自定义 HTML/CSS
  → appTemplate.vue + data URL
  → 上传代码 → publishPptItem
  → skill.html?id=...
```

## 重要行为

- `documentType`：Agent 写 `agent`，Skill 写 `skill`；`transweb-ai` 的 `run` 据此决定输出字符串还是链接。
- 默认私有：`publishStatus=false`，不会进入 `getPublishedList`；直接链接仍可打开。
- `creator` 取当前 API Key 所有者 `name_zh`（如“刘文津”）。
- 所有字符串做 JS `escape()`，标题/描述含 `(` `)` 也不会破坏 `extractContentInBrackets`。
- 创建消耗 AI 积分；上传需要系统 `curl`。
- PDF 需 `pypdf`/`PyPDF2`，docx 需 `python-docx`。

## 排障

| 现象 | 处理 |
| --- | --- |
| 缺少 API Key | `configure --api-key-stdin` 或设置 `TRANSWEB_API_KEY` |
| 缺少 scope | 仅对应标注接口会报；写接口不靠 scope 拦截 |
| 上传失败 | 确认有 `curl`，重新运行 |
| `getAppConfig`/`agentList_zh` 失败 | 检查平台可访问与 `agentGenerator` / `appGenerator` 模板 |
| 生成结果不是 JSON | 重试；查看返回的原始输出开头 |

更细的接口字段见 [`references/api.md`](references/api.md)。

## 安全

- 不要在对话、代码或日志中回显完整 Key。
- Key 只保存在本地 `0600` 配置或环境变量中。
