#!usr/bin/env python
import os
from app import create_app, db
from app.auth.models import User, Role
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('APP_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(threaded=True))

@manager.command
def deploy():
    """Run deployment tasks"""
    from flask.ext.migrate import upgrade
    from app.auth.models import User
    from app.auth.models import Role

    #migrate database to latest revision
    upgrade()
    
if __name__ == '__main__':
    manager.run()