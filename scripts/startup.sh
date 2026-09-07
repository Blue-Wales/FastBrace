#!/bin/sh

# 初始化标记文件
CONTAINER_ALREADY_STARTED=".CONTAINER_ALREADY_STARTED_PLACEHOLDER"

# 项目根目录（容器内固定路径）
PROJECT_ROOT="/code"
export PYTHONPATH="$PROJECT_ROOT"

cd "$PROJECT_ROOT" || exit 1

# 第一次启动时初始化数据库
if [ ! -e "$CONTAINER_ALREADY_STARTED" ]; then
    echo "-- First container startup --"
    echo "🔧 初始化数据库..."
    python scripts/init_database.py && python scripts/permission_init.py
    if [ $? -eq 0 ]; then
        touch "$CONTAINER_ALREADY_STARTED"
        echo "✅ 数据库初始化完成"
    else
        echo "❌ 数据库初始化失败"
        exit 1
    fi
else
    echo "-- Not first container startup --"
    # 运行 Alembic 迁移确保数据库结构是最新的
    alembic upgrade head
    python scripts/permission_init.py --force-recreate
    if [ $? -eq 0 ]; then
        echo "✅ 数据库迁移检查完成"
    else
        echo "❌ 数据库迁移检查失败"
        exit 1
    fi
fi

# 启动应用服务
echo "🚀 启动应用服务..."
echo "📄 执行命令: $@"

exec "$@"
