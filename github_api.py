import json
import os
import requests

token = os.environ.get('GITHUB_TOKEN')
gist_id = '0e20ac005990555d9e7a761b078e084c'

def read_database():
    """Returns Python dictionary"""
    r = requests.get("https://api.github.com/gists/{}".format(gist_id), auth=('OrkoHunter', token))
    data = r.json()['files']['database.json']['content']
    return json.loads(data)

def write_database(data):
    """Takes python dictionary
    Returns status code
    """
    options = {
        'files': {
            'database.json': {
                'content': json.dumps(data)
            }
        }
    }
    r = requests.patch("https://api.github.com/gists/{}".format(gist_id), auth=('OrkoHunter', token), json=options)

    return r.status_code  # Should be 200
