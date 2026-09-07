# Domain Service Design Guide

This document describes in detail the use cases, directory structure, and writing conventions of `domain/service/`.



## When to Write a Domain Service

Domain services carry business logic that **does not belong to a single entity**. Consider a domain service only when a use case cannot fit into any entity's method. There are three specific scenarios:



### 1. Cross-Domain Coordination

When a use case needs **multiple entities, repositories, or domain services combined** to complete, put the coordination logic in a domain service.

Example: `RoleService.get_relation_users` queries and aggregates related users role by role, while `UserService.get_users` combines user query results with role mappings:

```python
async def get_relation_users(self, role_repo: RoleRepository, role_ids: list[int]):
    """Aggregate and deduplicate related user IDs role by role."""
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

**Criterion**: the logic involves multiple objects and cannot reasonably be assigned to any single entity's responsibility.



### 2. Calling Third-Party Services

When integrating with **external systems** (SMTP, OSS, third-party APIs), wrap them in a domain service to keep external dependencies isolated from the domain layer.

Example: `SMTPEmailService` hands the `EmailMessage` value object to `EmailSender` (`infrastructure/utils/email_utils.py`) for delivery:

```python
@domain_service_factory.autowire("email_domain_service", scope=BeanScope.PROTOTYPE.value)
class SMTPEmailService(BaseService):
    """SMTP-based email service implementation"""

    def send_email(self, email: EmailMessage) -> bool:
        """Send an email"""
        return self.email_sender.send_email(
            to=[str(addr) for addr in email.to],
            subject=email.subject,
            body=email.body,
            is_html=email.is_html,
        )
```

**Criterion**: the logic is "invoke an external capability and adapt its input/output", independent of any specific business entity.



### 3. Complex Business Computations

When the logic involves **multi-entity state, computations across repositories, or rule validation**, put it in a domain service.

Example: `PermissionService` handles permission tree assembly, saving role permissions, and computing user permission levels (combining the permission resource repository with the role repository):

```python
async def validate_user_permission(
    self, user_permissions, module_code: str, required_level: int
) -> bool:
    """Check whether the user's permission meets the required level."""
    user_level = self.get_max_permission_level(user_permissions, module_code)
    return user_level >= required_level
```

**Criterion**: the computation needs to read multiple data sources or apply multiple rules; writing it as entity methods would bloat the entities.



## When NOT to Write a Domain Service

- **Simple single-entity operations**: write them as entity methods;
- **Pure database reads/writes**: the repository's responsibility;
- **Use case orchestration and transaction boundaries**: they belong to the `application/` layer; domain services do not manage HTTP sessions or request context.



## Writing Conventions

- Register each implementation class with `@domain_service_factory.autowire("{module}_domain_service", scope=BeanScope.PROTOTYPE.value)`;

- Service methods do not return ORM objects directly; return entities/value objects/dicts;




## Flow for Adding a New Domain Service

1. First confirm the logic does not belong to a single entity or repository (check against the three scenarios above);
1. Implement it in `domain/service/{module}_service.py` by inheriting `BaseService`;
1. When a contract boundary is needed, declare an interface in `domain/service/interfaces/{module}.py`;
1. Register with `autowire` and add it to the `auto_load_modules` preload list in `app.py`;
1. Application services fetch and call it via `domain_service_factory.get_bean("{module}_domain_service")`.
