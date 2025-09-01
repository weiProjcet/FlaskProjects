import io
import uuid
from flask import Blueprint, request, render_template, g, redirect, url_for, send_file, current_app, jsonify
from sqlalchemy import or_
from exts import db, redis_client
from models import BlogModel, CommentModel
from .forms import BlogFrom, CommentForm
from decorators import login_required
from markdown import markdown

# 导入Celery任务
from celery_app import generate_pdf_task

bp = Blueprint('blogs', __name__, url_prefix='/')

# 设置每页显示的博客数量
PER_PAGE = 10


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    blogs = BlogModel.query.order_by(BlogModel.create_time.desc()).paginate(
        page=page, per_page=PER_PAGE, error_out=False)

    return render_template('index.html', blogs=blogs)


@bp.route("/search")
def search():
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    blogs = BlogModel.query.filter(
        or_(BlogModel.title.contains(q), BlogModel.tag.contains(q))
    ).paginate(page=page, per_page=PER_PAGE, error_out=False)
    current_app.logger.info(f'用户{g.user.username}搜索了关键字{q}')
    return render_template('index.html', blogs=blogs, q=q)


@bp.route('/blogs', methods=['GET', 'POST'])
@login_required
def publish_blog():
    if request.method == 'GET':
        return render_template('publish.html')
    else:
        form = BlogFrom(request.form)
        if form.validate():
            title = form.title.data
            tag = form.tag.data
            content = form.content.data
            blog = BlogModel(title=title, tag=tag, content=content, author=g.user)
            db.session.add(blog)
            db.session.commit()
            current_app.logger.info(f'用户{g.user.username}发布了博客{title}')
            # 跳转到首页
            return redirect('/')
        else:
            return render_template('publish.html', errors=form.errors, form=form)


@bp.route('/blogs/detail/<blog_id>')
def blog_detail(blog_id):
    # 获取博客详情,内容转换为HTML
    blog = BlogModel.query.get_or_404(blog_id)
    blog.content = markdown(blog.content)

    # 获取页码参数，默认为第1页（用于评论分页）
    page = request.args.get('page', 1, type=int)

    # 获取该博客的评论并分页（每页显示10条评论）
    comments = CommentModel.query.filter_by(blog_id=blog_id).order_by(
        CommentModel.create_time.desc()).paginate(
        page=page, per_page=10, error_out=False)

    # 将博客和评论分页对象传递给模板
    return render_template('detail.html', blog=blog, comments=comments)


@bp.post('/blogs/comment/public')
@login_required
def publish_comment():
    form = CommentForm(request.form)
    if form.validate():
        comment_data = form.comment.data
        blog_id = form.blog_id.data
        comment = CommentModel(comment=comment_data, blog_id=blog_id, author_id=g.user.id)
        db.session.add(comment)
        db.session.commit()
        current_app.logger.info(f'用户{g.user.username}评论了博客{blog_id}，评论为{comment.id}')
        return redirect(url_for('blogs.blog_detail', blog_id=blog_id))
    else:
        return redirect(url_for('blogs.blog_detail', blog_id=request.form.get('blog_id')))


# 启动PDF生成任务
@bp.route('/download/<int:blog_id>/pdf/start', methods=['POST'])
@login_required
def start_pdf_download(blog_id):
    # 生成唯一的任务ID
    task_id = str(uuid.uuid4())

    # 启动异步任务生成PDF
    generate_pdf_task.delay(blog_id, task_id)

    # 立即返回任务ID
    return jsonify({
        'status': 'success',
        'task_id': task_id,
    })


# 检查任务状态并提供下载
@bp.route('/download/<int:blog_id>/pdf/check/<task_id>')
@login_required
def check_pdf_download(blog_id, task_id):
    # 检查Redis中是否有生成的PDF数据
    pdf_data = redis_client.get(f"pdf_{task_id}")

    if pdf_data:
        return jsonify({
            'status': 'ready'
        })
    else:
        # 检查Celery任务状态
        # 这里我们简化处理，假设任务仍在进行中
        return jsonify({
            'status': 'processing'
        })


# 实际下载PDF文件
@bp.route('/download/<int:blog_id>/pdf/download/<task_id>')
@login_required
def download_pdf_file(blog_id, task_id):
    # 从Redis获取PDF数据
    pdf_data = redis_client.get(f"pdf_{task_id}")

    if pdf_data:
        # 获取博客标题用于文件名
        blog = BlogModel.query.get_or_404(blog_id)

        # 创建内存中的文件
        buffer = io.BytesIO(pdf_data)
        buffer.seek(0)

        current_app.logger.info(f'用户{g.user.username}下载了博客{blog_id}的PDF版本')

        # 删除Redis中的数据（一次性下载）
        redis_client.delete(f"pdf_{task_id}")

        # 返回文件下载响应
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'{blog.title}.pdf',
            mimetype='application/pdf'
        )

    # 如果没有找到PDF数据，重定向回详情页
    return redirect(url_for('blogs.blog_detail', blog_id=blog_id))
