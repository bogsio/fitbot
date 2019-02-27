from datetime import timedelta

from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.db.models import Max

from fitbot.models import Meal


def display_meals(bot, person, meals):
    gallery = []
    for meal in meals:
        gallery.append(
            (meal.type, meal.image, meal.comments, meal.image, [('View', meal.image), ])
        )

    bot.send_carousel(person, gallery)


def complete_meal(bot, person, event):
    person.save_meal()
    bot.send_text(person, "Done! Keep up the good work!")

    # meals for today
    today_meals = Meal.objects.filter(date=now().date())
    if not today_meals:
        return

    bot.send_text(person, "Here's how you're doing today so far")
    display_meals(bot, person, today_meals)



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


def display_meal_diary(bot, person, event):
    from fitbot.chatbot import PostBacks
    # Put in the latest day, if there is one
    if person.context.get('day') is None:
        latest_date = Meal.objects.all().aggregate(Max('date'))['date__max']
        if latest_date is None:
            bot.send_text(person, "You haven't logged anything yet, why don't you start now?",
                          quick_replies=[('Log Meal Now', PostBacks.LOG_SNACK)])
            return
        print(latest_date)
        person.context['day'] = str(latest_date)
        person.save()

    d = parse_date(person.context['day'])
    print("d", d)

    # Get all the meals for that day
    meals = Meal.objects.filter(date=d)

    # No meals logged on that day
    if not meals:
        bot.send_text(person, f"You haven't logged anything on {d}",
                      quick_replies=[('Prev Day', PostBacks.PREV_DAY), ('Next Day', PostBacks.NEXT_DAY)])
        return

    # Finally, display the meals for that day
    bot.send_text(person, f"Here's what you had on {d}")
    display_meals(bot, person, meals)
    bot.send_text(person, "Checkout other days",
                  quick_replies=[('Prev Day', PostBacks.PREV_DAY), ('Next Day', PostBacks.NEXT_DAY)])


def handle_check_food(bot, person, event):
    from fitbot.chatbot import States
    person.state = States.CHECKING_FOOD
    person.context.pop('day', None)
    person.save()
    display_meal_diary(bot, person, event)


def handle_prev_day(bot, person, event):
    day = person.context.pop('day', None)
    if day is not None:
        day = parse_date(day) + timedelta(days=-1)
        person.context['day'] = str(day)
        person.save()

    display_meal_diary(bot, person, event)


def handle_next_day(bot, person, event):
    day = person.context.pop('day', None)
    if day is not None:
        day = parse_date(day) + timedelta(days=1)
        person.context['day'] = str(day)
        person.save()

    display_meal_diary(bot, person, event)
