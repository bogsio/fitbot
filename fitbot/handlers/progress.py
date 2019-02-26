from django.utils.timezone import now


def handle_log_progress(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    ctx = {'date': str(now().date())}
    state = States.WAITING_FOR_PROGRESS_PHOTO
    person.state = state
    person.context = ctx
    person.save()
    bot.send_text(person, "Just snap a picture of you",
                  quick_replies=[('Skip Photo', PostBacks.SKIP_PHOTO)])


def handle_progress_photo(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    if not event.has_images():
        bot.send_text(person, "Sorry, I didn't get that ... Please upload a picture or press \"Skip Photo\"",
                      quick_replies=[('Skip Photo', PostBacks.SKIP_PHOTO)])
        return

    images = event.get_images()
    image_url = images[0]['payload']['url']
    person.state = States.WAITING_FOR_PROGRESS_WEIGHT
    person.context['image'] = image_url
    person.save()

    bot.send_text(person, "What's your current weight? (example: \"90 kg\" or \"180lbs\")",
                  quick_replies=[('Skip Weight', PostBacks.SKIP_WEIGHT)])


def handle_skip_progress_photo(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    person.state = States.WAITING_FOR_PROGRESS_WEIGHT
    person.context['image'] = None
    person.save()

    bot.send_text(person, "What's your current weight?",
                  quick_replies=[('Skip Weight', PostBacks.SKIP_WEIGHT)])


def handle_progress_weight(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    WEIGHT_UNITS = ['gram', 'pound']
    nlp = event.get_nlp()
    entities = nlp.get('entities', {})
    quantities = entities.get('quantity', [])

    weight, unit = None, None

    for q in quantities:
        if q['unit'] in WEIGHT_UNITS:
            unit = q['unit']
            weight = q['value']
            break

    if weight is None or unit is None:
        bot.send_text(person, "Sorry, didn't get that. Just write your weight like this: \"90 kg\" or \"180lbs\"",
                      quick_replies=[('Skip Weight', PostBacks.SKIP_WEIGHT)])
        return

    if unit == 'gram':
        unit = 'kg'
        weight /= 1000
    if unit == 'pound':
        unit = 'lbs'

    person.state = States.WAITING_FOR_PROGRESS_BMI
    person.context['weight'] = weight
    person.context['weight_units'] = unit
    person.save()

    bot.send_text(person, "What's your current BMI? (example: \"25\" or \"21.5\")",
                  quick_replies=[('Skip BMI', PostBacks.SKIP_BMI)])


def handle_skip_progress_weight(bot, person, event):
    from fitbot.chatbot import States, PostBacks
    person.state = States.WAITING_FOR_PROGRESS_BMI
    person.context['weight'] = None
    person.context['weight_units'] = None
    person.save()

    bot.send_text(person, "What's your current BMI? (example: \"25\" or \"21.5\")",
                  quick_replies=[('Skip BMI', PostBacks.SKIP_BMI)])


def handle_progress_bmi(bot, person, event):
    from fitbot.chatbot import PostBacks
    try:
        bmi = float(event.get_text().strip())
    except:
        bot.send_text(person, "Did not get that, try something like: \"25\" or \"21.5\"",
                      quick_replies=[('Skip BMI', PostBacks.SKIP_BMI)])
        return

    person.context['bmi'] = bmi
    person.save()

    complete_progress(bot, person, event)


def handle_skip_progress_bmi(bot, person, event):
    person.context['bmi'] = None
    person.save()
    complete_progress(bot, person, event)


def complete_progress(bot, person, event):
    person.save_progress()
    bot.send_text(person, "Done! Keep up the good work!")

