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


def init_messenger_profile(**kwargs):
    URL = f'https://graph.facebook.com/v2.6/me/messenger_profile?access_token={settings.FB_ACCESS_TOKEN}'
    return json.loads(requests.post(URL, data=json.dumps(kwargs), headers={'content-type': 'application/json'}).content)


class MessengerEvent(object):
    def __init__(self, event):
        """
        Example event
        {'id': '210835912375384',
            'messaging': [{'postback': {'payload': 'LOG_BREAKFAST',
                                        'title': 'Breakfast'},
                           'recipient': {'id': '210835912375384'},
                           'sender': {'id': '2184528808238067'},
                           'timestamp': 1551041045880}],
            'time': 1551041045880}

        :param event: The Facebook Messenger json
        """
        self._event = event

    def has_postback(self):
        try:
            _ = self._event['messaging'][0]['postback']
            return True
        except:
            pass

        try:
            _ = self._event['messaging'][0]['message']['quick_reply']
            return True
        except:
            pass

        return False

    def has_message(self):
        try:
            _ = self._event['messaging'][0]['message']
            return True
        except:
            return False

    def has_text(self):
        try:
            _ = self._event['messaging'][0]['message']['text']
            return True
        except:
            return False

    def has_attachments(self):
        try:
            _ = self._event['messaging'][0]['message']['attachments'][0]
            return True
        except:
            return False

    def has_images(self):
        try:
            attachments = self._event['messaging'][0]['message']['attachments']
            return any([a['type'] == 'image' for a in attachments])
        except:
            return False

    def get_postback(self):
        if not self.has_postback():
            return None

        try:
            return self._event['messaging'][0]['postback']['payload']
        except:
            return self._event['messaging'][0]['message']['quick_reply']['payload']

    def get_text(self):
        if not self.has_message():
            return None

        return self._event['messaging'][0]['message']['text']

    def get_nlp(self):
        if not self.has_text():
            return {}

        return self._event['messaging'][0]['message'].get('nlp', {})

    def get_attachments(self):
        if not self.has_attachments():
            return []
        return self._event['messaging'][0]['message']['attachments']

    def get_images(self):
        if not self.has_images():
            return []
        return [a for a in self.get_attachments() if a['type'] == 'image']

    def get_sender(self):
        return self._event['messaging'][0]['sender']['id']




