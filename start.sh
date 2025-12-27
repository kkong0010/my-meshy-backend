#!/bin/bash

echo "🎨 Tripo 3D 魔法工坊启动器"
echo "=========================="
echo ""

# 检查 API Key
if [ ! -f "api_key.txt" ] && [ ! -f "api_key" ]; then
    echo "❌ 错误：找不到 api_key.txt 文件"
    echo "请创建 api_key.txt 文件并写入你的 Tripo API Key"
    exit 1
fi

# 检查 Python 依赖
echo "🔍 检查 Python 依赖..."
if ! python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
    echo "📦 安装 Python 依赖..."
    pip3 install -r requirements.txt
fi

# 检查 Node 依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装 Node.js 依赖..."
    npm install
fi

echo ""
echo "✅ 环境检查完毕！"
echo ""
echo "🚀 启动后端 API..."
python3 api.py &
API_PID=$!

# 等待后端启动
sleep 3

echo "🎨 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================="
echo "✨ 应用已启动！"
echo "📍 前端地址: http://localhost:3000"
echo "📍 后端地址: https://my-meshy-backend.zeabur.app"
echo "=========================="
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $API_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
