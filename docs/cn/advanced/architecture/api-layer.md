# API 层设计指南

本文档说明 `api/` 层的目录职责、模型约定与接口编写规范

## 分层定位

`api/` 是 DDD 的表现层，职责主要包含三件事：解析请求、编排调用下层服务、统一返回响应。业务规则在 `domain/`，流程编排在 `application/`，API 层不承载业务逻辑。

## 目录职责

```text
api/
├── dto/             # 跨层传输的数据载体，仅含数据，无行为
├── request_body/    # 入参模型：Pydantic 校验与类型转换
├── response_body/   # 出参模型：响应数据结构定义
├── response_model/  # 响应模型：Swagger（接口文档）展示的信息
└── *.py             # 路由模块，一个文件一个业务域
```

## 模型约定

### dto

主要用途：字段裁剪。多数接口直接使用 request/response 模型即可，DTO 仅在需要显式跨层传递视图时引入。



### request_body

入参模型。约束写在 `Field` 中，由 FastAPI 自动校验，非法入参返回 422。列表接口继承 `PageRequest` 获得分页参数

```python
@field_validator("password")
@classmethod
def validate_password(cls, v: str) -> str:
    """验证并自动解密密码"""
    return rsa_password_validator(v)
```



### response_body

出参模型，定义返回给前端的结构。与实体的字段差异用 `alias` 处理，输出格式化用 `field_validator`：

```python
class UserItemResponse(BaseModel):
    """用户列表信息响应体"""

    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
```

响应体可继承组合公共字段，如 `CreateDepartmentResponse(DepartmentInfoResponse)`。



### response_model

`response_body` 定义数据内容，`response_model` 定义完整响应数据结构（code/message/data）并在 Swagger 文档呈现，由 `infrastructure/utils/response_model_generator.py` 动态生成：

```python
@user_router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=generate_response_model(CurrentUserModel, "current_user"),
)
```

分页/列表接口分别使用 `generate_paged_response_model`（total/page/page_size/items/pages）与 `generate_list_response_model`（items）。



## 路由编写约定

路由模块统一三段式：

1. 装饰器声明契约：`summary`、`response_model`、权限依赖（`Depends(require_admin())`、`Depends(oauth2_scheme)` 等）；
1. 工厂获取依赖：`application_factory.get_bean(...)` / `repository_factory.get_bean(...)`；
1. 调用应用服务，`JSONResponse(status_code=HTTP_200_OK, content=result)` 统一出口。

```python
@user_router.get(
    "/{user_id}",
    summary="用户详细信息",
    response_model=generate_response_model(UserInfoModel, "user_info"),
    dependencies=[Depends(oauth2_scheme)],
)
async def users_info(user_id: int, db: Session = Depends(get_db)):
    """获取用户详细信息
    """
    user_app_service: IUserAppService = application_factory.get_bean("user_app_service", db=db)
    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)
    result = await user_app_service.get_user_info(user_repo=user_repo, user_id=user_id)
    return JSONResponse(status_code=HTTP_200_OK, content=result)
```



## 新增接口流程

1. `api/request_body/{module}_request.py` 定义入参模型；
1. `api/response_body/{module}_response.py` 定义出参模型；
1. `api/response_model/{module}_res_model.py` 定义响应模型；
1. `api/{module}.py` 编写路由（上述三段式）；
1. `infrastructure/core/routers.py` 注册路由（`prefix` + `tags`）；
1. 访问 `/docs` 核对 Swagger 文档。
