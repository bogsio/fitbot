import json
import time
from random import choice

import requests

from django.conf import settings

from fitbot.handlers import progress, meals, recipes, default, profanity
from fitbot.models import Person
from fitbot.utils import MessengerEvent


class States:
    WAITING_FOR_MEAL_PHOTO = 'WAITING_FOR_MEAL_PHOTO'
    WAITING_FOR_MEAL_COMMENTS = 'WAITING_FOR_MEAL_COMMENTS'

    WAITING_FOR_PROGRESS_PHOTO = 'WAITING_FOR_PROGRESS_PHOTO'
    WAITING_FOR_PROGRESS_WEIGHT = 'WAITING_FOR_PROGRESS_WEIGHT'
    WAITING_FOR_PROGRESS_BMI = 'WAITING_FOR_PROGRESS_BMI'

    CHECKING_FOOD = "CHECKING_FOOD"
    CHECKING_PROGRESS = "CHECKING_PROGRESS"


class PostBacks:
    SKIP_COMMENTS = "SKIP_COMMENTS"
    SKIP_PHOTO = "SKIP_PHOTO"
    SKIP_WEIGHT = "SKIP_WEIGHT"
    SKIP_BMI = "SKIP_BMI"

    LOG_BREAKFAST = "LOG_BREAKFAST"
    LOG_LUNCH = "LOG_LUNCH"
    LOG_DINNER = "LOG_DINNER"
    LOG_SNACK = "LOG_SNACK"

    LOG_PROGRESS = "LOG_PROGRESS"

    CHECK_FOOD = "CHECK_FOOD"
    CHECK_PROGRESS = "CHECK_PROGRESS"

    PREV_DAY = "PREV_DAY"
    NEXT_DAY = "NEXT_DAY"

    GET_STARTED = "GET_STARTED"
    CONTINUE_INTRO_PART2 = "CONTINUE_INTRO1"


class Intents:
    LOG_MEAL = "LOG_MEAL"
    VIEW_MEAL_DIARY = "VIEW_MEAL_DIARY"
    SUGGEST_RECIPE = "SUGGEST_RECIPE"
    GREETING = "GREETING"
    GOOD_BYE = "GOOD_BYE"
    PROFANITY = "PROFANITY"


class Meals:
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    SNACK = 'snack'


PB_TO_MEAL_TYPES = {
    PostBacks.LOG_BREAKFAST: Meals.BREAKFAST,
    PostBacks.LOG_LUNCH: Meals.LUNCH,
    PostBacks.LOG_DINNER: Meals.DINNER,
    PostBacks.LOG_SNACK: Meals.SNACK
}


class Chatbot(object):

    _handlers = []

    class SenderActions:
        MARK_SEEN = 'mark_seen'
        TYPING_ON = 'typing_on'
        TYPING_OFF = 'typing_off'

    @property
    def handlers(self):
        return self._handlers

    @staticmethod
    def get_server_uri():
        return "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % settings.FB_ACCESS_TOKEN

    @classmethod
    def send_action(cls, person, action):
        data = {
            'recipient': {'id': person.fb_id},
            'sender_action': action
        }

        response = requests.post(
            cls.get_server_uri(),
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    @classmethod
    def send_mark_seen(cls, person):
        cls.send_action(person, Chatbot.SenderActions.MARK_SEEN)

    @classmethod
    def send_typing(cls, person, seconds=1.2):
        cls.send_action(person, Chatbot.SenderActions.TYPING_ON)
        time.sleep(seconds)
        cls.send_action(person, Chatbot.SenderActions.TYPING_OFF)

    @classmethod
    def send_text(cls, person, text, quick_replies=None):
        """

        :param text: plain text string
        :param quick_replies: [(display1, postback1), ...]
        :return:
        """

        # If we have more than one choice, choose a random one
        if isinstance(text, (list, tuple)):
            text = choice(text)

        data = {
            'messaging_type': 'RESPONSE',
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

        # print("Outgoing data")
        # print("======================")
        # pprint(data)
        # print("======================")
        response = requests.post(
            cls.get_server_uri(),
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

    @classmethod
    def send_carousel(cls, person, elements, height_ratio="tall"):
        data = {
            'messaging_type': 'RESPONSE',
            "recipient": {"id": person.fb_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": []
                    }

                }
            }
        }

        for element in elements:
            title, image_url, subtitle, action, buttons = element
            element_payload = {
                "title": title,
                "image_url": image_url,
                "subtitle": subtitle,
                "default_action": {
                    "webview_height_ratio": height_ratio
                },
                "buttons": []
            }
            if action[:4] == 'http':
                element_payload["default_action"]["type"] = "web_url"
                element_payload["default_action"]["url"] = action
            else:
                element_payload["default_action"]["type"] = "postback"
                element_payload["default_action"]["payload"] = action

            for button in buttons:
                title, action = button
                button_payload = {
                    "title": title
                }
                if action[:4] == 'http':
                    button_payload["type"] = "web_url"
                    button_payload["url"] = action
                else:
                    button_payload["type"] = "postback"
                    button_payload["payload"] = action

                element_payload["buttons"].append(button_payload)

            data["message"]["attachment"]["payload"]["elements"].append(element_payload)

        # print("\n\n")
        # print("Outgoing data")
        # print("======================")
        # pprint(data)
        # print("======================")
        response = requests.post(
            cls.get_server_uri(),
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )

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
            print("Checking for postback")
            if not event.has_postback():
                return False

            pb = event.get_postback()
            print("pb=", pb)

            if chunks[1] == 'eq':
                print("pb == value", pb, condition_value, pb == condition_value)
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

        if chunks[0] == 'intent':
            if chunks[1] == 'eq':
                if not event.has_intent():
                    return False
                return event.get_intent() == condition_value

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
            print("No appropriate handler found ...")
            return

        return best_handler(self, person, event)


# Meal Related handlers
Chatbot.register_handler(postback__in=PB_TO_MEAL_TYPES.keys())(
    meals.handle_log_meal_via_postback)
Chatbot.register_handler(intent__eq=Intents.LOG_MEAL)(
    meals.handle_log_meal_via_intent)
Chatbot.register_handler(postback__eq=PostBacks.SKIP_PHOTO, state__eq=States.WAITING_FOR_MEAL_PHOTO)(
    meals.handle_skip_meal_photo)
Chatbot.register_handler(postback__eq=PostBacks.SKIP_COMMENTS, state__eq=States.WAITING_FOR_MEAL_COMMENTS)(
    meals.handle_skip_comments)
Chatbot.register_handler(state__eq=States.WAITING_FOR_MEAL_PHOTO)(
    meals.handle_meal_photo)
Chatbot.register_handler(state__eq=States.WAITING_FOR_MEAL_COMMENTS)(
    meals.handle_meal_comments)
Chatbot.register_handler(postback__eq=PostBacks.CHECK_FOOD)(
    meals.handle_check_food)
Chatbot.register_handler(postback__eq=PostBacks.PREV_DAY, state__eq=States.CHECKING_FOOD)(
    meals.handle_prev_day)
Chatbot.register_handler(postback__eq=PostBacks.NEXT_DAY, state__eq=States.CHECKING_FOOD)(
    meals.handle_next_day)
Chatbot.register_handler(intent__eq=Intents.VIEW_MEAL_DIARY)(
    meals.handle_check_food_via_intent)


# Log Progress handlers
Chatbot.register_handler(postback__eq=PostBacks.LOG_PROGRESS)(
    progress.handle_log_progress)
Chatbot.register_handler(state__eq=States.WAITING_FOR_PROGRESS_PHOTO)(
    progress.handle_progress_photo)
Chatbot.register_handler(postback__eq=PostBacks.SKIP_PHOTO, state__eq=States.WAITING_FOR_PROGRESS_PHOTO)(
    progress.handle_skip_progress_photo)
Chatbot.register_handler(state__eq=States.WAITING_FOR_PROGRESS_WEIGHT)(
    progress.handle_progress_weight)
Chatbot.register_handler(postback__eq=PostBacks.SKIP_WEIGHT, state__eq=States.WAITING_FOR_PROGRESS_WEIGHT)(
    progress.handle_skip_progress_weight)
Chatbot.register_handler(state__eq=States.WAITING_FOR_PROGRESS_BMI)(
    progress.handle_progress_bmi)
Chatbot.register_handler(postback__eq=PostBacks.SKIP_BMI, state__eq=States.WAITING_FOR_PROGRESS_BMI)(
    progress.handle_skip_progress_bmi)


# Suggest Recipes
Chatbot.register_handler(intent__eq=Intents.SUGGEST_RECIPE)(
    recipes.handle_recipe_request_via_intent)


# Default Answer
Chatbot.register_handler(intent__eq=Intents.GREETING)(default.handle_say_hello)
Chatbot.register_handler(intent__eq=Intents.GOOD_BYE)(default.handle_say_bye)
Chatbot.register_handler(intent__eq=Intents.PROFANITY)(profanity.handle_profanity)
Chatbot.register_handler(postback__eq=PostBacks.GET_STARTED)(default.handle_get_started)
Chatbot.register_handler(postback__eq=PostBacks.CONTINUE_INTRO_PART2)(default.handle_get_started_part2)
Chatbot.register_handler()(default.handle_default)
