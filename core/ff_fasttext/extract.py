import os
import logging
import json
from sortedcontainers import SortedDict
from collections import Counter
from elasticsearch2 import Elasticsearch
from elasticsearch_dsl import Search, Q
from nltk import download
from tqdm import tqdm

from .settings import settings
from .ff_fasttext import FfModel
from .category_manager import CategoryManager
from .taxonomy import get_taxonomy, taxonomy_to_categories, categories_to_classifier_bow

APPEARANCE_THRESHOLD = settings.get('APPEARANCE_THRESHOLD', 5)
UPPER_APPEARANCE_THRESHOLD = settings.get('UPPER_APPEARANCE_THRESHOLD', 10)
HOST = settings.get('ELASTICSEARCH_HOST', os.getenv('ELASTICSEARCH_HOST', 'http://elasticsearch-master:9200'))
ELASTICSEARCH_INDEX = settings.get('ELASTICSEARCH_INDEX', os.getenv('ELASTICSEARCH_INDEX', 'ons1639492069322'))
CACHE_TARGET = settings.get('CACHE_TARGET', None)
REBUILD_CACHE = settings.get('REBUILD_CACHE', False)

def get_datasets(cm, classifier_bow):
    classifier_bow_vec = {
        k: [cm._model[w[1]] for w in words]
        for k, words in classifier_bow.items()
    }
    datasets = {}
    #results_df = pd.DataFrame((d.to_dict() for d in s.scan()))
    # /businesseconomy../business/activitiespeopel/123745
    client = Elasticsearch([HOST])

    s = Search(using=client, index=ELASTICSEARCH_INDEX) \
            .filter('bool', must=[Q('exists', field="description.title")])
    expecting = s.count()
    size = 50
    s = s.params(size=size)
    with tqdm(total=expecting) as pbar:
        for hit in s.scan():
            try:
                datasets[hit.description.title] = {
                    'category': tuple(hit.uri.split('/')[1:4]),
                    'text': f'{hit.description.title} {hit.description.metaDescription}'
                }
                cat = datasets[hit.description.title]['category']
                if cat not in classifier_bow_vec and cat[:-1] in classifier_bow_vec:
                    cat = cat[:-1]
                    datasets[hit.description.title]['category'] = cat

                datasets[hit.description.title]['bow'] = cm.closest(datasets[hit.description.title]['text'], cat, classifier_bow_vec)
            except AttributeError as e:
                pass
            pbar.update(1)
    return datasets

def discover_terms(datasets, classifier_bow):
    discovered_terms = {}
    # could do with lemmatizing
    for ds in datasets.values():
        if ds['category'][0:2] not in discovered_terms:
            discovered_terms[ds['category'][0:2]] = Counter()
        discovered_terms[ds['category'][0:2]].update(set(ds['bow']))
        if ds['category'] not in discovered_terms:
            discovered_terms[ds['category']] = Counter()
        discovered_terms[ds['category']].update(set(ds['bow']))

    discovered_terms = {
        k: [w for w, c in count.items() if c > (APPEARANCE_THRESHOLD if len(k) > 2 else UPPER_APPEARANCE_THRESHOLD)]
        for k, count in discovered_terms.items()
    }
    for key, terms in classifier_bow.items():
        if key in discovered_terms:
            terms += [('WSSC', w) for w in discovered_terms[key]]
        if key[0:2] in discovered_terms:
            terms += [('WC', w) for w in discovered_terms[key[0:2]]]

    if CACHE_TARGET and (not os.path.exists(CACHE_TARGET) or REBUILD_CACHE):
        cached = {
            'config': {
                'APPEARANCE_THRESHOLD': APPEARANCE_THRESHOLD,
                'UPPER_APPEARANCE_THRESHOLD': UPPER_APPEARANCE_THRESHOLD,
            },
            'classifier-bow': [
                ['|'.join(key), [[c, v] for c, v in terms]]
                for key, terms in classifier_bow.items()
            ]
        }
        try:
            with open(CACHE_TARGET, 'w') as cache_f:
                json.dump(cached, cache_f)
        except OSError:
            logging.warning("Could not write cache to target %s", CACHE_TARGET)

def append_discovered_terms_from_elasticsearch(cm, classifier_bow):
    datasets = get_datasets(cm, classifier_bow)
    discover_terms(datasets, classifier_bow)

def load(model_file):
    model = FfModel(model_file)
    # Import and download stopwords from NLTK.
    download('stopwords')  # Download stopwords list.

    category_manager = CategoryManager(model)

    taxonomy = get_taxonomy()
    categories = taxonomy_to_categories(taxonomy)

    if CACHE_TARGET and os.path.isfile(CACHE_TARGET) and not REBUILD_CACHE:
        with open(CACHE_TARGET, 'r') as cache_f:
            cached = json.load(cache_f)
        classifier_bow = SortedDict({
                tuple(key.split('|')): tuple((c, v) for c, v in terms)
                for key, terms in cached['classifier-bow']
        })
    else:
        classifier_bow = categories_to_classifier_bow(category_manager.strip_document, categories)
        append_discovered_terms_from_elasticsearch(category_manager, classifier_bow)
    category_manager.add_categories_from_bow('onyxcats', classifier_bow)

    return category_manager
