import json
import requests
from django.http import HttpResponse
from django.conf import settings


def message_handler(sender_id, message):
    text = message['text']
    answer = "Hi"
    uri = "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % settings.FB_ACCESS_TOKEN
    data = {
        'messaging_type': 'RESPONSE',
        'recipient': {'id': sender_id},
        'message': {'text': answer}
    }
    requests.post(uri, data=json.dumps(data), headers={'content-type': 'application/json'})


def webhook(request):
    # Webhook verification
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == settings.FB_CHALLENGE:
                return challenge

    # Incoming message
    elif request.method == 'POST':
        event = request.get_json()
        if event['object'] == 'page':
            for entry in event['entry']:
                try:
                    message_event = entry['messaging'][0]
                    message_handler(message_event['sender']['id'], message_event['message'])
                except IndexError:
                    pass

    return HttpResponse("Text only, please.", content_type="text/plain")