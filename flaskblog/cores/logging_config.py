# cores/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import request, has_request_context


class AdvancedRequestFilter(logging.Filter):
    """高级请求过滤器"""

    STATIC_EXTENSIONS = {'.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf',
                         '.map'}

    # 需要记录的路由端点前缀
    ALLOWED_ENDPOINTS = ['auth.', 'blogs.', 'users.']

    def filter(self, record):
        # 如果不在请求上下文中，允许记录
        if not has_request_context():
            return True

        # 检查是否为静态文件请求
        if self._is_static_request():
            return False

        # 检查是否为需要记录的路由
        if self._is_monitored_endpoint():
            return True

        # 默认不记录
        return False

    def _is_static_request(self):
        """判断是否为静态文件请求"""
        if not hasattr(request, 'path'):
            return False

        # 检查路径是否以 /static/ 开头
        if request.path.startswith('/static/'):
            return True

        # 检查是否有静态文件扩展名
        for ext in self.STATIC_EXTENSIONS:
            if request.path.endswith(ext):
                return True

        return False

    def _is_monitored_endpoint(self):
        """判断是否为需要监控的端点"""
        if not hasattr(request, 'endpoint') or not request.endpoint:
            return False

        # 检查端点是否在允许列表中
        return any(request.endpoint.startswith(prefix) for prefix in self.ALLOWED_ENDPOINTS)


def setup_logging(app):
    """
    配置应用日志
    """
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/flaskblog.log',  # 文件路径
        maxBytes=1024 * 1024 * 10,  # 10MB 单个日志文件容量
        backupCount=10,  # 10 日志文件数量
        encoding='utf-8'
    )

    # 设置格式 时间戳 日志级别 日志内容 产生日志的文件路径 行号
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 添加过滤器
    file_handler.addFilter(AdvancedRequestFilter())

    # 添加到应用
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
