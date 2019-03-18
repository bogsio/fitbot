from datetime import datetime
import io
import os
import json
from pathlib import Path

import requests
from snips_nlu import SnipsNLUEngine
from snips_nlu.default_configs import CONFIG_EN
from django.conf import settings

nlu = None


SLOT_TRANSFORMERS = {
    'snips/datetime': lambda value: datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')
}

# if not os.path.exists(f"fitbot/nlu_models/{settings.TRAIN_FILE}.model"):
with io.open(f"fitbot/datasets/{settings.TRAIN_FILE}") as f:
    data = f.read().replace('\ufeff', '')
    dataset = json.loads(data)
    nlu = SnipsNLUEngine(config=CONFIG_EN)
    nlu.fit(dataset)
    nlu.parse("I ate some bread with butter for breakfast")
        # nlu.persist(f"fitbot/nlu_models/{settings.TRAIN_FILE}.model")
        # nlu.persist_metadata(Path(f"fitbot/nlu_models/{settings.TRAIN_FILE}.model"))
# else:
#     nlu = SnipsNLUEngine.load_from_path(Path(f"fitbot/nlu_models/{settings.TRAIN_FILE}.model"))


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
        self._nlu_result = None

    @staticmethod
    def fetch_nlu_data(text):
        # text_input = dialogflow.types.TextInput(text=text, language_code='en')
        # query_input = dialogflow.types.QueryInput(text=text_input)
        # response = session_client.detect_intent(
        #     session=session, query_input=query_input)
        #
        # print(response)
        # print(response.intent)
        # print(response.entities)
        if nlu is not None:
            p = nlu.parse(text)
            print(p)

    @property
    def nlu_result(self):
        if self._nlu_result is None:
            if not self.has_text():
                return

            text = self.get_text()
            if not text:
                return

            self._nlu_result = nlu.parse(text)
        return self._nlu_result


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

    def has_intent(self):
        if self.nlu_result is not None:
            return self.nlu_result['intent']['intentName'] is not None
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

    def get_intent(self):
        if not self.has_intent():
            return None

        return self.nlu_result['intent']['intentName']

    def get_entities(self):
        if self.nlu_result is None:
            return {}

        entities_ = {}
        for slot in self.nlu_result['slots']:
            type_ = slot['entity']
            value_ = slot['value']['value']
            slot_ = slot['slotName']

            if type_ in SLOT_TRANSFORMERS:
                value_ = SLOT_TRANSFORMERS[type_](value_)

            entities_[slot_] = value_

        return entities_

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




