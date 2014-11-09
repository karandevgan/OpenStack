from flask import Blueprint

swift = Blueprint('swift', __name__)

from . import views