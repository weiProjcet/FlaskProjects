from datetime import datetime
from sqlalchemy import or_
from exts import db


# flask db init  只需要运行一次
# flask db migrate  将orm模型生成迁移脚本
# flask db upgrade  将迁移脚本生成数据库

class UserModel(db.Model):
    """
    用户模型
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)


class UserProfileModel(db.Model):
    """
    用户资料模型
    """
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
    """
    博客模型
    """
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False, index=True)
    tag = db.Column(db.String(100), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship(UserModel, backref=db.backref('blogs', cascade='all, delete-orphan'))
    """
        优化的类方法 - 提高性能和可读性
    """

    @classmethod
    def get_recent_blogs_paginated(cls, page=1, per_page=10):
        """
        获取最近博客文章的分页查询（优化版本）
        作用:
            1. 使用索引字段排序，提高查询效率
            2. 统一处理分页逻辑
            3. 保持与原分页对象的兼容性
        """
        return cls.query.order_by(cls.create_time.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @classmethod
    def search_blogs_paginated(cls, query, page=1, per_page=10):
        """
        优化的博客搜索功能（分页版本）
        """
        return cls.query.filter(
            or_(
                cls.title.contains(query),  # 使用索引字段
                cls.tag.contains(query)  # 使用索引字段
            )
        ).order_by(cls.create_time.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @classmethod
    def get_blogs_by_tag_paginated(cls, tag, page=1, per_page=10):
        """
        根据标签获取博客文章（分页版本）
        """
        return cls.query.filter(cls.tag == tag).order_by(
            cls.create_time.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


class CommentModel(db.Model):
    """
    评论模型
    """
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    blog = db.relationship(BlogModel,
                           backref=db.backref('comments', order_by=create_time.desc(), cascade='all, delete-orphan'))
    author = db.relationship(UserModel, backref=db.backref('comments', cascade='all, delete-orphan'))
