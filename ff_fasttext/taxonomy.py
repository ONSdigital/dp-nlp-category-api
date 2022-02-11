from ._ff_fasttext import FfModel

from gensim.models import FastText as fasttext
import sys
import codecs
import logging
#import fasttext
from gensim.models import KeyedVectors
import os
import nltk
import re
from nltk.corpus import stopwords
from sortedcontainers import SortedDict
import numpy as np
from nltk.corpus import stopwords
from nltk import download

import json
from collections import Counter
from elasticsearch2 import Elasticsearch
from elasticsearch_dsl import Search, Q

import pandas as pd

THRESHOLD = 0.1

re_sw = re.compile(r'\b\w\b')
re_ws = re.compile(r'\s+')
re_num = re.compile('[^\w\s\']', flags=re.UNICODE)

lang_map = {
    'en': 'english',
    'fr': 'french'
}

DATA_LOCATION = os.environ['TDATIM_DATA'] if 'TDATIM_DATA' in os.environ else '/data'
DATA_CATEGORIES = os.environ['TDATIM_CATEGORIES'] if 'TDATIM_CATEGORIES' in os.environ else f'{DATA_LOCATION}/dtcats.LANG.md'

model = FfModel('test_data/wiki.en.fifu')

# Import and download stopwords from NLTK.
download('stopwords')  # Download stopwords list.

# Remove stopwords.
stop_words = stopwords.words('english')

categories = {
   'employment': {
     'employment': ('personnel', 'employment', 'employee', 'work', 'staff', 'parental'),
     'earnings': ('working hours', 'paye', 'pay', 'earnings'),
     'workplace': ('workplace', 'disputes', 'conditions', 'labour'),
     'productivity': ('productivity', 'output'),
     'public sector personnel': ('civil service', 'public sector', 'personnel'),
     'unemployment': ('unemployment', 'economic inactivity', 'neet'),
    },
    'population': {
        'population': ('population', 'projections'),
    },
    'migration': {
        'migration': ('migration', 'migrant')
    }
}
classifier_bow = SortedDict(sum([[
    [(k, k2), list(v)]
    for k2, v in c_dict.items()
] for k, c_dict in categories.items()], []))
classifier_bow

DATA_LOCATION = 'data'
class WModel:
    def __init__(self, model):
        self.model = model
        self._model_dims = model.get_dims()

    def __getitem__(self, name):
        a = np.zeros((300,), dtype=np.float32)
        self.model.load_embedding(name, a)
        return a

weighting = {
    'C': 2,
    'SC': 2,
    'SSC': 1,
    'WC': 3,
    'WSSC': 5
}
class CategoryManager:
    _stop_words = None
    _model = None
    _classifier_bow = None
    _topic_vectors = None

    def __init__(self):
        self._categories = {}

    def load(self, lang='en'):
        if not self._stop_words:
            nltk.data.path.append(DATA_LOCATION)
            self._stop_words = stopwords.words(lang_map[lang])
        if not self._model:
            print('LOADING MODEL', file=sys.stderr)
            self._model = fasttext.load_model(f'{DATA_LOCATION}/wiki.{lang}.bin')
            print('LOADED MODEL', file=sys.stderr)
        if 'dtcats' not in self._categories or not self._categories['dtcats']:
            categories_file = DATA_CATEGORIES.replace('LANG', lang)
            classifier_bow = self._load_data_times_categories(categories_file)
            self.add_categories_from_bow('dtcats', classifier_bow)


    def add_categories_from_bow(self, name, classifier_bow):
        topic_vectors = [
            (np.mean([weighting[code] * self._model[w] for code, w in l], axis=0), [w for _, w in l]) for k, l in classifier_bow.items()
        ]
        self._categories[name] = (classifier_bow, topic_vectors)

    def strip_document(self, doc):
        if type(doc) is list:
            doc = ' '.join(doc)

        docs = doc.split(',')
        word_list = []
        for doc in docs:
            doc = doc.replace('\n', ' ').replace('_', ' ').replace('\'', '').lower()
            doc = re_ws.sub(' ', re_num.sub('', doc)).strip()

            if doc == '':
                return []

            word_list.append([w for w in doc.split(' ') if w not in self._stop_words])

        return word_list

    def _load_data_times_categories(self, dtcat_filename):
        classifier_bow = SortedDict([])

        with codecs.open(dtcat_filename, 'r') as cat_f:
            category = ''
            for line in (l.strip().lower() for l in cat_f.readlines()):
                if not line:
                    continue

                if line.startswith('[') and line.endswith(']'):
                    category = line[1:-1]
                    continue

                if ':' in line:
                    label, words = line.split(':')
                    words = words.split(',')
                else:
                    label, words = (line, [line])

                classifier_bow[(category, label)] = [category] + words
        return classifier_bow

    def test(self, sentence, category_group='dtcats'):
        classifier_bow, topic_vectors = self._categories[category_group]

        clean = self.strip_document(sentence)

        if not clean:
            return []

        tags = set()
        for words in clean:
            if not words:
                continue

            vec = np.mean([self._model[w] for w in words], axis=0)
            result = KeyedVectors.cosine_similarities(vec, [t for t, _ in topic_vectors])
            #result = sorted([(t, model.wv.n_similarity(t, clean)) for t in topics], key=lambda x: x[1], reverse=False)

            top = np.nonzero(result > THRESHOLD)[0]

            tags.update({(result[i], classifier_bow.keys()[i]) for i in top})

        return sorted(tags, reverse=True)

def make_category_manager():
    category_manager = CategoryManager()

    return category_manager

cm = make_category_manager()
cm._model = WModel(model)
cm._stop_words = stopwords.words('english')

with open('taxonomy.json', 'r') as f:
    taxonomy = json.load(f)
child_topics = sum([topic['child_topics'] for topic in taxonomy['topics']], [])
categories = {
    (topic['filterable_title'], topic['title']): {
        (subtopic['filterable_title'], subtopic['title']): sum([
            [(subsubtopic['filterable_title'], subsubtopic['title'])]
            for subsubtopic in subtopic['child_topics']
        ], []) if 'child_topics' in subtopic else []
        for subtopic in topic['child_topics']
    }
    for topic in taxonomy['topics']
}
print(categories)
classifier_categories = {
    catf: {
        subcatf: {
            subsubcatf: sum([
                [('C', v) for w in cm.strip_document(cat) for v in w] + 
                [('SC', v) for w in cm.strip_document(subcat) for v in w] + 
                [('SSC', v) for w in cm.strip_document(subsubcat) for v in w]], [])
            for subsubcatf, subsubcat in subcat_sub
        }
        for (subcatf, subcat), subcat_sub in cat_sub.items()
    } for (catf, cat), cat_sub in categories.items()
}
#categories = {
#    cat: {
#        subcat: model.wv.most_similar(np.mean([cm._model[scw] for scw in sc], axis=0))
#        for subcat, sc in c.items()
#    } for cat, c in categories.items()
#}
classifier_categories
#+ np.mean(2 * [self._model[k[0]]] + [self._model[w] for w in l]
#                                                             model.wv.most_similar('asylum')

classifier_bow = SortedDict(sum([[
    [(k, k2, k3), list(v)]
    for k2, c2_dict in c_dict.items()
    for k3, v in c2_dict.items()
] for k, c_dict in classifier_categories.items()], []))
classifier_bow

c = Counter()
c.update(['a'])
c.update(['a'])
[n for k, n in c.items()]

client = Elasticsearch(['http://localhost:9200'])

s = Search(using=client, index="ons1639492069322") \
        .filter('bool', must=[Q('exists', field="description.title")])
datasets = {}
classifier_bow_vec = {
    k: [cm._model[w[1]] for w in words]
    for k, words in classifier_bow.items()
}
def get_cat_bow(cat):
    return classifier_bow_vec[cat]
def closest(text, cat):
    word_list = set(sum(cm.strip_document(text), []))
    word_scores = [
        (word,
            np.array([
                np.dot(
                    cm._model[word] / np.abs(cm._model[word]),
                    v / np.abs(v)
                )
                for v in get_cat_bow(cat)
            ]).mean()

            # TODO: double check model.embedding_similarities(
            # cm._model[word], get_cat_bow(cat)
        #)
        )
        for word in word_list
        if cat in classifier_bow_vec
    ]
    return [
        word for word, score in sorted(word_scores, key=lambda word: word[1], reverse=True)
        if score > 0.5
    ]
win = 0
#results_df = pd.DataFrame((d.to_dict() for d in s.scan()))
# /businesseconomy../business/activitiespeopel/123745
for hit in s.scan():
    try:
        datasets[hit.description.title] = {
            'category': tuple(hit.uri.split('/')[1:4]),
            'text': f'{hit.description.title} {hit.description.metaDescription}'
        }
        datasets[hit.description.title]['bow'] = closest(datasets[hit.description.title]['text'], datasets[hit.description.title]['category'])
    except AttributeError as e:
        pass
        
discovered_terms = {}
# could do with lemmatizing
APPEARANCE_THRESHOLD = 5
UPPER_APPEARANCE_THRESHOLD = 10


for ds in datasets.values():
    if ds['category'][0:2] not in discovered_terms:
        discovered_terms[ds['category'][0:2]] = Counter()
    discovered_terms[ds['category'][0:2]].update(set(ds['bow']))
    if ds['category'] not in discovered_terms:
        discovered_terms[ds['category']] = Counter()
    discovered_terms[ds['category']].update(set(ds['bow']))
# print([list(c.items()) for k, c in discovered_terms.items()])
discovered_terms = {
    k: [w for w, c in count.items() if c > (APPEARANCE_THRESHOLD if len(k) > 2 else UPPER_APPEARANCE_THRESHOLD)]
    for k, count in discovered_terms.items()
}
for key, terms in classifier_bow.items():
    if key in discovered_terms:
        terms += [('WSSC', w) for w in discovered_terms[key]]
    if key[0:2] in discovered_terms:
        terms += [('WC', w) for w in discovered_terms[key[0:2]]]

{k: len(v) for k, v in classifier_bow.items()}

pd.options.display.max_rows = None
pd.options.display.max_colwidth = 600
df = pd.DataFrame([(k[0], k[1], k[2], v) for k, v in classifier_bow.items()])
df

cm.add_categories_from_bow('onyxcats', classifier_bow)

if __name__ == "__main__":
   while True:
      word = input()
      print(cm.test(word.strip(), 'onyxcats'))
