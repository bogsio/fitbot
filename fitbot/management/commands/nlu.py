from pprint import pprint
from django.core.management.base import BaseCommand, CommandError
from fitbot.utils import nlu

class Command(BaseCommand):

    def handle(self, *args, **options):
        while(True):
            line = input("ChatLine: ")
            pprint(nlu.parse(line))

