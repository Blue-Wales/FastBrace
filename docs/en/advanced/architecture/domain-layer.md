# Domain Layer Design Guide

This document describes the directory structure of the `domain/` layer and the scenarios each subdirectory is designed for.



## Layer Positioning

`domain/` is the core layer of DDD, carrying business rules and domain models.



## Directory Responsibilities

```text
domain/
├── aggregate_root/     # Aggregate root: strongly consistent entry point bounded by the aggregate
├── entity/             # Domain entities: identifiable, mutable domain objects
├── events/             # Domain events: async task events are defined here
├── repo/               # Repositories: database operation implementations and interface contracts
│   └── interfaces/     # Repository abstract interfaces
├── service/            # Domain services: cross-domain coordination, third-party calls, complex computations
│   └── interfaces/     # Domain abstract interfaces
└── value_object/       # Value objects: identity-free, immutable descriptive objects
```



## Domain Events (events)

**When to use them**: define events here when a business operation needs follow-up handling through async tasks after it succeeds.

Common scenarios: sending notifications such as emails, writing logs, syncing caches, etc. Publish a domain event and let `event_handlers/` consume it asynchronously, avoiding direct calls to side-effect logic inside a transaction.





## Document Navigation

| Document                            | Content                                                         |
| ----------------------------------- | --------------------------------------------------------------- |
| [Entity](domain-entity)             | Entity definition, Entity base class, writing conventions      |
| [Value Object](domain-value-object) | Value object scenarios, keep-or-drop guidance, writing conventions |
| [Repository](domain-repo)           | Database operation boundaries, base class, interface contracts |
| [Domain Service](domain-service)    | Details on cross-domain / third-party / complex computations   |
