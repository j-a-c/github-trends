from flask import Flask

app = Flask(__name__)

try:
    # app.config.from_object('app.default_settings')
    app.config.from_envvar('FLASK_SETTINGS')
except:
    with open('github.creds') as f:
        credentials = f.read().strip().split(',')
        app.config['GITHUB_ID'] = credentials[0]
        app.config['GITHUB_PW'] = credentials[1]

from app import *