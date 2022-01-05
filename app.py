import requests
import os
import sys
import json
from datetime import datetime, timedelta
import time
import dotenv
import traceback


def log(obj, log_type="info"):
    obj["type"] = log_type
    print(json.dumps(obj))


def info(msg, obj=None):
    if not obj:
        obj = {}
    obj['message'] = msg
    log(obj, log_type='info')


def error(msg, obj=None):
    if not obj:
        obj = {}
    obj['error'] = msg
    log(obj, log_type='error')


dotenv.load_dotenv()
host = os.getenv('host', 'https://api.smtp2go.com/v3')
apikey = os.getenv('apikey')
query_interval = int(os.getenv('query_interval', 30 * 60))
if not apikey:
    error("No API Key defined by environment variable 'apikey'!")
    exit(1)


def api(path, json):
    json['api_key'] = apikey
    res = requests.post(host + path, json=json)
    rjson = res.json()
    if res.status_code != 200 or (rjson.get('data') and rjson['data'].get('error')):
        error('Error during API request', {
            'request': {
                'path': path,
                'json': json
            },
            'response': {
                'status_code': res.status_code,
                'json': rjson
            }
        })
        return None
    return rjson


def query_activity(after=None):
    # https://apidoc.smtp2go.com/documentation/#/POST%20/activity/search
    """
    after = only show events after this ISO-8601 string date time format, can be None to search all events.
    """
    json = {
        'limit': 100,  # 100 is max
        'only_latest': False
    }
    if after:
        # start_date is inclusive, so add a second to search after. Second is smallest increment we can add
        after = after + timedelta(seconds=1)
        json['start_date'] = after.isoformat() + 'Z'
    res = api('/activity/search', json)
    events = res['data']['events']
    while res.get('continue_token'):
        json['continue_token'] = res['continue_token']
        res = api('/activity/search', json)
        events += res['data']['events']
    return events


def save_after(after):
    with open('/config/last_event.isoformat', 'w') as file:
        file.write(after.isoformat())


if __name__ == '__main__':
    info('Starting smtp2go activity monitor', {'host': host, 'query_interval': query_interval})
    after = datetime(1970, 1, 1)
    if os.path.isfile('/config/last_event.isoformat'):
        with open('/config/last_event.isoformat') as file:
            after = datetime.fromisoformat(file.read())
            info('Found /config/last_event.isoformat', {'after': after.isoformat()})
    while True:
        try:
            events = query_activity(after=after)
            for event in events:
                log({'event': event}, log_type='email')
                after = max(after, datetime.fromisoformat(event['date'].replace('Z', '')))
            save_after(after)
        except Exception as e:
            error('Runtime exception', {'error object': repr(e), 'stacktrace': traceback.format_exc()})
        time.sleep(query_interval)
log(query_activity())
