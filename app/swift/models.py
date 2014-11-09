from flask import current_app, abort, session
import requests
import json
from contextlib import closing

class Swift(object):
    Account = {
        'number_of_objects': None,
        'total_size': 0,
        'containers': []
    }

    Container = {
        'total_size': 0,
        'name': None
    }

    def getAccountInfo(self):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id')
        headers = {'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 204 or r.status_code == 200:
            if r.status_code == 200:
                self.Account['containers'] = json.loads(r.content)
                self.Account['number_of_objects'] = r.headers['X-Account-Object-Count']
                self.Account['total_size'] = float(r.headers['X-Account-Bytes-Used'])
            if not r.headers.get('X-Account-Meta-Quota-Bytes'):
                headers2 = {'X-Auth-Token': session.get('user_token'),
                        'X-Account-Meta-Quota-Bytes': current_app.config['DEFAULT_OBJECT_STORE']}
                r2 = requests.post(url, headers=headers2)
                if r2.status_code != 200 and r2.status_code != 204:
                    abort(500)
            return True
        abort(500)

    def getContainerInfo(self, container_name):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(container_name) + '?delimiter=/'
        headers = {'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        if r.status_code == 204 or r.status_code == 200:
            if r.status_code == 200:
                self.Container['name'] = container_name
                self.Container['total_size'] = float(r.headers['X-Container-Bytes-Used'])
            return json.loads(r.content)
        if r.status_code == 404:
            abort(404)
        abort(500)

    def createContainer(self, container_name):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(container_name)
        headers = {'X-Auth-Token': session.get('user_token')}
        r = requests.put(url, headers=headers)
        if r.status_code == 201 or r.status_code == 204:
            return
        abort(500)

    def deleteContainer(self,container_name):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(container_name)
        headers = {'X-Auth-Token': session.get('user_token')}
        r = requests.delete(url, headers=headers)
        if r.status_code == 204:
            return True
        if r.status_code == 409:
            return False
        if r.status_code == 404:
            abort(404)
        abort(500)


    def deleteObject(self,path):
        if path[-1] == '/':         #Its a folder, delete it using bulk delete
            container_name = path[:path.find('/')]
            folder_path = path[path.find('/')+1:]
            content = self.openFolder(container_name, folder_path, use_delimiter=False)
            bulk_delete_body = ""
            for item in content:
                bulk_delete_body += container_name + '/' + item.get('name') + '\n'
            bulk_delete_body = bulk_delete_body.encode('utf-8')
            response_content = self.bulkDelete(bulk_delete_body)
            if response_content.get('Number Not Found') > 0 and response_content.get('Number Deleted') == 0:
                abort(404)
            return

        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(path)
        headers = {'X-Auth-Token': session.get('user_token')}
        r = requests.delete(url, headers=headers)
        if r.status_code == 204:
            return
        if r.status_code == 404:
            abort(404)
        abort(500)

    def getObject(self, container_name, object_name):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(container_name) + '/' + str(object_name)
        headers = {'X-Auth-Token': session.get('user_token')}
        #Streams the object i.e. does not get whole object at once
        with closing(requests.get(url, headers=headers, stream=True)) as r:
            if r.status_code == 200:
                return r
            if r.status_code == 404:
                abort(404)
        abort(500)

    def openFolder(self,container_name, folder_path, use_delimiter=True):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + str(container_name) + '?prefix=' + str(folder_path)
        if use_delimiter:
            url += '&delimiter=/'
        headers = {'Accept': 'application/json', 'X-Auth-Token': session.get('user_token')}
        r = requests.get(url, headers=headers)
        data = json.loads(r.content)
        if r.status_code == 200 and len(data):
            return data
        if r.status_code == 404 or len(data)==0:
            abort(404)
        abort(500)

    def createFolder(self, path):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + \
            '/' + path
        headers = {'X-Auth-Token': session.get('user_token')}
        r = requests.put(url, headers=headers)
        if r.status_code == 201:
            return
        if r.status_code == 404:
            abort(404)
        abort(500)

    def setSecretKey(self, key):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id')
        headers = {'X-Auth-Token': session.get('user_token'), 'X-Account-Meta-Temp-URL-Key': key}
        r = requests.post(url, headers=headers)
        if r.status_code == 204:
            return r.headers.get('X-Account-Meta-Temp-URL-Key')
        abort(500)

    def getSecretKey(self):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id')
        headers = {'X-Auth-Token': session.get('user_token')}
        r = requests.head(url, headers=headers)
        if r.status_code == 204:
            return r.headers.get('X-Account-Meta-Temp-URL-Key')
        elif r.status_code == 401:
            abort(403)
        abort(500)

    def bulkDelete(self, bulk_delete_body):
        url = current_app.config['SWIFT_URL'] + '/AUTH_' + session.get('current_project_id') + '?bulk-delete=true'
        headers = {'X-Auth-Token': session.get('user_token'), 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, data=bulk_delete_body)
        if r.status_code == 200:
            return json.loads(r.content)
        abort(500)