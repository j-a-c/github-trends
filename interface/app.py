from flask import Flask
from flask import render_template
from flask import request
from jhlearner import metadata_learner as ml
import requests
import pdb

app = Flask(__name__)
# app.config.from_object('app.default_settings')
app.config.from_envvar('FLASK_SETTINGS')

@app.route("/")
def main(name=None):
    return render_template('main.html', name=name)

def update_repos(similar_repos):
  # INSTEAD OF USING THE STORED DATA FOR SIMILAR REPOS, WE CAN JUST REQUEST THE NEW DATA
  # AS LONG AS WE HAVE THE URLS TO THE SIMILAR REPOS

  updated_repos = []
  for repo in similar_repos:
    repo_url = repo.get('repo_url', '').strip()
    new_repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])

    updated_repo = {
      'repo_url': repo_url,
      'similarity': repo.get('similarity', 0),
      'days_active': repo.get('days_active', 0),
      'full_name': new_repo.get('full_name', ''),
      'description': new_repo.get('description', ''),
      'repo_size': new_repo.get('repo_size', 0),
      'issues_count': new_repo.get('issues_count', 0),
      'stars_count': new_repo.get('stars_count', 0),
      'forks_count': new_repo.get('forks_count', 0),
      'watchers_count': new_repo.get('watchers_count', 0)
    }

    updated_repos.append(updated_repo)
  return updated_repos

@app.route("/analysis")
def analysis():
  repo_url = request.args.get('repo_url', '')

  if not repo_url:
    repo_url = 'https://github.com/j-a-c/github-trends'

  similar_repos = []

  if repo_url.endswith('/'):
    repo_url = repo_url[0:len(repo_url)-1]

  if repo_url:
    repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])
    similar_repos = ml.learn(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])
    similar_repos = update_repos(similar_repos) # update the code later: on-the-fly information?
  else:
    repo, similar_repos = None, []

  return render_template('analysis.html',
    repo_url=repo_url, 
    watchers_count=repo.get('watchers_count', 0),
    forks_count=repo.get('forks_count', 0),
    stars_count=repo.get('stars_count', 0),
    issues_count=repo.get('issues_count', 0),
    repo_size=repo.get('repo_size', 0),
    full_name=repo.get('full_name', ''),
    description=repo.get('description', ''),
    # readme_content=repo.get('readme_content', ''),
    tokens=repo.get('tokens', ''),
    similar_repos=similar_repos
  )

if __name__ == "__main__":
  app.run(debug=True)


# auth=(app.config["GITHUB_USER"], app.config["GITHUB_PW"]))