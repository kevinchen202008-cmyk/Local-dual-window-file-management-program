#!/bin/bash
# Linux/macOS 启动脚本 - 文件管理器

cd "$(dirname "$0")"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.7+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
if ! pip list | grep -q PyQt5; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

# 启动应用
python3 main.py
