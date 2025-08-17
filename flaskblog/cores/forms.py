import wtforms
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Email, Length, EqualTo, InputRequired
from models import UserModel


# form：验证前端提交的表单数据是否符合要求

# 注册页面的表单
class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    captcha = wtforms.StringField(validators=[Length(min=4, max=4, message='验证码格式错误')])
    username = wtforms.StringField(validators=[Length(min=3, max=20, message='用户名字符不等少于3个，多于20个')])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message='密码格式错误！大于3，小于20')])
    password_confirm = wtforms.StringField(validators=[EqualTo('password', message='两次密码不一致')])

    # 自定义表单验证，邮箱是否被注册
    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message='邮箱已被注册')


class EmailForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])

    # 注册时（发送验证码），检测邮箱是否被注册
    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message='邮箱已被注册')


class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message='密码格式错误！大于3，小于20')])


class BlogFrom(wtforms.Form):
    title = wtforms.StringField(validators=[Length(min=5, max=100, message='标题格式错误，大于5，小于100')])
    tag = wtforms.StringField(validators=[Length(min=5, max=100, message='概述格式，大于5，小于100')])
    content = wtforms.StringField(validators=[Length(min=5, message='内容格式错误，至少有5个字符')])


class CommentForm(wtforms.Form):
    blog_id = wtforms.IntegerField(validators=[InputRequired(message='必须要传入ID')])
    comment = wtforms.StringField()


class UserProfileForm(wtforms.Form):
    image = FileField('图片文件', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif'], '只能上传图片文件')
    ])
    video = FileField('视频文件', validators=[
        FileAllowed(['mp4', 'avi', 'mov', 'wmv'], '只能上传视频文件')
    ])