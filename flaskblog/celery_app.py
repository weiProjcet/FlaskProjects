"""
Celery 配置文件，用于异步处理任务（如发送邮件）
该文件配置了 Celery 与 Flask 应用的集成，使任务可以在后台执行
"""
from celery import Celery
from flask import Flask
from flask_mail import Message
from exts import mail
import config

"""
   创建并配置 Celery 应用
   使用与主 Flask 应用相同的配置，确保一致性
   开发阶段：使用 --pool=solo 参数，这是 Windows 上最稳定的选项
   启动命令：python -m celery -A celery_app.celery worker --loglevel=info --pool=solo
"""


def create_celery_app():
    # 创建 Flask 应用实例
    app = Flask(__name__)
    # 加载与主应用相同的配置
    app.config.from_object(config)
    # 初始化邮件扩展
    mail.init_app(app)
    # 创建 Celery 实例
    celery = Celery(app.import_name)
    # 配置 Celery 使用 Redis 作为消息代理和结果后端
    celery.conf.update(
        broker_url=app.config['REDIS_URL'],  # Redis 作为消息代理
        result_backend=app.config['REDIS_URL'],  # Redis 作为结果存储
        broker_connection_retry_on_startup=True  # 启动时重试连接
    )

    # 定义 Celery 任务的基类，用于在任务执行时设置 Flask 上下文
    class ContextTask(celery.Task):
        """为 Celery 任务提供 Flask 应用上下文"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # 将自定义任务类设置为 Celery 的默认任务类
    celery.Task = ContextTask
    # 将 Flask 应用附加到 Celery 实例上
    celery.app = app
    return celery


# 创建 Celery 实例，供其他模块导入使用
celery = create_celery_app()


@celery.task
def send_email_task(subject, recipients, body):
    """
    异步发送邮件的任务函数
    参数:
        subject (str): 邮件主题
        recipients (list): 收件人列表
        body (str): 邮件正文内容
    此函数将在 Celery Worker 中执行，不会阻塞主应用
    """
    # 在 Flask 应用上下文中执行邮件发送
    with celery.app.app_context():
        # 创建邮件消息对象
        message = Message(
            subject=subject,  # 邮件主题
            recipients=recipients,  # 收件人列表
            body=body  # 邮件正文
        )
        # 发送邮件
        mail.send(message)
        # 返回成功信息
        return "邮件发送成功"
