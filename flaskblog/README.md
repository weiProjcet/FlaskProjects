# 基于falsk的博客系统
***这本身是一个问答网站，基于自己的理解，改进为一个博客系统。系统包含用户验证注册登录，发布博客，进行评论***

## 安装
1. 从Github上下载项目
2. 安装python环境，并在项目内创建虚拟环境
3. 下载所需的库
   ```bash
   pip install -r requirements.txt
   ```

## 配置
可以向我一样，创建一个mydate文件，其中定义一些隐私数据，然后导入config文件。

**进入config.py文件进行修改配置**

**数据库：**
**先创建一个名为BlogSystem的mysql数据库**
```Python
# 数据库的配置
DIALCT = "mysql"   
DRITVER = "pymysql"
HOSTNAME = '127.0.0.1'
PORT = "3306"
USERNAME = "root"   # 用户名
PASSWORD = "123456"  # 密码
DBNAME = 'BlogSystem'   # 数据库名
SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}?charset=utf8"
```

**邮箱：**
```Python
MAIL_SERVER = 'smtp.qq.com'  # SMTP服务器地址 QQ邮箱
MAIL_PORT = 465  # SMTP服务端口
MAIL_USE_SSL = True  # 启用SSL加密
MAIL_USERNAME = ''  # 邮箱账户
MAIL_PASSWORD = ''  # 授权码
MAIL_DEFAULT_SENDER = ''  # 邮箱账户
```

**生成数据库迁移文件**
```base
flask db init  只需要运行一次
flask db migrate  将orm模型生成迁移脚本
flask db upgrade  将迁移脚本生成数据库
```

## 运行
正常启动 (仅 Flask)
```bash
python app.py
```
完整服务启动 (Flask + Celery + Redis)
```bash
python app.py start
```
访问：http://127.0.0.1:5000/
