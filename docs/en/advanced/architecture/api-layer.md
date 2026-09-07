# API Layer Design Guide

This document describes the directory responsibilities, model conventions, and endpoint writing standards of the `api/` layer.

## Layer Positioning

`api/` is the presentation layer of DDD. Its responsibilities mainly cover three things: parsing requests, orchestrating calls to lower-layer services, and returning unified responses. Business rules live in `domain/`, flow orchestration in `application/`; the API layer carries no business logic.

## Directory Responsibilities

```text
api/
├── dto/             # Cross-layer data carriers: data only, no behavior
├── request_body/    # Input models: Pydantic validation and type conversion
├── response_body/   # Output models: response data structure definitions
├── response_model/  # Response models: information shown in Swagger (API docs)
└── *.py             # Router modules, one file per business domain
```

## Model Conventions

### dto

Main purpose: field trimming. Most endpoints can use the request/response models directly; introduce a DTO only when a view needs to be passed across layers explicitly.



### request_body

Input models. Constraints are written in `Field` and validated automatically by FastAPI; invalid input returns 422. List endpoints inherit `PageRequest` to gain pagination parameters.

```python
@field_validator("password")
@classmethod
def validate_password(cls, v: str) -> str:
    """Validate and decrypt the password automatically"""
    return rsa_password_validator(v)
```



### response_body

Output models defining the structure returned to the frontend. Field name differences from entities are handled with `alias`; output formatting uses `field_validator`:

```python
class UserItemResponse(BaseModel):
    """User list item response body"""

    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
```

Response bodies can inherit to compose common fields, e.g., `CreateDepartmentResponse(DepartmentInfoResponse)`.



### response_model

`response_body` defines the data content; `response_model` defines the full response envelope (code/message/data) and is rendered in the Swagger docs, generated dynamically by `infrastructure/utils/response_model_generator.py`:

```python
@user_router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=generate_response_model(CurrentUserModel, "current_user"),
)
```

Pagination/list endpoints use `generate_paged_response_model` (total/page/page_size/items/pages) and `generate_list_response_model` (items) respectively.



## Router Writing Conventions

Router modules follow a unified three-part structure:

1. Decorators declare the contract: `summary`, `response_model`, permission dependencies (`Depends(require_admin())`, `Depends(oauth2_scheme)`, etc.);
1. Factories fetch dependencies: `application_factory.get_bean(...)` / `repository_factory.get_bean(...)`;
1. Call the application service, with `JSONResponse(status_code=HTTP_200_OK, content=result)` as the unified exit.

```python
@user_router.get(
    "/{user_id}",
    summary="用户详细信息",
    response_model=generate_response_model(UserInfoModel, "user_info"),
    dependencies=[Depends(oauth2_scheme)],
)
async def users_info(user_id: int, db: Session = Depends(get_db)):
    """Get user detail info
    """
    user_app_service: IUserAppService = application_factory.get_bean("user_app_service", db=db)
    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)
    result = await user_app_service.get_user_info(user_repo=user_repo, user_id=user_id)
    return JSONResponse(status_code=HTTP_200_OK, content=result)
```



## Flow for Adding a New Endpoint

1. Define the input model in `api/request_body/{module}_request.py`;
1. Define the output model in `api/response_body/{module}_response.py`;
1. Define the response model in `api/response_model/{module}_res_model.py`;
1. Write the router in `api/{module}.py` (the three-part structure above);
1. Register the router in `infrastructure/core/routers.py` (`prefix` + `tags`);
1. Visit `/docs` to verify the Swagger documentation.
