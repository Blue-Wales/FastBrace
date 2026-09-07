# 值对象设计指南

本文档说明 `domain/value_object/` 的适用场景、现有文件与去留判断。



## 什么情况写值对象

值对象是**无身份标识、不可变**的描述性对象：值相同即相等，判断标准：

- 只描述"是什么"（如邮件消息、文件元数据、用户摘要），不关心"是哪一个" → 值对象；
- 有独立 ID、需要单独追踪修改 → 实体（见[实体文档](domain-entity)）。

值对象适合：跨实体/跨仓储复用的数据传输形态、方法的入参与出参、不可变配置。用 Pydantic `BaseModel` 定义，配置 `frozen = True` 或 `from_attributes = True` 按需启用。



## 现有值对象

| 文件                            | 值对象                                                           | 使用方                    |
| ------------------------------- | ---------------------------------------------------------------- | ------------------------- |
| `value_object/email_message.py` | `EmailMessage` / `EmailAttachment`                               | 邮件服务与邮件事件处理器  |
| `value_object/file_vo.py`       | `FileVO`                                                         | 文件仓储（附件读写）      |
| `value_object/user_vo.py`       | `UserSummaryVO` / `UserMobileVO` / `UserInfoVO` / `UserWorkWxVO` | 用户仓储（列表/投影查询） |



## 编写约定

- 继承 `BaseModel`，字段用 `Field(title="中文名")` 声明；
- 不可变语义使用 `frozen = True`；需要从 ORM/实体转换使用 `from_attributes = True`；
- 类文档字符串简短一句（如「文件值对象」）；
- 文件名统一 `{module}_vo.py`，类名以 `VO` 结尾。



## 新增值对象的流程

1. 判断确实无身份、不可变，且存在复用价值（避免仅为单处使用建文件）；
1. `domain/value_object/{module}_vo.py` 定义模型；
1. 仓储/服务返回 VO 时，通过 `model_validate(orm_obj)` 转换。
