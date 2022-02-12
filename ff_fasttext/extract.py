import os
from collections import Counter
from elasticsearch2 import Elasticsearch
from elasticsearch_dsl import Search, Q
from nltk import download

from ._ff_fasttext import FfModel
from .category_manager import CategoryManager
from .taxonomy import get_taxonomy, taxonomy_to_categories, categories_to_classifier_bow

APPEARANCE_THRESHOLD = 5
UPPER_APPEARANCE_THRESHOLD = 10
HOST = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX', 'ons1639492069322')

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
    for hit in s.scan():
        try:
            datasets[hit.description.title] = {
                'category': tuple(hit.uri.split('/')[1:4]),
                'text': f'{hit.description.title} {hit.description.metaDescription}'
            }
            datasets[hit.description.title]['bow'] = cm.closest(datasets[hit.description.title]['text'], datasets[hit.description.title]['category'], classifier_bow_vec)
        except AttributeError as e:
            pass
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

    classifier_bow = categories_to_classifier_bow(category_manager.strip_document, categories)
    append_discovered_terms_from_elasticsearch(category_manager, classifier_bow)
    category_manager.add_categories_from_bow('onyxcats', classifier_bow)

    return category_manager
