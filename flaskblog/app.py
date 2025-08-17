from flask import Flask, session, g
from flask_migrate import Migrate
import config
from exts import db, mail, redis_client
from models import UserModel
from cores.auth import bp as auth_bp
from cores.blogs import bp as blogs_bp
from cores.users import bp as users_bp
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)

# 扩展组件初始化
# 数据库
db.init_app(app)
# 邮件
mail.init_app(app)
# CSRF 保护
csrf = CSRFProtect(app)

# Redis 连接
redis_client.init_app(app)
# 数据库迁移
migrate = Migrate(app, db)


# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(blogs_bp)
app.register_blueprint(users_bp)


# 钩子函数
@app.before_request
def my_before_request():
    # 检查用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = UserModel.query.get(user_id)
        setattr(g, 'user', user) # 已登录，全局变量 g.user存储用户信息
    else:
        setattr(g, 'user', None)


@app.context_processor
def my_context_processor():
    # 上下文处理器，使 user 变量在所有模板中可用
    return {'user': g.user}


if __name__ == '__main__':
    import sys
    import subprocess
    import os

    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        # 启动完整服务的模式
        print("正在启动 Flask + Celery + Redis 服务...")

        try:
            # 启动 Celery Worker (在后台)
            print("启动 Celery Worker...")
            celery_process = subprocess.Popen([
                sys.executable, '-m', 'celery',
                '-A', 'celery_app.celery',
                'worker',
                '--loglevel=info',
                '--pool=solo'  # Windows 兼容的池类型
            ], cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_CONSOLE)  # 在新控制台窗口中运行

            print(f"Celery Worker PID: {celery_process.pid}")
            print("Celery Worker 已启动（在新控制台窗口中运行）")

            # 启动 Flask 应用
            print("启动 Flask 应用...")
            app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)

        except KeyboardInterrupt:
            print("\n正在关闭服务...")
            if 'celery_process' in locals():
                celery_process.terminate()
            print("服务已关闭")
        except Exception as e:
            print(f"启动过程中出现错误: {e}")
            if 'celery_process' in locals():
                celery_process.terminate()
    else:
        # 正常运行 Flask 应用（仅 Flask）
        print("启动 Flask 应用...")
        print("请确保 Redis 服务器已在后台运行...")
        print("如需同时启动 Celery，请使用: python app.py start")
        # app.run(debug=True, host='0.0.0.0', port=5000)   可以让同一wifi的访问服务
        app.run(debug=True)
