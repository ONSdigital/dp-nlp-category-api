import sys
import codecs
import logging
import os
import re
from sortedcontainers import SortedDict
import numpy as np

import json

def get_taxonomy():
    with open('/app/test_data/taxonomy.json', 'r') as f:
        taxonomy = json.load(f)
    return taxonomy

def categories_to_classifier_bow(strip_document, categories):
    classifier_categories = {
        catf: {
            subcatf: {
                subsubcatf: sum([
                    [('C', v) for w in strip_document(cat) for v in w] + 
                    [('SC', v) for w in strip_document(subcat) for v in w] + 
                    [('SSC', v) for w in strip_document(subsubcat) for v in w]], [])
                for subsubcatf, subsubcat in subcat_sub
            }
            for (subcatf, subcat), subcat_sub in cat_sub.items()
        } for (catf, cat), cat_sub in categories.items()
    }
    classifier_bow = SortedDict(sum([[
        [(k, k2, k3), list(v)]
        for k2, c2_dict in c_dict.items()
        for k3, v in c2_dict.items()
    ] for k, c_dict in classifier_categories.items()], []))

    return classifier_bow

def taxonomy_to_categories(taxonomy):
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
    return categories
