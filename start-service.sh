#!/bin/bash
# 启动服务脚本（后台运行模式）

cd "$(dirname "$0")"
source venv/bin/activate

echo "🦜 正在启动鹦鹉智能喂食器+换水系统..."

# 检查是否已有实例在运行
if [ -f "feeder.pid" ]; then
    PID=$(cat feeder.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  服务已在运行中 (PID: $PID)"
        echo "   如需重启，请先运行: bash stop-service.sh"
        exit 1
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动服务（后台运行）
nohup python3 main.py > logs/feeder-output.log 2>&1 &

# 保存PID
echo $! > feeder.pid

sleep 2

# 检查是否启动成功
if ps -p $(cat feeder.pid) > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "📍 服务信息:"
    echo "   进程ID: $(cat feeder.pid)"
    echo "   日志文件: logs/feeder-output.log"
    echo ""
    IP=$(hostname -I | awk '{print $1}')
    echo "🌐 访问地址:"
    echo "   http://localhost:5000"
    echo "   http://${IP}:5000"
    echo ""
    echo "📊 查看日志: tail -f logs/feeder-output.log"
    echo "⏹️  停止服务: bash stop-service.sh"
else
    echo "❌ 服务启动失败，请查看日志："
    echo "   cat logs/feeder-output.log"
    exit 1
fi
