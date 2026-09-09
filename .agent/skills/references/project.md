## Project rules

当前项目是 **FastBrace**，采用 **DDD (领域驱动设计) + 分层架构**，基于 **FastAPI + SQLAlchemy + MySQL** 构建。项目定位为 Agent-first FastAPI 后端框架，通过工程规范、测试和 CI 反馈回路，让 Codex、Claude Code 等 AI 编程工具能稳定生成可维护的业务接口。

### 技术栈

| 层级     | 技术组件          | 版本     |
| -------- | ----------------- | -------- |
| Web框架  | FastAPI           | 0.115.12 |
| ORM      | SQLAlchemy        | 2.0.40   |
| 数据库   | MySQL             | -        |
| 缓存     | Redis             | 5.2.1    |
| 任务队列 | Celery            | 5.3.6    |
| 配置管理 | Pydantic-Settings | 2.8.1    |
| 日志     | Loguru            | 0.7.3    |
| 文档     | Swagger/OpenAPI   | 内置     |

### 项目目录结构

```
digital-process-backend/
├── api/                          # API接口层 (Presentation Layer)
│   ├── dto/                      # 数据传输对象
│   ├── request_body/             # 请求体模型
│   ├── response_body/            # 响应体模型
│   ├── response_model/           # 响应模型 (用于Swagger文档)
│   ├── third_party_body/         # 第三方接口模型
│   └── *.py                      # 路由模块文件
├── application/                  # 应用服务层 (Application Layer)
│   ├── tasks/                    # Celery定时任务
│   └── *_app.py                  # 应用服务类
├── domain/                       # 领域层 (Domain Layer)
│   ├── aggregate_root/           # 聚合根
│   ├── entity/                   # 领域实体
│   ├── events/                   # 领域事件
│   ├── repo/                     # 仓储实现
│   │   └── interfaces/          # 仓储接口
│   ├── service/                  # 领域服务实现
│   │   └── interfaces/          # 领域服务接口
│   └── value_object/             # 值对象
├── infrastructure/               # 基础设施层 (Infrastructure Layer)
│   ├── config/                   # 配置文件
│   ├── core/                     # 核心组件
│   │   ├── app.py               # FastAPI应用创建
│   │   ├── routers.py           # 路由注册
│   │   ├── settings.py          # 配置模型
│   │   ├── factorys.py          # Bean工厂
│   │   ├── middlewares.py       # 中间件
│   │   ├── error_handler.py     # 异常处理
│   │   ├── permissions_limit.py # 权限控制
│   │   └── enum_var.py          # 枚举常量
│   ├── cron/                     # 定时任务配置
│   ├── events/                   # 事件总线
│   ├── migrations/               # 数据库迁移
│   ├── models/                   # 数据库模型 (SQLAlchemy)
│   └── utils/                    # 工具类
├── docs/                         # 文档目录
├── db/                           # 建表SQL文件
├── event_handlers/               # 事件处理器
├── tests/                        # 测试目录
├── README.md                     # 中文开源说明
├── README.en.md                  # 英文开源说明
├── pyproject.toml                # 依赖、构建、lint和测试配置
└── Makefile                      # 工程质量脚本入口
```

### 代码规范

#### 文件命名规范

| 类型         | 命名规则                    | 示例                         |
| ------------ | --------------------------- | ---------------------------- |
| API路由      | `{模块名}.py`               | `apartment.py`               |
| 应用服务     | `{模块名}_app.py`           | `apartment_app.py`           |
| 领域实体     | `{模块名}.py`               | `apartment.py`               |
| 领域服务实现 | `{模块名}_service.py`       | `apartment_service.py`       |
| 领域服务接口 | `interfaces/{模块名}.py`    | `interfaces/apartment.py`    |
| 仓储实现     | `{模块名}_repo.py`          | `apartment_repo.py`          |
| 仓储接口     | `interfaces/{模块名}.py`    | `interfaces/apartment.py`    |
| 数据模型     | `{模块名}.py`               | `apartment.py`               |
| SQL文件      | `create_{模块名}_table.sql` | `create_apartment_table.sql` |
| 请求体       | `{模块名}_request.py`       | `apartment_request.py`       |
| 响应体       | `{模块名}_response.py`      | `apartment_response.py`      |
| 响应模型     | `{模块名}_res_model.py`     | `apartment_res_model.py`     |
| DTO          | 统一放在 `dto/{模块名}.py`  | `dto/apartment.py`           |
| 值对象       | `{模块名}_vo.py`            | `apartment_vo.py`            |

#### 类命名规范

| 类型     | 命名规则                   | 示例                          |
| -------- | -------------------------- | ----------------------------- |
| 实体     | `{Name}Entity`             | `ApartmentEntity`             |
| 应用服务 | `{Name}ApplicationService` | `ApartmentApplicationService` |
| 领域服务 | `{Name}DomainService`      | `ApartmentDomainService`      |
| 仓储     | `{Name}Repository`         | `ApartmentRepository`         |
| 值对象   | `{Name}VO`                 | `ApartmentSummaryVO`          |
| DTO      | `{Name}DTO`                | `ApartmentListDTO`            |
| 请求体   | `{Action}{Name}Request`    | `CreateApartmentRequest`      |
| 响应体   | `{Name}{Info}Response`     | `ApartmentItemResponse`       |

#### 领域接口契约文档规范

`domain/repo/interfaces/` 和 `domain/service/interfaces/` 是领域层的稳定依赖边界，完整契约必须写在接口定义处：

- 模块文件头说明该组接口提供的全局领域 Repo 或 Service 能力。
- 接口类文档说明职责边界、标识语义、事务归属、协作对象，以及调用方可依赖的通用约束。
- 每个公开方法必须说明业务意图、参数语义、返回结果和可能抛出的领域异常；分页、排序、幂等、空值、数据范围或事务行为存在特殊约定时，补充 `Notes`。
- 仓储接口只描述领域层需要的持久化能力，不暴露 SQLAlchemy Session、SQL 语句、表结构等实现细节，也不承载跨领域业务判断。
- 领域服务接口描述跨领域规则、输入输出和失败语义，不包含 HTTP、依赖注入容器或具体基础设施细节。
- 接口签名、类型注解、实现和调用方必须保持一致；调整契约时同步更新实现与回归测试。
- 具体实现类和方法只记录接口之外的实现策略，例如闭包表、批量 upsert、兼容逻辑或外部协议，不重复接口中的参数和返回值文档。

#### 文件头模板

所有Python文件必须包含以下文件头：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : {filename}.py
@Author  : Blue-Wales
@Date    : {YYYY-MM-DD}
@Desc    : {简要描述}
"""
```

API 层（`api/`）、应用服务层（`application/`）与领域层（`domain/`）的文件头由 `scripts/check_headers.py` 机械化校验，修改后必须通过 `make lint`。类文档字符串后空一行再写成员，函数文档字符串后直接写代码，同一作用域内定义之间空两行。

### 常量定义

所有枚举定义在 `infrastructure/core/enum_var.py`：

```python
class ApartmentType(BaseCodeLabelEnum):
    """公寓类型"""
    student_apartment = (1, "学生公寓")
    social_apartment = (2, "社会公寓")
```

### 数据库 SQL 文件规范

新增或调整业务表时，完成 `infrastructure/models/{module}.py` 后必须同步维护 `db/create_{module}_table.sql`。

- SQL 文件用于开源项目快速初始化和人工审阅数据库结构，不替代 SQLAlchemy model。
- 文件名使用小写蛇形命名，例如 `db/create_mini_program_card_table.sql`。
- 建表语句使用 `CREATE TABLE IF NOT EXISTS`。
- 字段类型、默认值、是否允许为空、字段注释、表注释、主键、唯一键和普通索引必须与 model 保持一致。
- 默认使用 `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4`。
- 建议按当前 `db/create_mini_program_card_table.sql` 的格式组织注释、字段、主键和索引。
