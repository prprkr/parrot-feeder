#!/bin/bash
# 停止服务脚本

cd "$(dirname "$0")"

if [ ! -f "feeder.pid" ]; then
    echo "⚠️  未找到PID文件，服务可能未运行"
    exit 1
fi

PID=$(cat feeder.pid)

if ps -p $PID > /dev/null 2>&1; then
    echo "⏹️  正在停止服务 (PID: $PID)..."
    kill $PID
    
    # 等待进程结束
    sleep 2
    
    # 强制杀死（如果还没死）
    if ps -p $PID > /dev/null 2>&1; then
        echo "   强制终止..."
        kill -9 $PID
    fi
    
    rm feeder.pid
    echo "✅ 服务已停止"
else
    echo "⚠️  进程不存在 (PID: $PID)，清理PID文件"
    rm -f feeder.pid
fi
