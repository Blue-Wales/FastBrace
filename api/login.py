#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : login.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 认证登录接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from api.request_body.user_request import (
    LoginRequest,
    RefreshTokenRequest,
    RoleLoginRequest,
)
from api.response_model.user_res_model import (
    AccessTokenModel,
    CurrentRoleModel,
    LoginTokenModel,
    LogoutModel,
    UserRolesModel,
)
from infrastructure.core.container import application_factory, repository_factory
from infrastructure.utils.database import get_db
from infrastructure.utils.oauth2_tools import check_token, oauth2_scheme

login_router = APIRouter()


@login_router.post(
    "/login",
    summary="用户名密码登录",
    response_model=LoginTokenModel,
)
async def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    """用户名密码登录"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    role_repo = repository_factory.get_bean("role_repo", db=user_app_service.db)

    access_token, refresh_token = await user_app_service.login_with_role(
        username=request_data.username,
        password_hash=request_data.password,
        role_id=request_data.role_id,
        user_repo=user_repo,
        role_repo=role_repo,
    )

    return JSONResponse(
        status_code=HTTP_200_OK,
        content={"code": 200, "access_token": access_token, "refresh_token": refresh_token},
    )


@login_router.post(
    "/switch-role",
    summary="切换用户角色",
    response_model=AccessTokenModel,
    dependencies=[Depends(check_token)],
)
async def switch_role(request_data: RoleLoginRequest, db: Session = Depends(get_db)):
    """切换用户角色"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    role_repo = repository_factory.get_bean("role_repo", db=user_app_service.db)

    access_token, expires_in = await user_app_service.switch_user_role(
        new_role_id=request_data.role_id,
        user_repo=user_repo,
        role_repo=role_repo,
    )

    return JSONResponse(
        status_code=HTTP_200_OK,
        content={"code": 200, "access_token": access_token, "expires_in": expires_in},
    )


@login_router.get(
    "/users/{username}/roles",
    summary="获取用户角色列表",
    response_model=UserRolesModel,
)
async def get_user_roles(username: str, db: Session = Depends(get_db)):
    """获取用户角色列表"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    user_repo = repository_factory.get_bean("user_repo", db=user_app_service.db)

    roles = await user_app_service.get_user_roles(username=username, user_repo=user_repo)

    return JSONResponse(status_code=HTTP_200_OK, content={"code": 200, "roles": roles})


@login_router.post(
    "/refresh-token",
    summary="刷新token",
    response_model=AccessTokenModel,
)
async def refresh_token(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新token"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    access_token, expires_in = await user_app_service.refresh_token(request_data.refresh_token)

    return JSONResponse(
        status_code=HTTP_200_OK,
        content={"code": 200, "access_token": access_token, "expires_in": expires_in},
    )


@login_router.post(
    "/logout",
    summary="退出登录",
    response_model=LogoutModel,
    dependencies=[Depends(oauth2_scheme)],
)
async def logout(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """退出登录"""

    user_app_service = application_factory.get_bean("user_app_service", db=db)

    await user_app_service.logout(request_data.refresh_token)

    return JSONResponse(status_code=HTTP_200_OK, content={"code": 200, "message": "退出登录成功"})


@login_router.get(
    "/current-role",
    summary="获取当前用户角色",
    response_model=CurrentRoleModel,
    dependencies=[Depends(check_token)],
)
async def get_current_role(db: Session = Depends(get_db)):
    """获取当前用户角色"""

    role_app_service = application_factory.get_bean("role_app_service", db=db)

    role_repo = repository_factory.get_bean("role_repo", db=role_app_service.db)

    result = await role_app_service.get_current_role(role_repo=role_repo)

    return JSONResponse(status_code=HTTP_200_OK, content=result)
