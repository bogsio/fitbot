


def handle_default(bot, person, event):
    bot.send_typing(person)
    bot.send_text(person, [
        "Not sure what you mean by that",
        "Not sure I can help you with that",
        "That's an interesting idea, but I don't think I can help you with that"
    ])


def handle_say_hello(bot, person, event):
    from fitbot.chatbot import PostBacks
    bot.send_typing(person)
    bot.send_text(person, [
        "Hi there!",
        "Hello",
        "Hey, how are you?"
    ])

    bot.send_typing(person)
    bot.send_text(person, [
        "Here's how I can help you",
        "Here are some quick actions you can take",
        "How can I help you?",
    ], quick_replies=[
        ("Check Food Diary", PostBacks.CHECK_FOOD),
        ("Log Breakfast", PostBacks.LOG_BREAKFAST),
        ("Log Lunch", PostBacks.LOG_LUNCH),
        ("Log Dinner", PostBacks.LOG_DINNER),
    ])


def handle_say_bye(bot, person, event):
    bot.send_typing(person)
    bot.send_text(person, [
        "Talk to you next time",
        "It's been real!",
        "Great talking to you",
        "Talk to you soon!"
    ])


def handle_get_started(bot, person, event):
    from fitbot.chatbot import PostBacks
    bot.send_typing(person)
    bot.send_text(person, [
        "Hello stranger!",
        "Hi there!",
    ])

    bot.send_typing(person)
    bot.send_text(person, [
        "I'm FitBot. I can help you track and achieve your fitness goals.",
    ])

    bot.send_typing(person)
    bot.send_text(person, [
        "I can keep a diary of your food, keep a collection "
        "of your progress pics or give you meal prep ideas.",
    ], quick_replies=[("Got it!", PostBacks.CONTINUE_INTRO_PART2)])


def handle_get_started_part2(bot, person, event):
    from fitbot.chatbot import PostBacks
    bot.send_typing(person)
    bot.send_text(person, [
        "You can either invoke me by using the Messenger "
        "fixed Menu at the bottom (check the hamburger icon)"
    ])

    bot.send_typing(person)
    bot.send_text(person, [
        " ... or you can send me a message ..."
    ])

    bot.send_typing(person, seconds=2)
    bot.send_text(person, [
        "something like ... \"Today I had eggs and bacon\""
    ])

    bot.send_typing(person, seconds=2)
    bot.send_text(person,
                  "... or just say \"Hi\" and I'll give you some quick actions "
                  "I can help with, like this:",
                  quick_replies=[
                      ("Check Food Diary", PostBacks.CHECK_FOOD),
                      ("Log Breakfast", PostBacks.LOG_BREAKFAST),
                      ("Log Lunch", PostBacks.LOG_LUNCH),
                      ("Log Dinner", PostBacks.LOG_DINNER)]
    )