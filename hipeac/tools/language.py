from django.conf import settings
from google.cloud import language_v1


class NaturalLanguageAnalyzer:
    def __init__(self):
        self.client = language_v1.LanguageServiceClient()

    def analyze_entities(self, text):
        document = language_v1.types.Document(content=text, type=language_v1.enums.Document.Type.PLAIN_TEXT)
        entities = self.client.analyze_entities(document).entities
        return entities

    def get_keywords(self, text, min_salience=0.01):
        if settings.DEBUG:
            return []

        entities = [entity for entity in self.analyze_entities(text) if entity.salience >= min_salience]
        return list(set([entity.name.lower() for entity in entities]))
