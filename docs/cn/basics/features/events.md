# 事件系统

FastBrace 内置了基于**领域事件**的事件总线系统，支持本地事件和跨域事件两种模式，实现领域间的松耦合通信。



## 核心概念

- **领域事件**：继承自 `DomainEvent` 基类，包含聚合类型、事件类型、事件数据等字段
- **事件处理器**：继承 `BaseEventHandler`，通过 `@EventBusService.subscribe()` 装饰器订阅指定领域的事件
- **本地事件**：使用内存线程池（`MemoryEventBus`）处理，适用于同进程内的事件通知
- **跨域事件**：基于 Celery + Redis 实现（`CeleryEventBus`），适用于跨服务/跨领域的异步事件处理
- **事件总线服务**：`EventBusService` 采用单例模式，统一管理本地和跨域事件总线的注册、订阅和发布



## 文件位置

| 文件 | 说明 |
|------|------|
| `infrastructure/events/base.py` | 事件基类（DomainEvent、BaseEventHandler、BaseEventBus） |
| `infrastructure/events/event_bus_service.py` | 事件总线服务（单例，核心调度） |
| `infrastructure/events/memory.py` | 内存事件总线实现 |
| `infrastructure/events/celery.py` | Celery 事件总线实现 |
| `domain/events/user_events.py` | 用户领域事件定义 |
| `event_handlers/email_send_handler.py` | 邮件事件处理器示例 |
| `entrance/event_bus.py` | 事件总线启动入口 |



## 使用方式

### 1. 定义事件

在 `domain/events/` 下创建事件类，继承 `DomainEvent`：

```python
from infrastructure.events.base import DomainEvent

class UserCreatedEvent(DomainEvent):
    aggregate_type: str = "User"
    event_type: str = "user.created"
    is_local: bool = False  # 跨域事件
```



### 2. 创建事件处理器

在 `event_handlers/` 下创建处理器，使用装饰器订阅：

```python
from infrastructure.events.base import BaseEventHandler, DomainEvent
from infrastructure.events.event_bus_service import EventBusService

@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    __type__ = "email_send_handler"
    SUPPORTED_EVENT_TYPES = ["user.created"]

    def _handle_event(self, event: DomainEvent) -> None:
        # 处理事件逻辑
        ...
```



### 3. 发布事件

在业务逻辑中通过 `EventBusService` 发布事件：

```python
event_bus = EventBusService.get_instance()
event_bus.publish_async(UserCreatedEvent(
    event_data={"name": "张三", "email": "zhangsan@example.com"}
))
```



### 4. 启动事件总线

```bash
python main.py server events
```

## 常见业务场景

以下业务场景适合使用事件系统：

- **异步调用耗时第三方接口**：当用户操作无需等待第三方接口返回时，发布事件交由事件处理器异步调用，如同步快递单号、接入外部风控或支付回调
- **批量解析 / 批量上传**：将文件解析、批量数据落库等耗时操作放入事件处理器异步执行，避免阻塞请求线程
- **业务解耦通知**：注册、下单等业务完成后发布事件，异步触发邮件、短信等通知，各处理器相互独立、互不影响
