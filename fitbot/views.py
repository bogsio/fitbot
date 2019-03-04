import json
import requests

from pprint import pprint
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from fitbot.chatbot import Chatbot
from fitbot.models import Person
from fitbot.utils import MessengerEvent


def message_handler(sender_id, message):
    answer = "Hi"
    uri = "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % settings.FB_ACCESS_TOKEN
    data = {
        # 'messaging_type': 'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': answer}
    }
    print("Posting to", uri)
    print("Sending data", data)
    response = requests.post(uri, data=json.dumps(data), headers={'content-type': 'application/json'})
    print(response.status_code)
    print(response.content)


@csrf_exempt
def webhook(request):
    # Webhook verification
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == settings.FB_CHALLENGE:
                return HttpResponse(challenge, content_type="text/plain")

    # Incoming message
    elif request.method == 'POST':
        event = json.loads(request.body)
        print("\n\n")
        print("Incoming Event")
        print('--------------------------')
        pprint(event)
        print('--------------------------')

        if event['object'] == 'page':
            for entry in event['entry']:
                msg_event = MessengerEvent(entry)
                person, _ = Person.objects.get_or_create(fb_id=str(msg_event.get_sender()))
                person.last_seen = now()
                person.save()

                if msg_event.has_text():
                    print("=" * 20)
                    try:
                        msg_event.fetch_nlu_data(msg_event.get_text())
                    except:
                        pass
                    print("=" * 20)

                bot = Chatbot()
                bot.handle(person, msg_event)

                #
                # try:
                #     message_event = entry['messaging'][0]
                #     message_handler(message_event['sender']['id'], message_event['message'])
                # except (IndexError, KeyError):
                #     pass

    return HttpResponse("ok", content_type="text/plain")