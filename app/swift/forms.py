from flask.ext.wtf import Form
from wtforms import FileField, HiddenField, SubmitField, StringField
from wtforms.validators import Required, Regexp, Length
from time import time
from ..userhmac import calculateHMACSignature

class CreateContainerForm(Form):
    name = StringField('Container Name', validators=[Required(), Length(1,20), Regexp("^[ A-Za-z0-9_]*$", 
                                                    message="Only alphanumeric characters, space and underscores are allowed")])
    submit = SubmitField('Submit')

class CreateFolderForm(Form):
    name = StringField('Folder Name', validators=[Required(), Length(1,20), Regexp("^[ A-Za-z0-9_]*$", 
                                                message="Only alphanumeric characters, space and underscores are allowed")])
    submit = SubmitField('Submit')

class SetSecretKeyForm(Form):
    key = StringField('Key', validators=[Required(), Length(5,10)])
    submit = SubmitField('Submit')