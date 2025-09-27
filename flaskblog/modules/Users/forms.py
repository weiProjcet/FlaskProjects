import wtforms
from flask_wtf.file import FileField, FileAllowed


class UserProfileForm(wtforms.Form):
    image = FileField('图片文件', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'gif'], '只能上传图片文件')
    ])
    video = FileField('视频文件', validators=[
        FileAllowed(['mp4', 'avi', 'mov', 'wmv'], '只能上传视频文件')
    ])