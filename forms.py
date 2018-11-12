from wtforms import Form, StringField, SelectField
class UserSearchForm(Form):
    choices = [('username')]
    SelectField = SelectField('Search users:', choices= choices)
    search = StringField('')