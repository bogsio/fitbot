from django.utils.dateparse import parse_date
from django.contrib.postgres.fields import JSONField
from django.db import models


class Person(models.Model):
    fb_id = models.CharField(max_length=200)
    last_seen = models.DateTimeField(blank=True, null=True)
    state_name = models.CharField(max_length=100, null=True, blank=True)
    state_params = JSONField(null=True, blank=True)

    def save_meal(self):
        if not self.state_params:
            self.state_params = {}
            self.save()
        try:
            meal_date = parse_date(self.state_params['date'])
        except:
            meal_date = None

        meal = Meal.objects.create(
            person=self,
            date=meal_date,
            type=self.state_params.get('type', None),
            comments=self.state_params.get('comments', None),
            image=self.state_params.get('image', None)
        )

        self.state_name = None
        self.state_params = {}
        self.save()

        return meal


class Meal(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(null=True, blank=True, max_length=1000)
    comments = models.TextField(null=True, blank=True)

