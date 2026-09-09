#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_app.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户应用服务
"""

from typing import Any, Protocol

from loguru import logger
from redis.exceptions import RedisError

from api.request_body.user_request import (
    CreateUserRequest,
    EditUserPasswordRequest,
    EditUserRequest,
    EditUserStatusRequest,
)
from api.response_body.json_response import ResponseListModel
from api.response_body.user_response import (
    CurrentUserInfo,
    UserExtraInfoResponse,
    UserItemResponse,
)
from application.base import BaseApplicationService, IBaseApplicationService
from domain.entity.user import UserEntity
from domain.events.user_events import UserCreatedEvent
from domain.repo.file_repo import FileRepository
from domain.repo.interfaces.file import IFileRepository
from domain.repo.interfaces.user import IUserRepository
from domain.repo.role_repo import RoleRepository
from domain.service.role_service import RoleService
from domain.service.user_service import UserService
from infrastructure.core.container import application_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.core.error_handler import (
    InvalidInputError,
    NotFoundError,
    PermissionDeniedError,
    StatusError,
)
from infrastructure.core.settings import app_settings
from infrastructure.events.event_bus_service import EventBusService
from infrastructure.utils.admin_constants import ADMIN_USER_ID
from infrastructure.utils.context import (
    get_current_token,
    get_current_user_id,
    get_username,
)
from infrastructure.utils.jwt_utils import create_access_token, create_refresh_token
from infrastructure.utils.oauth2_tools import (
    revoke_token,
    revoke_user_tokens,
    verify_token,
)
from infrastructure.utils.password_utils import (
    generate_random_password,
    hash_password,
    verify_password,
)


class IUserAppService(IBaseApplicationService, Protocol):
    """用户应用服务接口"""

    async def login(
        self, username: str, password_hash: str, user_repo: IUserRepository
    ) -> tuple[str, int]:
        """用户登录"""
        ...


    async def refresh_token(self, refresh_token: str) -> tuple[str, int]:
        """刷新 token"""
        ...


    async def get_user_info(
        self,
        role_domain_service: RoleService,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        file_repo: FileRepository,
        user_id: int,
    ) -> dict[str, Any]:
        """获取用户详细信息"""
        ...


    async def add_user(
        self,
        user_repo: IUserRepository,
        file_repo: FileRepository,
        request_data: CreateUserRequest,
    ) -> dict[str, Any]:
        """新增用户"""
        ...


    async def delete_user(
        self,
        user_id: int,
        user_repo: IUserRepository,
        file_repo: IFileRepository,
    ):
        """删除用户"""
        ...


    async def get_users(
        self,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        role_domain_service: RoleService,
        user_domain_service: UserService,
        name: str | None = None,
        mobile: str | None = None,
        role_ids: list[int] | None = None,
        status: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """获取用户列表"""
        ...


    async def edit_user(
        self,
        user_id: int,
        user_repo: IUserRepository,
        file_repo: FileRepository,
        request_data: EditUserRequest,
    ) -> dict[str, Any]:
        """编辑用户"""
        ...


    async def get_current_user(
        self,
        role_domain_service: RoleService,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        file_repo: FileRepository,
    ) -> dict[str, Any]:
        """获取当前用户信息"""
        ...


    async def change_user_status(
        self,
        user_repo: IUserRepository,
        request_data: EditUserStatusRequest,
    ) -> dict[str, Any]:
        """变更用户状态"""
        ...


    async def change_user_password(
        self,
        user_id: int,
        user_repo: IUserRepository,
        request_data: EditUserPasswordRequest,
    ) -> dict[str, Any]:
        """修改用户密码"""
        ...


    async def change_current_user_password(
        self,
        user_repo: IUserRepository,
        request_data: EditUserPasswordRequest,
    ) -> dict[str, Any]:
        """修改当前用户密码"""
        ...


    async def delete_refresh_token(self, user_id: int):
        """删除 refresh_token"""
        ...


    async def logout(self, refresh_token: str):
        """用户退出登录"""
        ...


    async def revoke_all_user_tokens(self, user_id: int):
        """撤销用户的所有 token（用于禁用用户或强制下线）"""
        ...


    async def get_user_roles(self, username: str, user_repo: IUserRepository) -> list[int]:
        """获取用户角色列表"""
        ...


    async def switch_user_role(
        self,
        new_role_id: int,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
    ) -> tuple[str, int]:
        """切换用户角色"""
        ...


    async def login_with_role(
        self,
        username: str,
        password_hash: str,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        role_id: int | None = None,
    ) -> tuple[str, int]:
        """带角色选择的用户登录"""
        ...


@application_factory.autowire("user_app_service", scope=BeanScope.PROTOTYPE.value)
class UserAppService(BaseApplicationService):
    """用户应用服务"""

    async def login(
        self, username: str, password_hash: str, user_repo: IUserRepository
    ) -> tuple[str, str]:
        """用户登录"""

        user: UserEntity | None = await user_repo.get_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")
        if not user.status:
            raise StatusError("用户已禁用")
        if not verify_password(password_hash, user.password_hash):
            raise InvalidInputError("密码错误")
        payload = {
            "sub": str(user.entity_id),
            "user_name": user.name,
        }
        access_token = create_access_token(
            payload,
            redis_client=self.redis_client,
        )
        refresh_token = create_refresh_token(
            payload,
            redis_client=self.redis_client,
        )

        return access_token, refresh_token


    async def login_with_role(
        self,
        username: str,
        password_hash: str,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        role_id: int | None = None,
    ) -> tuple[str, str]:
        """带角色选择的用户登录"""
        user: UserEntity | None = await user_repo.get_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")
        if not user.status:
            raise StatusError("用户已禁用")
        if not verify_password(password_hash, user.password_hash):
            raise InvalidInputError("密码错误")

        if not role_id:
            role_id = await user_repo.get_default_role_id(user.entity_id)
        elif not await user_repo.has_role(user.entity_id, role_id):
            raise PermissionDeniedError("用户没有该角色权限，请选择其他角色")

        role_permissions = await role_repo.get_by_id(role_id)
        if not role_permissions:
            raise NotFoundError("角色不存在")

        payload = {


            "sub": str(user.entity_id),
            "user_name": user.name,
            "role_id": role_id,
            "permissions": role_permissions.permissions,
        }
        access_token = create_access_token(
            payload,
            redis_client=self.redis_client,
        )
        refresh_token = create_refresh_token(
            payload,
            redis_client=self.redis_client,
        )

        return access_token, refresh_token


    async def switch_user_role(
        self,
        new_role_id: int,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
    ) -> tuple[str, int]:
        """切换用户角色"""
        user_id = get_current_user_id()
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("用户不存在")

        if not await user_repo.has_role(user_id, new_role_id):
            raise PermissionDeniedError("用户没有该角色权限")


        role_permissions = await role_repo.get_by_id(new_role_id)
        if not role_permissions:
            raise NotFoundError("角色不存在")

        token_data = {
            "sub": str(user.entity_id),
            "user_name": user.name,
            "role_id": new_role_id,
            "permissions": role_permissions.permissions,
        }


        token = create_access_token(data=token_data, redis_client=self.redis_client)
        expires_in = int(app_settings.jwt.expire_time)

        return token, expires_in


    async def get_user_roles(self, username: str, user_repo: IUserRepository) -> list[int]:
        """获取用户角色列表"""
        user = await user_repo.get_by_username(username)
        if not user:
            raise NotFoundError("用户不存在")

        # 获取用户角色
        user_roles = await user_repo.user_role_relations(user_ids=[user.entity_id])
        return user_roles.get(user.entity_id, [])


    async def refresh_token(self, refresh_token: str) -> tuple[str, int]:
        """刷新token"""
        payload = verify_token(refresh_token, redis_client=self.redis_client)
        # 生成新的access_token
        access_token = create_access_token(payload, redis_client=self.redis_client)
        return access_token, app_settings.jwt.expire_time


    async def get_user_info(
        self,
        role_domain_service: RoleService,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        file_repo: FileRepository,
        user_id: int,
    ):
        """获取指定用户的完整信息（包含角色信息和附件信息）"""

        role_info = await role_domain_service.get_role_info(role_repo=role_repo)

        user_entity = await user_repo.get_by_id(user_id)  # 基础用户实体
        user_role_map = await user_repo.user_role_relations(user_ids=[user_id])  # 用户-角色关联关系
        file_vo_list = await file_repo.get(
            master_id=user_entity.entity_id, file_types=user_entity.get_file_type_list()
        )  # 用户关联的附件列表

        user_entity.add_roles_info(user_role_map.get(user_entity.entity_id, []), role_info)
        user_entity.add_attachments(file_vo_list)
        data = await self.generate_response(user_entity, UserExtraInfoResponse)
        return data.model_dump()


    async def add_user(
        self,
        user_repo: IUserRepository,
        file_repo: FileRepository,
        request_data: CreateUserRequest,
    ):
        """新增用户"""
        # 保存明文密码用于邮件通知
        plain_password = request_data.password or generate_random_password()
        if not request_data.password:
            request_data.password = plain_password

        # 保存用户数据
        user_entity = UserEntity(
            **request_data.model_dump(
                include={
                    "entity_id",
                    "name",
                    "username",
                    "password",
                    "email",
                    "mobile",
                    "gender",
                    "nick_name",
                    "personal_profile",
                    "personal_advantage",
                    "update_time",
                    "status",
                    "personal_avatar",
                    "personal_photo",
                    "personal_qr_code",
                    "wecom_number",
                },
                exclude_none=True,
            ),
            last_operator=get_username() or "",
        )

        await user_repo.add(user_entity)

        # 保存角色数据
        role_ids = request_data.roles
        if len(role_ids) != 0:
            await user_repo.update_related_roles(user_entity.entity_id, role_ids)

        # 保存附件数据
        file_vo_list = user_entity.get_file_vo_list()
        if len(file_vo_list) != 0:
            await file_repo.save(file_vo_list)

        user_repo.flush()

        # 发布用户创建事件
        user_created_event = UserCreatedEvent(
            event_data={
                "user_id": user_entity.entity_id,
                "username": user_entity.username,
                "email": request_data.email,
                "name": user_entity.name,
                "plain_password": plain_password,
                "company_name": app_settings.email.company_name,
                "login_url": app_settings.login_url,
            },
        )
        EventBusService.get_instance().publish_async(user_created_event)

        # 返回结果
        data = await self.generate_response(data=str(user_entity.entity_id))

        return data.model_dump()


    async def delete_user(
        self,
        user_id: int,
        user_repo: IUserRepository,
        file_repo: IFileRepository,
    ):
        """删除用户"""
        if user_id == ADMIN_USER_ID:
            raise PermissionDeniedError("超级管理员用户无法删除或编辑")

        # 删除关联的角色


        await user_repo.update_related_roles(user_id, [])
        user = await user_repo.get_by_id(user_id)
        file_vo_list = user.get_file_vo_list()
        file_vo_empty_list = user.get_file_vo_empty_list()

        await file_repo.delete(file_vo_list + file_vo_empty_list)

        await user_repo.delete(user_id)

        await self.delete_refresh_token(user_id)

        user_repo.flush()

        response = await self.generate_response(data=str(user_id))
        return response.model_dump()


    async def get_users(
        self,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        role_domain_service: RoleService,
        user_domain_service: UserService,
        name: str | None = None,
        mobile: str | None = None,
        role_ids: list[int] | None = None,
        status: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """获取用户列表"""
        role_ids = role_ids or []
        role_info_dict = await role_domain_service.get_role_info(role_repo=role_repo)
        relation_user_id_list = await role_domain_service.get_relation_users(
            role_repo=role_repo, role_ids=role_ids
        )
        # 添加了角色筛选 但是没有角色相关用户
        if len(role_ids) != 0 and len(relation_user_id_list) == 0:
            result = await self.generate_page_response(
                page=page or 1,
                page_size=page_size or 10,
                total=0,
                items=[],
                item_class=UserItemResponse,
            )
            return result.model_dump()

        users, total = await user_domain_service.get_users(
            user_repo=user_repo,
            name=name,


            mobile=mobile,
            user_id_list=relation_user_id_list,
            role_info=role_info_dict,
            status=status,
            page=page,
            page_size=page_size,
        )
        result = await self.generate_page_response(
            page=page,
            page_size=page_size,
            total=total,
            items=users,
            item_class=UserItemResponse,
        )
        return result.model_dump()


    async def edit_user(
        self,
        user_id: int,
        user_repo: IUserRepository,
        file_repo: FileRepository,
        request_data: EditUserRequest,
    ):
        """编辑用户"""
        if user_id == ADMIN_USER_ID:
            raise PermissionDeniedError("超级管理员用户无法删除或编辑")

        user_entity = UserEntity(
            **request_data.model_dump(
                include={
                    "nick_name",
                    "personal_profile",
                    "personal_advantage",
                    "personal_qr_code",
                    "personal_avatar",
                    "personal_photo",
                    "update_time",
                    "wecom_number",
                    "status",
                    "name",
                    "mobile",
                    "username",
                    "gender",
                    "email",
                },
                exclude_none=True,
            ),
            entity_id=user_id,
            last_operator=get_username() or "",
        )


        file_vo_list = user_entity.get_file_vo_list()
        file_vo_empty_list = user_entity.get_file_vo_empty_list()
        await file_repo.delete(pair_list=file_vo_empty_list + file_vo_list)
        if len(file_vo_list) != 0:
            await file_repo.save(file_vo_list)

        # 保存角色数据
        if request_data.roles is not None:
            await user_repo.update_related_roles(user_entity.entity_id, request_data.roles)

        await user_repo.save(user_entity)


        data = await self.generate_response(data=str(user_entity.entity_id))
        return data.model_dump()


    async def get_current_user(
        self,
        role_domain_service: RoleService,
        user_repo: IUserRepository,
        role_repo: RoleRepository,
        file_repo: FileRepository,
    ):
        """获取指定用户的完整信息（包含角色信息和附件信息）"""

        user_id = get_current_user_id()

        role_info = await role_domain_service.get_role_info(role_repo=role_repo)

        # 核心用户数据获取流程
        user_entity: UserEntity = await user_repo.get_by_id(user_id)  # 基础用户实体
        user_role_map = await user_repo.user_role_relations(user_ids=[user_id])  # 用户-角色关联关系
        file_vo_list = await file_repo.get(
            master_id=user_entity.entity_id, file_types=user_entity.get_file_type_list()
        )  # 用户关联的附件列表

        user_entity.add_roles_info(user_role_map.get(user_entity.entity_id, []), role_info)
        user_entity.add_attachments(file_vo_list)
        # 将领域对象转换为响应模型并序列化
        data = await self.generate_response(user_entity, CurrentUserInfo)
        return data.model_dump()


    async def get_user_name_list(
        self, user_repo: IUserRepository, name: str | None = None
    ) -> dict[str, Any]:
        """获取用户名称列表"""
        user_name_list = await user_repo.name_list(name=name)

        data = ResponseListModel(data=user_name_list)

        return data.model_dump()


    async def logout(self, refresh_token: str):
        """用户退出登录"""
        token = get_current_token()
        if not self.redis_client:
            logger.warning("redis连接尚未初始化")
            return


        try:
            self.redis_client.ping()
        except (RedisError, OSError, TimeoutError) as err:
            logger.warning(
                f"退出登录时Redis不可用，跳过token黑名单写入：{type(err).__name__}: {err}"
            )
            return

        token_revoked = revoke_token(token, self.redis_client)
        refresh_token_revoked = revoke_token(refresh_token, self.redis_client)
        logger.debug(
            f"用户已退出登录，access_token撤销结果={token_revoked}，"
            f"refresh_token撤销结果={refresh_token_revoked}"
        )


    async def revoke_all_user_tokens(self, user_id: int):
        """撤销用户的所有token（用于禁用用户或强制下线）"""
        if not self.redis_client:
            logger.warning("redis连接尚未初始化")
            return

        # 撤销用户所有token
        revoke_user_tokens(str(user_id), self.redis_client)


    async def change_user_status(
        self,
        user_repo: IUserRepository,
        request_data: EditUserStatusRequest,
    ) -> dict[str, Any]:
        """变更用户状态"""
        if ADMIN_USER_ID in request_data.entity_id_list:
            raise PermissionDeniedError("超级管理员用户无法禁用")

        result = await user_repo.change_status(
            request_data.entity_id_list, request_data.status, get_username() or ""
        )

        # 变更完用户状态之后，若用户被禁用，那么需要撤销所有token
        if not request_data.status:
            for user_id in request_data.entity_id_list:
                await self.revoke_all_user_tokens(user_id)

        data = await self.generate_response(data=result)
        return data.model_dump()


    async def change_user_password(
        self,
        user_id: int,
        user_repo: IUserRepository,
        request_data: EditUserPasswordRequest,
    ) -> dict[str, Any]:
        """修改用户密码"""
        user_entity: UserEntity = await user_repo.get_by_id(user_id)
        if not user_entity:
            raise NotFoundError("用户不存在")
        if user_entity.password_hash and not verify_password(
            request_data.old_password, user_entity.password_hash
        ):
            raise InvalidInputError("旧密码错误")
        if request_data.password != request_data.password_confirm:
            raise InvalidInputError("两次输入的密码不一致")


        password_hash = hash_password(request_data.password)
        user_entity_update = UserEntity(
            password_hash=password_hash,
            entity_id=user_id,
        )
        await user_repo.save(user_entity_update)

        # 修改密码后，撤销用户所有token，强制重新登录
        await self.revoke_all_user_tokens(user_id)

        user_repo.flush()

        data = await self.generate_response(data=str(user_id))

        return data.model_dump()


    async def change_current_user_password(
        self,
        user_repo: IUserRepository,
        request_data: EditUserPasswordRequest,
    ) -> dict[str, Any]:
        """修改当前用户密码"""
        return await self.change_user_password(
            user_id=get_current_user_id(),
            user_repo=user_repo,
            request_data=request_data,
        )


    @staticmethod
    def get_refresh_token_key(user_id: int) -> str:
        """获取刷新token的键"""
        return f"refresh_token:{user_id}"
