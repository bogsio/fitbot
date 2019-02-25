import json
from pprint import pprint

import requests
from django.utils.timezone import now

from django.conf import settings
from fitbot.utils import MessengerEvent


class Meals:
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    SNACK = 'snack'


class States:
    WAITING_FOR_MEAL_PHOTO = 'WAITING_FOR_MEAL_PHOTO'
    WAITING_FOR_MEAL_COMMENTS = 'WAITING_FOR_MEAL_COMMENTS'
    COMPLETE_MEAL_LOG = 'COMPLETE_MEAL_LOG'


PB_TO_MEAL_TYPES = {
    'LOG_BREAKFAST': Meals.BREAKFAST,
    'LOG_LUNCH': Meals.LUNCH,
    'LOG_DINNER': Meals.DINNER,
    'LOG_SNACK': Meals.SNACK
}


class Chatbot(object):
    def __init__(self, person):
        self._person = person

    def send_text(self, text, quick_replies=None):
        """

        :param text: plain text string
        :param quick_replies: [(display1, postback1), ...]
        :return:
        """
        uri = "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % settings.FB_ACCESS_TOKEN
        data = {
            # 'messaging_type': 'RESPONSE',
            'recipient': {'id': self._person.fb_id},
            'message': {'text': text}
        }

        if quick_replies is not None:
                data['message']['quick_replies'] = [
                    {
                        'content_type': "text",
                        'title': qr[0],
                        'payload': qr[1],

                    } for qr in quick_replies
                ]
        # print("Posting to", uri)
        print("\n\n")
        print("Outgoing data")
        print("======================")
        pprint(data)
        print("======================")
        response = requests.post(uri, data=json.dumps(data), headers={'content-type': 'application/json'})
        # print(response.status_code)
        # print(response.content)

    def handle(self, event):
        assert isinstance(event, MessengerEvent)
        if event.has_postback():
            pb = event.get_postback()

            if pb in PB_TO_MEAL_TYPES.keys():
                self.handle_log_meal(event)

            elif pb == 'SKIP_PHOTO':
                self.handle_skip_photo(event)

            elif pb == 'SKIP_COMMENTS':
                self.handle_skip_comments(event)

        elif event.is_message():
            if self._person.state_name == States.WAITING_FOR_MEAL_PHOTO:
                self.handle_meal_photo(event)

            elif self._person.state_name == States.WAITING_FOR_MEAL_COMMENTS:
                self.handle_meal_comments(event)

    def handle_meal_photo(self, event):
        assert self._person.state_name == States.WAITING_FOR_MEAL_PHOTO
        if not event.has_images():
            self.send_text("Sorry, I didn't get that ... Please upload a picture and/or write a description")
            return

        images = event.get_images()
        image_url = images[0]['payload']['url']
        self._person.state_name = States.WAITING_FOR_MEAL_COMMENTS
        self._person.state_params['image'] = image_url
        self._person.save()

        self.send_text("Ok, tell me a bit about your meal",
                       quick_replies=[('Skip Comments', 'SKIP_COMMENTS')])


    def handle_meal_comments(self, event):
        assert self._person.state_name == States.WAITING_FOR_MEAL_COMMENTS

        if not event.has_text():
            self.send_text("Sorry, I didn't get that ... ")
            return

        text = event.get_text()
        self._person.state_params['comments'] = text
        self._person.save()
        self.complete_meal(event)


    def handle_skip_photo(self, event):
        if self._person.state_name == States.WAITING_FOR_MEAL_PHOTO:
            self.send_text("Ok, tell me a bit about your meal",
                       quick_replies=[('Skip Comments', 'SKIP_COMMENTS')])

            self._person.state_name = States.WAITING_FOR_MEAL_COMMENTS
            self._person.save()

    def handle_skip_comments(self, event):
        if self._person.state_name == States.WAITING_FOR_MEAL_COMMENTS:
            self._person.state_name = States.COMPLETE_MEAL_LOG
            self._person.save()
            self.complete_meal(event)

    def handle_log_meal(self, event):
        pb = event.get_postback()
        params = {'type': PB_TO_MEAL_TYPES[pb], 'date': str(now().date())}
        state = States.WAITING_FOR_MEAL_PHOTO
        self._person.state_name = state
        self._person.state_params = params
        self._person.save()
        self.send_text("Great, let's do that, just snap a picture of your food",
                       quick_replies=[('Skip Photo', 'SKIP_PHOTO')])

    def complete_meal(self, event):
        meal = self._person.save_meal()
        self.send_text("Done! Keep up the good work!")





