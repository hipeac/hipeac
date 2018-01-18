import nltk

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Downloads all data necessary for NLTK.'

    def handle(self, *args, **options):
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
