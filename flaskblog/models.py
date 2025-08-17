from datetime import datetime
from exts import db


# flask db init  只需要运行一次
# flask db migrate  将orm模型生成迁移脚本
# flask db upgrade  将迁移脚本生成数据库

class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)


class UserProfileModel(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 图片字段，可以存储图片路径或URL
    image = db.Column(db.String(500), nullable=True)
    # 视频字段，可以存储视频路径或URL
    video = db.Column(db.String(500), nullable=True)
    # 添加创建和更新时间字段
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 与UserModel建立一对一关系
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship(UserModel, backref=db.backref('profile', uselist=False, cascade='all, delete-orphan'))


class BlogModel(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship(UserModel, backref=db.backref('blogs', cascade='all, delete-orphan'))


class CommentModel(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # lazy='dynamic'
    blog = db.relationship(BlogModel,
                           backref=db.backref('comments', order_by=create_time.desc(), cascade='all, delete-orphan'))
    author = db.relationship(UserModel, backref=db.backref('comments', cascade='all, delete-orphan'))
