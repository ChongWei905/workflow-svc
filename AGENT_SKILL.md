# Agent Skills（Anthropic 定义）规范摘要（用于校验 skill_executor 是否遵循设计）

> 本文是对 Agent Skills “overview” 页面的**浓缩定义**，面向实现方（skill_executor）。  
> 目标：你的执行器实现应满足下列**包结构、加载语义、运行时约束与安全语义**。  [oai_citation:0‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 1. 定义与边界

**Skill = 一个文件系统目录（folder）**，用于向 Claude 提供可复用的领域能力包。目录内至少包含 `SKILL.md`，可选包含脚本与参考资料。  [oai_citation:1‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

- 与一次性 prompt 的区别：Skill **按需加载（on-demand）**，避免重复提供同一套指令。  [oai_citation:2‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- Skill 依托一个带文件系统访问能力的运行环境（VM/container），让模型可以“读文件/跑脚本”，而不是把所有内容预塞进上下文。  [oai_citation:3‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 2. Skill 包结构（artifact contract）

**必需文件**
- `SKILL.md`：必须以 YAML frontmatter 开头，且至少包含：
  - `name`
  - `description`  [oai_citation:4‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

**可选内容（典型约定）**
- 额外 Markdown：如 `FORMS.md`、`REFERENCE.md`（被 `SKILL.md` 引用后才会读取）
- `scripts/`：可执行脚本（Python/Bash 等）
- 其他 resources/assets：数据、模板、示例等  [oai_citation:5‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 3. 渐进式披露（Progressive disclosure）与加载语义

Skill 内容分三层加载（这是最核心的“语义契约”）：  [oai_citation:6‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Level 1：Metadata（总是加载）
- 来源：`SKILL.md` 的 YAML frontmatter（`name`/`description`）
- 何时加载：**启动时**加载并放入 system prompt（用于“发现/路由”）
- 目的：让模型知道“有什么 skill、何时该用”，但不加载细节  [oai_citation:7‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Level 2：Instructions（触发时加载）
- 来源：`SKILL.md` 正文
- 何时加载：当用户请求与 `description` 匹配、模型判定需要该 skill 时，模型通过 bash 读取 `SKILL.md`，其正文才进入上下文  [oai_citation:8‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Level 3+：Resources & Code（按需加载/执行）
- 来源：skill 目录内的其他文件与脚本
- 何时加载：仅当 `SKILL.md` 指引或任务需要时才会读取/执行
- 关键语义：
  - 额外文件：通过 bash 读取后进入上下文（只读需要的那份）
  - 脚本：通过 bash 执行；**脚本源码不进入上下文，只返回执行输出（stdout/stderr）**  [oai_citation:9‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 4. 运行架构语义（executor 应提供的能力）

overview 将 Skills 描述为：模型在一个带文件系统的环境里，像人类使用终端一样通过 bash 交互：  [oai_citation:10‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

执行流程（抽象）：
1. 启动：system prompt 预置每个 skill 的 `name/description`（Level 1）
2. 触发：模型决定使用 skill → bash 读取 `SKILL.md`（Level 2）
3. 扩展：模型按需读取引用文件（Level 3 resources）
4. 执行：模型按需运行脚本并消费其输出（Level 3 code output）  [oai_citation:11‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 5. `SKILL.md` frontmatter 的格式约束（必须校验）

`name` 约束：  [oai_citation:12‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- ≤ 64 字符
- 仅允许：小写字母 / 数字 / 连字符 `-`
- 不能包含 XML tags
- 不能包含保留词：`anthropic`、`claude`

`description` 约束：  [oai_citation:13‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- 非空
- ≤ 1024 字符
- 不能包含 XML tags
- 应同时包含：**做什么** + **什么时候用**

> executor 建议：安装/加载时强校验；校验失败则拒绝加载该 skill（或标记不可用）。

---

## 6. 产品面（surface）差异（executor 必须可配置）

overview 明确 Skills 可用于多个 surface，但**共享范围、同步方式、运行环境约束不同**：  [oai_citation:14‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Claude API
- 使用方式：在 `container` 参数里指定 `skill_id`，并启用 code execution
- 前置条件：需要 beta headers（至少包含：`code-execution-2025-08-25`、`skills-2025-10-02`、`files-api-2025-04-14`）  [oai_citation:15‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- 运行约束：无外网；不可运行时安装新包；只能用预装依赖  [oai_citation:16‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### Claude Code / Claude Agent SDK / Claude.ai
- 发现与分发机制不同（filesystem / `.claude/skills/` / 上传 zip 等）
- 自定义 Skills 不会跨 surface 自动同步；需要分别管理上传/分发  [oai_citation:17‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- 网络与依赖约束因 surface 不同而不同（尤其 claude.ai 的网络访问可能受设置影响）  [oai_citation:18‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

---

## 7. 安全语义（executor 侧的最低要求）

官方安全建议（对 executor 的含义）：  [oai_citation:19‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- 默认只信任自己或 [Anthropic](chatgpt://generic-entity?number=0) 提供的 Skills
- 若加载不可信 skill：必须“像装软件一样审计”
  - 审计所有文件：`SKILL.md`、scripts、资源
  - 警惕外部 URL 拉取（内容可能变更/被注入）
  - 防止工具滥用、数据外泄与异常文件访问  [oai_citation:20‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

> executor 建议（实现层面）：
> - 提供 allowlist/denylist（脚本可执行范围、可访问路径、是否允许网络等）
> - 日志与审计：记录“读了哪些文件、执行了哪些脚本、输出摘要”
> - 对敏感数据做最小暴露与脱敏策略

---

## 8. 预置 Skills（用于兼容性测试）

overview 列出预置 skills（API 与 claude.ai 可用）：  [oai_citation:21‡Claude开发平台](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- `pptx`（PowerPoint）
- `xlsx`（Excel）
- `docx`（Word）
- `pdf`（PDF）

---

# skill_executor 合规检查清单（最短版）

你的执行器若要“完全遵循 overview 的设计”，至少应满足：

1. ✅ 以“目录”为 skill 单位；必须包含 `SKILL.md`  
2. ✅ 启动时仅加载每个 skill 的 `name/description` 到 system prompt（Level 1）  
3. ✅ 触发时才读入 `SKILL.md` 正文（Level 2）  
4. ✅ 支持按需读取额外资源文件（Level 3 resources）  
5. ✅ 支持按需执行脚本，并且上下文中只消费脚本输出，不注入脚本源码（Level 3 code）  
6. ✅ 强校验 frontmatter：name/description 的格式与保留词规则  
7. ✅ 对不同 surface 的运行约束可配置（尤其 API：无网、不可安装包）  
8. ✅ 提供最基本的安全护栏（来源可信、审计、限制外部拉取/工具滥用/数据暴露）