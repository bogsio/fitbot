import json
import requests

from pprint import pprint
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def message_handler(sender_id, message):
    text = message['text']
    print("Received text", text)
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
        print("In request.method == GET")
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        print("mode", mode)
        print("token", token)

        if mode and token:
            if mode == 'subscribe' and token == settings.FB_CHALLENGE:
                print("Return challenge")
                return HttpResponse(challenge, content_type="text/plain")

    # Incoming message
    elif request.method == 'POST':
        event = json.loads(request.body)
        pprint(event)
        if event['object'] == 'page':
            for entry in event['entry']:
                try:
                    message_event = entry['messaging'][0]
                    message_handler(message_event['sender']['id'], message_event['message'])
                except IndexError:
                    pass

    return HttpResponse("ok", content_type="text/plain")