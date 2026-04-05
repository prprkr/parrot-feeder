# -*- coding: utf-8 -*-
"""
鹦鹉智能喂食器 + 换水系统 - 主程序入口
"""

import os
import sys
import logging
from datetime import datetime

from web_app import create_app


def setup_logging(app):
    """配置日志系统"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'feeder.log')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    app.logger.addHandler(file_handler)
    
    return log_file


def main():
    """主函数"""
    print("=" * 60)
    print("🦜 鹦鹉智能喂食器 + 换水系统")
    print(f"   启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 创建Flask应用
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    
    # 配置日志
    log_file = setup_logging(app)
    print(f"\n✅ 日志文件: {log_file}")
    
    # 打印服务信息
    print(f"\n🌐 Web服务地址:")
    print(f"   本地访问: http://localhost:{app.config['PORT']}")
    print(f"   局域网访问: http://{get_local_ip()}:{app.config['PORT']}")
    print(f"\n⚙️  系统配置:")
    print(f"   - 喂食引脚: GPIO{app.config.SERVO_PIN}")
    print(f"   - 水泵继电器: GPIO{app.config.PUMP_RELAY_PIN}")
    print(f"   - 电磁阀继电器: GPIO{app.config.VALVE_RELAY_PIN}")
    print(f"   - 自动换水间隔: {app.config.WATER_INTERVAL_HOURS} 小时")
    print(f"\n💡 提示: 按 Ctrl+C 停止服务\n")
    
    # 启动Web服务
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'],
            use_reloader=False  # 禁用重载器，避免重复初始化GPIO
        )
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止服务...")
        
        # 清理资源
        if hasattr(app, 'feeder'):
            app.feeder.cleanup()
        if hasattr(app, 'water_system'):
            app.water_system.cleanup()
        
        print("✅ 服务已停止，资源已清理")
        sys.exit(0)


def get_local_ip():
    """获取本机局域网IP地址"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    main()
