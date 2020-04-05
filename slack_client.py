import requests
import json
import logging
from auth import DEFAULT_SLACK_WEBHOOK
from auth import DEFAULT_SLACK_WEBHOOK2

HEADERS = {
    'Content-type': 'application/json'
}


def slacker(webhook_url=DEFAULT_SLACK_WEBHOOK):
    def slackit(msg):
        logging.info('Sending {msg} to slack'.format(msg=msg))
        payload = { 'text': msg }
        requests.post(DEFAULT_SLACK_WEBHOOK2, headers=HEADERS, data=json.dumps(payload))
        return requests.post(webhook_url, headers=HEADERS, data=json.dumps(payload))
    return slackit