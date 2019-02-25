from django.contrib import admin
from .models import Person, Meal

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('fb_id', 'last_seen')
    list_filter = ('last_seen', )


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    pass