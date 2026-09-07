# 领域服务设计指南

本文档详细说明 `domain/service/` 的使用场景、目录结构与编写约定



## 什么情况写领域服务

领域服务承载**不属于单一实体**的业务逻辑。当一个用例无法放进某个实体的方法里时，才考虑领域服务。具体分三种场景：



### 1. 跨领域协调

一个用例需要**组合多个实体、仓储或领域服务**完成时，协调逻辑放在领域服务。

示例：`RoleService.get_relation_users` 逐角色查询并聚合关联用户，`UserService.get_users` 组合用户查询结果与角色映射：

```python
async def get_relation_users(self, role_repo: RoleRepository, role_ids: list[int]):
    """逐角色聚合并去重关联用户 ID。"""
    if len(role_ids) == 0:
        return []
    users_id_list = []
    for role_id in role_ids:
        role_entity = await role_repo.get_by_id(role_id=role_id)
        if role_entity is None:
            continue
        users_id_list.extend(role_entity.related_users)
    return list(set(users_id_list))
```

**判断标准**：逻辑涉及多个对象，且无法合理地归入其中任何一个实体的职责。



### 2. 调用三方服务

需要对接**外部系统**（SMTP、OSS、第三方 API）时，封装在领域服务中，把外部依赖隔离在领域层之外。

示例：`SMTPEmailService` 将 `EmailMessage` 值对象交给 `EmailSender`（`infrastructure/utils/email_utils.py`）发送：

```python
@domain_service_factory.autowire("email_domain_service", scope=BeanScope.PROTOTYPE.value)
class SMTPEmailService(BaseService):
    """基于SMTP的邮件服务实现"""

    def send_email(self, email: EmailMessage) -> bool:
        """发送邮件"""
        return self.email_sender.send_email(
            to=[str(addr) for addr in email.to],
            subject=email.subject,
            body=email.body,
            is_html=email.is_html,
        )
```

**判断标准**：逻辑是"调用外部能力并转换其入参/出参"，与具体业务实体无关。



### 3. 复杂业务计算

涉及**多实体状态、跨仓储数据的计算或规则校验**时，放入领域服务。

示例：`PermissionService` 负责权限树的组装、角色权限保存、用户权限级别运算（组合权限资源仓储与角色仓储）：

```python
async def validate_user_permission(
    self, user_permissions, module_code: str, required_level: int
) -> bool:
    """判断用户权限是否满足所需级别。"""
    user_level = self.get_max_permission_level(user_permissions, module_code)
    return user_level >= required_level
```

**判断标准**：计算需要读取多个数据源或应用多条规则，写成实体方法会导致实体臃肿。



## 什么情况不写领域服务

- **单实体简单操作**： 写在实体方法里；
- **纯数据库读写**：属于仓储职责；
- **用例编排与事务边界**：属于 `application/` 层，领域服务不管理 HTTP 会话与请求上下文。



## 编写约定

- 每个实现类用 `@domain_service_factory.autowire("{module}_domain_service", scope=BeanScope.PROTOTYPE.value)` 注册；

- 服务方法不直接返回 ORM 对象，返回实体/值对象/字典；

  



## 新增领域服务的流程

1. 先确认逻辑不属于单个实体或仓储（对照上文三种场景）；
1. `domain/service/{module}_service.py` 继承 `BaseService` 实现；
1. 需要契约边界时在 `domain/service/interfaces/{module}.py` 声明接口；
1. 用 `autowire` 注册并加入 `app.py` 的 `auto_load_modules` 预加载列表；
1. 应用服务通过 `domain_service_factory.get_bean("{module}_domain_service")` 获取调用。
