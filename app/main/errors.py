from flask import render_template, current_app, request
from datetime import datetime
from . import main
import traceback

@main.app_errorhandler(403)
def forbidden(e):
    error_msg = "\n--------------------------------------------ERROR----------------------------------------------\n" \
                "URL : " + request.url + "\n" \
                "Time: " + str(datetime.time(datetime.now()))
    current_app.logger.error(error_msg)
    current_app.logger.exception(e)
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    error_msg = "\n--------------------------------------------ERROR----------------------------------------------\n" \
                "URL : " + request.url + "\n" \
                "Time: " + str(datetime.time(datetime.now()))
    current_app.logger.error(error_msg)
    current_app.logger.exception(e)
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    error_msg = "\n--------------------------------------------ERROR----------------------------------------------\n" \
                "URL : " + request.url + "\n" \
                "Time: " + str(datetime.time(datetime.now()))
    current_app.logger.error(error_msg)
    current_app.logger.exception(e)
    return render_template('500.html'), 500