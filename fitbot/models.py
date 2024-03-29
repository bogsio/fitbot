from django.utils.dateparse import parse_date
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models

from fitbot.utils import pick_probabilistically


class Cuisine:
    STANDARD = 'STANDARD'
    KETO = 'KETO'
    PALEO = 'PALEO'
    VEGETARIAN = 'VEGETARIAN'
    PRIMAL = 'PRIMAL'
    VEGAN = 'VEGAN'
    RAW_VEGAN = 'RAW_VEGAN'
    LOW_CARB = 'LOW_CARB'

    ALL = [
        (STANDARD, 'Standard'),
        (KETO, 'Keto'),
        (PALEO, 'Paleo'),
        (VEGETARIAN, 'Vegetarian'),
        (PRIMAL, 'Primal'),
        (VEGAN, 'Vegan'),
        (RAW_VEGAN, 'Raw Vegan'),
        (LOW_CARB, 'Low Carb')
    ]


class Person(models.Model):
    fb_id = models.CharField(max_length=200)
    last_seen = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    context = JSONField(null=True, blank=True)

    def save_meal(self):
        if not self.context:
            self.context = {}
            self.save()
        try:
            meal_date = parse_date(self.context['date'])
        except:
            print("!! Could not parse date meal", self.context['date'])
            meal_date = None

        if 'image' not in self.context:
            image = MealImage.find_best(self.context.get('comments', ''))
            if image is not None:
                image_url = image.image
            else:
                image_url = "https://dl.dropboxusercontent.com/s/r2tgdyfag9egtql/Depositphotos_11389585_m-2015.jpg?dl=0"
        else:
            image_url = self.context['image']

        meal = Meal.objects.create(
            person=self,
            date=meal_date,
            type=self.context.get('type', None),
            comments=self.context.get('comments', None),
            # image=self.context.get('image', None)
            image=image_url
        )

        self.state = None
        self.context = {}
        self.save()

        return meal

    def save_progress(self):
        if not self.context:
            self.context = {}
            self.save()
        try:
            progress_date = parse_date(self.context['date'])
        except:
            progress_date = None

        meal = Progress.objects.create(
            person=self,
            date=progress_date,
            image=self.context.get('image', None),
            weight=self.context.get('weight', None),
            weight_units=self.context.get('weight_units', None),
            bmi=self.context.get('bmi', None),
        )

        self.state = None
        self.context = {}
        self.save()

        return meal


class Meal(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(null=True, blank=True, max_length=1000)
    comments = models.TextField(null=True, blank=True)


class Progress(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    image = models.URLField(null=True, blank=True, max_length=1000)
    weight = models.FloatField(null=True, blank=True)
    weight_units = models.CharField(max_length=20, null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)


class MealImage(models.Model):
    image = models.URLField(null=True, blank=True, max_length=1000)
    name = models.CharField(max_length=200)
    keywords = ArrayField(models.CharField(max_length=200), blank=True)

    @staticmethod
    def find_best(description):
        if isinstance(description, str):
            description = set(description.replace('.', '').replace(',', '').split())

        best_image = None
        best_score = 0

        for meal_image in MealImage.objects.all():
            image_keywords = set(meal_image.keywords)
            intersected_keywords = image_keywords.intersection(description)
            if len(intersected_keywords) > best_score:
                best_score = len(intersected_keywords)
                best_image = meal_image

        return best_image


class Recipe(models.Model):
    title = models.CharField(max_length=300)
    image = models.URLField(null=True, blank=True, max_length=1000)
    website_name = models.CharField(max_length=200)
    url = models.URLField(max_length=1000)
    cuisine = models.CharField(max_length=100, choices=Cuisine.ALL, default=Cuisine.STANDARD)
    keywords = ArrayField(models.CharField(max_length=200), blank=True)
    description = models.TextField(null=True, blank=True)

    @staticmethod
    def find_best(cuisine=None, keywords=None, count=5):
        if keywords is None:
            keywords = []

        recipes = Recipe.objects.all()
        if cuisine is not None:
            recipes = recipes.filter(cuisine=cuisine)

        suitable_recipes = []

        for recipe in recipes:
            recipe_keywords = set(recipe.keywords)
            intersected_keywords = recipe_keywords.intersection(keywords)
            if len(intersected_keywords) > 0:
                suitable_recipes.append((recipe, len(intersected_keywords)))

        selected_recipes = pick_probabilistically(suitable_recipes, max_count=5)
        return selected_recipes

    def __str__(self):
        return f"Recipe[\"{self.title}\"]"


class WeirdPhrase(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text
