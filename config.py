# -*- coding: utf-8 -*-
"""
鹦鹉智能喂食器 + 换水系统 - 配置文件
"""

import os

class Config:
    """基础配置"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'parrot-feeder-secret-key-2024'
    DEBUG = False
    
    # Web服务配置
    HOST = '0.0.0.0'
    PORT = 5000
    
    # GPIO配置（BCM编号）
    # 喂食系统
    SERVO_PIN = 18           # 舵机控制引脚
    SERVO_OPEN_ANGLE = 90    # 开启角度
    SERVO_CLOSE_ANGLE = 0    # 关闭角度
    FEED_DURATION = 2        # 喂食持续时间(秒)
    
    # 换水系统
    PUMP_RELAY_PIN = 23      # 水泵继电器引脚
    VALVE_RELAY_PIN = 24     # 电磁阀继电器引脚
    WATER_PUMP_TIME = 2.2    # 抽水时间(秒) ≈ 150ml
    WATER_INTERVAL_HOURS = 24  # 自动换水间隔(小时)
    
    # 传感器配置（可选）
    ULTRASONIC_TRIG_PIN = 17  # 超声波Trig
    ULTRASONIC_ECHO_PIN = 27  # 超声波Echo
    DHT_PIN = 22              # 温湿度传感器
    
    # 定时任务配置
    FEED_SCHEDULES = [
        {'time': '08:00', 'portion': 'normal'},   # 早上
        {'time': '12:00', 'portion': 'small'},    # 中午
        {'time': '18:00', 'portion': 'normal'},    # 晚上
    ]
    
    # 数据库配置
    DATABASE_PATH = 'data/feeder.db'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/feeder.log'
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    HOST = '127.0.0.1'  # 生产环境建议只监听本地，通过反向代理访问


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
