import pdb
import requests

from flask import Flask
from flask import render_template
from flask import request
from jhlearner import metadata_learner as ml

import random

# backend API
from crystal_api import GithubCrystalApi

# This must be last.
from interface import app

LABEL_MAP = {0: 'shadowsocks', 1: 'JUNK_TOPIC', 2: 'Jenkins', 3: 'iOS App', 4: 'Mustache', 5: 'Cozy', 6: 'iOS', 7: 'Administration', 8: 'Watchman', 9: 'Inter-process Communication', 10: 'Java', 11: 'JUNK_TOPIC', 12: '___', 13: 'State Machine', 14: 'Confluence', 15: 'CarrierWave', 16: 'Rails Database', 17: 'RSpec', 18: 'Machine Learning', 19: '___', 20: 'Zend', 21: 'Wordpress', 22: 'typeahead', 23: 'Chef', 24: '___', 25: '___', 26: '___', 27: 'Stocks', 28: 'Mobile Applications', 29: 'WebGL/WebVR', 30: '___', 31: 'YouTube', 32: 'DevTools', 33: 'Discourse', 34: 'Game Deployment', 35: '___', 36: '___', 37: 'Shopify', 38: '___', 39: '___', 40: 'Media Player', 41: 'Composer', 42: 'Sinatra', 43: '___', 44: 'JUNK_TOPIC', 45: 'JUNK_TOPIC', 46: '___', 47: 'Ubuntu', 48: '___', 49: '___', 50: 'Database', 51: 'Currency', 52: '___', 53: 'Sphinx', 54: '___', 55: 'Sidekiq', 56: '___', 57: '___', 58: 'Django', 59: '___', 60: 'Creative Commons', 61: '___', 62: 'KeystoneJS', 63: 'Awesome', 64: 'Ghost', 65: 'Themes', 66: 'jsdom/Gunicorn', 67: '___', 68: '___', 69: 'Form Validation', 70: '___', 71: 'PHPUnit', 72: '___', 73: 'Asynchronous Messaging', 74: 'Minecraft', 75: 'Analytics', 76: 'Web Library', 77: 'Segmentation', 78: 'CSS Animation', 79: 'JUNK_TOPIC', 80: '___', 81: '___', 82: 'Xero', 83: '___', 84: 'Puppet', 85: '___', 86: 'Drupal', 87: 'JUNK_TOPIC', 88: 'JUNK_TOPIC', 89: 'Custom Fields', 90: '___', 91: '___', 92: '___', 93: 'Component', 94: 'Institutional Repository', 95: 'JUNK_TOPIC', 96: 'AWS', 97: 'Eclipse', 98: 'ShowdownJS', 99: '___', 100: 'Cards', 101: '___', 102: '___', 103: '___', 104: '___', 105: 'Chinese', 106: '___', 107: '___', 108: '___', 109: '___', 110: '___', 111: '___', 112: '___', 113: 'Microsoft', 114: '___', 115: '___', 116: 'PHP', 117: '___', 118: '___', 119: 'JUNK_TOPIC', 120: 'Data Mining', 121: 'ClojureScript', 122: 'Rails', 123: 'Cloud Foundry', 124: 'JUNK_TOPIC', 125: 'Base Boxes', 126: 'PhantomJS', 127: 'FuelUX', 128: 'Text', 129: '___', 130: '___', 131: 'Spreadsheet', 132: '___', 133: 'Meteor', 134: 'JUNK_TOPIC', 135: '___', 136: 'MySQL', 137: '___', 138: 'Encrpytion', 139: 'Networking', 140: '___', 141: 'Vim', 142: 'Workflow', 143: '___', 144: 'Nginx', 145: 'Infrastructure Monitoring', 146: 'JUNK_TOPIC', 147: '___', 148: '___', 149: '___', 150: 'MIT License', 151: 'JUNK_TOPIC', 152: '___', 153: '___', 154: 'NodeJS', 155: 'Algorithms', 156: 'HHVM', 157: '___', 158: 'Spanish', 159: '___', 160: 'Autocomplete/Suggestions', 161: '___', 162: 'Scheduler', 163: 'Game Development', 164: 'Lua', 165: 'Pricing', 166: '___', 167: 'Parser', 168: 'EmberJS', 169: 'Image Caching', 170: 'Yii', 171: '___', 172: '___', 173: 'Emacs', 174: 'Mobile Device Detection', 175: 'Apache License', 176: 'Authentication/Authorization', 177: 'Kitchenplan', 178: 'Concurrent Programming', 179: 'CSS', 180: 'Image', 181: 'Arduino', 182: 'AngularJS', 183: 'JUNK_TOPIC', 184: '___', 185: 'Oscar', 186: 'Guard', 187: 'Music', 188: 'TextMate', 189: 'Datepicker', 190: 'Color Palette', 191: 'Cloudinary', 192: 'GNOME Extension', 193: 'Sitemap Generator', 194: 'Cordova', 195: 'Nexus', 196: '___', 197: '___', 198: 'UI', 199: 'Templating', 200: '___', 201: 'Java', 202: '___', 203: 'Kernel', 204: 'Contacts', 205: 'Deployment', 206: 'XPrivacy', 207: 'Build System', 208: 'Mobile', 209: 'RevealJS', 210: 'Erlang', 211: 'Fake Data', 212: '___', 213: '___', 214: 'Server Tools', 215: '___', 216: 'Spanish', 217: 'Perl Code/Module', 218: 'Rails', 219: 'SilverStripe', 220: 'Bootstrap', 221: '___', 222: 'PHPMailer', 223: 'Twitter', 224: 'Feeds', 225: '___', 226: 'Web API', 227: 'Readmine', 228: 'Events', 229: '___', 230: 'Android', 231: '___', 232: 'JavaScript', 233: 'Samples', 234: 'JUNK_TOPIC', 235: '___', 236: 'Selenium', 237: 'iOS', 238: 'iOS', 239: 'JUNK_TOPIC', 240: 'RESTful Web Service', 241: '___', 242: 'Game Development', 243: 'TrinityCore', 244: '___', 245: 'Relational Database', 246: 'Firewall', 247: 'Riak', 248: 'SaltStack', 249: '___', 250: '___', 251: '___', 252: 'Swagger UI', 253: 'Torrent Clients', 254: 'Gradle', 255: 'CoffeeScript', 256: 'Distributed Computing', 257: '___', 258: '___', 259: 'Flask', 260: '___', 261: 'Concurrent Programming', 262: '___', 263: 'JUNK_TOPIC', 264: 'NodeJS', 265: '___', 266: 'Python', 267: '___', 268: '___', 269: 'Application Framework', 270: 'French', 271: 'Fog/Nokogiri', 272: 'ServiceStack', 273: 'Bitcoin Mining', 274: 'Templating', 275: 'Energy', 276: 'JavaScript', 277: 'openSUSE', 278: '___', 279: 'Logging', 280: 'Octopress', 281: 'GulpJS', 282: 'CodeIgniter', 283: 'iPython', 284: 'SlidingMenu', 285: 'Trinea', 286: 'WebRTC', 287: '___', 288: '___', 289: 'Docker', 290: 'BackboneJS', 291: 'JUNK_TOPIC', 292: 'IntroJS', 293: 'Sublime', 294: 'Job Creation/Queuing', 295: 'MomentJS', 296: 'JUNK_TOPIC', 297: 'SVN/SVM', 298: 'NodeJS', 299: 'Rendering', 300: '___', 301: 'JUNK_TOPIC', 302: 'Plugin', 303: 'Markup Language', 304: '___', 305: '___', 306: 'eAccelerator', 307: '___', 308: 'Encrpytion', 309: 'Templating', 310: 'Game Development', 311: '___', 312: 'Mozilla', 313: 'Redis', 314: 'Clojure', 315: 'memcached', 316: 'SQL', 317: '___', 318: 'Gitflow', 319: '___', 320: 'JavaScript Library', 321: 'JUNK_TOPIC', 322: 'jQuery', 323: 'Internet Currency', 324: 'NuGet', 325: 'Subscriptions', 326: 'JUNK_TOPIC', 327: 'JUNK_TOPIC', 328: 'Email', 329: '___', 330: '___', 331: 'Icons', 332: 'Authentication/Authorization', 333: '___', 334: '___', 335: 'Progress Monitoring', 336: '___', 337: 'Languages', 338: 'GruntJS', 339: 'Database', 340: 'JUNK_TOPIC', 341: '___', 342: '___', 343: '___', 344: '___', 345: 'Elasticsearch', 346: '___', 347: 'developerWorks', 348: '___', 349: 'skrollr', 350: 'SockJS', 351: 'Active Record Ruby Model', 352: 'Grails', 353: 'Paperclip', 354: 'Errbit', 355: 'Elixir', 356: 'git', 357: 'GNU GPL', 358: 'TimelineJS', 359: '___', 360: 'Scala', 361: '___', 362: 'JUNK_TOPIC', 363: '___', 364: 'Processes', 365: '___', 366: 'Strings', 367: 'Data Management', 368: '___', 369: 'Evernote', 370: 'Kubernetes', 371: 'Event-Processing', 372: 'Symfony', 373: 'Rails Tutorial', 374: 'Image Loading Detection', 375: 'Apache', 376: 'Commit', 377: 'Distributed Monitoring', 378: 'Skins', 379: 'Android Canvas', 380: 'RestKit', 381: 'MorrisJS', 382: 'Cassandra', 383: 'Scrolling', 384: '___', 385: 'HTML Styling/Markup', 386: 'Asset Packaging', 387: 'Boxen', 388: '___', 389: 'Calendar', 390: 'jQuery Uploads', 391: 'Monitoring', 392: 'Jekyll', 393: 'Prototyping', 394: 'Charts', 395: 'Distributed Communication', 396: 'Rack Middleware', 397: 'Distributed Computing', 398: 'Key-Value Store', 399: '___', 400: '___', 401: 'Scrolling', 402: 'IPython', 403: 'CakePHP', 404: 'Adafruit', 405: '___', 406: 'Ruby Gem', 407: 'Analytics', 408: 'Eclipse', 409: 'Content Management', 410: 'Messaging', 411: 'GNU GPL', 412: 'Spatial/Geographic Objects', 413: 'JUNK_TOPIC', 414: 'PDF', 415: 'Image Caching', 416: 'Color Scheme', 417: 'Ads', 418: 'Checkboxes / Radio Buttons', 419: 'Content Management', 420: 'Maven', 421: 'Plataformatec/Zxing', 422: 'Content Repository', 423: 'Baidu', 424: 'Editor', 425: 'Rails', 426: 'SQL', 427: 'Bots', 428: 'AngularJS', 429: 'Bitcoin', 430: 'Email', 431: 'JavaScript Library', 432: '___', 433: 'Web Browser Automation', 434: '___', 435: 'Mobile', 436: 'Payments', 437: 'Java', 438: 'MongoDB', 439: 'Dart', 440: 'Push Notifications', 441: '___', 442: 'Spring Integration', 443: '___', 444: 'jQuery Slider', 445: 'Configuration', 446: 'Markdown', 447: 'Localization', 448: 'Grid Layout', 449: 'Plugins', 450: 'Science', 451: 'Android', 452: '___', 453: 'DevArt', 454: 'Text', 455: 'Timezone', 456: 'datepicker', 457: 'Backup Software', 458: 'Teaspoon', 459: 'Android', 460: 'Appcelerator Titanium', 461: 'Maps', 462: 'Game Development', 463: 'Facebook', 464: 'Gradle', 465: 'JUNK_TOPIC', 466: 'CKEditor', 467: 'Mongoose', 468: 'OpenShift', 469: 'IntelliJ IDEA', 470: 'Sequencing', 471: 'Exercises', 472: 'PHP Package Management', 473: 'PHP Package Management', 474: 'Terminal', 475: 'Photos', 476: 'Questions', 477: 'Drivers', 478: 'Data Storage', 479: 'Swiping', 480: 'Roles', 481: 'Preprocessor', 482: 'Heroku', 483: 'iPhone Development', 484: 'Cordova', 485: 'Spring', 486: 'JUNK_TOPIC', 487: 'Vagrant', 488: 'JUNK_TOPIC', 489: 'Gist', 490: 'Sensu', 491: 'Proxy', 492: 'RPC', 493: 'Ansible', 494: 'Crowbar', 495: 'Berkshelf', 496: 'ExpressJS', 497: 'Phalcon', 498: 'Channels', 499: 'Database'}

@app.route("/")
def main(name=None):
    api = GithubCrystalApi()

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

# def update_repos_url_input(similar_repos):
#   # INSTEAD OF USING THE STORED DATA FOR SIMILAR REPOS, WE CAN JUST REQUEST THE NEW DATA
#   # AS LONG AS WE HAVE THE URLS TO THE SIMILAR REPOS

#   updated_repos = []
#   for repo in similar_repos:
#     repo_url = repo[0].strip()
#     new_repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])

#     updated_repo = {
#       'repo_url': repo_url,
#       'similarity': repo[1],
#       'days_active': repo.get('days_active', 0),
#       'full_name': new_repo.get('full_name', ''),
#       'description': new_repo.get('description', ''),
#       'repo_size': new_repo.get('repo_size', 0),
#       'issues_count': new_repo.get('issues_count', 0),
#       'stars_count': new_repo.get('stars_count', 0),
#       'forks_count': new_repo.get('forks_count', 0),
#       'watchers_count': new_repo.get('watchers_count', 0)
#     }

#     updated_repos.append(updated_repo)
#   return updated_repos

def update_repos_keyword_input(similar_repos):
  # INSTEAD OF USING THE STORED DATA FOR SIMILAR REPOS, WE CAN JUST REQUEST THE NEW DATA
  # AS LONG AS WE HAVE THE URLS TO THE SIMILAR REPOS

  updated_repos = []
  for repo in similar_repos:
    repo_url = repo[0].strip()
    # pdb.set_trace()
    new_repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])

    updated_repo = {
      'repo_url': repo_url,
      'similarity': "{0:.2f}".format(repo[1]),
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

def update_repos_tags_input(similar_repos):
  # INSTEAD OF USING THE STORED DATA FOR SIMILAR REPOS, WE CAN JUST REQUEST THE NEW DATA
  # AS LONG AS WE HAVE THE URLS TO THE SIMILAR REPOS

  updated_repos = []

  for repo in similar_repos:
    repo_url = repo.strip()

    new_repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])

    updated_repo = {
      'repo_url': repo_url,
      'similarity': 'N/A',
      'days_active': 'N/A',
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
  api = GithubCrystalApi()
  keyword = request.args.get('keyword', '')
  is_code_only = request.args.get('codeonly', 0)

  # repo_url = request.args.get('repo_url', '')
  tags = request.args.get('tags', '')
  repo, similar_repos = None, []

  # if repo_url:
  #   if repo_url.endswith('/'):
  #     repo_url = repo_url[0:len(repo_url)-1]

  #   if (repo_url.find("github.com/") > -1): #URL AS INPUT
  #     repo = ml.get_repo(repo_url, app.config["GITHUB_ID"], app.config["GITHUB_PW"])
  #     similar_repos = api.get_similar_repos_by_lucene(repo.get('readme_content', ''))


  if keyword:
    similar_repos = []
    num_trys = 0


    while (len(similar_repos) < 1) and num_trys < 10:
      if is_code_only:
        similar_repos = api.get_similar_repos_by_lucene(keyword, show_non_repos=False)[:10]
      else:
        similar_repos = api.get_similar_repos_by_lucene(keyword)[:10]

    similar_repos = update_repos_keyword_input(similar_repos)

  elif tags: # TOPICS AS INPUT
    similar_repos = []

    #FIXME: add in time constraint to prevent infinite loop
    num_trys = 0
    while (len(similar_repos) < 1) and num_trys < 10:
      num_trys += 1
      topics = tags.split(",")
      num_topics = len(topics)
      topic_weight = 1.0/num_topics
      weight_init = 0.85
      query_arr = []
      for topic_idx, topic in enumerate(topics):
        topic_weight = random.uniform(0, weight_init)
        weight_init = weight_init - topic_weight
        query = ("", topic_weight, topic)
        query_arr.append(query)      
      similar_repos = api.get_similar_repos_by_topic(query_arr)

    similar_repos = update_repos_tags_input(similar_repos[:10])  

  else:
    repo, similar_repos = None, []

  if (tags):
    topics = [LABEL_MAP[int(topic)] for topic in topics]
    return render_template('analysis_tags.html',
      tags=topics,
      similar_repos=similar_repos
    )

  elif keyword and not (keyword.find("//github.com") > 0):
    keyword = keyword.split(" ")
    return render_template('analysis_keyword.html',
      keyword=keyword,
      similar_repos=similar_repos
    )

  else:
    return render_template('analysis_keyword.html',
      repo_url=repo_url, 
      watchers_count=repo.get('watchers_count', 0),
      forks_count=repo.get('forks_count', 0),
      stars_count=repo.get('stars_count', 0),
      issues_count=repo.get('issues_count', 0),
      repo_size=repo.get('repo_size', 0),
      full_name=repo.get('full_name', ''),
      description=repo.get('description', ''),
      tokens=repo.get('tokens', ''),
      similar_repos=similar_repos
    )