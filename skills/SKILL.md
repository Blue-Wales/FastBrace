---
name: FastBrace
description: Implement, modify, review, and verify FastBrace backend business modules from requirements or business documents. FastBrace is an Agent-first FastAPI + SQLAlchemy + MySQL backend framework with DDD layering. Use this skill for any FastBrace work involving database models (infrastructure/models), create-table SQL files (db/), domain entities, value objects, repositories, services, application services, API routes, request/response models, DTOs, router registration, permissions, file resources, maintenance scripts, tests, acceptance fixes, code style, or version iteration notes. Trigger whenever the user asks to add or change a FastBrace backend module, generate backend code from a business document, sync a SQLAlchemy model with its db/ SQL file, or fix a module's acceptance-test failures — even if they don't explicitly name FastBrace.
---

# FastBrace Backend Agent

本文件是 `FastBrace` skill 的入口文档，用于指导 AI 编程工具在 FastBrace 项目中根据业务文档快速完成后端代码实现、SQL 建表文件、测试验收和版本说明。FastBrace 是面向独立开发者、小团队和 AI 应用开发者的 Agent-first FastAPI 后端框架，强调 DDD 分层、工程规范、测试与 CI 反馈回路。业务模块细节按需加载 `references/` 下的参考资料，不要把全部业务细节重复写入本文件。

## 适用场景

当用户要求完成以下任务时，使用本 skill：

- 新增或修改后台业务模块。
- 根据业务需求、模型设计、接口设计、流程设计、验收标准生成后端代码。
- 按项目 DDD 分层结构补齐 model、entity、repo、service、application、api、dto、request、response 等文件。
- 在完善 SQLAlchemy model 后，同步在 `db/` 目录产出对应建表 SQL 文件。
- 按需补充权限、通知、脚本、数据库 SQL、测试、版本迭代说明。
- 修复业务模块验收测试失败或对照业务文档做一致性检查。

## 核心目标

1. 先理解项目结构和业务文档，再修改代码。
2. 代码必须符合现有项目目录、命名、分层职责和文件风格。
3. 业务逻辑必须可追溯到业务文档中的模型、接口、流程和验收标准。
4. 数据库结构必须同时体现在 `infrastructure/models/{module}.py` 和 `db/create_{module}_table.sql` 中，字段、类型、默认值、注释、唯一约束和索引必须保持一致。
5. 业务开发前必须读取 `pyproject.toml` 中 Ruff、mypy、pytest 等 lint/测试配置，按工具规则产出代码，减少上下文规范重复。
6. 每一批次对话完成前必须执行确定性脚本修复格式并验证质量，优先使用 `make agent-finish`。
7. 每个模块完成后必须产出必要的测试验证结果和版本迭代说明。
8. ‼️不修改无关文档和无关代码；遇到用户已有改动时，基于现状继续工作。

## 文档职责索引

| 文档                              | 唯一负责内容                                |
| --------------------------------- | ------------------------------------------- |
| `references/project.md`           | 技术栈、分层、目录、命名、文件头和 SQL 约定 |
| `references/code-style.md`        | 思考、简化、精准修改与日志原则              |
| `references/modules.md`           | 业务模块实现次序和各层职责                  |
| `references/file-resource.md`     | 文件资源                                    |
| `references/permission.md`        | 权限                                        |
| `references/scripts.md`           | 维护脚本                                    |
| `references/version-iter-template.md` | 版本迭代说明                             |
| `pyproject.toml` / `Makefile`     | 格式、lint、类型、测试的可执行规则          |

## 上下文加载顺序

按任务需要逐步加载资料，避免一次性读取全部文档。

1. 必读 `references/project.md`

   - 用于了解技术栈、DDD 分层结构、目录规范、命名规范、文件头模板和公共枚举规则。

2. 必读 `pyproject.toml`

   - 读取 `[tool.ruff]`、`[tool.ruff.lint]`、`[tool.ruff.lint.per-file-ignores]`、`[tool.mypy]`、`[tool.pytest.ini_options]`。
   - 用于确认当前可机械化执行的代码规范、类型检查边界、放宽目录和测试入口；空行与文件头约定以 `scripts/check_headers.py` 为准（项目未启用 `ruff format`）。
   - 不要在 skill 文档中重复展开全部 lint 规则；以 `pyproject.toml` 为准。

3. 必读 `Makefile`

   - 用于确认 `make lint-fix`、`make lint`、`make test`、`make agent-finish` 等确定性脚本入口。
   - 每批次开发收尾优先运行 `make agent-finish`；如果只改 Python 且需要快速格式化，可先运行 `make format`。

4. 必读 `references/code-style.md`

   - 用于确认实现前思考、简化、精准修改和日志约束。

5. 按需读取 `docs/lint-and-style-guide.md`

   - 当用户询问 lint 规范、工具用途、一键修复方式或新增质量工具时读取。
   - 该文档用于解释工具分工，实际执行规则仍以 `pyproject.toml` 和 `Makefile` 为准。

6. 业务模块开发时读取 `references/modules.md`

   - 用于确定模块实现顺序、各层职责边界和参考文件。
   - 用于确认模型完成后在 `db/` 目录同步产出建表 SQL 文件。
   - 涉及图片、视频、PDF、附件等文件资源时读取 `references/file-resource.md`。

7. 涉及权限时读取 `references/permission.md`

   - 适用于新增管理模块、子模块、接口权限或菜单权限绑定。

8. 涉及脚本时读取 `references/scripts.md`

   - 适用于批处理、初始化、修复、重算、导入导出等脚本。

9. 需要编写版本说明时读取 `references/version-iter-template.md`

   - 版本文件命名规则：`version-iter-{YYYY-MM-DD}-{module}.md`。

10. 业务模块专属文档

    - 后续用户补充的模型设计、接口设计、流程设计、验收标准等文档，应在实现对应模块前读取。
    - 如果文档信息不完整，关键业务规则无法判断时向用户确认。

## 标准工作流

### 1. 需求解析

- 明确本次任务的业务模块、接口范围、数据模型、流程节点和验收标准。
- 提取需要新增、修改、复用的表、枚举、权限、通知、脚本和测试。
- 搜索现有相似模块，优先复用项目内已有风格和工具函数。
- 识别是否需要 `db/` 建表 SQL、数据库迁移、路由注册、权限初始化、通知配置或异步事件。
- 在写代码前确认本次改动会触发的 lint 范围：业务代码、脚本、迁移、测试或文档，并按 `pyproject.toml` 中对应放宽规则处理。

### 2. 结构映射

按 `references/project.md` 和 `references/modules.md` 将业务需求映射到项目分层：

- `infrastructure/models/{module}.py`：数据库模型。
- `db/create_{module}_table.sql`：建表 SQL 文件，必须在模型完成后同步产出。
- `domain/entity/{module}.py`：领域实体。
- `domain/value_object/{module}_vo.py`：值对象。
- `domain/repo/interfaces/{module}.py`：仓储接口。
- `domain/repo/{module}_repo.py`：仓储数据库 CRUD 实现。
- `domain/service/interfaces/{module}.py`：领域服务接口。
- `domain/service/{module}_service.py`：跨领域业务实现；⚠️：单领域编排不强行新增。
- `application/{module}_app.py`：应用服务编排。
- `api/{module}.py`：API 路由。
- `api/request_body/{module}_request.py`：请求模型和入参校验。
- `api/response_body/{module}_response.py`：响应体。
- `api/response_model/{module}_res_model.py`：Swagger 响应模型。
- `api/dto/{module}.py`：接口 DTO。
- `infrastructure/core/routers.py`：路由注册。
- `infrastructure/core/enum_var.py`：枚举、权限、提醒类型等公共定义。
- `tests/`：验收测试和必要的回归测试。

### 3. 代码实现原则

- 修改策略、简化原则和日志边界以 `references/code-style.md` 为准。
- 分层、命名、文件头和 SQL 合同以 `references/project.md` 为准。
- 模块顺序、各层职责、Swagger 示例和大整数 ID 规则以 `references/modules.md` 为准。
- 格式、lint、类型检查和目录放宽规则以 `pyproject.toml` 为准。

### 4. Lint 与确定性脚本

每一批次对话完成前，必须按改动范围执行确定性脚本，优先级如下：

1. 常规业务开发收尾：

   ```bash
   make agent-finish
   ```

   该命令会先执行 `make lint-fix`，再执行 `make lint`，用于自动修复 Ruff/mdformat 可修复问题并验证 Ruff、Ruff format、mypy、Markdown 格式。

2. 只需要快速修复格式：

   ```bash
   make format
   ```

3. 只需要检查不修改文件：

   ```bash
   make lint
   ```

4. 涉及业务逻辑、接口或公共层时：

   ```bash
   make test
   ```

执行要求：

- 如果脚本失败，先按输出修复确定性问题，再重新执行同一脚本。
- 如果失败来自网络、权限、外部服务或数据库环境，记录失败原因和已完成的替代验证。
- 不要绕过 `Makefile` 手写零散命令，除非正在定位脚本失败原因。
- 不要为了让 lint 通过而改变业务语义；无法确定的改动必须保守处理并说明。

### 5. 权限、脚本专项规则

- 权限变更读取 `references/permission.md`。
- 维护脚本读取 `references/scripts.md`。

## 业务文档要求

后续新增模块文档建议至少包含以下内容，实现时也应主动对照这些部分：

- 模块背景：业务目标、角色、边界、依赖模块。
- 模型设计：表结构、字段类型、默认值、索引、唯一约束、状态枚举、软删除规则。
- SQL 设计：`db/create_{module}_table.sql` 文件名、建表语句、字段注释、索引、唯一约束、表注释以及与 SQLAlchemy model 的一致性。
- 接口设计：路径、方法、权限、请求字段、响应字段、分页、排序、筛选、错误码。
- 流程设计：创建、编辑、审核、状态流转、撤销、删除、导入导出、通知触发点。
- 规则设计：字段校验、状态约束、跨模块校验、并发处理、幂等规则。
- 验收标准：正常用例、边界用例、异常用例、权限用例、通知用例、数据一致性用例。
- 版本说明：本次改动范围、潜在风险、待确认事项。

如果业务文档和现有代码冲突，优先指出冲突点，并以用户确认后的规则为准；无法确认时，优先保持与现有项目行为一致。

## 测试与验收

每个模块完成后必须执行与改动范围匹配的验证：

- 批次收尾先运行 `make agent-finish`，确保格式、静态检查、类型检查和 Markdown 格式通过。
- 对照业务文档验收标准补充或更新测试脚本。
- 覆盖核心成功路径、权限限制、参数校验、状态流转、异常分支和数据持久化。
- 涉及脚本时验证 dry-run、参数解析、数据过滤和写入结果。
- 优先运行最小相关测试；如果改动影响公共层，再运行更大范围测试。
- 如果测试无法运行，必须记录原因、阻塞点和已完成的替代验证。

## 版本迭代说明

每个业务模块完成后，在项目约定位置产出版本修改说明文件，命名为：

```text
version-iter-{YYYY-MM-DD}-{module}.md
```

内容参考 `references/version-iter-template.md`，至少包含：

- 当前模型。
- 完成时间。
- 本次修改内容。
- 需要确认的事项。
- 本次修改潜在的问题。

版本说明应简洁记录真实改动，不写无关总结。

## 交付前检查清单

提交给用户前逐项确认：

- 已读取本次任务需要的 `references/` 文档和业务模块文档。
- 已读取 `pyproject.toml` 中 lint/测试配置，并按 `Makefile` 的确定性脚本完成批次收尾。
- 代码文件位置、命名、类名、文件头符合 `references/project.md`。
- Repo/Service 接口类及公开方法具有完整契约文档，具体实现未重复接口说明。
- 模块实现顺序和分层职责符合 `references/modules.md`。
- 新增或变更数据表时，已同步维护 `db/create_{module}_table.sql`，并确认 SQL 与 Model 一致。
- API 已注册路由，Swagger request/response 示例完整。
- 权限、脚本等专项内容已按对应文档处理。
- `make agent-finish` 已运行通过；若未运行或失败，已说明具体原因。
- 测试脚本覆盖验收标准，相关测试已运行或说明无法运行原因。
- 已生成本模块版本迭代说明。
- 未修改用户未要求变更的其他文档。
