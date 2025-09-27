import wtforms
from wtforms.validators import Email, Length, EqualTo

from modules.models import UserModel


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
