from flask import Flask
import os
import pdb

app = Flask(__name__)

# app.config.from_envvar('FLASK_SETTINGS')

try:
    os.environ["FLASK_SETTINGS"] = "./settings.cfg"
    app.config.from_envvar('FLASK_SETTINGS')
    #pdb.set_trace()
except:
    with open('github.creds') as f:
        credentials = f.read().strip().split(',')
        app.config['GITHUB_ID'] = credentials[0]
        app.config['GITHUB_PW'] = credentials[1]

from app import *