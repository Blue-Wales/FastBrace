#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户管理接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from api.request_body.user_request import (
    CreateUserRequest,
    EditUserPasswordRequest,
    EditUserRequest,
    EditUserStatusRequest,
    GetUserNameListRequest,
    GetUsersRequest,
)
from api.response_body.json_response import BaseResponseModel
from api.response_model.user_res_model import (
    CurrentUserModel,
    UserInfoModel,
    UserItemModel,
    UserResModel,
)
from infrastructure.core.container import (
    application_factory,
    domain_service_factory,
    repository_factory,
)
from infrastructure.core.enum_var import PermissionLevel, Permissions
from infrastructure.core.permissions_limit import require_admin, require_permission
from infrastructure.utils.database import get_db
from infrastructure.utils.oauth2_tools import oauth2_scheme
from infrastructure.utils.response_model_generator import (
    generate_list_response_model,
    generate_paged_response_model,
    generate_response_model,
)

user_router = APIRouter()


@user_router.post(
    "",
    summary="新增用户",
    response_model=generate_response_model(BaseResponseModel, "add_user"),
    dependencies=[Depends(require_admin())],
)
async def add_user(request_data: CreateUserRequest, db: Session = Depends(get_db)):
    """新增用户"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    file_repo = repository_factory.get_bean("file_repo", db=user_app_service.db)

    result = await user_app_service.add_user(
        user_repo=user_repo,
        file_repo=file_repo,
        request_data=request_data,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.get(
    "",
    summary="获取用户列表",
    response_model=generate_paged_response_model(UserItemModel, "user_list"),
    dependencies=[
        Depends(
            require_permission(
                permission_module=Permissions.ACCOUNT,
                required_permissions=[PermissionLevel.VIEW],
            )
        )
    ],
)
async def users_list(request_data: GetUsersRequest, db: Session = Depends(get_db)):
    """获取用户列表"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_domain_service = domain_service_factory.get_bean("user_domain_service")

    role_domain_service = domain_service_factory.get_bean("role_domain_service")

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    role_repo = repository_factory.get_bean("role_repo", db=user_app_service.db)

    result = await user_app_service.get_users(
        user_repo=user_repo,
        role_repo=role_repo,
        user_domain_service=user_domain_service,
        role_domain_service=role_domain_service,
        name=request_data.name,
        mobile=request_data.mobile,
        role_ids=request_data.role_ids,
        status=request_data.status,
        page=request_data.page,
        page_size=request_data.page_size,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=generate_response_model(CurrentUserModel, "current_user"),
)
async def get_current_user(db: Session = Depends(get_db)):
    """获取当前用户信息"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    role_domain_service = domain_service_factory.get_bean("role_domain_service")

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    role_repo = repository_factory.get_bean("role_repo", db=user_app_service.db)

    file_repo = repository_factory.get_bean("file_repo", db=user_app_service.db)

    result = await user_app_service.get_current_user(
        role_domain_service=role_domain_service,
        user_repo=user_repo,
        role_repo=role_repo,
        file_repo=file_repo,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.get(
    "/choices",
    summary="获取用户名称列表",
    response_model=generate_list_response_model(UserResModel, "user_name_list"),
    dependencies=[
        Depends(
            require_permission(
                permission_module=Permissions.ACCOUNT,
                required_permissions=[PermissionLevel.VIEW],
            )
        )
    ],
)
async def user_name_list(
    request_data: GetUserNameListRequest, db: Session = Depends(get_db)
):
    """获取用户名称列表"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    result = await user_app_service.get_user_name_list(
        user_repo=user_repo, name=request_data.name
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.get(
    "/{user_id}",
    summary="用户详细信息",
    response_model=generate_response_model(UserInfoModel, "user_info"),
    dependencies=[
        Depends(
            require_permission(
                permission_module=Permissions.ACCOUNT,
                required_permissions=[PermissionLevel.VIEW],
            )
        ),
        Depends(oauth2_scheme),
    ],
)
async def users_info(user_id: int, db: Session = Depends(get_db)):
    """获取用户详细信息"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    role_domain_service = domain_service_factory.get_bean("role_domain_service")

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    role_repo = repository_factory.get_bean("role_repo", db=user_app_service.db)

    file_repo = repository_factory.get_bean("file_repo", db=user_app_service.db)

    result = await user_app_service.get_user_info(
        role_domain_service=role_domain_service,
        user_repo=user_repo,
        role_repo=role_repo,
        file_repo=file_repo,
        user_id=user_id,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.post(
    "/{user_id}",
    summary="编辑用户",
    response_model=generate_response_model(BaseResponseModel, "edit_user"),
    dependencies=[Depends(require_admin())],
)
async def edit_user(
    user_id: int, request_data: EditUserRequest, db: Session = Depends(get_db)
):
    """编辑用户"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    file_repo = repository_factory.get_bean("file_repo", db=user_app_service.db)

    result = await user_app_service.edit_user(
        user_id=user_id,
        user_repo=user_repo,
        file_repo=file_repo,
        request_data=request_data,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.delete(
    "/{user_id}",
    summary="删除用户",
    response_model=generate_response_model(BaseResponseModel, "delete_user"),
    dependencies=[Depends(require_admin())],
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    file_repo = repository_factory.get_bean("file_repo", db=user_app_service.db)

    result = await user_app_service.delete_user(
        user_id=user_id, user_repo=user_repo, file_repo=file_repo
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.post(
    "/me/password",
    summary="修改当前用户密码",
    response_model=generate_response_model(BaseResponseModel, "edit_user_password"),
)
async def edit_current_user_password(
    request_data: EditUserPasswordRequest, db: Session = Depends(get_db)
):
    """修改当前用户密码"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    result = await user_app_service.change_current_user_password(
        user_repo=user_repo,
        request_data=request_data,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.post(
    "/{user_id}/password",
    summary="修改用户密码",
    response_model=generate_response_model(BaseResponseModel, "edit_user_password"),
    dependencies=[Depends(require_admin())],
)
async def edit_user_password(
    user_id: int,
    request_data: EditUserPasswordRequest,
    db: Session = Depends(get_db),
):
    """修改用户密码"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    result = await user_app_service.change_user_password(
        user_id=user_id, user_repo=user_repo, request_data=request_data
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@user_router.post(
    "/batch/status",
    summary="批量修改用户状态",
    response_model=generate_response_model(BaseResponseModel, "edit_user_status"),
    dependencies=[Depends(require_admin())],
)
async def edit_user_status(
    request_data: EditUserStatusRequest, db: Session = Depends(get_db)
):
    """批量修改用户状态"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    result = await user_app_service.change_user_status(
        user_repo=user_repo,
        request_data=request_data,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)
