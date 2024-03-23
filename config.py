import json

DB_CONFIG = {
    'username': '',
    'password': '',
    'database' : '',
    'host': '',
}

OPEN_AI_KEY = ''


with open("secret.json", 'r') as file:
    data = json.load(file)

    DB_CONFIG['username'] = data['username']
    DB_CONFIG['password'] = data['password']
    DB_CONFIG['database'] = data['database']
    DB_CONFIG['host'] = data['host']

    OPEN_AI_KEY = data['openai_key']


