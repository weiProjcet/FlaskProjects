from functools import wraps
from flask import redirect, url_for, g, session


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user_id') and g.user:
            print('已登录')
            return func(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))

    return wrapper
