# Skill



## 什么是 Skill

**Skill** 是面向 AI 编程工具的**可复用指令集**，以 Markdown 文件的形式存在。它告诉 AI「在特定项目中应该怎么写代码」——包括项目规范、分层约定、命名规则、工作流程和验收标准。

当你在 **Codex、ClaudeCode、WorkBuddy、Qoder、Trae** 等 AI 编程工具中开发时，AI 会自动加载 Skill 中定义的约束，使生成的代码天然符合项目的架构风格和工程规范，无需每次手动描述项目上下文。



### 核心理念

```
传统方式：每次对话都要重复描述项目结构、命名规则、分层约定...
Skill 方式：写一次 → 所有 AI 工具自动遵循
```

Skill 的本质是**项目知识的标准化沉淀**：
- **任务导向**：每个 Skill 解决一类特定问题（如当前FastBrace侧重于工程化后端模块开发）
- **标准化流程**：Skill会定义清晰的执行步骤和验收标准
- **可复用**：一次定义，跨会话、跨工具复用，不限于哪一个AI编程工具
- **按需加载**：业务细节放在 `references/` 子目录，AI 按任务需要逐步加载，避免上下文溢出，减少Token消耗



## FastBrace 的 Skill 目录

FastBrace 在项目根目录下内置了完整的 Skill 文件体系：

```
skills/
├── SKILL.md                          # Skill 入口文档（AI 首先读取）
└── references/                       # 按需加载的参考资料
    ├── project.md                    # 技术栈、DDD 分层、目录规范、命名规则
    ├── code-style.md                 # 代码风格、思考原则、日志规范
    ├── modules.md                    # 业务模块实现次序和各层职责
    ├── file-resource.md              # 文件资源处理规范
    ├── permission.md                 # 权限系统规范
    ├── scripts.md                    # 维护脚本规范
    └── version-iter-template.md      # 版本迭代说明模板
```

**`SKILL.md`** 是核心入口文件，它向 AI 说明如何写出符合项目规范的代码，写完如何验收和交付

**`references/`** 目录存放业务细节文档，AI 按任务需要逐步加载：

| 文档 | 职责 |
|------|------|
| `project.md` | 技术栈、分层、目录、命名、文件头和 SQL 约定 |
| `code-style.md` | 思考、简化、精准修改与日志原则（灵感来源于： https://github.com/multica-ai/andrej-karpathy-skills） |
| `modules.md` | 业务模块实现次序和各层职责 |
| `file-resource.md` | 文件资源处理 |
| `permission.md` | 权限系统 |
| `scripts.md` | 维护脚本 |
| `version-iter-template.md` | 版本迭代说明模板 |



## 集成到 AI 编程工具



### Codex

**配置方式：**

1. Codex存在创建SKill的技能，下载FastBrace后打开项目，在项目目录下引用该技能，然后输入下方提示词信息（如下图所示）

   ```
   请完整引用skills下内容生成FastBrace的skill信息，并将上述图片内容作为logo展示
   ```

   

​	![截屏2026-08-31 17.48.40](https://picgocloud.com/m/fcc0d7b2-aa3e-42d8-8813-b002e3110903.png)



2. 创建完技能后，可以直接在左侧找到插件，然后在技能部分找到创建好的技能
3. 在具体的项目中可以引用该技能

⚠️： 因为codex支持显示技能logo信息，所示上述提示词加了logo图片内容，正常来讲不上传logo图片也可以生成skill





### Qoder

Qoder 原生支持项目级 Skill 发现。将 Skill 文件放在项目根目录的 `.agent/skills/` 下即可自动识别,如果不能识别，在项目中上传skills文件夹即可







### Trae

Trae 原生支持项目级 Skill 发现。将 Skill 文件放在项目根目录的 `.agent/skills/` 下即可自动识别。



## 下一步

- 了解 MCP 如何扩展 AI 工具能力：[MCP](./mcp)
