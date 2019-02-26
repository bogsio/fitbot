from django.utils.timezone import now

from fitbot.models import Meal


def complete_meal(bot, person, event):
    person.save_meal()
    bot.send_text(person, "Done! Keep up the good work!")

    # meals for today
    today_meals = Meal.objects.filter(date=now().date())
    if not today_meals:
        return

    bot.send_text(person, "Here's how you're doing today so far")

    gallery = []
    for meal in today_meals:
        gallery.append(
            (meal.type, meal.image, meal.comments, meal.image, [('View', meal.image), ])
        )

    bot.send_carousel(person, gallery)


def handle_log_meal(bot, person, event):
    from fitbot.chatbot import States, PostBacks, PB_TO_MEAL_TYPES
    pb = event.get_postback()
    ctx = {'type': PB_TO_MEAL_TYPES[pb], 'date': str(now().date())}
    state = States.WAITING_FOR_MEAL_PHOTO
    person.state = state
    person.context = ctx
    person.save()
    bot.send_text(person, "Great, let's do that, just snap a picture of your food",
                  quick_replies=[('Skip Photo', PostBacks.SKIP_PHOTO)])


def handle_skip_meal_photo(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    bot.send_text(person, "Ok, tell me a bit about your meal",
                  quick_replies=[('Skip Comments', PostBacks.SKIP_COMMENTS)])

    person.state = States.WAITING_FOR_MEAL_COMMENTS
    person.save()


def handle_skip_comments(bot, person, event):
    complete_meal(bot, person, event)


def handle_meal_photo(bot, person, event):
    from fitbot.chatbot import States, PostBacks
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


def handle_meal_comments(bot, person, event):
    from fitbot.chatbot import PostBacks
    if not event.has_text():
        bot.send_text(person, "Sorry, I didn't get that ... ",
                      quick_replies=[('Skip Comments', PostBacks.SKIP_COMMENTS)])
        return

    text = event.get_text()
    person.context['comments'] = text
    person.save()
    complete_meal(bot, person, event)