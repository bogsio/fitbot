import json
import requests
from django.conf import settings


def get_messenger_profile():
    FIELDS = [
        'account_linking_url',
        'persistent_menu',
        'get_started',
        'greeting',
        'whitelisted_domains',
        'payment_settings',
        'target_audience',
        'home_url'
    ]
    URL = f'https://graph.facebook.com/v2.6/me/messenger_profile?fields={",".join(FIELDS)}&access_token={settings.FB_ACCESS_TOKEN}'

    return json.loads(requests.get(URL).content)


def set_messenger_profile(field, value):
    URL = f'https://graph.facebook.com/v2.6/me/messenger_profile?access_token={settings.FB_ACCESS_TOKEN}'

    data = {
        field: value,
    }

    return json.loads(requests.post(URL, data=json.dumps(data), headers={'content-type': 'application/json'}).content)


def set_persistent_menu(menu):
    return set_messenger_profile('persistent_menu', menu)


def set_get_started(get_started):
    return set_messenger_profile('get_started', get_started)
