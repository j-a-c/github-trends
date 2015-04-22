import base64

from flask import redirect, render_template, request, url_for
from utils import download_readme

# Keep this last.
from app import app

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print 'posting'
        if request.form['submit'] == 'Find Similar':
            repo_url = request.form.get('repo_url')
            
            # Sample URL
            # https://github.com/j-a-c/github-trends
            
            # TODO better error handling.
            base_64_repo_url = base64.b64encode(repo_url)
            return redirect('similar/' + base_64_repo_url)
    return render_template('index.html', title='Home')
    
@app.route('/similar/<base_64_repo_url>/')
def find_similar(base_64_repo_url):
    orig_url = base64.b64decode(base_64_repo_url)
    original_readme = download_readme(orig_url)
    similar_repos = ['test']
    return render_template('similar.html', title='Similar repositories', original_readme=original_readme, similar_repos=similar_repos)