"""
跟踪中间件 - 用于自动跟踪页面访问
"""
from flask import request, g
from functools import wraps
from .user_tracker import tracker


def track_user_behavior():
    """
    装饰器：跟踪用户行为
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取当前用户信息
            user_id = getattr(g, 'user_id', 'anonymous')

            # 跟踪页面访问
            tracker.track_page_view(
                user_id=user_id,
                page_url=request.url,
                referrer=request.referrer
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def track_click_event(element_id):
    """
    装饰器：跟踪点击事件
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'user_id', 'anonymous')

            tracker.track_click(
                user_id=user_id,
                page_url=request.url,
                element_id=element_id
            )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
