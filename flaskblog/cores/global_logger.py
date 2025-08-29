# cores/global_logger.py
from flask import request, g
import time


def setup_global_logging(app):
    """设置全局日志记录"""

    @app.before_request
    def log_request_start():
        g.start_time = time.time()
        user_info = f"用户ID: {g.get('user').id}" if g.get('user') else "未登录用户"
        app.logger.info(f"[请求开始] {user_info} | {request.method} {request.url} | 端点: {request.endpoint}")

    @app.after_request
    def log_request_end(response):
        duration = time.time() - g.get('start_time', time.time())
        user_info = f"用户ID: {g.get('user').id}" if g.get('user') else "未登录用户"
        app.logger.info(
            f"[请求结束] {user_info} | {request.method} {request.url} | 状态码: {response.status_code} | 耗时: {duration:.4f}秒")
        return response

    @app.teardown_request
    def log_request_exception(exception):
        if exception:
            duration = time.time() - g.get('start_time', time.time())
            user_info = f"用户ID: {g.get('user').id}" if g.get('user') else "未登录用户"
            app.logger.error(
                f"[请求异常] {user_info} | {request.method} {request.url} | 错误: {str(exception)} | 耗时: {duration:.4f}秒")
