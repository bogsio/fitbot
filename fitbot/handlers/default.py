def handle_default(bot, person, event):
    bot.send_typing(person)
    bot.send_text(person, [
        "Not sure what you mean by that",
        "Not sure I can help you with that",
        "That's an interesting idea, but I don't think I can help you with that"
    ])
