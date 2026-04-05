# 🦜 鹦鹉智能喂食器 + 换水系统

基于树莓派4的智能远程控制鹦鹉喂食+换水系统，支持手机/PC远程控制、定时喂食/换水、状态监控等功能。

## ✨ 功能特性

### 🍖 喂食系统
- ✅ 手动远程控制喂食（少量/正常/多量）
- ✅ 定时自动喂食（可配置时间表）
- ✅ 舵机精确控制下食口开合
- ✅ 喂食记录和统计

### 💧 换水系统
- ✅ 手动远程控制换水（精准水量控制）
- ✅ 定时自动换水（可配置间隔）
- ✅ 水泵+电磁阀双重控制
- ✅ 换水记录和状态监控

### 🌐 Web界面
- ✅ 响应式设计（手机/平板/电脑）
- ✅ 实时状态显示
- ✅ 简洁直观的操作界面
- ✅ 自动刷新数据

## 📋 系统要求

### 硬件要求
- **主控**: 树莓派4 Model B (2GB/4GB RAM)
- **喂食模块**:
  - SG90微型舵机 ×1
  - 3D打印或自制下食机构
- **换水模块**:
  - DC 5V微型潜水泵 ×1
  - DC 5V电磁水阀 ×1
  - 5V双路继电器模块 ×1
  - 食品级硅胶软管等配件

### 软件要求
- **操作系统**: Raspberry Pi OS Lite (64-bit) 推荐
- **Python**: 3.9+
- **网络**: WiFi连接（用于远程访问）

## 🚀 快速开始

### 1. 克隆项目

```bash
cd ~
git clone https://github.com/prprkr/parrot-feeder.git
cd parrot-feeder
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置系统（可选）

编辑 `config.py` 文件，根据实际硬件调整GPIO引脚配置：

```python
# 喂食系统
SERVO_PIN = 18           # 舵机引脚

# 换水系统
PUMP_RELAY_PIN = 23      # 水泵继电器
VALVE_RELAY_PIN = 24     # 电磁阀继电器
```

### 5. 运行服务

#### 开发模式（前台运行）

```bash
python3 main.py
```

访问 `http://localhost:5000` 打开控制面板。

#### 生产模式（后台服务）

```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/parrot-feeder.service
```

粘贴以下内容：

```ini
[Unit]
Description=Parrot Feeder Service
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/parrot-feeder
ExecStart=/home/pi/parrot-feeder/venv/bin/python3 /home/pi/parrot-feeder/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable parrot-feeder.service
sudo systemctl start parrot-feeder.service
```

查看日志：

```bash
journalctl -u parrot-feeder.service -f
```

## 🔌 GPIO接线说明

### 喂食系统
```
树莓派 GPIO ──┬── GPIO18 ──→ 舵机信号线(橙色)
              ├── 5V      ──→ 舵机电源(红色)
              └── GND     ──→ 舵机地线(棕色)
```

### 换水系统
```
树莓派 GPIO ──┬── GPIO23 ──→ 继电器IN1 ──→ 水泵
              ├── GPIO24 ──→ 继电器IN2 ──→ 电磁阀
              ├── 5V      ──→ 继电器VCC
              └── GND     ──→ 继电器GND
```

## 🌐 远程访问配置

### 方案1：Tailscale（推荐）

安装Tailscale实现安全的远程访问：

```bash
# 树莓派上执行
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

手机安装Tailscale App后，通过分配的IP地址访问：`http://100.x.y.z:5000`

### 方案2：Cloudflare Tunnel

详见项目文档中的远程控制方案章节。

## 📁 项目结构

```
parrot-feeder/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── web_app.py           # Flask Web应用
├── feeder.py            # 喂食控制模块
├── water_system.py      # 换水控制模块
├── requirements.txt     # Python依赖
├── templates/
│   └── index.html       # Web界面模板
└── static/
    ├── style.css        # 样式表
    └── app.js           # 前端交互逻辑
```

## ⚙️ API接口文档

### 喂食相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/feed` | 触发喂食（body: `{portion: "small|normal|large"}`）|
| GET | `/api/feed/status` | 获取喂食状态 |

### 换水相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/water/change` | 触发换水（body: `{volume: 150}` 单位ml）|
| GET | `/api/water/status` | 获取换水状态 |
| POST | `/api/water/schedule` | 设置换水间隔（body: `{interval_hours: 24}`）|

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 获取系统整体状态 |

## 🔧 故障排查

### 常见问题

**Q: 舵机不转动？**
- 检查GPIO接线是否正确
- 确认电源供电充足（建议使用独立5V电源给舵机供电）
- 查看日志确认是否有错误信息

**Q: 换水时水泵不工作？**
- 检查继电器接线
- 确认水泵和电磁阀供电正常
- 测试继电器模块是否工作

**Q: 无法从外部网络访问？**
- 确认树莓派已连接WiFi
- 检查防火墙设置
- 确认远程访问方案（Tailscale/Cloudflare）已正确配置

### 日志查看

```bash
# 查看实时日志
tail -f logs/feeder.log

# 或使用journalctl（如果使用systemd服务）
journalctl -u parrot-feeder.service -f
```

## 🛠️ 开发指南

### 本地开发测试

在非树莓派环境（如Windows/Mac）开发时，代码会自动进入模拟模式，无需真实硬件即可测试Web界面和API逻辑。

### 添加新功能

1. 在对应模块中添加功能代码
2. 在 `web_app.py` 中添加API路由
3. 更新前端界面（可选）
4. 更新此README文档

## 📄 许可证

MIT License

## 👨‍💻 作者

**prprkr** - [GitHub](https://github.com/prprkr)

## 🙏 致谢

- RPi.GPIO 库团队
- Flask 框架团队
- 树莓派基金会

---

🦜 **让科技关爱每一个小生命！**
