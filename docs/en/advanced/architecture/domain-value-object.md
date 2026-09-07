# Value Object Design Guide

This document describes the applicable scenarios, existing files, and keep-or-drop criteria of `domain/value_object/`.



## When to Write a Value Object

Value objects are descriptive objects that are **identity-free and immutable**: equal values mean equal objects. Criteria:

- It only describes "what it is" (e.g., an email message, file metadata, a user summary) and does not care "which one it is" → Value object;
- It has its own ID and its changes need to be tracked individually → Entity (see the [Entity guide](domain-entity)).

Value objects fit: data transfer shapes reused across entities/repositories, method inputs and outputs, and immutable configuration. Define them with a Pydantic `BaseModel`, enabling `frozen = True` or `from_attributes = True` as needed.



## Existing Value Objects

| File                            | Value Objects                                                    | Used By                                   |
| ------------------------------- | ---------------------------------------------------------------- | ----------------------------------------- |
| `value_object/email_message.py` | `EmailMessage` / `EmailAttachment`                               | Email service and email event handlers    |
| `value_object/file_vo.py`       | `FileVO`                                                         | File repository (attachment read/write)   |
| `value_object/user_vo.py`       | `UserSummaryVO` / `UserMobileVO` / `UserInfoVO` / `UserWorkWxVO` | User repository (list/projection queries) |



## Writing Conventions

- Inherit from `BaseModel`; declare fields with `Field(title="...")`;
- Use `frozen = True` for immutability semantics; use `from_attributes = True` when converting from ORM/entities;
- Class docstrings: one short sentence (e.g., "File value object");
- File names follow `{module}_vo.py`; class names end with `VO`.



## Flow for Adding a New Value Object

1. Confirm it is truly identity-free and immutable, and worth reusing (avoid creating a file for a single use only);
1. Define the model in `domain/value_object/{module}_vo.py`;
1. When repositories/services return VOs, convert them via `model_validate(orm_obj)`.
