import io
from flask import Blueprint, request, render_template, g, redirect, url_for, send_file
from sqlalchemy import or_
from exts import db
from models import BlogModel, CommentModel
from .forms import BlogFrom, CommentForm
from decorators import login_required

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
            # 跳转到首页
            return redirect('/')
        else:
            return render_template('publish.html', errors=form.errors, form=form)


@bp.route('/blogs/detail/<blog_id>')
def blog_detail(blog_id):
    # 获取博客详情
    blog = BlogModel.query.get_or_404(blog_id)

    # 获取页码参数，默认为第1页（用于评论分页）
    page = request.args.get('page', 1, type=int)

    # 获取该博客的评论并分页（每页显示5条评论）
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
        return redirect(url_for('blogs.blog_detail', blog_id=blog_id))
    else:
        return redirect(url_for('blogs.blog_detail', blog_id=request.form.get('blog_id')))


@bp.route('/download/<int:blog_id>')
def download_blog(blog_id):
    # 获取博客内容
    blog = BlogModel.query.get_or_404(blog_id)

    # 将博客内容转换为文本格式
    content = f"标题：{blog.title}\n作者：{blog.author.username}\n发布时间：{blog.create_time}\n\n{blog.content}"

    # 创建内存中的文件
    buffer = io.BytesIO()
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)

    # 返回文件下载响应
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'{blog.title}.txt',
        mimetype='text/plain'
    )