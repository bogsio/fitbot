GET_STARTED = {
    "payload": "GET_STARTED"
}


PERSISTENT_MENU = [
    {
        "locale": "default",
        "composer_input_disabled": False,
        "call_to_actions": [
            {
                "title": "Log Meal",
                "type": "nested",
                "call_to_actions": [
                    {
                        "title": "Breakfast",
                        "type": "postback",
                        "payload": "LOG_BREAKFAST"
                    },
                    {
                        "title": "Lunch",
                        "type": "postback",
                        "payload": "LOG_LUNCH"
                    },
                    {
                        "title": "Dinner",
                        "type": "postback",
                        "payload": "LOG_DINNER"
                    },
                    {
                        "title": "Snack",
                        "type": "postback",
                        "payload": "LOG_SNACK"
                    }
                ]
            },
        # {
        #   "type": "web_url",
        #   "title": "Latest News",
        #   "url": "http://www.messenger.com/",
        #   "webview_height_ratio": "full"
        # }
        ]
    },
]
