from flask import current_app, abort, session
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import requests
import json
from datetime import datetime
from .. import db,login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    role = db.Column(db.String(32), default="Users")

    def __repr__(self):
        return '<User %r>' % self.username

    def authenticateUser(self,password):
        url = current_app.config['IDENTITY_URL'] + '/tokens'
        payload = {
                    "auth": {
                        "tenantName": self.username + "_project",
                        "passwordCredentials": {
                            "username": self.username,
                            "password": password
                        }                        
                    }
                }
        headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}
        data = json.dumps(payload)

        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 203 or r.status_code == 200:
            response_content = json.loads(r.content)
            #Saves the token generated for the user in session
            session['user_token'] = response_content.get('access').get('token').get('id')
            #Saves the login time
            session['login_time'] = datetime.utcnow()
            #Saves the tenant id
            session['current_project_id'] = response_content.get('access').get('token').get('tenant').get('id')
            return True
        if r.status_code == 401:
            return False
        session.clear()
        abort(500)

    def createProject(self):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/projects'
        payload = {
                    "project": {
                        "domain_id": current_app.config['DEFAULT_DOMAIN_ID'],
                        "description": "Project for user " + self.username, 
                        "name": self.username + '_project',
                        "enabled": True,
                    }
                }
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                    'X-Auth-Token': current_app.config['ADMIN_TOKEN']}

        data = json.dumps(payload)
        r = requests.post(url, headers=headers, data=data)
        if r.status_code == 201:
            session['current_project_id'] = json.loads(r.content).get('project').get('id')
            return
        abort(500)
               
    def createUser(self, password):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/users'
        payload = {
                    "user": {
                        "domain_id": current_app.config['DEFAULT_DOMAIN_ID'],
                        "email": self.email,
                        "name": self.username,
                        "enabled": True,
                        "password": password
                    }
        }
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 
                'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        data = json.dumps(payload)
        r = requests.post(url, data=data, headers=headers)
        if r.status_code == 201:
            response_content = json.loads(r.content)
            self.id = response_content.get('user').get('id')
            return True
        abort(500)

    def addMemberRole(self):
        url = current_app.config['ADMIN_IDENTITY_URL_V3'] + '/projects/' + \
            session.get('current_project_id') + '/users/' + self.id + \
            '/roles/' + current_app.config['DEFAULT_MEMBER_ROLE']

        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        r = requests.put(url, headers=headers)        
        if r.status_code == 204:
            db.session.add(self)
            db.session.commit()
            return True
        abort(500)

    def invalidateToken(self):
        url = current_app.config['IDENTITY_URL'] + '/tokens/' + session.get('user_token')
        headers = {'X-Auth-Token': current_app.config['ADMIN_TOKEN']}
        r = requests.delete(url,headers=headers)
        if r.status_code == 204:
            return True
        abort(500)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def updateProfile(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        db.session.add(self)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()