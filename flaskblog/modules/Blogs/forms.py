import wtforms
from wtforms.validators import Length, InputRequired


class BlogFrom(wtforms.Form):
    title = wtforms.StringField(validators=[Length(min=5, max=100, message='标题格式错误，大于5，小于100')])
    tag = wtforms.StringField(validators=[Length(min=5, max=100, message='概述格式，大于5，小于100')])
    content = wtforms.StringField(validators=[Length(min=5, message='内容格式错误，至少有5个字符')])


class CommentForm(wtforms.Form):
    blog_id = wtforms.IntegerField(validators=[InputRequired(message='必须要传入ID')])
    comment = wtforms.StringField()
