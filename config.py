from datetime import timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    MAIL_SUBJECT_PREFIX = '[OpenStack]'
    MAIL_SENDER = 'OpenStack Admin <test@example.com>'
    #Clears the session after 30 seconds of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000)

    IDENTITY_URL = 'http://112.196.38.243:5000/v2.0'
    ADMIN_IDENTITY_URL = 'http://112.196.38.243:35357/v2.0'
    ADMIN_TOKEN = 'openstack'
    ADMIN_IDENTITY_URL_V3 = 'http://112.196.38.243:35357/v3'

    SWIFT_URL = 'http://112.196.38.243:8080/v1'

    #ID for 'users' tenant
    DEFAULT_DOMAIN_ID = "default"
    #ID for _member_ role
    DEFAULT_MEMBER_ROLE = "9fe2ff9ee4384b1894a90878d3e92bab"
    #Default space provided for Object Storage
    DEFAULT_OBJECT_STORE = 5368709120

    ADMIN = os.environ.get('OPENSTACK_ADMIN') or 'karan.dewgun@gmail.com'

    #Email id used to send emails for confirmation
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SSL_DISABLE =  True
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SSL_DISABLE = os.environ.get('SSL_DISABLE')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}