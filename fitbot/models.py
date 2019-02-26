from django.utils.dateparse import parse_date
from django.contrib.postgres.fields import JSONField
from django.db import models


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
            meal_date = None

        meal = Meal.objects.create(
            person=self,
            date=meal_date,
            type=self.context.get('type', None),
            comments=self.context.get('comments', None),
            image=self.context.get('image', None)
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

