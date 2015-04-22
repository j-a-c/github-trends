from wtforms import Form
from wtforms import TextField

class LoginForm(Form):
    url = TextField('url')
