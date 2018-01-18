import googleapiclient.discovery
import nltk

from collections import namedtuple
from django.conf import settings


Token = namedtuple('Token', 'word, speech_tag, lemma, salience')


class NaturalLanguageAnalyzer(object):
    def __init__(self):
        self.service = googleapiclient.discovery.build('language', 'v1', developerKey=settings.GOOGLE_API_KEY)

    def analyze_entities(self, text):
        body = {
            'encoding_type': 'UTF8',
            'document': {
                'type': 'PLAIN_TEXT',
                'content': text,
            }
        }

        request = self.service.documents().analyzeEntities(body=body)
        response = request.execute()

        # catch errors

        return response

    def classify_text(self, text, verbose=True):
        body = {
            'document': {
                'type': 'PLAIN_TEXT',
                'content': text,
            }
        }

        request = self.service.documents().classifyText(body=body)
        response = request.execute()

        # catch errors

        return response

    def get_keywords(self, text, min_salience=0.01):
        entities = [entity for entity in self.analyze_entities(text)['entities'] if entity['salience'] >= min_salience]
        keywords = [entity['name'].lower() for entity in entities]
        saliences = {entity['name'].lower(): entity['salience'] for entity in entities}

        lemmatizer = nltk.stem.WordNetLemmatizer()
        tokens = [Token(t[0], t[1], lemmatizer.lemmatize(t[0]), saliences[t[0]]) for t in nltk.pos_tag(keywords)]
        tokens = sorted(tokens, key=lambda x: x.salience, reverse=True)
        plurals = [t.lemma for t in tokens if t.speech_tag == 'NNS']
        singulars_with_plural = [t.word for t in tokens if t.speech_tag == 'NN' and t.lemma in plurals]

        return list(dict.fromkeys([t.word for t in tokens if t.word not in singulars_with_plural]))
