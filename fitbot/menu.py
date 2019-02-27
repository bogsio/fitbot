from fitbot.chatbot import PostBacks


GET_STARTED = {
    "payload": "GET_STARTED"
}


PERSISTENT_MENU = [
    {
        "locale": "default",
        "composer_input_disabled": False,
        "call_to_actions": [
            {
                "title": "Diary",
                "type": "nested",
                "call_to_actions": [
                    {
                        "title": "Food",
                        "type": "postback",
                        "payload": PostBacks.CHECK_FOOD
                    },
                    {
                        "title": "Progress",
                        "type": "postback",
                        "payload": PostBacks.CHECK_PROGRESS
                    },
                ]
            },
            {
                "title": "Log Meal",
                "type": "nested",
                "call_to_actions": [
                    {
                        "title": "Breakfast",
                        "type": "postback",
                        "payload": PostBacks.LOG_BREAKFAST
                    },
                    {
                        "title": "Lunch",
                        "type": "postback",
                        "payload": PostBacks.LOG_LUNCH
                    },
                    {
                        "title": "Dinner",
                        "type": "postback",
                        "payload": PostBacks.LOG_DINNER
                    },
                    {
                        "title": "Snack",
                        "type": "postback",
                        "payload": PostBacks.LOG_SNACK
                    }
                ]
            },

            {
                "title": "Log Progress",
                "type": "postback",
                "payload": PostBacks.LOG_PROGRESS
            },
        ]
    },
]
