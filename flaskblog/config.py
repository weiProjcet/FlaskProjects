from mydate import Email, AuthorizationCode
import os

# 安全密钥，用于各种安全相关的功能。
SECRET_KEY = 'WEISJDFH123486'

# 数据库的配置
DIALCT = "mysql"
DRITVER = "pymysql"
HOSTNAME = '127.0.0.1'
PORT = "3306"
USERNAME = "root"
PASSWORD = "123456"
DBNAME = 'FalskBlog'
SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}?charset=utf8"

# 数据库连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,  # 连接池大小
    'pool_recycle': 3600,  # 连接回收时间（秒）
    'pool_pre_ping': True,  # 连接前检查有效性
    'max_overflow': 30,  # 超出pool_size后最多允许的连接数
    'pool_timeout': 30,  # 获取连接的超时时间（秒）
}

# 配置邮箱
MAIL_SERVER = 'smtp.qq.com'  # SMTP服务器地址
MAIL_PORT = 465  # SMTP服务端口
MAIL_USE_SSL = True  # 启用SSL加密
MAIL_USERNAME = Email  # 邮箱账户
MAIL_PASSWORD = AuthorizationCode  # 邮箱密码或授权码
MAIL_DEFAULT_SENDER = Email

# 配置redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = None  # 如果没有设置密码则为 None
REDIS_DB = 0
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Celery 配置
CELERY_BROKER_URL = REDIS_URL  # 使用 Redis 作为消息代理
CELERY_RESULT_BACKEND = REDIS_URL  # 使用 Redis 作为结果后端
CELERY_RESULT_EXPIRES = 3600  # 任务结果1小时后过期
CELERY_TASK_RESULT_EXPIRES = 3600  # 兼容旧版本配置项

# 文件上传配置
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'wmv'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
