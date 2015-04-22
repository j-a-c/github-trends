Steps to run the app:


1. create ./settings.cfg

# Example configuration
DEBUG = True
GITHUB_ID = 'sdf'
GITHUB_PW = 'sdf'

2. export the setting

$export FLASK_SETTINGS=./settings.cfg

3. run the app

$python app.py