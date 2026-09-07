# Event System

The FastBrace event system follows the **Domain Event** pattern, using an event bus to achieve loose coupling between domains. It supports both local in-memory events and cross-domain Celery events, which can be flexibly combined.

## Design Philosophy

### Why Is an Event System Needed?

In a DDD architecture, a single business operation may trigger actions across multiple domains. For example: after a user is created, a welcome email needs to be sent. Calling the email service directly from the user service would create tight coupling. The event system decouples them through the **publish-subscribe** pattern:

```
User service (publisher)              Email service (subscriber)
    │                                     │
    ├── Create user                       │
    ├── Publish UserCreatedEvent ──→ Event bus ──→ EmailSendEventHandler
    │                                     │
    ├── Return success                    ├── Send email
```

## Configuration

Configure the event bus in `infrastructure/config/settings.dev.yaml`:

```yaml
event_bus:
  local_transport_type: "memory"       # local event transport: memory
  cross_domain_transport_type: "celery" # cross-domain event transport: celery
  name: "FastBrace"
  enable_event_store: true
  local_event_bus_concurrency: 0        # 0 = default (10)
  cross_domain_event_bus_concurrency: 1
```

## Usage Steps

### Step 1: Define Domain Events

Create event classes under `domain/events/`, inheriting from `DomainEvent`:

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
    is_local: bool = False  # False = also dispatch as a cross-domain event

class UserCreatedEvent(_BaseUserEvent):
    event_type: str = UserEventType.CREATED.value
```

**Key fields:**
- `aggregate_type`: aggregate root name, used for event classification
- `event_type`: event type identifier; handlers dispatch on it
- `is_local`: `True` processes locally only, `False` also sends to the cross-domain bus
- `event_data`: business data carried by the event (a dict)

### Step 2: Create an Event Handler

Create handlers under `event_handlers/` and subscribe with the `@EventBusService.subscribe()` decorator:

```python
# event_handlers/email_send_handler.py
from infrastructure.events.base import BaseEventHandler, DomainEvent
from infrastructure.events.event_bus_service import EventBusService

@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    __type__ = "email_send_handler"
    SUPPORTED_EVENT_TYPES = ["user.created"]

    def _handle_event(self, event: DomainEvent) -> None:
        # Extract business data from event.event_data
        email = event.event_data["email"]
        name = event.event_data["name"]
        # Call the email service to send the notification...
```

### Step 3: Publish Events in Business Logic

```python
from infrastructure.events.event_bus_service import EventBusService
from domain.events.user_events import UserCreatedEvent

# After a user is created successfully
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

# Optional: wait for results synchronously
# results = event_bus.publish_sync(event)
```

### Step 4: Register Modules and Start

Make sure the event handler modules are loaded at startup. Add them to `auto_load_modules` in `entrance/event_bus.py`:

```python
auto_load_modules(
    base_packages=[
        # ... other modules
        "domain.events.user_events",
        "event_handlers.email_send_handler",
    ]
)
```

Start the event bus process:

```bash
python main.py server events
```

## Event Handler Registration Mechanism

```python
@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    ...
```

## Extending: Adding a New Event Type

1. Define the new event class under `domain/events/`
2. Create a handler under `event_handlers/` and declare its `SUPPORTED_EVENT_TYPES`
3. Register it to the target domain with `@EventBusService.subscribe()`
4. Add the new module path to `auto_load_modules` in `entrance/event_bus.py`
5. Restart the event bus service
