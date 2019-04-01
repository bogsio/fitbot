def handle_profanity(bot, person, event):
    bot.send_typing(person)
    bot.send_text(person, [
        "There's really no reason to talk like that",
        "Hey! be nice!",
        "Sorry if whatever I said offended you",
        "Try and be nice please!"
    ])