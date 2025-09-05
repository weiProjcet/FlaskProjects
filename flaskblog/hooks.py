from flask import session, g
from models import UserModel


def register_hooks(app):
    @app.before_request
    def my_before_request():
        user_id = session.get('user_id')
        if user_id:
            user = UserModel.query.get(user_id)
            g.user = user
        else:
            g.user = None

    @app.context_processor
    def my_context_processor():
        return {'user': g.user}
