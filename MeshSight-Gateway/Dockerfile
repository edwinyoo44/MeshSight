FROM python:3.11-slim

# 環境
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 工作區
WORKDIR /workspace
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip3 install -r requirements.txt

# 啟動
CMD ["sh", "run.sh"]
