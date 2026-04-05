# -*- coding: utf-8 -*-
"""
换水系统控制模块
负责控制水泵和电磁阀实现自动换水功能
"""

import time
import logging
from datetime import datetime, timedelta

try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    HARDWARE_AVAILABLE = False
    print("警告: RPi.GPIO 不可用，将使用模拟模式（用于开发测试）")


class WaterSystem:
    """智能换水系统"""
    
    def __init__(self, config):
        self.config = config
        self.pump_pin = config.PUMP_RELAY_PIN
        self.valve_pin = config.VALVE_RELAY_PIN
        self.pump_time = config.WATER_PUMP_TIME  # 抽水时间(秒)
        self.interval_hours = config.WATER_INTERVAL_HOURS  # 换水间隔
        
        self.last_change_time = None
        self.water_count = 0
        self.logger = logging.getLogger(__name__)
        
        self._setup_gpio()
    
    def _setup_gpio(self):
        """初始化GPIO"""
        if not HARDWARE_AVAILABLE:
            self.logger.warning("硬件不可用，使用模拟模式")
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            
            # 设置继电器引脚为输出
            GPIO.setup(self.pump_pin, GPIO.OUT)
            GPIO.setup(self.valve_pin, GPIO.OUT)
            
            # 初始状态：关闭
            GPIO.output(self.pump_pin, GPIO.LOW)
            GPIO.output(self.valve_pin, GPIO.LOW)
            
            self.logger.info(f"换水系统初始化成功 - 水泵: GPIO{self.pump_pin}, 电磁阀: GPIO{self.valve_pin}")
        except Exception as e:
            self.logger.error(f"GPIO初始化失败: {e}")
            raise
    
    def _pump_on(self):
        """开启水泵"""
        if not HARDWARE_AVAILABLE:
            self.logger.info("[模拟] 开启水泵")
            return
        GPIO.output(self.pump_pin, GPIO.HIGH)
    
    def _pump_off(self):
        """关闭水泵"""
        if not HARDWARE_AVAILABLE:
            self.logger.info("[模拟] 关闭水泵")
            return
        GPIO.output(self.pump_pin, GPIO.LOW)
    
    def _valve_open(self):
        """打开电磁阀"""
        if not HARDWARE_AVAILABLE:
            self.logger.info("[模拟] 打开电磁阀")
            return
        GPIO.output(self.valve_pin, GPIO.HIGH)
    
    def _valve_close(self):
        """关闭电磁阀"""
        if not HARDWARE_AVAILABLE:
            self.logger.info("[模拟] 关闭电磁阀")
            return
        GPIO.output(self.valve_pin, GPIO.LOW)
    
    def change_water(self, volume_ml=None):
        """
        执行换水操作
        
        Args:
            volume_ml: 需要的水量(ml)，None则使用默认值
        
        Returns:
            dict: 换水结果信息
        """
        # 计算抽水时间
        if volume_ml:
            # 假设水泵流量约69ml/s (250L/H)
            pump_time = volume_ml / 69.0
        else:
            pump_time = self.pump_time
            volume_ml = int(pump_time * 69)  # 反算水量
        
        self.logger.info(f"开始换水 - 目标水量: {volume_ml}ml, 抽水时间: {pump_time:.1f}s")
        
        try:
            # 1. 开启水泵和电磁阀
            self._pump_on()
            time.sleep(0.2)  # 短暂延迟确保水泵启动
            self._valve_open()
            
            self.logger.info("水泵和电磁阀已开启")
            
            # 2. 抽水指定时间
            time.sleep(pump_time)
            
            # 3. 先关电磁阀（防止回流）
            self._valve_close()
            time.sleep(0.1)
            
            # 4. 再关水泵
            self._pump_off()
            
            # 5. 更新状态
            self.last_change_time = datetime.now()
            self.water_count += 1
            
            result = {
                'success': True,
                'timestamp': self.last_change_time.isoformat(),
                'volume_ml': volume_ml,
                'pump_duration': round(pump_time, 2),
                'total_changes': self.water_count,
                'message': f'换水成功！出水量: {volume_ml}ml'
            }
            
            self.logger.info(f"换水完成 - {result['message']}")
            return result
            
        except Exception as e:
            # 异常时确保关闭设备
            self._emergency_stop()
            
            error_msg = f"换水失败: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
    
    def _emergency_stop(self):
        """紧急停止所有设备"""
        self.logger.warning("执行紧急停止！")
        self._pump_off()
        self._valve_close()
    
    def auto_check_and_change(self):
        """定时检查并自动换水"""
        if self.should_change_water():
            self.logger.info("触发自动换水")
            return self.change_water()
        
        return None
    
    def should_change_water(self):
        """判断是否需要换水"""
        if self.last_change_time is None:
            return True
        
        hours_since_last = (datetime.now() - self.last_change_time).total_seconds() / 3600
        return hours_since_last >= self.interval_hours
    
    def get_status(self):
        """获取换水系统状态"""
        now = datetime.now()
        
        status = {
            'system_status': 'online' if HARDWARE_AVAILABLE else 'simulation',
            'last_change': self.last_change_time.isoformat() if self.last_change_time else None,
            'total_changes': self.water_count,
            'interval_hours': self.interval_hours,
            'needs_change': self.should_change_water(),
            'pump_pin': self.pump_pin,
            'valve_pin': self.valve_pin
        }
        
        # 计算下次换水时间
        if self.last_change_time:
            next_change = self.last_change_time + timedelta(hours=self.interval_hours)
            status['next_change'] = next_change.isoformat()
            status['hours_until_next'] = round((next_change - now).total_seconds() / 3600, 1)
        else:
            status['next_change'] = None
            status['hours_until_next'] = 0
        
        return status
    
    def set_interval(self, hours):
        """设置自动换水间隔"""
        if hours < 1 or hours > 168:  # 最小1小时，最大7天
            raise ValueError("换水间隔必须在1-168小时之间")
        
        self.interval_hours = hours
        self.logger.info(f"换水间隔已设置为 {hours} 小时")
    
    def cleanup(self):
        """清理资源"""
        if HARDWARE_AVAILABLE:
            try:
                self._emergency_stop()
                GPIO.cleanup()
                self.logger.info("换水系统资源已清理")
            except Exception as e:
                self.logger.error(f"清理资源失败: {e}")
