# Generated by Django 2.1.7 on 2019-03-20 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fitbot', '0010_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mealimage',
            old_name='tags',
            new_name='keywords',
        ),
    ]