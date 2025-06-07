FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_CACHE_DIR=/opt/uv-cache/

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash app

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-client \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=app:app pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/opt/uv-cache/ \
    uv sync --locked --no-install-project --no-dev

# Copy the entire project
COPY --chown=app:app . .

RUN --mount=type=cache,target=/opt/uv-cache/ \
    uv sync --locked --no-dev

USER app

RUN mkdir -p /home/app/.ssh && \
    chmod 700 /home/app/.ssh

ENV PATH="/app/.venv/bin:$PATH"

CMD ["ssh-mcp", "server"]
