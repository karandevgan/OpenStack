from flask import render_template, redirect, url_for, session
from flask.ext.login import current_user
from . import main
from ..decorators import admin_required

@main.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('swift.account'))
    return render_template('index.html')