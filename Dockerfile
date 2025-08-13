FROM nvidia/cuda:12.9.0-base-ubuntu22.04

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.7 /uv /uvx /bin/

COPY . .

RUN uv sync --frozen --no-cache

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
