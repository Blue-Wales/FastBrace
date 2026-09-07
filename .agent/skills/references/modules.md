## modules rules

### 主流程

1. **定义数据模型** (`infrastructure/models/{module}.py`)
2. **同步建表 SQL** (`db/create_{module}_table.sql`)
3. **定义领域实体** (`domain/entity/{module}.py`)
4. **定义值对象** (`domain/value_object/{module}_vo.py`)
5. **注册路由** (`infrastructure/core/routers.py`)
6. **定义API路由** (`api/{module}.py`)
7. **定义请求/响应模型** (`api/request_body/`, `api/response_body/`,`api/response_model/`)
8. **定义仓储接口** (`domain/repo/interfaces/{module}.py`)
9. **实现仓储** (`domain/repo/{module}_repo.py`)
10. **定义应用服务** (`application/{module}_app.py`)
11. **定义领域服务接口** (`domain/service/interfaces/{module}.py`)，仅当存在跨领域服务时新增
12. **实现领域服务** (`domain/service/{module}_service.py`)，单领域编排放在 Application 层
13. **定义DTO** (`api/dto/{module}.py`)

### 流程边界限制条件

1. **定义数据模型** (`infrastructure/models/{module}.py`)

   依据给定的业务文档以及现有model下文件代码风格，完善模型定义

2. **同步建表 SQL** (`db/create_{module}_table.sql`)

   1. 在完成 `infrastructure/models/{module}.py` 后立即同步产出或更新 SQL 文件。
   2. SQL 文件命名使用 `create_{module}_table.sql`，统一放在项目根目录 `db/` 下。
   3. 建表 SQL 参考 `db/create_mini_program_card_table.sql` 的格式，使用 `CREATE TABLE IF NOT EXISTS`。
   4. SQL 字段、类型、默认值、是否允许为空、注释、主键、唯一约束和索引必须与 SQLAlchemy model 保持一致。
   5. 业务文档中的模型设计如果包含唯一约束、组合索引、状态字段、软删除字段或审计字段，SQL 文件必须同步体现。
   6. 如果当前模块只修改已有表字段，也需要在对应 SQL 文件中反映最终完整表结构；无法确认历史表结构时先说明缺口，不凭空补全高风险字段。

3. **定义领域实体** (`domain/entity/{module}.py`)

   依据给定的业务文档以及业务model完善领域实体

4. **定义值对象** (`domain/value_object/{module}_vo.py`)

   依据给定的业务文档以及业务model完善值对象

5. **注册路由** (`infrastructure/core/routers.py`)

6. **定义API路由** (`api/{module}.py`)

7. **定义请求/响应模型** (`api/request_body/`, `api/response_body/`)

   1. 请求响应模型，需要依据业务文档要求完善
   2. 如果涉及到校验信息，直接在该部分模型中完善校验信息，诸如针对entity_id前端需要传递str类型，避免大精度丢失，如果传递其他类型需要校验转化
   3. 需要包含swagger文档中示例信息，在字段examples=\[[2025, 2024]\]定义，以便于导入api直接可以查看请求、响应数据格式

8. **定义仓储接口** (`domain/repo/interfaces/{module}.py`)

   1. 仓储接口仅包含领域层需要的 CRUD、查询和批量持久化能力，不包含跨领域业务判断，也不暴露 ORM、Session 或 SQL 细节。
   2. 接口类必须描述仓储的全局职责、标识规则、事务边界和通用约束。
   3. 每个公开接口必须完整描述业务意图、参数、返回值、领域异常；分页、排序、幂等、空值或数据范围有特殊行为时补充说明。
   4. 方法签名和类型注解属于契约，必须与实现、调用方和测试保持一致。

9. **实现仓储** (`domain/repo/{module}_repo.py`)

   1. 仓储实现尽量使用 SQLAlchemy `select`、`update` 等 2.x 写法
   2. 实现文档只说明接口之外的持久化策略、查询算法、数据库兼容或性能注意事项，不重复接口契约。

10. **定义应用服务** (`application/{module}_app.py`)

    1. 在应用服务层，完成相应模块内容调度，诸如针对repo、service、request、response进行调度服务编排处理
    2. 在应用服务层，可完善定义异步事件发送、通知发送等内容
    3. 在应用服务层，针对编排信息基于业务要求进行处理

11. **定义领域服务** (`domain/service/interfaces/{module}.py`, `domain/service/{module}_service.py`)

    1. 领域服务为跨领域部分相关业务交互处理需要完善定义，诸如产品模块和订单模块相关有业务联动，需要定义该文件进行处理
    2. 如果在单一领域能完成直接在app应用服务层完善即可
    3. 领域服务接口类需要描述跨领域职责和协作边界，每个公开方法需要描述输入、输出、失败语义及特殊业务约束。
    4. 领域服务实现只补充具体规则组合或算法策略，避免复制接口层已有文档。

12. **定义DTO** (`api/dto/{module}.py`)

    1. 基于接口完成的响应信息定义DTO

13. **处理文件资源**

    1. 涉及图片、视频、PDF、附件等资源时，读取 `references/file-resource.md`。
    2. 按统一上传、统一 `file` 表关联、业务主表不冗余资源字段的规则实现。
