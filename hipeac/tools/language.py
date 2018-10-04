import nltk

from collections import namedtuple
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types


Token = namedtuple('Token', 'word, speech_tag, lemma, salience')


class NaturalLanguageAnalyzer:

    def __init__(self):
        self.client = language.LanguageServiceClient()

    def analyze_entities(self, text):
        document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)
        entities = self.client.analyze_entities(document).entities
        return entities

    def get_keywords(self, text, min_salience=0.01):
        entities = [entity for entity in self.analyze_entities(text) if entity.salience >= min_salience]
        keywords = [entity.name.lower() for entity in entities]
        saliences = {entity.name.lower(): entity.salience for entity in entities}

        lemmatizer = nltk.stem.WordNetLemmatizer()
        tokens = [Token(t[0], t[1], lemmatizer.lemmatize(t[0]), saliences[t[0]]) for t in nltk.pos_tag(keywords)]
        tokens = sorted(tokens, key=lambda x: x.salience, reverse=True)
        plurals = [t.lemma for t in tokens if t.speech_tag == 'NNS']
        singulars_with_plural = [t.word for t in tokens if t.speech_tag == 'NN' and t.lemma in plurals]

        return list(dict.fromkeys([t.word for t in tokens if t.word not in singulars_with_plural]))
