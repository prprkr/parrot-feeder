#!/bin/bash
# 鹦鹉智能喂食器+换水系统 - 一键部署脚本
# 在树莓派上运行: bash deploy.sh

set -e  # 遇到错误立即停止

echo "=========================================="
echo "🦜 鹦鹉智能喂食器+换水系统 部署脚本"
echo "=========================================="
echo ""

# 检测是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  请不要使用root用户运行此脚本"
    echo "   请使用普通用户（如 pi 或 krkrkr）运行"
    exit 1
fi

echo "📋 第1步：更新系统软件包..."
sudo apt update
sudo apt upgrade -y -q
echo "✅ 系统更新完成"

echo ""
echo "📋 第2步：安装基础依赖..."
sudo apt install -y -q git python3 python3-pip python3-venv python3-dev
echo "✅ 基础依赖安装完成"

echo ""
echo "📋 第3步：安装GPIO库..."
sudo apt install -y -q python3-rpi.gpio python3-gpiozero
echo "✅ GPIO库安装完成"

echo ""
echo "📋 第4步：克隆项目代码..."
if [ -d "parrot-feeder" ]; then
    echo "   项目目录已存在，正在更新..."
    cd parrot-feeder
    git pull origin main
else
    echo "   正在从GitHub克隆..."
    git clone https://github.com/prprkr/parrot-feeder.git
    cd parrot-feeder
fi
echo "✅ 代码准备完成"

echo ""
echo "📋 第5步：创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✅ 虚拟环境创建完成"

echo ""
echo "📋 第6步：安装Python依赖..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Python依赖安装完成"

echo ""
echo "📋 第7步：创建必要目录..."
mkdir -p logs data
echo "✅ 目录创建完成"

echo ""
echo "📋 第8步：测试GPIO库..."
python3 -c "
try:
    import RPi.GPIO as GPIO
    print('✅ RPi.GPIO 库正常')
except ImportError:
    print('⚠️  RPi.GPIO 未安装（开发模式将启用模拟模式）')

try:
    import gpiozero
    print('✅ gpiozero 库正常')
except ImportError:
    print('⚠️  gpiozero 未安装')
"
echo ""

echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "📍 项目位置: $(pwd)"
echo "🔧 启动命令:"
echo ""
echo "   方法A（前台运行，用于调试）:"
echo "     source venv/bin/activate"
echo "     python3 main.py"
echo ""
echo "   方法B（后台运行，生产模式）:"
echo "     bash start-service.sh"
echo ""
echo "🌐 访问地址:"
IP=$(hostname -I | awk '{print $1}')
echo "   本地: http://localhost:5000"
echo "   局域网: http://${IP}:5000"
echo ""
echo "📖 更多信息请查看 README.md"
echo "=========================================="
