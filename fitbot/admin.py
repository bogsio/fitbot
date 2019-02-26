from django.contrib import admin
from .models import Person, Meal, Progress


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('fb_id', 'last_seen')
    list_filter = ('last_seen', )


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('type', 'date')
    list_filter = ('type', 'date')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('weight', 'date')
    list_filter = ('date', )