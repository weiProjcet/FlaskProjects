from flask import Blueprint

bp = Blueprint('blogs', __name__, url_prefix='/')

from . import views