import io
import uuid
from flask import Blueprint, request, render_template, g, redirect, url_for, send_file, current_app, jsonify
from exts import db, redis_client, cache
from models import BlogModel, CommentModel
from .forms import BlogFrom, CommentForm
from decorators import login_required
from markdown import markdown
from celery_app import generate_pdf_task  # 导入Celery任务

bp = Blueprint('blogs', __name__, url_prefix='/')

# 设置每页显示的博客数量
PER_PAGE = 10
"""
    index：默认展示博客
    search：根据输入的关键字展示博客
    publish_blog：发布博客
    blog_detail：显示博客，包括相关评论
    publish_comment：发布评论
    start_pdf_download、check_pdf_download、download_pdf_file：下载博客
"""


@bp.route('/')
@cache.cached(timeout=60, key_prefix='index_page')
def index():
    """
        首页路由 - 使用优化的数据库查询 - redis缓存
    """
    page = request.args.get('page', 1, type=int)
    # 使用优化的分页查询方法
    blogs = BlogModel.get_recent_blogs_paginated(
        page=page,
        per_page=PER_PAGE
    )
    return render_template('index.html', blogs=blogs)


@bp.route("/search")
def search():
    """
        搜索功能 - 使用优化的搜索查询
    """
    q = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    # 参数验证
    if not q:
        # 如果没有搜索关键字，重定向到首页
        return redirect(url_for('blogs.index'))

    # 使用缓存键
    cache_key = f'search_{q}_{page}'

    cached_result = cache.get(cache_key)
    if cached_result:
        current_app.logger.info(f'搜索结果从缓存获取: {q}')
        return render_template('index.html', blogs=cached_result, q=q)

    # 缓存未命中，执行查询    使用优化的搜索分页方法
    blogs = BlogModel.search_blogs_paginated(
        query=q,
        page=page,
        per_page=PER_PAGE
    )

    # 缓存搜索结果10分钟
    cache.set(cache_key, blogs, timeout=600)
    current_app.logger.info(f'搜索结果已缓存: {q}')

    # 记录这个搜索缓存键，便于发布新博客后全部删除
    search_keys = cache.get('all_search_keys') or set()
    search_keys.add(cache_key)
    cache.set('all_search_keys', search_keys, timeout=3600)

    # 记录搜索日志（用于分析用户行为）
    current_app.logger.info(f'用户{g.user.username if g.user else "匿名用户"}搜索了关键字"{q}"')
    # 渲染搜索结果页面
    return render_template('index.html', blogs=blogs, q=q)


# 当有新博客发布时，需要清除相关缓存
def clear_blog_cache():
    # 清理首页缓存
    cache.delete('index_page')
    # 清理搜索缓存（可以根据需要实现更精细的清理），当前是直接删除所有
    search_keys = cache.get('all_search_keys') or set()
    if search_keys:
        # 批量删除搜索缓存
        for key in search_keys:
            cache.delete(key)
        # 清理搜索键记录
        cache.delete('all_search_keys')

    current_app.logger.info('相关缓存已清理')


# 发布评论时清理评论缓存
def clear_comment_cache(blog_id):
    # 清理该博客的所有评论分页缓存
    # 假设最多有10页评论（可根据实际调整）
    for page in range(1, 11):
        cache_key = f'blog_{blog_id}_comments_{page}'
        cache.delete(cache_key)

    current_app.logger.info(f'博客{blog_id}的评论缓存已清理')


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

            # 发布成功后清理相关缓存
            clear_blog_cache()

            current_app.logger.info(f'用户{g.user.username}发布了博客{title}')
            return redirect('/')
        else:
            return render_template('publish.html', errors=form.errors, form=form)


@bp.route('/blogs/detail/<blog_id>')
def blog_detail(blog_id):
    """
       博客详情页 - 优化的详情查询 - 带缓存
    """
    # 为每篇博客创建独立的缓存键
    cache_key = f'blog_detail_{blog_id}'

    # 尝试从缓存获取博客详情
    cached_blog = cache.get(cache_key)
    if cached_blog:
        blog = cached_blog
        current_app.logger.info(f'博客详情从缓存获取: {blog_id}')
    else:
        # 缓存未命中，查询数据库
        blog = BlogModel.query.get_or_404(blog_id)
        # 这样可以减轻前端负担，提高页面渲染速度
        blog.content = markdown(blog.content)
        # 缓存5分钟
        cache.set(cache_key, blog, timeout=300)
        current_app.logger.info(f'博客详情已缓存: {blog_id}')
    # 评论分页也使用缓存
    page = request.args.get('page', 1, type=int)
    comments_cache_key = f'blog_{blog_id}_comments_{page}'
    cached_comments = cache.get(comments_cache_key)
    if cached_comments:
        comments = cached_comments
        current_app.logger.info(f'评论从缓存获取: {blog_id}, page {page}')
    else:
        comments = CommentModel.query.filter_by(blog_id=blog_id).order_by(
            CommentModel.create_time.desc()
        ).paginate(
            page=page,
            per_page=10,  # 每页10条评论
            error_out=False  # 页码错误不抛异常
        )
        cache.set(comments_cache_key, comments, timeout=120)
        current_app.logger.info(f'评论已缓存: {blog_id}, page {page}')

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
        # 发布评论后清理该博客的评论缓存
        clear_comment_cache(blog_id)

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
    print(f"pdf_{task_id}")
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
