#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 权限相关接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from api.request_body.permission_request import (
    SaveRolePermissionsRequest,
    ValidatePermissionRequest,
)
from api.response_body.permission_response import (
    DetailedPermissionNodeResponse,
    PermissionSystemInfoResponse,
    PermissionTreeNodeResponse,
    SavePermissionResponse,
    ValidatePermissionResponse,
)
from infrastructure.core.container import (
    application_factory,
    domain_service_factory,
    repository_factory,
)
from infrastructure.utils.database import get_db
from infrastructure.utils.oauth2_tools import oauth2_scheme
from infrastructure.utils.response_model_generator import generate_response_model

permission_router = APIRouter()


@permission_router.get(
    "/tree",
    summary="获取权限树",
    response_model=generate_response_model(list[PermissionTreeNodeResponse], "permission_tree"),
)
async def get_permission_tree(db: Session = Depends(get_db)):
    """获取权限树"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.get_permission_tree(permission_service=permission_service)

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.get(
    "/role/{role_id}",
    summary="获取角色权限树",
    response_model=generate_response_model(
        list[PermissionTreeNodeResponse], "role_permission_tree"
    ),
)
async def get_role_permission_tree(role_id: int, db: Session = Depends(get_db)):
    """获取角色权限树"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.get_role_permission_tree(
        role_id=role_id, permission_service=permission_service
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.post(
    "/role/save",
    summary="保存角色权限",
    response_model=generate_response_model(SavePermissionResponse, "save_permission_result"),
)
async def save_role_permissions(
    request_data: SaveRolePermissionsRequest, db: Session = Depends(get_db)
):
    """保存角色权限"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.save_role_permissions(
        role_id=request_data.role_id,
        permissions=request_data.permissions,
        permission_service=permission_service,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.get(
    "/role/{role_id}/detailed",
    summary="获取角色细粒度权限",
    response_model=generate_response_model(
        list[DetailedPermissionNodeResponse], "detailed_permissions"
    ),
)
async def get_role_detailed_permissions(role_id: int, db: Session = Depends(get_db)):
    """获取角色细粒度权限"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.get_role_detailed_permissions(
        role_id=role_id, permission_service=permission_service
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.get(
    "/user/detailed",
    summary="获取当前用户细粒度权限",
    response_model=generate_response_model(
        list[DetailedPermissionNodeResponse], "user_detailed_permissions"
    ),
    dependencies=[Depends(oauth2_scheme)],
)
async def get_user_detailed_permissions(db: Session = Depends(get_db)):
    """获取当前用户细粒度权限"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.get_user_detailed_permissions(
        permission_service=permission_service
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.post(
    "/validate",
    summary="验证权限",
    response_model=generate_response_model(
        ValidatePermissionResponse, "validate_permission_result"
    ),
)
async def validate_permission(
    request_data: ValidatePermissionRequest, db: Session = Depends(get_db)
):
    """验证权限"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    role_repo = repository_factory.get_bean("role_repo", db=permission_app_service.db)

    permission_service = domain_service_factory.get_bean(
        "permission_service",
        permission_repo=permission_repo,
        role_repo=role_repo,
    )

    result = await permission_app_service.validate_permission(
        user_permissions=request_data.user_permissions,
        module_code=request_data.module_code,
        required_level=request_data.required_level,
        permission_service=permission_service,
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)


@permission_router.get(
    "/system/info",
    summary="获取权限系统信息",
    response_model=generate_response_model(PermissionSystemInfoResponse, "permission_system_info"),
)
async def get_permission_system_info(db: Session = Depends(get_db)):
    """获取权限系统信息"""

    permission_app_service = application_factory.get_bean("permission_app_service", db=db)

    permission_repo = repository_factory.get_bean(
        "permission_resource_repo", db=permission_app_service.db
    )

    result = await permission_app_service.get_permission_system_info(
        permission_repo=permission_repo
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)
