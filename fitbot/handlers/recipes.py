from datetime import timedelta
from random import shuffle

from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.db.models import Max

from fitbot.models import Recipe


def build_recipe_galery(recipes):
    gallery = []
    for recipe in recipes:
        gallery.append(
            (recipe.title, recipe.image, recipe.website_name, recipe.url, [('View', recipe.url), ])
        )

    return gallery


def handle_recipe_request_via_intent(bot, person, event):
    slots = event.get_entities()

    recipes = Recipe.find_best(cuisine=slots.get('cuisine'), keywords=[slots.get('ingredient')])
    found = True

    bot.send_typing(person)

    if not recipes:
        found = False
        recipes = list(Recipe.objects.all())
        shuffle(recipes)
        recipes = recipes[:5]

    if recipes and found:
        bot.send_text(person, "I know exactly what you need! Here are some healthy recipes you can cook yourself")
    elif recipes and not found:
        bot.send_text(person, "Might not be exactly what you need, but here's something you can put together")
    else:
        bot.send_text(person, "Ummm, ... I don't know how to cook stuff like that :/")

    if recipes:
        bot.send_typing(person)
        bot.send_carousel(person, build_recipe_galery(recipes))