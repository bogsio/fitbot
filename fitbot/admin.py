from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Person, Meal, Progress, MealImage, Recipe


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


@admin.register(MealImage)
class MealImageAdmin(admin.ModelAdmin):
    list_display = ('admin_image', 'name', 'keywords')

    def admin_image(self, obj):
        return mark_safe('<img width="50px" src="%s"/>' % obj.image)

    admin_image.allow_tags = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('admin_image', 'title', 'keywords', 'website_name', 'url', 'cuisine')
    list_filter = ('website_name', 'cuisine')

    def admin_image(self, obj):
        return mark_safe('<img width="50px" src="%s"/>' % obj.image)