from flask import session, g
from modules.models import UserModel
import uuid


def register_hooks(app):
    @app.before_request
    def my_before_request():
        # 生成或获取会话ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        # 用户认证
        g.session_id = session['session_id']
        user_id = session.get('user_id')
        if user_id:
            user = UserModel.query.get(user_id)
            g.user = user
        else:
            g.user = None

    @app.context_processor
    def my_context_processor():
        return {'user': g.user}
