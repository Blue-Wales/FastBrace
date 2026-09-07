FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/code/.venv/bin:${PATH}"

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates tzdata && \
    ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -g 10001 FastBrace && \
    adduser --disabled-password --gecos '' --uid 10001 --gid 10001 FastBrace && \
    mkdir -p /log/FastBrace/api /log/FastBrace/event /log/FastBrace/cron && \
    chown -R 10001:10001 /log/FastBrace && \
    mkdir -p /code/templates && \
    chown -R 10001:10001 /code/templates

COPY pyproject.toml uv.lock /code/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY ./ /code/

EXPOSE 8888

ENTRYPOINT ["sh", "./scripts/startup.sh"]
