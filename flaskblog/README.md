# 基于falsk的博客系统

***这本身是一个问答网站，基于自己的理解，改进为一个博客系统。系统包含用户验证注册登录，发布博客，进行评论，日志等核心功能。***

此外，项目采用模块化方法，扩展实现相关功能：

1. 邮件发送：使用celery异步操作邮箱，发送邮件，实现用户登录
2. 文档下载：使用celery异步将博客信息生成PDF文档，实现文档下载
3. 用户日志：使用kafka收集相关用户行为，方便后续分析使用

## 安装

1. 从Github上下载项目
2. 安装python环境，并在项目内创建虚拟环境
3. 下载所需的库
   ```bash
   pip install -r requirements.txt
   ```
4. 如果要启动kafka服务，可以像我一样配置：
   下载docker容器，并配置好
   导入common/kafkaTest/docker-compose.yml文件，然后运行docker-compose up -d，即可成功启动kafka

## 配置

可以像我一样，创建一个mydate文件，其中定义一些隐私数据，然后导入config文件。

**进入config.py文件进行修改配置**

**数据库：**

先创建一个名为BlogSystem的mysql数据库，接下来连接，如下所示：

```Python
# 数据库的配置
DIALCT = "mysql"
DRITVER = "pymysql"
HOSTNAME = '127.0.0.1'
PORT = "3306"
USERNAME = "root"  # 用户名
PASSWORD = "123456"  # 密码
DBNAME = 'BlogSystem'  # 数据库名
SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}?charset=utf8"
```

**邮箱：**

我是用的是QQ邮箱，打开邮箱的SMTP服务后，在config中配置如下：

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

**可选**

将config文件的KAFKA_ENABLED设为True，表明使用kafka服务。此时可以根据安装，启动kafka服务。如果kafka服务未启动，程序也不会报错，只是没有这个功能。

## 运行

正常启动 (仅 Flask)

```bash
python app.py
```

完整服务启动 (Flask + Celery + Redis)

```bash
python app.py start
```

(可选)启动kafka消费者

```bash
python start_consumers.py
```

访问：http://127.0.0.1:5000/

## 部署

- 先获得一个服务器（阿里云），用应用连接。
- 下载docker,安装docker- compose。
- 从github上下载项目到服务器上。
- 进入项目根目录，即有docker-compose.yml文件,nginx.conf文件的目录。
- 运行docker-compose up -d，启动容器（时间可能很长，要下载镜像），提供服务。
- （可选）进入comment的kafkaTest目录，运行docker-compose up -d，启动kafka服务（可能有地址的问题，自己解决）。