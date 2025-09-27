from flask import Blueprint

# 创建蓝图实例
bp = Blueprint('auth', __name__, url_prefix='/auth')
# 导入视图函数（避免循环导入）
from . import views
