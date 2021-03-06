from datetime import timedelta
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    MAIL_SUBJECT_PREFIX = '[XenonSwift]'
    MAIL_SENDER = 'XenonSwift Admin <test@example.com>'
    #Clears the session after 30 seconds of inactivity
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=3000)

    IDENTITY_URL = 'http://112.196.38.244:5000/v2.0'
    ADMIN_IDENTITY_URL = 'http://112.196.38.244:35357/v2.0'
    ADMIN_TOKEN = 'openstack'
    ADMIN_IDENTITY_URL_V3 = 'http://112.196.38.244:35357/v3'

    SWIFT_URL = 'http://112.196.38.244:8080'

    #ID for 'users' tenant
    DEFAULT_DOMAIN_ID = "default"
    #ID for _member_ role
    DEFAULT_MEMBER_ROLE = "9fe2ff9ee4384b1894a90878d3e92bab"
    #Default space provided for Object Storage
    DEFAULT_OBJECT_STORE = os.environ.get('DEFAULT_OBJECT_STORE') or 5368709120

    #Max number of objects that can be store in the container
    CONTAINER_META_COUNT = 1000

    ADMIN = os.environ.get('OPENSTACK_ADMIN') or 'karan.dewgun@gmail.com'

    #Email id used to send emails for confirmation
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    BITLY_USERNAME = 'xenonswift'
    BITLY_APIKEY = 'R_d9c3298302834b5d9cef402d78270c4e'

    SSL_DISABLE =  True
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                        'postgres://ljotzwznkfbbsj:fijRfOburSbGK_gNpg90_3Zmds@ec2-54-83-196-7.compute-1.amazonaws.com:5432/dan7osdgq6ca7r' or \
                        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler
        file_name = os.path.join(basedir, 'app/errors.log')
        file_handler = RotatingFileHandler(file_name)
        file_handler.setLevel(logging.NOTSET)
        app.logger.addHandler(file_handler)

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SSL_DISABLE = os.environ.get('SSL_DISABLE')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        import logging
        from logging.handlers import RotatingFileHandler
        file_name = os.path.join(basedir,  'app/errors.log')
        file_handler = RotatingFileHandler(file_name)
        file_handler.setLevel(logging.NOTSET)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}