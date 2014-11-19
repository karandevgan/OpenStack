from flask import render_template
from flask import current_app
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    current_app.logger.exception(e)
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    current_app.logger.exception(e)
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    current_app.logger.exception(e)
    return render_template('500.html'), 500