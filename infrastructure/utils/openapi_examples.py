#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : openapi_examples.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : OpenAPI 文档示例增强
"""

from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

TAGS_METADATA = [
    {"name": "健康检查", "description": "服务存活、就绪和依赖组件健康状态检查。"},
    {"name": "安全", "description": "RSA 公钥等前端安全能力。"},
    {"name": "文件", "description": "文件上传与文件资源返回。"},
    {"name": "认证", "description": "登录、刷新 token、退出登录、角色切换与当前角色查询。"},
    {"name": "用户", "description": "用户新增、查询、编辑、删除、密码和状态管理。"},
    {"name": "角色", "description": "角色树、角色详情、角色用户关系和角色维护。"},
    {"name": "权限", "description": "权限树、角色权限保存、细粒度权限和权限验证。"},
    {"name": "测试", "description": "非生产环境下的测试辅助接口。"},
]


COMMON_SUCCESS = {"code": 200, "message": "success", "data": {"result": True}}


OPENAPI_EXAMPLES: dict[str, dict[str, dict[str, Any]]] = {
    "/health": {
        "get": {
            "response": {
                "status": "healthy",
                "version": "2.0.0",
                "environment": "dev",
                "timestamp": "2026-05-26T10:30:00Z",
                "components": {
                    "database": {"status": "healthy", "message": ""},
                    "redis": {"status": "healthy", "message": ""},
                },
            }
        }
    },
    "/health/live": {"get": {"response": {"status": "alive"}}},
    "/health/ready": {"get": {"response": {"status": "ready"}}},
    "/security/public-key": {
        "get": {
            "response": {
                "code": 200,
                "data": {
                    "encryption_enabled": True,
                    "public_key": "-----BEGIN PUBLIC KEY-----\\nMIIBIjANBgkq...\\n-----END PUBLIC KEY-----",
                    "algorithm": "RSA/ECB/PKCS1Padding",
                    "usage": "使用此公钥加密密码后再发送登录请求",
                },
            }
        }
    },
    "/file/upload": {
        "post": {
            "request": {"file_type": "avatar", "file": "avatar.png"},
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "file_name": "avatar.png",
                    "file_path": "https://oss.example.com/avatar.png",
                },
            },
        }
    },
    "/login": {
        "post": {
            "request": {"username": "admin", "password": "rsa_encrypted_password", "role_id": 1},
            "response": {
                "code": 200,
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "refresh_token_example",
            },
        }
    },
    "/switch-role": {
        "post": {
            "request": {"role_id": 2},
            "response": {
                "code": 200,
                "access_token": "new_access_token_example",
                "expires_in": 1800,
            },
        }
    },
    "/users/{username}/roles": {
        "get": {
            "response": {
                "code": 200,
                "roles": [
                    {"role_id": 1, "code": "admin", "name": "管理员"},
                    {"role_id": 2, "code": "operator", "name": "运营"},
                ],
            }
        }
    },
    "/refresh-token": {
        "post": {
            "request": {"refresh_token": "refresh_token_example"},
            "response": {
                "code": 200,
                "access_token": "new_access_token_example",
                "expires_in": 1800,
            },
        }
    },
    "/logout": {
        "post": {
            "request": {"refresh_token": "refresh_token_example"},
            "response": {"code": 200, "message": "退出登录成功"},
        }
    },
    "/current-role": {
        "get": {
            "response": {
                "code": 200,
                "role_id": "1",
                "role_name": "管理员",
                "permissions": {"account": [1, 2], "role": [1, 2, 3]},
            }
        }
    },
    "/users": {
        "post": {
            "request": {
                "nick_name": "张三",
                "name": "张三",
                "mobile": "13800000000",
                "username": "zhangsan",
                "email": "zhangsan@example.com",
                "password": "rsa_encrypted_password",
                "roles": [1],
                "dept_ids": [1],
                "gender": 1,
                "status": True,
            },
            "response": COMMON_SUCCESS,
        },
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "total": 1,
                    "page": 1,
                    "page_size": 10,
                    "pages": 1,
                    "items": [
                        {
                            "user_id": "1",
                            "name": "zhangsan",
                            "nick_name": "张三",
                            "mobile": "13800000000",
                            "roles": ["管理员"],
                            "status": True,
                        }
                    ],
                },
            }
        },
    },
    "/users/me": {
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "entity_id": "1",
                    "name": "zhangsan",
                    "nick_name": "张三",
                    "mobile": "13800000000",
                    "personal_avatar": [],
                    "roles": [
                        {"entity_id": 1, "code": "admin", "name": "管理员", "permissions": {}}
                    ],
                },
            }
        }
    },
    "/users/choices": {
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": [{"user_id": "1", "name": "zhangsan"}],
            }
        }
    },
    "/users/{user_id}": {
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "entity_id": "1",
                    "username": "zhangsan",
                    "name": "张三",
                    "mobile": "13800000000",
                    "email": "zhangsan@example.com",
                    "roles": [{"role_id": 1, "code": "admin", "name": "管理员"}],
                    "status": True,
                },
            }
        },
        "post": {
            "request": {"nick_name": "张三", "mobile": "13800000001", "roles": [1], "status": True},
            "response": COMMON_SUCCESS,
        },
        "delete": {"response": COMMON_SUCCESS},
    },
    "/users/me/password": {
        "post": {
            "request": {
                "old_password": "rsa_encrypted_old_password",
                "password": "rsa_encrypted_new_password",
                "password_confirm": "rsa_encrypted_new_password",
            },
            "response": COMMON_SUCCESS,
        }
    },
    "/users/{user_id}/password": {
        "post": {
            "request": {
                "old_password": "rsa_encrypted_old_password",
                "password": "rsa_encrypted_new_password",
                "password_confirm": "rsa_encrypted_new_password",
            },
            "response": COMMON_SUCCESS,
        }
    },
    "/users/batch/status": {
        "post": {"request": {"user_id_list": [1, 2], "status": False}, "response": COMMON_SUCCESS}
    },
    "/role/add": {
        "post": {
            "request": {"parent_root_id": 1, "code": "operator", "name": "运营"},
            "response": COMMON_SUCCESS,
        }
    },
    "/role/tree": {
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "role_id": 1,
                    "code": "admin",
                    "name": "管理员",
                    "child_role": [
                        {"role_id": 2, "code": "operator", "name": "运营", "child_role": []}
                    ],
                },
            }
        }
    },
    "/role/edit": {
        "post": {
            "request": {"role_id": 2, "code": "operator", "name": "运营"},
            "response": COMMON_SUCCESS,
        }
    },
    "/role/user_list": {
        "post": {
            "request": {
                "role_id": 1,
                "name": "张三",
                "mobile": "13800000000",
                "unregistered": False,
                "page": 1,
                "page_size": 10,
            },
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "total": 1,
                    "page": 1,
                    "page_size": 10,
                    "pages": 1,
                    "items": [
                        {
                            "user_id": "1",
                            "name": "zhangsan",
                            "nick_name": "张三",
                            "mobile": "13800000000",
                            "roles": ["管理员"],
                        }
                    ],
                },
            },
        }
    },
    "/role/info": {
        "get": {
            "response": {
                "code": 200,
                "message": "success",
                "data": {
                    "role_id": 1,
                    "code": "admin",
                    "name": "管理员",
                    "permissions": {"account": [1, 2]},
                },
            }
        }
    },
    "/role/delete": {"delete": {"response": COMMON_SUCCESS}},
    "/role/add_users": {
        "post": {"request": {"role_id": 1, "user_ids": [1, 2]}, "response": COMMON_SUCCESS}
    },
    "/role/delete_users": {
        "delete": {"request": {"role_id": 1, "user_ids": [2]}, "response": COMMON_SUCCESS}
    },
    "/permissions/tree": {
        "get": {
            "response": {
                "code": 200,
                "message": "获取权限树成功",
                "data": [
                    {
                        "entity_id": 1,
                        "name": "账号管理",
                        "code": "account",
                        "description": "用户账号相关权限",
                        "resource_type": "module",
                        "parent_id": None,
                        "depth": 1,
                        "level": 1,
                        "available_levels": [1, 2, 3],
                        "selected_levels": [],
                        "children": [],
                    }
                ],
            }
        }
    },
    "/permissions/role/{role_id}": {
        "get": {
            "response": {
                "code": 200,
                "message": "获取角色权限树成功",
                "data": [
                    {
                        "entity_id": 1,
                        "name": "账号管理",
                        "code": "account",
                        "description": "用户账号相关权限",
                        "resource_type": "module",
                        "parent_id": None,
                        "depth": 1,
                        "level": 1,
                        "available_levels": [1, 2, 3],
                        "selected_levels": [1, 2],
                        "children": [],
                    }
                ],
            }
        }
    },
    "/permissions/role/save": {
        "post": {
            "request": {"role_id": 1, "permissions": {"account": [1, 2], "role": [1]}},
            "response": {
                "code": 200,
                "message": "保存角色权限成功",
                "data": {"success": True, "message": "保存角色权限成功", "role_id": 1},
            },
        }
    },
    "/permissions/role/{role_id}/detailed": {
        "get": {
            "response": {
                "code": 200,
                "message": "获取角色细粒度权限成功",
                "data": [
                    {
                        "entity_id": 1,
                        "name": "账号管理",
                        "code": "account",
                        "description": "用户账号相关权限",
                        "resource_type": "module",
                        "parent_id": None,
                        "depth": 1,
                        "level": 1,
                        "permission_level": 2,
                        "children": [],
                        "action": [],
                    }
                ],
            }
        }
    },
    "/permissions/user/detailed": {
        "get": {
            "response": {
                "code": 200,
                "message": "获取用户细粒度权限成功",
                "data": [
                    {
                        "entity_id": 1,
                        "name": "账号管理",
                        "code": "account",
                        "description": "用户账号相关权限",
                        "resource_type": "module",
                        "parent_id": None,
                        "depth": 1,
                        "level": 1,
                        "permission_level": 2,
                        "children": [],
                        "action": [],
                    }
                ],
            }
        }
    },
    "/permissions/validate": {
        "post": {
            "request": {
                "module_code": "account",
                "required_level": 2,
                "user_permissions": {"account": [1, 2]},
            },
            "response": {
                "code": 200,
                "message": "权限验证完成",
                "data": {
                    "has_permission": True,
                    "module_code": "account",
                    "required_level": 2,
                    "user_level": 2,
                },
            },
        }
    },
    "/permissions/system/info": {
        "get": {
            "response": {
                "code": 200,
                "message": "获取权限系统信息成功",
                "data": {
                    "permission_levels": [
                        {
                            "level": 1,
                            "name": "查看",
                            "description": "可以查看模块对应页面以及页面中的数据",
                        },
                        {
                            "level": 2,
                            "name": "操作",
                            "description": "可以访问页面中的所有编辑/删除等涉及修改资源的操作",
                        },
                        {"level": 3, "name": "导出", "description": "可以导出模块中的所有数据"},
                    ],
                    "module_count": 8,
                    "action_count": 24,
                },
            }
        }
    },
}


def install_openapi_examples(app: FastAPI) -> None:
    """Install a custom OpenAPI builder with module examples."""
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=TAGS_METADATA,
        )
        _merge_examples(openapi_schema, OPENAPI_EXAMPLES)
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi


def _merge_examples(
    openapi_schema: dict[str, Any], examples: dict[str, dict[str, dict[str, Any]]]
) -> None:
    paths = openapi_schema.get("paths", {})
    for path, method_examples in examples.items():
        if path not in paths:
            continue

        for method, example in method_examples.items():
            operation = paths[path].get(method)
            if not operation:
                continue

            request_example = example.get("request")
            response_example = example.get("response")
            if request_example is not None:
                _set_request_example(operation, request_example)
            if response_example is not None:
                _set_response_example(operation, response_example)


def _set_request_example(operation: dict[str, Any], example: dict[str, Any]) -> None:
    request_body = operation.get("requestBody")
    if not request_body:
        return

    for content in request_body.get("content", {}).values():
        content.setdefault("examples", {})
        content["examples"]["frontend_debug"] = {
            "summary": "前端调试示例",
            "value": deepcopy(example),
        }


def _set_response_example(operation: dict[str, Any], example: dict[str, Any]) -> None:
    response = operation.setdefault("responses", {}).setdefault(
        "200", {"description": "Successful Response"}
    )
    content = response.setdefault("content", {}).setdefault("application/json", {})
    content.setdefault("examples", {})
    content["examples"]["success"] = {
        "summary": "成功响应示例",
        "value": deepcopy(example),
    }
