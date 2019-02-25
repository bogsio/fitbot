import json
from pprint import pprint

import requests
from django.utils.timezone import now

from django.conf import settings

from fitbot.models import Person
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


class PostBacks:
    SKIP_COMMENTS = "SKIP_COMMENTS"
    SKIP_PHOTO = "SKIP_PHOTO"

    LOG_BREAKFAST = "LOG_BREAKFAST"
    LOG_LUNCH = "LOG_LUNCH"
    LOG_DINNER = "LOG_DINNER"
    LOG_SNACK = "LOG_SNACK"


PB_TO_MEAL_TYPES = {
    PostBacks.LOG_BREAKFAST: Meals.BREAKFAST,
    PostBacks.LOG_LUNCH: Meals.LUNCH,
    PostBacks.LOG_DINNER: Meals.DINNER,
    PostBacks.LOG_SNACK: Meals.SNACK
}


class Chatbot(object):

    _handlers = []

    @property
    def handlers(self):
        return self._handlers

    @classmethod
    def send_text(cls, person, text, quick_replies=None):
        """

        :param text: plain text string
        :param quick_replies: [(display1, postback1), ...]
        :return:
        """
        uri = "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % settings.FB_ACCESS_TOKEN
        data = {
            # 'messaging_type': 'RESPONSE',
            'recipient': {'id': person.fb_id},
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

    @classmethod
    def register_handler(cls, **conditions):
        """ Decorator for registering a chatbot handler """
        def wrapper(handler):
            cls._handlers.append((conditions, handler))

        return wrapper

    @classmethod
    def check_condition(cls, person, event, condition_name, condition_value):
        chunks = condition_name.split("__")
        if chunks[0] == 'context':
            if condition_name[1] == 'contains':
                return condition_value in person.context

        if len(chunks) == 1:
            chunks.append('')

        if chunks[0] == 'postback':
            if not event.has_postback():
                return False

            pb = event.get_postback()

            if chunks[1] == 'eq':
                return pb == condition_value

            if chunks[1] == 'in':
                return pb in condition_value

        if chunks[0] == 'message':
            if not event.has_message():
                return False

            if chunks[1] == 'eq':
                return event.get_message() == condition_value

            if chunks[1] == '':
                return condition_value

        if chunks[0] == 'state':
            if chunks[1] == 'eq':
                return person.state == condition_value

            if chunks[1] == 'in':
                return person.state in condition_value

    def handle(self, person, event):
        assert isinstance(event, MessengerEvent)
        assert isinstance(person, Person)

        best_handler, best_score = None, -1

        for conditions, handler in self.handlers:
            if len(conditions) <= best_score:
                continue

            passed = True
            for c, v in conditions.items():
                if not self.check_condition(person, event, c, v):
                    passed = False
                    break

            if passed:
                best_handler = handler
                best_score = len(conditions)

        if best_handler is None:
            return

        return best_handler(self, person, event)


def complete_meal(bot, person, event):
    meal = person.save_meal()
    bot.send_text(person, "Done! Keep up the good work!")


@Chatbot.register_handler(postback__in=PB_TO_MEAL_TYPES.keys())
def handle_log_meal(bot, person, event):
    pb = event.get_postback()
    ctx = {'type': PB_TO_MEAL_TYPES[pb], 'date': str(now().date())}
    state = States.WAITING_FOR_MEAL_PHOTO
    person.state = state
    person.context = ctx
    person.save()
    bot.send_text(person, "Great, let's do that, just snap a picture of your food",
                  quick_replies=[('Skip Photo', PostBacks.SKIP_PHOTO)])


@Chatbot.register_handler(postback__eq=PostBacks.SKIP_PHOTO, state__eq=States.WAITING_FOR_MEAL_PHOTO)
def handle_skip_photo(bot, person, event):
    if person.state == States.WAITING_FOR_MEAL_PHOTO:
        bot.send_text(person, "Ok, tell me a bit about your meal",
                      quick_replies=[('Skip Comments', PostBacks.SKIP_COMMENTS)])

        person.state = States.WAITING_FOR_MEAL_COMMENTS
        person.save()


@Chatbot.register_handler(postback__eq=PostBacks.SKIP_COMMENTS, state__eq=States.WAITING_FOR_MEAL_COMMENTS)
def handle_skip_comments(bot, person, event):
    if person.state == States.WAITING_FOR_MEAL_COMMENTS:
        person.state = States.COMPLETE_MEAL_LOG
        person.save()
        complete_meal(bot, person, event)


@Chatbot.register_handler(state__eq=States.WAITING_FOR_MEAL_PHOTO)
def handle_meal_photo(bot, person, event):
    assert person.state == States.WAITING_FOR_MEAL_PHOTO
    if not event.has_images():
        bot.send_text(person, "Sorry, I didn't get that ... Please upload a picture or press \"Skip Photo\"",
                      quick_replies=[('Skip Photo', PostBacks.SKIP_PHOTO)])
        return

    images = event.get_images()
    image_url = images[0]['payload']['url']
    person.state = States.WAITING_FOR_MEAL_COMMENTS
    person.context['image'] = image_url
    person.save()

    bot.send_text(person, "Ok, tell me a bit about your meal",
                  quick_replies=[('Skip Comments', PostBacks.SKIP_COMMENTS)])


@Chatbot.register_handler(state__eq=States.WAITING_FOR_MEAL_COMMENTS)
def handle_meal_comments(bot, person, event):
    assert person.state == States.WAITING_FOR_MEAL_COMMENTS

    if not event.has_text():
        bot.send_text(person, "Sorry, I didn't get that ... ",
                      quick_replies=[('Skip Comments', PostBacks.SKIP_COMMENTS)])
        return

    text = event.get_text()
    person.context['comments'] = text
    person.save()
    complete_meal(bot, person, event)