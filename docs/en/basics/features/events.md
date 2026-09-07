# Event System

FastBrace ships with an event bus system based on **domain events**, supporting both local and cross-domain event modes for loosely coupled communication between domains.

## Core Concepts

- **Domain event (DomainEvent)**: Inherits from the `DomainEvent` base class and contains fields such as aggregate type, event type, and event data
- **Event handler (EventHandler)**: Inherits `BaseEventHandler` and subscribes to events of a specific domain via the `@EventBusService.subscribe()` decorator
- **Local events**: Handled by an in-memory thread pool (`MemoryEventBus`), suitable for in-process event notifications
- **Cross-domain events**: Built on Celery + Redis (`CeleryEventBus`), suitable for asynchronous event handling across services/domains
- **Event bus service**: `EventBusService` is a singleton that centrally manages registration, subscription, and publishing for both the local and cross-domain event buses

## File Locations

| File | Description |
|------|------|
| `infrastructure/events/base.py` | Event base classes (DomainEvent, BaseEventHandler, BaseEventBus) |
| `infrastructure/events/event_bus_service.py` | Event bus service (singleton, core dispatch) |
| `infrastructure/events/memory.py` | In-memory event bus implementation |
| `infrastructure/events/celery.py` | Celery event bus implementation |
| `domain/events/user_events.py` | User domain event definitions |
| `event_handlers/email_send_handler.py` | Example email event handler |
| `entrance/event_bus.py` | Event bus startup entry point |

## Usage

### 1. Define an Event

Create an event class under `domain/events/` that inherits from `DomainEvent`:

```python
from infrastructure.events.base import DomainEvent

class UserCreatedEvent(DomainEvent):
    aggregate_type: str = "User"
    event_type: str = "user.created"
    is_local: bool = False  # Cross-domain event
```

### 2. Create an Event Handler

Create a handler under `event_handlers/` and subscribe with the decorator:

```python
from infrastructure.events.base import BaseEventHandler, DomainEvent
from infrastructure.events.event_bus_service import EventBusService

@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    __type__ = "email_send_handler"
    SUPPORTED_EVENT_TYPES = ["user.created"]

    def _handle_event(self, event: DomainEvent) -> None:
        # Event handling logic
        ...
```

### 3. Publish an Event

Publish events in business logic via `EventBusService`:

```python
event_bus = EventBusService.get_instance()
event_bus.publish_async(UserCreatedEvent(
    event_data={"name": "张三", "email": "zhangsan@example.com"}
))
```

### 4. Start the Event Bus

```bash
python main.py server events
```

## Common Business Scenarios

The following scenarios benefit from the event system:

- **Async calls to slow third-party APIs**: when the user's operation does not need to wait for the third-party response, publish an event and let the event handler invoke the call asynchronously, e.g. syncing a tracking number, integrating an external risk-control or payment callback
- **Batch parsing / batch upload**: offload time-consuming operations such as file parsing and batch data persistence to event handlers, avoiding blocking the request thread
- **Decoupled notifications**: after a business operation such as registration or ordering completes, publish an event to asynchronously trigger email/SMS notifications, with each handler independent and non-blocking
