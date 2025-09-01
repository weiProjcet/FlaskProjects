"""
Celery 配置文件，用于异步处理任务（如发送邮件和生成PDF）
该文件配置了 Celery 与 Flask 应用的集成，使任务可以在后台执行
"""
from celery import Celery
from flask import Flask
from flask_mail import Message
from exts import mail, db, redis_client
from models import BlogModel
from markdown import markdown
import config
import io
import os

# 添加PDF生成库
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.colors import gray
except ImportError as e:
    print(f"PDF生成库导入失败: {e}")

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
    # 初始化扩展
    mail.init_app(app)
    db.init_app(app)
    redis_client.init_app(app)
    # 创建 Celery 实例
    celery = Celery(app.import_name)
    # 配置 Celery 使用 Redis 作为消息代理和结果后端
    celery.conf.update(
        broker_url=app.config['REDIS_URL'],  # Redis 作为消息代理
        result_backend=app.config['REDIS_URL'],  # Redis 作为结果存储
        broker_connection_retry_on_startup=True,  # 启动时重试连接
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


# 注册中文字体函数
def register_chinese_fonts():
    try:
        # 尝试使用项目 static/fonts 目录下的字体
        static_font_dir = os.path.join(os.path.dirname(__file__), 'static', 'fonts')
        project_fonts = [
            os.path.join(static_font_dir, 'simfang.ttf'),
            os.path.join(static_font_dir, 'simsun.ttc')
        ]

        for font_path in project_fonts:
            if os.path.exists(font_path):
                font_name = os.path.splitext(os.path.basename(font_path))[0]
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
        # 如果项目目录下没有字体文件，则尝试使用系统字体
        import platform
        system = platform.system()
        if system == "Windows":
            # 尝试使用Windows系统字体
            windows_font_paths = [
                 ("SimFang", "C:/Windows/Fonts/simfang.ttf"),
                ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
                ("SimSun", "C:/Windows/Fonts/simsun.ttc")
            ]
            for font_name,font_path in windows_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    return font_name
        return False
    except Exception as e:
        print(f"字体注册失败: {e}")
        return False


@celery.task
def generate_pdf_task(blog_id, task_id):
    print("异步生成博客PDF的任务已启动")
    """
    异步生成博客PDF的任务函数
    参数:
        blog_id: 博客ID
        task_id: 任务ID，用于标识生成的PDF
    """
    try:
        # 在 Flask 应用上下文中执行
        with celery.app.app_context():
            # 获取博客内容
            blog = BlogModel.query.get(blog_id)
            if not blog:
                raise ValueError(f"博客 {blog_id} 不存在")


            # 注册中文字体
            font_name = register_chinese_fonts()
            # 如果没有可用字体，使用默认字体
            if not font_name:
                font_name = 'Helvetica'
            font_registered = register_chinese_fonts()

            # 创建PDF文档到内存
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
            styles = getSampleStyleSheet()

            # 创建内容列表
            story = []

            # 标题样式 - 居中显示
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                alignment=TA_CENTER,  # 居中
                spaceAfter=30,
                fontName=font_name
            )
            title = Paragraph(blog.title, title_style)
            story.append(title)

            # 作者和时间信息 - 居中显示
            info_style = ParagraphStyle(
                'CustomInfo',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,  # 居中
                textColor=gray,
                fontName=font_name
            )
            info_text = f"作者：{blog.author.username}  发布时间：{blog.create_time.strftime('%Y-%m-%d %H:%M:%S')}"
            info = Paragraph(info_text, info_style)
            story.append(info)
            story.append(Spacer(1, 20))

            # 内容样式
            content_style = ParagraphStyle(
                'CustomContent',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_LEFT,
                fontName=font_name
            )

            # 处理Markdown内容
            content_html = markdown(blog.content)

            # 简单的HTML标签转换以支持基本格式
            content_html = content_html.replace('<h1>', '<font size="16" color="black"><b>').replace('</h1>',
                                                                                                     '</b></font><br/>')
            content_html = content_html.replace('<h2>', '<font size="14" color="black"><b>').replace('</h2>',
                                                                                                     '</b></font><br/>')
            content_html = content_html.replace('<h3>', '<font size="12" color="black"><b>').replace('</h3>',
                                                                                                     '</b></font><br/>')
            content_html = content_html.replace('<strong>', '<b>').replace('</strong>', '</b>')
            content_html = content_html.replace('<b>', '<b>').replace('</b>', '</b>')
            content_html = content_html.replace('<em>', '<i>').replace('</em>', '</i>')
            content_html = content_html.replace('<i>', '<i>').replace('</i>', '</i>')
            content_html = content_html.replace('<p>', '').replace('</p>', '<br/>')
            content_html = content_html.replace('<ul>', '').replace('</ul>', '<br/>')
            content_html = content_html.replace('<li>', '• ').replace('</li>', '<br/>')
            content_html = content_html.replace('<blockquote>', '<font color="gray"><i>').replace('</blockquote>',
                                                                                                  '</i></font><br/>')

            # 内容
            content = Paragraph(content_html, content_style)
            story.append(content)

            # 构建PDF
            doc.build(story)

            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            print("文档生成成功")

            # 将PDF数据存储到Redis中，设置过期时间（例如10分钟）
            redis_client.setex(f"pdf_{task_id}", 600, pdf_data)

            return {
                'status': 'success',
                'blog_id': blog_id,
                'title': blog.title,
                'task_id': task_id
            }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'PDF生成失败: {str(e)}',
            'task_id': task_id
        }
