# 文件存在的意义是为了解决循环导入的问题
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_caching import Cache

# 创建相关实例
redis_client = FlaskRedis()
mail = Mail()
db = SQLAlchemy()
cache = Cache()
