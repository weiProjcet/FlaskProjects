from flask import Flask
from flask_migrate import Migrate

import config
from exts import db, mail, redis_client, cache
from hooks import register_hooks

from cores.auth import bp as auth_bp
from cores.blogs import bp as blogs_bp
from cores.users import bp as users_bp
from cores.logging_config import setup_logging
from cores.global_logger import setup_global_logging

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)

# 扩展组件初始化
db.init_app(app)  # 数据库
mail.init_app(app)  # 邮件
csrf = CSRFProtect(app)  # CSRF 保护
setup_logging(app)  # 初始化日志
cache.init_app(app)  # 初始化缓存
redis_client.init_app(app)  # Redis 连接
migrate = Migrate(app, db)  # 数据库迁移

register_hooks(app)  # 注册钩子函数
setup_global_logging(app)  # 使用日志

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(blogs_bp)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    app.run(debug=True)
