#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 终止现有服务进程
pkill -f uvicorn || true
lsof -ti :8000 | xargs kill -9 >/dev/null 2>&1
sleep 1

# 启动FastAPI服务
python3 main.py