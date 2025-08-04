from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from exts import db, redis_client
from models import UserModel
from .forms import RegisterForm, LoginForm, EmailForm
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash
from celery_app import send_email_task

bp = Blueprint('auth', __name__, url_prefix='/auth')


# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                return render_template('login.html', error='用户不存在，请注册！')
            if check_password_hash(user.password, password):
                # cookie：存放登录授权的信息
                # session：加密后存储在cookie中
                session['user_id'] = user.id
                return redirect('/')
            else:
                return render_template('login.html', error='密码错误')
        else:
            return render_template('login.html', errors=form.errors)


# 退出
@bp.route('logout')
def logout():
    session.clear()
    return redirect('/')


# 获取验证码 注册页面提交请求
# bp.route:如果没有指定methods参数，默认就是GET请求
@bp.route('/captcha/email')
def get_email_captcha():
    # 获取用户输入的邮箱
    # 生成验证码并异步发送邮件，提高响应速度
    email = request.args.get('email')
    # 检查是否有邮箱参数，避免在模块导入时执行
    if not email:
        return jsonify({"code": 400, "message": "缺少邮箱参数", "data": None})

    form = EmailForm(data={'email': email})
    if not form.validate():
        if 'email' in form.errors:
            return jsonify({"code": 400, "message": form.errors['email'][0], "data": None})
        else:
            return jsonify({"code": 400, "message": "邮箱验证失败", "data": None})

    # 获得验证码
    source = string.digits * 4
    captcha = ''.join(random.sample(source, 4))
    print(captcha)
    # 向邮箱发送验证码
    send_email_task.delay(
        subject="问答网站验证码",  # 邮件主题
        recipients=[email],  # 收件人列表
        body=f"您的验证码是：{captcha}，验证码十分钟内有效！"  # 邮件正文
    )
    # 用redis存储验证信息，并设置过期时间
    # hset(name, key, value) - name是hash表名，key是字段名，value是字段值
    redis_client.hset("captcha_data", email, captcha)
    redis_client.expire("captcha_data", 600)
    # RESTful API
    return jsonify({"code": 200, "message": "", "data": None})


# 注册页面
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        form = RegisterForm(request.form)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            captcha = form.captcha.data
            # 从Redis hash中获取验证码
            stored_captcha = redis_client.hget("captcha_data", email)
            if not stored_captcha:
                return render_template('register.html', error='验证码已过期或邮箱不存在')

            if stored_captcha.decode() != captcha:
                return render_template('register.html', error='验证码错误')
            # 验证成功
            redis_client.hdel("captcha_data", email)
            user = UserModel(email=email, username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            return render_template('register.html', errors=form.errors)
