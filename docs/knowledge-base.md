# TransWeb 浏览器端数字劳动力知识库

> 版本：1.2（2026-11-16 更新 Agent/Skill 模板选择）  
> 适用对象：TransWeb 平台运营、Agent/Skill 设计者、提示词工程师、前端开发者、企业 AI 应用负责人  
> 说明：本文是面向知识库/Agent 语料的结构化文档，覆盖概念、架构、数据模型、创建、使用、发布、计费、安全与运维。文中不包含任何真实 API Key。
>
> 命令约定：文中的 `scripts/transweb_ai.py`、`scripts/transweb_create.py` 均以对应技能目录为工作目录；DSH 加载技能时会给出实际路径。

---

## 目录

1. [什么是浏览器端数字劳动力](#1-什么是浏览器端数字劳动力)
2. [平台架构](#2-平台架构)
3. [数字劳动力的类型](#3-数字劳动力的类型)
4. [核心数据模型](#4-核心数据模型)
5. [账号、API Key 与权限](#5-账号api-key-与权限)
6. [使用已有数字劳动力](#6-使用已有数字劳动力)
7. [创建 Agent](#7-创建-agent)
8. [创建 Skill](#8-创建-skill)
9. [发布、可见性与权限](#9-发布可见性与权限)
10. [计费、配额与性能](#10-计费配额与性能)
11. [API 参考](#11-api-参考)
12. [文档包装与序列化规范](#12-文档包装与序列化规范)
13. [运维与故障排查](#13-运维与故障排查)
14. [典型场景与案例](#14-典型场景与案例)
15. [数字劳动力设计方法论](#15-数字劳动力设计方法论)
16. [安全、合规与治理](#16-安全合规与治理)
17. [常见问题 FAQ](#17-常见问题-faq)
18. [术语表](#18-术语表)
19. [命令与接口速查](#19-命令与接口速查)
20. [版本与维护](#20-版本与维护)

---

## 1. 什么是浏览器端数字劳动力

### 1.1 定义

**浏览器端数字劳动力**是运行在浏览器中的、可被重复调用的 AI 工作单元。它把以下要素封装成一个可打开、可执行、可分发、可计费的应用：

- **角色**：这个数字劳动力是谁，服务谁；
- **知识**：依据哪些资料、规则、边界工作；
- **技能**：能完成哪些任务，输入输出是什么；
- **界面**：用户如何输入、查看结果、继续修改；
- **模型**：由哪个模型/应用承担生成；
- **权限**：谁能用、能否公开、结果给谁看；
- **版本**：每次生成/修改如何留痕；
- **成本**：每次执行消耗多少积分。

它不是单纯的 Prompt，也不是一个本地脚本，而是“**角色 + 知识 + 工作流 + 界面 + 治理**”的封装。

### 1.2 一句话理解

> 浏览器端数字劳动力 = 一个打开网页就能工作的 AI 岗位，而不是一段需要复制粘贴的提示词。

### 1.3 与常见形态的区别

| 形态 | 交付方式 | 知识 | 界面 | 权限/计费 | 典型问题 |
| --- | --- | --- | --- | --- | --- |
| 聊天 Prompt | 复制提示词 | 靠上下文 | 通用聊天框 | 无 | 难复用、难治理 |
| SaaS | 登录 SaaS | 厂商内置 | 厂商固定 | 订阅 | 定制难、数据出域 |
| RPA | 本地/服务器流程 | 规则 | 无/弱 | 需部署 | 界面变化即失效 |
| 本地 Agent | 安装运行 | 本地文件 | 需自建 | 自行管理 | 分发、权限、成本难 |
| **TransWeb 数字劳动力** | **浏览器链接** | **知识库可关联** | **生成式 UI** | **平台统一** | 依赖平台模板/模型 |

### 1.4 核心价值

1. **零安装**：用户只需浏览器和链接；
2. **可封装**：把专家经验固化为 Agent/Skill，而不是散落提示词；
3. **可分发**：一个 `agent.html` / `skill.html` 链接即可交付；
4. **可治理**：公开/私有、创建者、版本、积分、知识来源可追踪；
5. **可组合**：多个应用可以串行执行，形成数字劳动力流水线；
6. **可迭代**：应用代码、Prompt、知识关联都可持续更新。

### 1.5 能力边界

浏览器端数字劳动力适合：

- 知识问答、咨询、教练、陪练；
- 结构化提取、总结、改写、分类；
- 生成报告、方案、PPT 大纲、教学材料；
- 多步骤内容生产流水线；
- 企业内部的轻量业务助手。

不适合直接承担：

- 需要高权限后台操作的任务；
- 需要长期常驻、定时触发的任务；
- 需要复杂事务一致性/数据库写入的任务；
- 需要绕过平台权限模型的任务。

---

## 2. 平台架构

### 2.1 浏览器运行时

TransWeb 页面由静态 Shell + 应用代码组成：

- `skill.html?id=<documentId>`：加载 Skill 应用；
- `agent.html?id=<documentId>`：加载 Agent 应用；
- `?solo=true&dataView=true&dataId=<dataId>`：打开某次生成结果的存档视图；
- 页面加载 `index.js`、`main.js`，再通过 `getDocumentApp` / `getDocumentFile` 取应用代码。

应用代码本质是一个 **Vue 单文件组件（SFC）**，在浏览器端渲染。服务端主要负责：

- 登录/API Key 鉴权；
- 文档存储与版本；
- AI 网关调用；
- 积分计费；
- 公开市场与权限。

### 2.2 应用模板

平台提供多种模板：

| 模板 | 用途 |
| --- | --- |
| `agentTemplate.vue` | Agent 聊天界面 |
| `appTemplate.vue` | Skill 通用向导/自定义页面容器 |
| `imageTemplate.vue` | 图片类应用 |
| `textImageTemplate.vue` | 图文类应用 |
| `workflow.vue` | 工作流/流水线 |

创建 Agent 时使用聊天模板；创建 Skill 时使用通用向导模板并注入自定义 HTML/CSS。

### 2.3 文档与版本

- 应用元数据存在 `pptItem` 集合；
- 应用代码存在个人 bucket 的 document 文件；
- 每次 AI 生成的结果会归档到 `questionData`；
- 一次结果对应一个 `dataId`（`questionData._id`），可生成 `dataView` 链接；
- 应用可以有多个历史版本，前端通过版本列表切换。

### 2.4 AI 网关

统一入口：

```http
POST /gpt/aiGatewayRequest
Authorization: Bearer ak_live_...
Content-Type: application/json

{
  "documentId": "<应用ID>",
  "context": "<用户输入>",
  "apiName": "深度求索",
  "model": "deepseek-v4-flash"
}
```

返回：

```json
{
  "ret": 0,
  "usage": {
    "result": "模型输出文本",
    "pointsCost": 11
  }
}
```

`usage.result` 是模型输出；`pointsCost` 是本次消耗积分。服务端会异步把结果归档到 `questionData`。

### 2.5 账号与权限

- API Key 以 `ak_live_` 开头；
- Key 绑定账号 `folderName`；
- 不同 Key 可以有不同的 scope；
- 应用有 `folderName`、`creator`、`appOwner`、`publishStatus` 等归属字段；
- 应用代码文件按 `folderName` 存 bucket。

### 2.6 数据流概览

```text
用户输入
  → 浏览器应用（Vue SFC）
  → /gpt/aiGatewayRequest
  → 模型/应用 Prompt
  → usage.result
  → 服务端归档 questionData
  → dataId
  → 结果链接 / 字符串结果
```

---

## 3. 数字劳动力的类型

### 3.1 Agent 型

**特征**

- 聊天式交互；
- 使用 `agentTemplate.vue`；
- 人设、知识、约束来自 Prompt + 知识库；
- 输出是**字符串**；
- 不生成 `dataId` 链接（以当前 `transweb-ai` 的 `run` 逻辑为准）。

**适用**

- 知识问答；
- 教练/顾问；
- 排障助手；
- 角色扮演；
- 需要多轮追问的任务。

**关键字段**

```json
{
  "documentType": "agent",
  "type": "社交",
  "knowledges": [{"id": "<questionDataId>", "name": "<知识库名称>"}]
}
```

### 3.2 Skill 型

**特征**

- 有明确输入/输出 UI；
- 使用 `appTemplate.vue` + 自定义 HTML/CSS；
- 通过四步工作流生成 Prompt 和页面；
- 输出通常是结构化内容；
- 结果归档后返回**链接**。

**适用**

- 会议纪要转待办；
- 结构化提取；
- 文案/报告生成；
- 表单式工具；
- 需要固定输出格式的任务。

**关键字段**

```json
{
  "documentType": "skill",
  "type": "创意写作类"
}
```

### 3.3 PPT/文档型

- 由官方演示文稿应用生成；
- Prompt 要求返回严格 Reveal.js JSON；
- 生成后归档并返回可打开的演示链接；
- 可导出/分享，但不是本文重点。

### 3.4 `documentType` 判定

通过：

```http
GET /user/getDocumentData?table=pptItem&key=documentId&documentId=<appId>
```

读取：

```json
{
  "ret": 0,
  "data": [
    {
      "documentId": "...",
      "documentType": "agent",
      "title": "...",
      "creator": "...",
      "publishStatus": "false"
    }
  ]
}
```

规则：

| `documentType` | 输出 |
| --- | --- |
| `agent` | 字符串结果 |
| `skill` | 链接 |
| 缺失/未知 | 按 `skill` 兼容 |

### 3.5 输出差异

**Agent**

```json
{
  "ok": true,
  "documentType": "agent",
  "result": "回答文本……",
  "steps": [
    {"appId": "...", "documentType": "agent", "result": "回答文本……"}
  ]
}
```

**Skill**

```json
{
  "ok": true,
  "documentType": "skill",
  "link": "https://transweb.cn/?solo=true&dataView=true&dataId=...&id=...",
  "dataId": "..."
}
```

---

## 4. 核心数据模型

### 4.1 `pptItem` 应用记录

常用字段：

| 字段 | 说明 |
| --- | --- |
| `_id` | MongoDB 主键 |
| `documentId` | 32 位十六进制应用 ID |
| `document` | 应用代码文件路径，如 `/bucket/personal/<folder>/document/<id>` |
| `name` / `title` | 应用名称 |
| `description` | 详细描述 |
| `introduce` | 简介 |
| `type` | 应用类型（如社交/创意写作类） |
| `category` | 分类 |
| `grades` | 年级/适用对象（字符串化数组） |
| `tags` | 标签（字符串化数组） |
| `icon` | 图标 |
| `prompt` | 应用系统提示词 |
| `appName` | 模板/应用名，如 `appGenerator` |
| `appLabel` | 显示名，如“创智通” |
| `appAgent` | 发布者/模板发布者 folderName |
| `appOwner` | 发布者显示名 |
| `folderName` | 当前归属账号 folderName |
| `creator` | 创作者显示名（API Key 所有者） |
| `publishStatus` | `"true"` 已公开 / `"false"` 私有 |
| `documentType` | `agent` / `skill` |
| `knowledges` | Agent 关联的知识库存档 |
| `apiName` / `model` | 模型供应方与模型名 |
| `usageCount` | 使用次数 |
| `time` | 创建/更新时间戳 |
| `_delete` | 软删除标记 |

### 4.2 `questionData` 结果存档

每次 `aiGatewayRequest` 的结果会被归档：

| 字段 | 说明 |
| --- | --- |
| `_id` | 结果 ID，即 `dataId` |
| `documentId` | 应用 ID |
| `result` / `rawContent` | 生成结果 |
| `isShare` | 是否可公开访问 |
| `folderName` | 结果归属 |
| `time` | 生成时间 |

结果链接：

```text
https://transweb.cn/?solo=true&dataView=true&dataId=<dataId>&id=<documentId>
```

### 4.3 应用代码包装

应用代码不是裸 Vue 文件，而是包装成：

```js
transweb_<documentId>({
  "content": [
    {
      "content": {
        "title": "<标题>",
        "description": "<描述>",
        "code": "<JS escape 后的 Vue SFC>"
      }
    }
  ],
  "app": {
    "name": "agentGenerator | appGenerator",
    "publishInfo": {
      "folderName": "4140329349",
      "appName": "appGenerator",
      "user": "创博",
      "avatar": "https://transweb.cn/webApps/document/logo.png"
    },
    "meta": {"label": "创智通"}
  },
  "documentMeta": {
    "documentId": "<id>",
    "folderName": "<当前账号 folder>",
    "title": "<标题>"
  }
});
```

浏览器端会：

1. 读取文件；
2. 用 `WebTool.extractContentInBrackets` 提取括号内容；
3. `eval` 成 JS 对象；
4. 用 `WebTool.copyObject(..., true)` 反解字符串；
5. 取 `content[0].content.code` 渲染 Vue SFC。

### 4.4 `app` 模板数据

创建时先取：

```http
GET /admin/getAppConfig?callback=cb
```

解析 `publishInfo`：

```json
{
  "folderName": "4140329349",
  "appName": "appGenerator",
  "user": "创博",
  "avatar": "https://transweb.cn/webApps/document/logo.png"
}
```

再用 `publishInfo.folderName` 取模板：

```http
GET /user/getAgentData?agent=<publishInfo.folderName>&lang=zh
```

`data.agentList_zh` 是 JSON 字符串，解析后按创建类型选模板：

- Agent：`name === "agentGenerator"`
- Skill：`name === "appGenerator"`

`publishInfo.appName` 通常是 `appGenerator`，但创建 Agent 时不再用它选模板。

**注意区分两个 folderName：**

- `publishInfo.folderName`：模板发布者，用于 `getAgentData` 的 `agent` 参数；
- 当前账号 `folderName`：用于 bucket 上传、`pptItem.folderName`、文档归属。

### 4.5 链接格式

| 场景 | 格式 |
| --- | --- |
| Agent 应用 | `https://transweb.cn/agent.html?id=<documentId>` |
| Skill 应用 | `https://transweb.cn/skill.html?id=<documentId>` |
| 结果存档 | `https://transweb.cn/?solo=true&dataView=true&dataId=<dataId>&id=<documentId>` |
| 公开市场 | `https://transweb.cn/skillHub.html`（以实际页面为准） |

---

### 4.6 appEditor 中的创作者与发布状态

`appEditor.vue` 是应用元数据编辑界面，其中：

- “创作者”显示 `currentSettings.creator`；
- `currentSettings` 由 `main.js` 从 `/user/getDocumentData` 的 `doc.creator` 等字段组装；
- 修改创作者会通过 `setDocumentStatus` 写入 `creator`；
- 发布开关对应 `publishStatus`；
- 应用图片、税率、价格等也在该界面维护。

因此，创建应用时写入的 `creator` 会直接回显在 appEditor；`appOwner` 是模板发布者字段，不等同于“创作者”。

## 5. 账号、API Key 与权限

### 5.1 创建 API Key

登录 TransWeb 后创建：

```js
fetch("/apiKey/createApiKey", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "digital-labor",
    scopes: ["ai:chat", "account:read", "doc:read"]
  })
}).then(r => r.json()).then(console.log);
```

Key 前缀为 `ak_live_`。

### 5.2 Scope（重要：当前只有少数接口实际校验）

> 现状校正：API Key 的 scope **不是对所有接口生效**。平台只在接口显式声明 `requiredScope` 时校验；未声明的接口只要求“API Key 有效”，不再检查 scope。`doc:write`、`points:read`、`points:transfer` 等 scope 目前在代码里没有对应接口，实际不会产生权限差异。

#### 实际会校验 scope 的接口

| Scope | 拦截的接口 | 说明 |
| --- | --- | --- |
| `ai:chat` | `POST /gpt/aiGatewayRequest`、`POST /gpt/aiStreamRequest` | 执行应用/模型调用 |
| `doc:read` | `POST /user/getLoginedData`、`GET /user/getQuestionData`、`GET /user/getInteractionList`、`GET /user/getSubscriptionsData` | 列自己的应用、存档、互动、订阅 |
| `account:read` | `GET /user/getUserData`、`GET /user/getPartnerData`、`GET /user/getLoginInfo`、`POST /user/switchRoleItem`、`POST /user/cutPoints`、`POST /user/_putQuestionData` | 账号/合伙人/角色/积分相关 |

#### 不校验 scope 的接口（有效 Key 即可，另有归属校验）

- `GET /user/getPublishedList`（公开市场）
- `GET /user/getDocumentData`（应用元数据）
- `GET /user/getDocumentFile`（应用代码）
- `GET /user/getAgentData`（模板/账号展示名）
- `POST /user/publishPptItem`（创建/更新应用记录）
- `POST /user/setDocumentStatus`（发布状态、creator、documentType、knowledges）
- `GET /user/queryQuestionData`（结果存档）
- `POST /user/deleteDocumentData`（软删除）
- `PUT /bucket/personal/<folder>/document/<id>`（代码上传）
- `GET /admin/getAppConfig`（模板发布者配置）

这些接口仍会检查：

- API Key 是否有效；
- `folderName` 是否匹配（部分接口）；
- 文档是否属于当前账号；
- 是否登录（bucket 需要会话 cookie）。

#### 实际使用建议

| 目标 | 实际需要 |
| --- | --- |
| 执行应用 | `ai:chat` |
| 列自己的应用 | `doc:read`（`getLoginedData`） |
| 读取账号信息 / `whoami` | `account:read` |
| 创建 Agent/Skill | 有效 Key + `ai:chat`；`doc:read` 用于取当前 `folderName`；`doc:write` 当前不生效 |
| 发布/改状态/上传 | 有效 Key + 会话 cookie；scope 不拦 |

#### 安全含义

1. **不要把 scope 当作完整安全边界**。有 `doc:read` 的 Key 也可能调用 `publishPptItem`、`setDocumentStatus` 等未标注接口（仍受归属检查）。
2. 不能靠“没有 `doc:write`”阻止创建或修改；平台目前没有把 `doc:write` 接到写接口。
3. 需要隔离时，使用**不同账号/不同 Key**，并依赖归属、审计和人工流程，而不是只靠 scope。
4. 定期轮换 Key；泄露的 Key 即使 scope 很少，也可能读取公开接口或调用未标注接口。

### 5.3 配置

```bash
# 保存 Key
python3 scripts/transweb_ai.py configure --api-key-stdin --verify

# 查看（Key 已脱敏）
python3 scripts/transweb_ai.py config show

# 多 profile
python3 scripts/transweb_ai.py configure --profile work --api-key-stdin
python3 scripts/transweb_ai.py config use work
```

配置默认位置：

- 项目：`<project>/.dsh/transweb-ai.json`
- 全局：`~/.dsh/transweb-ai.json`
- 其他平台：`~/.config/transweb-ai/config.json`

`transweb-ai` 与 `transweb-create` 共用同一份配置。

### 5.4 切换服务地址

```bash
# 永久切换（共享配置）
python3 scripts/transweb_ai.py config base http://localhost

# 查看
python3 scripts/transweb_ai.py config base

# 单次
python3 scripts/transweb_ai.py list --base-url http://localhost

# 环境变量
TRANSWEB_BASE_URL=http://localhost python3 scripts/transweb_ai.py list
```

恢复：

```bash
python3 scripts/transweb_ai.py config base https://transweb.cn
```

本地服务需要实现相同的 `/user/*`、`/gpt/*`、`/admin/*`、bucket 上传和 API Key 认证。

### 5.5 所有者、创作者与发布者

| 字段 | 来源 | 用途 |
| --- | --- | --- |
| `folderName` | 当前账号 | 文档归属、bucket 路径 |
| `creator` | `getAgentData?agent=<当前账号>` 的 `name_zh` | appEditor“创作者”显示 |
| `appOwner` | `publishInfo.user`（模板发布者） | 模板/发布者标识 |
| `appAgent` | `publishInfo.folderName` | 模板发布者 folder |

`appEditor.vue` 显示的是 `currentSettings.creator`，因此需要把 `creator` 写成实际 API Key 所有者名称。

---

## 6. 使用已有数字劳动力

### 6.1 列出应用

```bash
python3 scripts/transweb_ai.py list --query "商业方案" --limit 10
python3 scripts/transweb_ai.py list --source published --query "数据分析" --limit 10
python3 scripts/transweb_ai.py list --source both --query "PPT" --limit 10
python3 scripts/transweb_ai.py list --all --query "内部工具" --limit 10
```

来源优先级：

1. `getLoginedData`：自己账号下的应用；
2. 没有匹配时回退 `getPublishedList`：公开市场。

`--with-document-type` 可逐个补查 `documentType`。

### 6.2 单例执行

```bash
python3 scripts/transweb_ai.py run \
  --ids <appId> \
  --input "你的需求" \
  --json
```

### 6.3 链式执行

```bash
python3 scripts/transweb_ai.py run \
  --ids <appId1>,<appId2> \
  --input "为一家 SaaS 公司做年度方案并生成汇报 PPT" \
  --json
```

链式输入模式：

| 模式 | 下一步输入 |
| --- | --- |
| `result`（默认） | 上一步输出 |
| `requirement` | 原始需求 |
| `both` | 原始需求 + 上一步输出 |

### 6.4 执行前类型判断

`run` 对每个 ID：

```text
getDocumentData(documentId)
  → documentType
  → agent: 生成后直接返回字符串
  → skill: 生成后查询存档、设置权限、返回链接
```

### 6.5 结果链接

Skill 结果：

```text
https://transweb.cn/?solo=true&dataView=true&dataId=<dataId>&id=<appId>
```

Agent 结果：直接返回 `usage.result` 字符串，不生成链接。

### 6.6 访问权限

- Skill 结果默认设置 `questionData.isShare=true`，并匿名验证；
- `--no-share` 可关闭；
- 应用本身是否公开由 `pptItem.publishStatus` 控制，与结果链接访问是两件事。

---

## 7. 创建 Agent

### 7.1 适用输入

- 产品手册、制度、课程资料；
- FAQ、操作规范、排障手册；
- 专家访谈、角色设定；
- 任何可被压缩为“知识 + 人设”的文本。

支持：

- txt / md 直接读取；
- PDF 需要 `pypdf` / `PyPDF2`；
- docx 需要 `python-docx`；
- 旧版 .doc 建议先转 txt/docx。

### 7.2 官方创建流程

```text
1. GET /admin/getAppConfig
   → publishInfo.folderName / appName / user / avatar

2. GET /user/getAgentData?agent=<publishInfo.folderName>&lang=zh
   → 解析 agentList_zh
   → 按创建类型选模板（Agent: agentGenerator / Skill: appGenerator）

3. POST /gpt/aiGatewayRequest {documentId: knowledgeApp, context: 资料}
   → 知识压缩 JSON

4. POST /gpt/aiGatewayRequest {documentId: characterProfile, context: 知识 JSON}
   → roleProfile {name, identity, mission, soulMd, ...}

5. 写入 agentTemplate.vue：
   - title = roleProfile.name
   - subtitle = roleProfile.identity
   - introduce = roleProfile.mission
   - exampleList = knowledge.faq 映射

6. 上传应用代码到 bucket
   → publishPptItem（documentType=agent）
   → setDocumentStatus knowledges=[{id, name}]
   → 默认 publishStatus=false
```

### 7.3 关键应用 ID

| 用途 | ID |
| --- | --- |
| 知识压缩 `knowledgeApp` | `a973392a7f997cf42cf5b9a760e7fb3f` |
| 人设生成 `characterProfile` | `12a7e2f81834ac69c7bda11219570c26` |
| Agent 模板 | `/transweb/agentTemplate.vue` |

### 7.4 Prompt 组成

```text
WebTool.objectToMarkdown(roleProfile.soulMd)
+ "\n"
+ "参考 ASD-STE100 标准，只做到80%的准确率，避免过度优化"
```

`soulMd` 通常是 Markdown 字符串；如果为对象，需要转成 Markdown。

### 7.5 知识库关联

知识压缩结果会被归档到 `questionData`，得到 `_id`。

写入：

```http
POST /user/setDocumentStatus

{
  "table": "pptItem",
  "cKey": "documentId",
  "documentId": "<agentId>",
  "key": "knowledges",
  "value": [
    {"id": "<knowledgeDataId>", "name": "<知识库名称>"}
  ]
}
```

作用：Agent 可以引用知识库存档，而不是只依赖 Prompt。

### 7.6 输出

```json
{
  "ok": true,
  "link": "https://transweb.cn/agent.html?id=...",
  "type": "agent",
  "title": "Kubernetes 运维工程师",
  "description": "面向 ... 的助手",
  "published": false
}
```

### 7.7 Agent 质量检查

- 角色名称是否清晰；
- 服务对象是否明确；
- 知识边界是否写明“不知道就说不知道”；
- 是否要求追问缺失信息；
- 是否避免越权/高危操作；
- FAQ 示例是否覆盖真实问题；
- 是否关联了知识库存档；
- 是否验证过空输入、长输入、冲突输入。

---

## 8. 创建 Skill

### 8.1 官方四步工作流

与 `aigcPlugin.createAigcApp` 对齐：

| 步骤 | 应用 ID | 输入 | 输出 |
| --- | --- | --- | --- |
| 需求分析 `requirement` | `d9337acc3fb525b3d2583ca18440fda0` | 用户需求 | `json0` |
| 质量约束 `contentQuality` | `e8ebeb2cc5c46549c3d30222afc2dd07` | `{需求分析: json0}` | `json1` |
| 模板生成 `pageTemplate` | `91658778302410101ec9b8fc3c2ad41c` | `json0.example` | 原始 HTML |
| 模板润色 `improveTemplate` | `dc6286ffb169f8b8f156ab5f87e9bf8d` | `{模板生成, 质量约束}` | `json3 {html, css}` |

### 8.2 输入输出字段

`json0`：

```json
{
  "title": "",
  "name": "",
  "introduce": "",
  "type": "",
  "category": "",
  "inputType": "text",
  "icon": "",
  "grades": "",
  "tags": "",
  "description": "",
  "struct": "",
  "example": {}
}
```

`json1`：

```json
{
  "role": "",
  "constraints": {},
  "requirements": {},
  "input": "",
  "icon": "",
  "inputExamples": []
}
```

`json3`：

```json
{
  "html": "",
  "css": ""
}
```

### 8.3 Prompt 结构

```text
# Role
{json1.role}

# Objective
{json0.description}

# JSON Output Enforcement
...严格 JSON 约束...

# Constraints
{json1.constraints}

# Requirements
{json1.requirements}

# Output Schema
{json0.struct}

# Output Example
{json0.example}
```

### 8.4 自定义页面

用 `json3.html` + `json3.css` + `json0.example` 生成：

```vue
<template>
  <div class="rootContainerItem tw-w-full tw-h-full tw-p-4 tw-overflow-auto">
    {json3.html}
  </div>
</template>
<script>
export default {
  name: "-",
  data() {
    return {
      accountData: {json0.example}
    };
  }
};
</script>
<style>
{json3.css}
</style>
```

再转成 data URL，绑定 `appTemplate.vue` 的 `{{ content }}`。

### 8.5 模板绑定

需要替换/写入：

- `title`
- `introduce`
- `defaultTemplate`（URI 编码后的 Prompt）
- `inputPlaceholder`（`json1.input`）
- `icon`（`json1.icon`）
- `exampleList`（`json1.inputExamples`）
- `query.documentId`

### 8.6 输出

```json
{
  "ok": true,
  "link": "https://transweb.cn/skill.html?id=...",
  "type": "skill",
  "title": "会议待办卡片",
  "description": "...",
  "published": false
}
```

### 8.7 Skill 质量检查

- 输入字段是否明确；
- 输出 JSON 是否与 `accountData` 字段一一对应；
- 空值/缺字段/类型错误是否处理；
- 自定义页面是否具备空态、加载态、错误态；
- 是否避免自动触发 AI；
- 是否通过 `JSON.parse` 和 Vue 渲染测试；
- 是否验证了 3 个以上真实样例。

---

## 9. 发布、可见性与权限

### 9.1 默认私有

创建时写：

```json
{"key": "publishStatus", "value": "false"}
```

效果：

- 不出现在 `getPublishedList`；
- 不出现在公开市场/他人列表；
- 直接链接仍然可以打开（取决于文档访问策略）；
- 需要全局可见时显式加 `--publish`。

### 9.2 公开

```bash
python3 scripts/transweb_create.py agent --file material.md --publish
python3 scripts/transweb_create.py skill --input "需求" --publish
```

或更新已有应用：

```http
POST /user/setDocumentStatus

{
  "table": "pptItem",
  "cKey": "documentId",
  "documentId": "<id>",
  "key": "publishStatus",
  "value": "true"
}
```

### 9.3 直接链接

- Agent：`/agent.html?id=<documentId>`
- Skill：`/skill.html?id=<documentId>`

`publishStatus=false` 不等于“绝对保密”；链接可能仍可访问。敏感应用应删除或配合访问控制策略。

### 9.4 结果链接

结果链接通过 `dataId` 指向一次生成存档：

```text
/?solo=true&dataView=true&dataId=<dataId>&id=<documentId>
```

默认 `isShare=true`，匿名可验证；`--no-share` 可关闭。

### 9.5 治理建议

- 公开前检查 Prompt 中是否包含敏感信息；
- 不要在前端代码/Prompt 中放密钥；
- 为不同团队使用不同 profile/Key；
- 定期清理测试应用和无效版本；
- 为公开应用建立负责人、用途、数据来源和下线机制。

---

## 10. 计费、配额与性能

### 10.1 积分

每次 `aiGatewayRequest` 返回 `usage.pointsCost`，按模型/应用/长度计费。

- Agent 创建通常包含知识压缩 + 人设生成两次调用；
- Skill 创建包含四步工作流；
- 使用应用每次调用都计费；
- 链式执行按步数累计。

### 10.2 成本控制

- 知识库先去重、压缩；
- 长文档分段，但不要过度切碎；
- 链式执行只在必要时使用；
- 失败重试前确认是否已扣费；
- 生产应用设置预算/额度；
- 高成本 Skill 先小样本验证。

### 10.3 性能

- 模型响应时间占主要部分；
- 存档查询有延迟，`--wait` 可延长；
- 大文件上传/解析增加耗时；
- 公开页面加载受浏览器/网络影响。

### 10.4 重试

四步工作流/知识生成可能返回非 JSON。生产实现应：

- 校验 JSON；
- 失败时重试有限次数；
- 保留原始输出开头便于排查；
- 避免无限重试导致重复扣费。

---

## 11. API 参考

> Scope 提示：本章部分接口没有 `requiredScope`，只要求有效 Key；实际校验范围以 5.2 节为准。

### 11.1 `GET /admin/getAppConfig`

返回 JSONP：

```text
typeof cb === 'function' && cb({...});
```

用途：取 `publishInfo`（模板发布者信息）。

### 11.2 `GET /user/getAgentData?agent=<folderName>&lang=zh`

返回账号/模板数据：

```json
{
  "ret": 0,
  "data": {
    "folderName": "...",
    "name_zh": "...",
    "account": "...",
    "agentList_zh": "[...]"
  }
}
```

用途：

- 取模板列表；
- 取当前 API Key 所有者名称 `name_zh`。

### 11.3 `POST /user/getLoginedData`

请求：

```json
{
  "table": "pptItem",
  "pageSize": 100,
  "pageNo": 1,
  "condition": {"publishStatus": "true"}
}
```

用途：取自己账号下的应用。

返回 `data[].documentId`。

### 11.4 `GET /user/getPublishedList`

用途：公开市场应用列表。

返回 `ret`、`total`、`data[].documentId`。

### 11.5 `GET /user/getDocumentData`

```http
GET /user/getDocumentData?table=pptItem&key=documentId&documentId=<id>
```

用途：读取应用元数据，包括 `documentType`、`creator`、`publishStatus`、`knowledges`。

### 11.6 `GET /user/getDocumentFile?documentId=<id>`

用途：读取应用代码包装文件。

### 11.7 `POST /gpt/aiGatewayRequest`

请求：

```json
{
  "documentId": "<appId>",
  "context": "<input>",
  "apiName": "深度求索",
  "model": "deepseek-v4-flash"
}
```

返回 `usage.result`、`usage.pointsCost`。

### 11.8 `GET /user/queryQuestionData`

用途：查询生成结果存档，找到 `dataId`。

### 11.9 `POST /user/setDocumentStatus`

用途：更新 `pptItem` 字段：

- `publishStatus`
- `creator`
- `knowledges`
- `documentType`

请求：

```json
{
  "table": "pptItem",
  "cKey": "documentId",
  "documentId": "<id>",
  "key": "publishStatus",
  "value": "false"
}
```

### 11.10 `POST /user/publishPptItem`

用途：创建/更新应用记录。

关键字段：

```json
{
  "id": "<documentId>",
  "document": "/bucket/personal/<folder>/document/<documentId>",
  "name": "标题",
  "title": "标题",
  "description": "描述",
  "introduce": "简介",
  "prompt": "系统 Prompt",
  "appName": "agentGenerator | appGenerator",
  "appLabel": "Agent | Skill",
  "appAgent": "4140329349",
  "appOwner": "创博",
  "avatar": "...",
  "folderName": "<当前账号>",
  "creator": "<API Key 所有者>",
  "documentType": "agent | skill",
  "publishStatus": "false",
  "table": "pptItem",
  "apiName": "深度求索",
  "model": "deepseek-v4-flash"
}
```

### 11.11 Bucket 上传

```http
PUT /bucket/personal/<folderName>/document/<documentId>
Content-Type: multipart/form-data
file=@document.txt
```

注意：bucket 中间件在 API Key 自动登录之前执行，只有 `Authorization` 头不够；需要先调用任意 `/user/*` 接口获取 `connect.sid` 会话 cookie，再带 cookie + API Key 头上传。

### 11.12 `POST /user/deleteDocumentData`

软删除：

```json
{"key": "documentId", "documentId": "<id>"}
```

---

## 12. 文档包装与序列化规范

### 12.1 为什么不能直接存 JSON

浏览器端用：

```js
/\(([^)]*)\)/
```

提取 `transweb_<id>( ... );` 中的内容。如果 JSON 字符串里出现字面量 `)`，提取会提前截断，`eval` 失败。

### 12.2 解决：所有字符串 JS `escape()`

| 字符 | 编码 |
| --- | --- |
| `)` | `%29` |
| `(` | `%28` |
| 空格 | `%20` |
| 中文 | `%uXXXX` |
| emoji | `%uD83D%uDE00` |

写文件前保证包装内部没有字面量 `)`。

### 12.3 客户端反解

`WebTool.copyObject(data, true)` 会对字符串执行 `unescape`，恢复原始内容。

### 12.4 常见错误

- 只编码 `code`，标题/描述中的 `)` 导致截断；
- 对已编码的 `code` 再次 `quote`，导致双重编码；
- `exampleList` 替换多出 `],`，导致 Vue `data()` 语法错误；
- 模板字段锚点变化，替换失败但未报错。

### 12.5 校验清单

- 包装内无字面量 `)`；
- `JSON.parse` 可解析；
- `content[0].content.code` 是 Vue SFC；
- 页面无 console 异常；
- 标题/描述中的括号显示正常。

---

## 13. 运维与故障排查

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| 401/未登录 | Key 无效或未配置 | 重新 configure |
| 缺少 scope | 仅 `requiredScope` 接口会报；创建/写入接口通常不校验 | 按 5.2 补 `doc:read` / `ai:chat` / `account:read` |
| 积分不足 | 余额/额度 | 充值或减少调用 |
| `getDocumentData` 为空 | ID 错/无权限/已删除 | 检查 ID、归属、`_delete` |
| `documentType` 为空 | 旧数据未写字段 | `setDocumentStatus` 补 `agent`/`skill` |
| Agent 返回链接 | 旧逻辑/类型缺失 | 补 `documentType=agent` |
| Skill 返回字符串 | 类型缺失/误判 | 检查 `documentType` |
| 上传失败 | 无 curl/无 cookie 会话 | 确认 curl，先建立 session |
| 创建后页面空白 | 代码序列化/SFC 语法错误 | 检查 console、括号、`exampleList` |
| 标题含括号后解析失败 | 未 JS escape | 全字符串 escape |
| 创建后全局可见 | 未设 `publishStatus=false` | `setDocumentStatus` 或加 `--publish` 逻辑 |
| 创建者显示 DSH | `creator` 未取 owner | 写 `name_zh` |
| 模板找不到 | 目标模板不存在（`agentGenerator` / `appGenerator`） | 检查 `agentList_zh` |
| `getAppConfig` 失败 | 服务地址错/本地服务未实现 | 检查 base URL |
| 结果链接打不开 | `isShare`/存档未就绪 | 查 `questionData`，加 `--wait` |
| 本地服务请求失败 | 接口/认证/CORS 未实现 | 补齐同构接口 |

---

## 14. 典型场景与案例

### 14.1 知识型 Agent：Kubernetes 运维助手

**资料**：Pod、Deployment、Service、Events、日志、排障顺序。

**流程**：

1. knowledgeApp 压缩知识；
2. characterProfile 生成“运维工程师”人设；
3. 写入 Agent 模板；
4. 关联知识库存档；
5. 用户提问返回字符串。

**价值**：把排障手册变成可对话的专家，不需要用户自己翻文档。

### 14.2 结构化 Skill：会议待办卡片

**需求**：把会议记录转成三条待办，每条含任务、负责人、截止时间。

**流程**：

1. 四步工作流生成 Prompt 和 HTML/CSS；
2. 自定义卡片 UI；
3. 用户输入会议记录；
4. AI 返回 JSON；
5. 页面渲染卡片；
6. 结果归档，返回链接。

**价值**：把“整理会议纪要”变成固定输出格式的轻应用。

### 14.3 PPT 生成

**需求**：年度汇报/商业方案/课程课件。

**流程**：

1. 调用官方演示文稿应用；
2. 严格 Reveal.js JSON；
3. 归档结果；
4. 返回演示链接。

### 14.4 链式流水线

```text
商业方案 Skill
  → 生成方案内容
  → PPT Skill
  → 生成演示文稿
```

注意：链式步骤之间没有强制 schema，下游需要能处理上游输出；必要时使用 `--chain-mode requirement` 或 `both`。

---

## 15. 数字劳动力设计方法论

### 15.1 先定义岗位，再写 Prompt

用“数字劳动力卡片”描述：

```text
名称：
角色：
服务对象：
核心任务：
输入：
输出：
知识来源：
禁止事项：
升级/转人工条件：
成本预算：
负责人：
版本：
```

### 15.2 任务拆解

- 单一职责优先；
- 一个 Skill 只解决一个可验收任务；
- 复杂任务拆成多个应用链式执行；
- 不要让一个 Prompt 同时做“理解、检索、计算、写作、排版”。

### 15.3 输入/输出契约

- 输入：必填/选填、格式、长度、缺失处理；
- 输出：字段、类型、顺序、空值、错误码；
- Agent：明确“何时追问、何时拒答”；
- Skill：输出 JSON 必须与 `accountData` 完全一致。

### 15.4 知识边界

- 只依据给定知识回答；
- 不知道时明确说不知道；
- 区分“知识库事实”和“模型推断”；
- 对高风险操作要求确认/转人工。

### 15.5 Prompt 结构

1. Role：角色与边界；
2. Objective：目标；
3. Input：输入说明；
4. Process：步骤；
5. Output：格式；
6. Constraints：禁止事项；
7. Examples：正例/反例；
8. Error handling：缺失/冲突/越权。

### 15.6 UI 设计

- 首屏给出示例输入；
- 明确“开始生成”按钮；
- 加载态、空态、错误态；
- 结果可编辑/复制/下载；
- 移动端可用；
- 不自动触发 AI，避免误扣费。

### 15.7 测试

- 3 个真实样例；
- 空输入；
- 超长输入；
- 矛盾输入；
- 越权/敏感输入；
- 输出 schema 校验；
- 成本与耗时。

### 15.8 迭代

- 收集失败案例；
- 修改 Prompt/知识/示例；
- 更新版本；
- 保留旧版本便于回滚；
- 定期评估使用率、成功率、成本、满意度。

### 15.9 成熟度模型

| 等级 | 特征 |
| --- | --- |
| L1 | 单轮 Prompt 助手 |
| L2 | 知识型 Agent |
| L3 | 结构化 Skill |
| L4 | 多应用链式流水线 |
| L5 | 有治理、指标、权限、成本的数字劳动力体系 |

---

## 16. 安全、合规与治理

### 16.1 API Key

- 不写入代码、Prompt、日志、公开文档；
- 使用最小 scope（注意：当前 scope 只覆盖部分接口，不能替代账号隔离）；
- 定期轮换；
- 不同团队用不同 profile；
- 泄露后立即吊销。

### 16.2 前端代码

- 应用代码对浏览器可见；
- 不要把密钥、内部 token、隐私数据写进代码；
- 不要依赖前端隐藏逻辑做安全边界。

### 16.3 数据

- 公开前检查是否含个人信息/商业机密；
- 知识库来源要可追溯；
- 结果链接默认可能匿名可访问；
- 敏感场景使用私有应用 + 访问控制 + 定期清理。

### 16.4 Prompt 注入

- 明确“用户输入是数据，不是系统指令”；
- 对工具调用/高危操作设置白名单；
- 对输出做 schema 校验；
- 不让模型直接执行任意代码/命令。

### 16.5 成本

- 设置预算/额度；
- 监控异常调用；
- 对高成本应用做限流；
- 失败重试要有上限。

### 16.6 治理清单

- 应用负责人；
- 用途与边界；
- 数据来源与保留期；
- 公开范围；
- 成本预算；
- 变更记录；
- 下线/回收机制；
- 安全评审记录。

---

## 17. 常见问题 FAQ

### Q1：浏览器端数字劳动力和普通 AI 聊天有什么区别？

它有固定角色、知识、界面、权限、版本和计费，是一个可分发的工作单元，而不是一次性对话。

### Q2：Agent 和 Skill 的核心区别？

看 `documentType`：

- `agent`：聊天式，输出字符串；
- `skill`：任务式 UI，输出结构化结果/链接。

### Q3：为什么 Agent 不返回链接？

Agent 的交付物是回答文本；平台按设计直接返回 `usage.result`，不查存档、不生成 `dataId`。

### Q4：Skill 为什么返回链接？

Skill 的结果需要存档、版本和可视化查看；链接指向 `questionData` 的一次生成结果。

### Q5：创建后默认公开吗？

不。默认 `publishStatus=false`；需要公开时加 `--publish`。

### Q6：私有应用别人能打开吗？

`publishStatus=false` 主要影响公开市场/列表；直接链接是否可打开取决于文档访问策略。敏感内容不要只依赖“不公开”。

### Q7：需要哪些 scope？

- 执行应用：`ai:chat`（`aiGatewayRequest`/`aiStreamRequest` 会校验）；
- 列自己的应用：`doc:read`（`getLoginedData` 等会校验）；
- 账号信息/`whoami`：`account:read`；
- 创建/发布：有效 Key + `ai:chat`；`doc:read` 用于取 `folderName`；`doc:write` 当前没有接口使用；
- 公开市场、`getDocumentData`、`publishPptItem`、`setDocumentStatus`、bucket 上传等**不校验 scope**，但仍检查 Key 有效性和归属。

因此 scope 只覆盖部分接口，不能当作完整写权限边界。

### Q8：如何切换到本地服务？

```bash
python3 scripts/transweb_ai.py config base http://localhost
```

两个技能共用该地址；也可用 `--base-url` 或 `TRANSWEB_BASE_URL` 只影响单次。

### Q9：创建失败会扣费吗？

模型调用成功即可能计费；失败重试前先确认。脚本会尽量在上传/发布前完成生成，避免无意义记录。

### Q10：知识库如何关联到 Agent？

把 knowledgeApp 存档 `_id` 写入 `pptItem.knowledges`：

```json
[{"id": "<dataId>", "name": "<知识库名称>"}]
```

### Q11：应用代码存在哪里？

个人 bucket：

```text
/bucket/personal/<folderName>/document/<documentId>
```

### Q12：为什么上传需要 cookie？

bucket 中间件在 API Key 自动登录之前执行；需要先建立 `connect.sid` 会话，再带 cookie + API Key 上传。

### Q13：如何修改创作者显示？

写 `pptItem.creator`；appEditor 的“创作者”读取该字段。创建时取 API Key 所有者的 `name_zh`。

### Q14：如何删除/下线？

`deleteDocumentData` 软删除；同时清理 bucket 文件、公开状态和知识关联。

### Q15：支持哪些输入？

Agent 支持 txt/md/PDF/docx；Skill 通常接收文本需求；PPT 接收大纲/需求。

### Q16：浏览器端需要自己的后端吗？

平台已提供 AI 网关、存储、鉴权、计费；只有在需要额外业务系统集成时才需要自建后端。

### Q17：如何做版本管理？

每次生成归档为 `questionData`，`dataId` 对应版本；应用代码/Prompt 更新后保留历史版本。

### Q18：公开链接安全吗？

链接可能匿名可访问；不要放敏感数据。公开前做内容审查，必要时使用私有应用。

### Q19：为什么创建结果页面空白？

常见原因：包装字符串未 escape、SFC 语法错误、`exampleList` 多出 `],`、模板字段替换失败。看浏览器 console。

### Q20：平台模板会变吗？

会。创建逻辑依赖模板锚点/字段；模板更新后需要重新验证并调整替换逻辑。

---

## 18. 术语表

| 术语 | 含义 |
| --- | --- |
| 数字劳动力 | 封装了角色、知识、技能、界面、权限、计费的 AI 工作单元 |
| Agent | 聊天式数字劳动力，输出字符串 |
| Skill | 任务式数字劳动力，输出结构化结果/链接 |
| `documentId` | 应用 ID，32 位十六进制 |
| `dataId` | 一次生成结果的存档 ID（`questionData._id`） |
| `documentType` | `agent` / `skill` |
| `publishStatus` | 是否公开到市场 |
| `creator` | 创作者显示名 |
| `folderName` | 账号/文档归属目录 |
| `publishInfo` | 模板发布者信息 |
| `agentList_zh` | 模板 JSON 字符串数组 |
| `agentGenerator` | Agent 模板应用名 |
| `appGenerator` | Skill 模板应用名 |
| `knowledgeApp` | 知识压缩应用 |
| `characterProfile` | 人设生成应用 |
| `aigcWorkflow` | Skill 四步工作流 |
| `appTemplate.vue` | Skill 通用模板 |
| `agentTemplate.vue` | Agent 聊天模板 |
| `questionData` | 生成结果存档集合 |
| `pptItem` | 应用元数据集合 |
| AI 网关 | `/gpt/aiGatewayRequest` |
| Bucket | 个人文档存储 |
| API Key | `ak_live_...` 访问凭证 |
| Scope | Key 权限范围 |
| Wrapper | `transweb_<id>(...)` 文档包装 |
| `extractContentInBrackets` | 提取包装括号内容的前端方法 |

---

## 19. 命令与接口速查

### 19.1 使用技能 `transweb-ai`

```bash
python3 scripts/transweb_ai.py configure --verify
python3 scripts/transweb_ai.py config base http://localhost
python3 scripts/transweb_ai.py list --query "商业方案" --limit 10
python3 scripts/transweb_ai.py list --with-document-type --limit 5
python3 scripts/transweb_ai.py run --ids <id> --input "需求" --json
python3 scripts/transweb_ai.py run --ids <id1>,<id2> --input "需求" --json
python3 scripts/transweb_ai.py ppt --input "做一个年度汇报 PPT" --json
```

### 19.2 创建技能 `transweb-create`

```bash
python3 scripts/transweb_create.py configure --verify
python3 scripts/transweb_create.py agent --file material.md --json
python3 scripts/transweb_create.py agent --input "资料正文" --json
python3 scripts/transweb_create.py skill --input "需求描述" --json
python3 scripts/transweb_create.py agent --file material.md --publish
```

### 19.3 关键接口

```text
GET  /admin/getAppConfig
GET  /user/getAgentData?agent=<folder>&lang=zh
POST /user/getLoginedData
GET  /user/getPublishedList
GET  /user/getDocumentData?table=pptItem&key=documentId&documentId=<id>
GET  /user/getDocumentFile?documentId=<id>
POST /gpt/aiGatewayRequest
GET  /user/queryQuestionData
POST /user/setDocumentStatus
POST /user/publishPptItem
PUT  /bucket/personal/<folder>/document/<id>
POST /user/deleteDocumentData
```

---

## 20. 版本与维护

### 20.1 本文档适用版本

- `transweb-ai` 1.2.0
- `transweb-create` 1.0.0
- 平台接口以实际部署为准

### 20.2 维护建议

- 平台 API/模板变更时更新第 11、12 章；
- 创建流程变更时更新第 7、8 章；
- 计费/权限策略变更时更新第 9、10、16 章；
- 每季度复核 FAQ 和故障排查；
- 公开前移除内部 ID、Key、个人信息。

### 20.3 如何使用本知识库

- **创建知识型 Agent**：将本文作为资料，运行 `transweb-create agent --file`；
- **创建 Skill**：优先使用第 4、7、8、12 章作为结构与约束参考；
- **培训/运营**：使用第 1、2、15、16 章；
- **排障**：直接检索第 13、17 章；
- **二次开发**：参考第 11、12 章接口与序列化规范。

---

> 本文是 TransWeb 浏览器端数字劳动力的基础 knowledge base。平台能力会持续演进，落地前请以当前部署版本的接口、模板和权限策略为准。
