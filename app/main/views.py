from flask import render_template, redirect, url_for, session
from . import main

@main.route('/')
def index():
    return render_template('index.html', token = session.get('user_token', None))