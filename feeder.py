# -*- coding: utf-8 -*-
"""
喂食系统控制模块
负责控制舵机实现自动下食功能
"""

import time
import logging
from datetime import datetime

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False
    print("警告: RPi.GPIO 不可用，将使用模拟模式（用于开发测试）")


class FeederSystem:
    """智能喂食系统"""
    
    def __init__(self, config):
        self.config = config
        self.servo_pin = config.SERVO_PIN
        self.open_angle = config.SERVO_OPEN_ANGLE
        self.close_angle = config.SERVO_CLOSE_ANGLE
        self.feed_duration = config.FEED_DURATION
        
        self.last_feed_time = None
        self.feed_count = 0
        self.logger = logging.getLogger(__name__)
        
        self._setup_gpio()
    
    def _setup_gpio(self):
        """初始化GPIO"""
        if not HARDWARE_AVAILABLE:
            self.logger.warning("硬件不可用，使用模拟模式")
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.servo_pin, GPIO.OUT)
            
            # 设置PWM控制舵机（50Hz）
            self.pwm = GPIO.PWM(self.servo_pin, 50)
            self.pwm.start(0)
            
            self.logger.info(f"喂食系统初始化成功 - GPIO引脚: {self.servo_pin}")
        except Exception as e:
            self.logger.error(f"GPIO初始化失败: {e}")
            raise
    
    def _set_angle(self, angle):
        """设置舵机角度"""
        if not HARDWARE_AVAILABLE:
            self.logger.info(f"[模拟] 设置角度: {angle}°")
            return
            
        # 将角度转换为占空比（0-180度对应2.5%-12.5%的占空比）
        duty = 2.5 + (angle / 18) * 0.5
        self.pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        self.pwm.ChangeDutyCycle(0)  # 停止信号，防止抖动
    
    def feed(self, portion='normal'):
        """
        执行喂食操作
        
        Args:
            portion: 喂食量 ('small', 'normal', 'large')
        
        Returns:
            dict: 喂食结果信息
        """
        self.logger.info(f"开始喂食 - 分量: {portion}")
        
        try:
            # 1. 打开下食口
            self._set_angle(self.open_angle)
            self.logger.info("下食口已开启")
            
            # 2. 根据分量调整等待时间
            duration_map = {
                'small': self.feed_duration * 0.5,
                'normal': self.feed_duration,
                'large': self.feed_duration * 1.5
            }
            duration = duration_map.get(portion, self.feed_duration)
            
            time.sleep(duration)
            
            # 3. 关闭下食口
            self._set_angle(self.close_angle)
            self.logger.info("下食口已关闭")
            
            # 4. 更新状态
            self.last_feed_time = datetime.now()
            self.feed_count += 1
            
            result = {
                'success': True,
                'timestamp': self.last_feed_time.isoformat(),
                'portion': portion,
                'feed_count': self.feed_count,
                'message': f'喂食成功！本次分量: {portion}'
            }
            
            self.logger.info(f"喂食完成 - {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"喂食失败: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self):
        """获取喂食系统状态"""
        return {
            'system_status': 'online' if HARDWARE_AVAILABLE else 'simulation',
            'last_feed_time': self.last_feed_time.isoformat() if self.last_feed_time else None,
            'total_feeds': self.feed_count,
            'servo_pin': self.servo_pin,
            'current_angle': self.close_angle  # 默认关闭状态
        }
    
    def cleanup(self):
        """清理资源"""
        if HARDWARE_AVAILABLE:
            try:
                self.pwm.stop()
                GPIO.cleanup()
                self.logger.info("喂食系统资源已清理")
            except Exception as e:
                self.logger.error(f"清理资源失败: {e}")
