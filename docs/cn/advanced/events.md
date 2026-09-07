# 事件系统

FastBrace 事件系统基于**领域事件（Domain Event）** 模式设计，通过事件总线实现领域间的松耦合通信。支持本地内存事件和跨域 Celery 事件两种传输方式，可灵活组合使用。

## 设计思想

### 为什么需要事件系统？

在 DDD 架构中，一个业务操作可能触发多个领域的联动。例如：创建用户后需要发送邮件通知。如果直接在用户服务中调用邮件服务，会产生强耦合。事件系统通过**发布-订阅**模式解耦：

```
用户服务（发布者）                    邮件服务（订阅者）
    │                                     │
    ├── 创建用户                           │
    ├── 发布 UserCreatedEvent ──→ 事件总线 ──→ EmailSendEventHandler
    │                                     │
    ├── 返回成功                            ├── 发送邮件
```



## 配置

在 `infrastructure/config/settings.dev.yaml` 中配置事件总线：

```yaml
event_bus:
  local_transport_type: "memory"       # 本地事件传输：memory
  cross_domain_transport_type: "celery" # 跨域事件传输：celery
  name: "FastBrace"
  enable_event_store: true
  local_event_bus_concurrency: 0        # 0 = 默认（10）
  cross_domain_event_bus_concurrency: 1
```

## 使用步骤

### 第一步：定义领域事件

在 `domain/events/` 下创建事件类，继承 `DomainEvent`：

```python
# domain/events/user_events.py
from enum import Enum
from infrastructure.events.base import DomainEvent

class UserEventType(Enum):
    CREATED = "user.created"
    PASSWORD_CHANGED = "user.password_changed"
    STATUS_CHANGED = "user.status_changed"
    DELETED = "user.deleted"

class _BaseUserEvent(DomainEvent):
    aggregate_type: str = "User"
    is_local: bool = False  # False = 同时发送跨域事件

class UserCreatedEvent(_BaseUserEvent):
    event_type: str = UserEventType.CREATED.value
```

**关键字段说明：**
- `aggregate_type`：聚合根名称，用于事件分类
- `event_type`：事件类型标识，处理器据此分发
- `is_local`：`True` 仅本地处理，`False` 同时发往跨域总线
- `event_data`：事件携带的业务数据（字典）

### 第二步：创建事件处理器

在 `event_handlers/` 下创建处理器，使用 `@EventBusService.subscribe()` 装饰器订阅：

```python
# event_handlers/email_send_handler.py
from infrastructure.events.base import BaseEventHandler, DomainEvent
from infrastructure.events.event_bus_service import EventBusService

@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    __type__ = "email_send_handler"
    SUPPORTED_EVENT_TYPES = ["user.created"]

    def _handle_event(self, event: DomainEvent) -> None:
        # 从 event.event_data 提取业务数据
        email = event.event_data["email"]
        name = event.event_data["name"]
        # 调用邮件服务发送通知...
```



### 第三步：在业务逻辑中发布事件

```python
from infrastructure.events.event_bus_service import EventBusService
from domain.events.user_events import UserCreatedEvent

# 在用户创建成功后
event_bus = EventBusService.get_instance()
task = event_bus.publish_async(UserCreatedEvent(
    aggregate_id=user_id,
    event_data={
        "name": user.name,
        "email": user.email,
        "username": user.username,
        "plain_password": password,
    }
))

# 可选：同步等待结果
# results = event_bus.publish_sync(event)
```



### 第四步：注册模块并启动

确保事件处理器模块在启动时被加载。在 `entrance/event_bus.py` 的 `auto_load_modules` 中添加：

```python
auto_load_modules(
    base_packages=[
        # ... 其他模块
        "domain.events.user_events",
        "event_handlers.email_send_handler",
    ]
)
```

启动事件总线进程：

```bash
python main.py server events
```

## 事件处理器注册机制

```python
@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    ...
```



## 扩展：添加新的事件类型

1. 在 `domain/events/` 下定义新事件类
2. 在 `event_handlers/` 下创建处理器，声明 `SUPPORTED_EVENT_TYPES`
3. 使用 `@EventBusService.subscribe()` 注册到目标领域
4. 在 `entrance/event_bus.py` 的 `auto_load_modules` 中添加新模块路径
5. 重启事件总线服务
