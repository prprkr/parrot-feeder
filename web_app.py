# -*- coding: utf-8 -*-
"""
鹦鹉智能喂食器 + 换水系统 - Flask Web应用
提供RESTful API和Web界面
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import logging
import os

from config import config
from feeder import FeederSystem
from water_system import WaterSystem


def create_app(config_name='default'):
    """应用工厂函数"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # 初始化系统
    feeder = FeederSystem(app.config)
    water_system = WaterSystem(app.config)
    
    logger = logging.getLogger(__name__)
    
    # ==================== 页面路由 ====================
    
    @app.route('/')
    def index():
        """主页 - 控制面板"""
        return render_template('index.html')
    
    @app.route('/api/status')
    def api_status():
        """获取系统整体状态"""
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'feeder': feeder.get_status(),
            'water': water_system.get_status()
        })
    
    # ==================== 喂食API ====================
    
    @app.route('/api/feed', methods=['POST'])
    def api_feed():
        """手动触发喂食"""
        data = request.json or {}
        portion = data.get('portion', 'normal')
        
        if portion not in ['small', 'normal', 'large']:
            return jsonify({
                'success': False,
                'message': '无效的分量参数，必须是: small, normal, large'
            }), 400
        
        result = feeder.feed(portion=portion)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    @app.route('/api/feed/status', methods=['GET'])
    def api_feed_status():
        """获取喂食系统状态"""
        return jsonify(feeder.get_status())
    
    @app.route('/api/feed/schedule', methods=['GET', 'POST'])
    def api_feed_schedule():
        """获取/设置喂食计划"""
        if request.method == 'GET':
            return jsonify({
                'schedules': app.config.FEED_SCHEDULES
            })
        
        # TODO: 实现动态修改喂食计划
        return jsonify({'message': '功能开发中'}), 501
    
    # ==================== 换水API ====================
    
    @app.route('/api/water/change', methods=['POST'])
    def api_water_change():
        """手动触发换水"""
        data = request.json or {}
        volume = data.get('volume')  # 可选，不传则使用默认值
        
        result = water_system.change_water(volume_ml=volume)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    @app.route('/api/water/status', methods=['GET'])
    def api_water_status():
        """获取换水系统状态"""
        return jsonify(water_system.get_status())
    
    @app.route('/api/water/schedule', methods=['POST'])
    def api_set_water_schedule():
        """设置定时换水计划"""
        data = request.json or {}
        interval = data.get('interval_hours', 24)
        
        try:
            water_system.set_interval(interval)
            
            # TODO: 更新APScheduler任务
            
            return jsonify({
                'success': True,
                'message': f'定时换水已设置为每 {interval} 小时',
                'interval_hours': interval
            })
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
    
    # ==================== 系统控制API ====================
    
    @app.route('/api/system/restart', methods=['POST'])
    def api_restart():
        """重启服务（仅用于开发调试）"""
        if not app.config['DEBUG']:
            return jsonify({'success': False, 'message': '生产环境禁止此操作'}), 403
        
        logger.warning("收到重启请求")
        # 在实际部署中，这里会调用systemctl restart
        return jsonify({
            'success': True,
            'message': '重启请求已接收'
        })
    
    @app.route('/api/system/logs', methods=['GET'])
    def api_logs():
        """获取最近日志（简化版）"""
        # TODO: 从日志文件读取
        return jsonify({
            'logs': [
                {'time': datetime.now().isoformat(), 'level': 'INFO', 'message': '系统运行正常'}
            ],
            'message': '完整日志功能开发中'
        })
    
    # 错误处理
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500
    
    # 导出实例供main.py使用
    app.feeder = feeder
    app.water_system = water_system
    
    return app


if __name__ == '__main__':
    application = create_app()
    application.run(
        host=application.config['HOST'],
        port=application.config['PORT'],
        debug=application.config['DEBUG']
    )
