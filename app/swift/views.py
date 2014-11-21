from flask import render_template, redirect, \
    url_for, abort, session, flash, request, \
    current_app, Response, stream_with_context, \
    make_response
from flask.ext.login import login_required, current_user
from . import swift
from .forms import CreateContainerForm, CreateFolderForm
from .models import Swift
from time import time
import hmac
from hashlib import sha1
from ..decorators import admin_required
from ..admin import readFile

def calculateHMACSignatureUpload(hmacpath, timestamp, redirect_path, key):
    hmac_body = '%s\n%s\n%s\n%s\n%s' % (hmacpath, redirect_path, 1073741824, 1, timestamp)
    return hmac.new(key, hmac_body, sha1).hexdigest()

def calculateHMACSignatureShare(hmacpath, expires, method, key):
    hmac_body = '%s\n%s\n%s' % (method, expires, hmacpath)
    return hmac.new(key, hmac_body, sha1).hexdigest()

swift_authentication_methods = {'keystoneauth': 'Keystone Authentication', 'tempauth': 'Temp Auth'}

swift_account = Swift()

@swift.route('/')
@login_required
def account():
    if swift_account.getAccountInfo():
        return render_template('/swift/index.html', Account=swift_account.Account)

@swift.route('/<path:path>')
@login_required
def container(path):
    if path[-1] == '/':
        #If there is only container name, open the container
        if len(path.split('/')) == 2:
            if request.args.get('status'):
                if request.args.get('status') == '201':
                    flash('Object will be uploaded soon.')
                elif request.args.get('status') == '400':
                    flash('No file to process.')
                else:
                    flash('Oops! Something went wrong. Please try again.')
                return redirect(url_for('swift.container', path=path))

            path = path[:-1]        #remove the trailing slash
            #If there is delete=yes parameter, delete the container
            if request.args.get('delete') == 'yes':
                result = swift_account.deleteContainer(path)
                if result:    
                    flash('Container ' + path + ' scheduled for deletion.')
                else:
                    flash('Container ' + path + ' is not empty.')
                return redirect(url_for('swift.account'))
        
            folder_list = []
            object_list = []
            for object in swift_account.getContainerInfo(path):
                if object.get('name'):
                    object_list.append(object) #Contains all the objects
                else:
                    folder_list.append(object) #Contains all the pseudo-folders
            return render_template('/swift/container.html',
                    Container=swift_account.Container,
                    object_list=object_list,
                    folder_list=folder_list)

        #If there is a trailing / its a folder
        if len(path.split('/')) > 2:
            #If there is delete=yes parameter, delete the folder
            if request.args.get('delete') == 'yes':
                swift_account.deleteObject(path)
                flash('Folder ' + path + ' scheduled for deletion.')
                path=path[:path[:-1].rfind('/')+1]
                return redirect(url_for('swift.container', path=path))

            if request.args.get('status'):
                if request.args.get('status') == '201':
                    flash('Object will be uploaded')
                elif request.args.get('status') == '400':
                    flash('No file to process')
                return redirect(url_for('swift.container', path=path))
            folder_path = path[path.find('/')+1:]
            container_name = path[:path.find('/')]
            folder_list = []
            object_list = []
            for object in swift_account.openFolder(container_name, folder_path):
                if object.get('name'):
                    if object.get('name')[-1] != '/':
                        object_list.append(object)
                else:
                    folder_list.append(object)
            folders = folder_path.split('/')
            #Current folder's path
            current_path = container_name + '/'
            for folder in folders[:-1]:
                current_path += folder + '/'
            
            return render_template('/swift/folder.html',
                        current_path = current_path, 
                        container_name=container_name,
                        folders=folders[:-1],
                        object_list=object_list,
                        folder_list=folder_list)

    #If there is no trailing / its an object, download the object
    if path[-1] != '/':
        #If there is delete=yes parameter, delete the object
        if request.args.get('delete') == 'yes':
            swift_account.deleteObject(path)
            flash('Object ' + path +' will be deleted.')
            # if len(path.split('/')) == 2:
            #     return redirect(url_for('swift.container', path=path[:path.find('/')]))
            return redirect(url_for('swift.container', path=path[:path.rfind('/')+1]))
        
        container_name = path[:path.find('/')]
        object_name = path[path.find('/')+1:]
        r = swift_account.getObject(container_name, object_name)
        filename = path[path.rfind('/')+1:]

        def generate():
            for chunk in r.iter_lines():
                yield chunk

        response = make_response(Response(generate()))
        response.headers['Content-Disposition'] = 'attachment; filename=' + filename
        response.headers['Content-Type'] = r.headers['Content-Type']
        return response

    #Else return error code 404
    abort(404)

@swift.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    key = swift_account.getSecretKey()
    hmacpath = '/v1/AUTH_' + session.get('current_project_id') + '/' + request.args.get('path')
    upload_path = current_app.config['SWIFT_URL'] + hmacpath
    timestamp = int(time() + 600)
    redirect_path=url_for('swift.container', path=request.args.get('path') , _external=True)
    hmackey = calculateHMACSignatureUpload(hmacpath, timestamp, redirect_path, key)
    
    return render_template('/swift/upload.html',
                        upload_path=upload_path,
                        redirect_path=redirect_path,
                        timestamp = timestamp,
                        hmackey = hmackey,
                        has_key = bool(key))

@swift.route('/share', methods=['GET', 'POST'])
@login_required
def share():
    import bitly_api

    object_path = request.args.get('path')
    method = 'GET'
    duration_for_seconds = 60*60*24
    expires = int(time() + duration_for_seconds)
    hmacpath = '/v1/AUTH_' + session.get('current_project_id') + '/' + object_path
    key = swift_account.getSecretKey()
    hmackey = calculateHMACSignatureShare(hmacpath, expires, method, key)

    shared_url = current_app.config['SWIFT_URL'] + hmacpath + '?temp_url_sig=' + hmackey + '&temp_url_expires=' + str(expires)
    b = bitly_api.Connection(current_app.config['BITLY_USERNAME'], current_app.config['BITLY_APIKEY'])
    bitlyURL = b.shorten(shared_url)

    
    flash('URL for object (Valid for 24 Hours): %s' % bitlyURL.get('url'))
    return redirect(url_for('swift.container', path=object_path[:object_path.rfind('/')+1]))


@swift.route('/create/container', methods=['GET', 'POST'])
@login_required
def create_container():
    form = CreateContainerForm()
    if form.validate_on_submit():
        if swift_account.getContainerMetadata(form.name.data):
            flash('Container already exists.')
        else:
            swift_account.createContainer(form.name.data)
            flash('Container ' + form.name.data + ' has been created.')
            return redirect(url_for('swift.account'))
    return render_template('/swift/create_container.html', form=form)

@swift.route('/create/folder', methods=['GET','POST'])
@login_required
def create_folder():
    form = CreateFolderForm()
    path = request.args.get('path')
    if form.validate_on_submit():
        upload_path = path + form.name.data + '/'
        if swift_account.folderExists(upload_path):
            flash('Folder already exists.')
        else:
            swift_account.createFolder(upload_path)
            flash('Folder ' + form.name.data + ' has been created.')
            return redirect(url_for('swift.container', path=path))
    return render_template('/swift/create_folder.html', form=form)

@swift.route('/bulkdelete', methods=['GET', 'POST'])
@login_required
def bulk_delete():
    path = request.args.get('next')
    checkbox_object_list = request.form.getlist("select_object_group")    
    bulk_delete_body = ""
    for checkbox in checkbox_object_list:
        bulk_delete_body += checkbox + '\n'
    swift_account.bulkDelete(bulk_delete_body)
    checkbox_folder_list = request.form.getlist('select_folder_group')
    for checkbox in checkbox_folder_list:
        swift_account.deleteObject(checkbox)
    return redirect(url_for('swift.container', path=path))

@swift.route('/overview')
@admin_required
def overview():
    content = swift_account.getOverview()
    health_status = swift_account.getHealthStatus()
    swift_details = content.get('swift')
    authentication_methods = [swift_authentication_methods.get(method) \
        for method in content.keys() if method in swift_authentication_methods]
    other_services = [service \
        for service in content.keys() if not service in swift_authentication_methods and service != 'swift']
    return render_template('/swift/admin/index.html', 
        swift_details=swift_details, 
        authentication_methods=authentication_methods, 
        other_services=other_services,
        health_status=health_status)

@swift.route('/limits')
@admin_required
def limits():
    content = swift_account.getOverview()
    return render_template('/swift/admin/limits.html', content=content)

@swift.route('/errors', methods=['GET', 'POST'])
@admin_required
def listErrors():
    import os
    from .. import basedir
    n = request.form.get('linestxt')
    if n is None:
        n = 10
    filename = os.path.join(basedir, 'errors.log')
    lines = readFile(path=filename, n=n)
    return render_template('/swift/admin/errors.html', lines=lines)