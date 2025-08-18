import os
import time
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app
from decorators import login_required
from models import UserProfileModel
from cores.forms import UserProfileForm
from exts import db

bp = Blueprint('users', __name__, url_prefix='/users')


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_file(file, folder):
    """保存文件并返回相对路径"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 确保文件名唯一
        name, ext = os.path.splitext(filename)
        timestamp = int(time.time())
        filename = f"{name}_{timestamp}{ext}" if name else f"{timestamp}{ext}"

        # 创建上传目录
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # 返回相对URL路径
        return f"uploads/{folder}/{filename}"
    return None


@bp.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    # 获取当前用户的资料
    user_profile = UserProfileModel.query.filter_by(user_id=g.user.id).first()
    # 如果不存在用户资料，则创建一个
    if not user_profile:
        user_profile = UserProfileModel(user_id=g.user.id)
        db.session.add(user_profile)
        try:
            db.session.commit()
            print(user_profile.user.username)
        except Exception as e:
            db.session.rollback()
            flash("系统错误，请重试")
            return redirect(url_for('users.profile'))
    if request.method == 'GET':
        form = UserProfileForm()
        return render_template('user_profile.html', form=form, user_profile=user_profile)
    else:
        form = UserProfileForm(request.form)  # 同时处理表单和文件数据

        if not form.validate():
            flash("表单填写有误")
            return render_template('user_profile.html', form=form, user_profile=user_profile)

        # 检查表单中的文件
        image_file = request.files.get('image')
        video_file = request.files.get('video')

        # 如果有文件上传，则处理文件
        image_path = None
        video_path = None

        if image_file and image_file.filename != '':
            image_path = save_file(image_file, 'images')
            if not image_path:
                flash("图片文件格式不支持")
                return redirect(request.url)

        if video_file and video_file.filename != '':
            video_path = save_file(video_file, 'videos')
            if not video_path:
                flash("视频文件格式不支持")
                return redirect(request.url)

        if user_profile:
            # 更新现有资料，并删除旧文件
            if image_path:
                # 删除旧的图片文件
                if user_profile.image:
                    old_image_path = os.path.join(current_app.root_path, 'static', user_profile.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                user_profile.image = image_path
            if video_path:
                # 删除旧的视频文件
                if user_profile.video:
                    old_video_path = os.path.join(current_app.root_path, 'static', user_profile.video)
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)
                user_profile.video = video_path
        else:
            # 创建新资料
            user_profile = UserProfileModel(
                image=image_path,
                video=video_path,
                user_id=g.user.id
            )
            db.session.add(user_profile)
        try:
            db.session.commit()
            flash("用户资料已更新")
        except Exception:
            db.session.rollback()
            flash("用户资料更新失败")
        return redirect(url_for('users.profile'))
