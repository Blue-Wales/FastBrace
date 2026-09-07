#!/usr/bin/env bash
# 本脚本仅供本地手动调试使用。
# 正式部署由 GitHub Actions workflow 自动完成，无需手动执行此脚本。
set -Eeuo pipefail

IMAGE="${HOUSE_IMAGE:?HOUSE_IMAGE is required}"
CONFIG_PORT="${CONFIG_PORT:-8888}"
COMPOSE_FILE="deploy/docker-compose.yml"

echo "停止旧容器..."
HOUSE_IMAGE="$IMAGE" docker compose -f "$COMPOSE_FILE" down --remove-orphans || true

echo "清理旧镜像..."
docker image prune -f

echo "启动服务..."
HOUSE_IMAGE="$IMAGE" CONFIG_PORT="$CONFIG_PORT" docker compose -f "$COMPOSE_FILE" up -d

echo "等待健康检查..."
for _ in $(seq 1 20); do
  if curl -fsS "http://127.0.0.1:${CONFIG_PORT}/health" | grep -q '"status":"healthy"'; then
    echo "部署成功"
    exit 0
  fi
  sleep 5
done

echo "健康检查超时"
HOUSE_IMAGE="$IMAGE" docker compose -f "$COMPOSE_FILE" logs --tail=50 api
exit 1
