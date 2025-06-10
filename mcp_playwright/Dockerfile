# syntax=docker/dockerfile:1
# python 3.12
# playwirght 1.50.0
FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

# 提供 build system 明確指定，避免 setuptools fallback legacy
# 這段是給 uv 用的，但萬一 fallback pip 也可用
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true \
  PYTHONUNBUFFERED=1

# 安裝 uv 並安裝所有 dependencies（含 rust build tool）
RUN apt-get update && \
  apt-get install -y build-essential curl && \
  pip install uv && \
  uv pip install --system .

COPY . .

CMD ["uv", "run", "main.py"]
