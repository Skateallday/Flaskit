from wtforms import Form, StringField, SelectField, PasswordField
from flask_wtf import Form
from wtforms.validators import DataRequired, length, Email, EqualTo

class UserSearchForm(Form):
    choices = [('username')]
    SelectField = SelectField('Search users:', choices= choices)
    search = StringField('')
