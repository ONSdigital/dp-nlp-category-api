import numpy as np
import re
from nltk.corpus import stopwords

from .utils import cosine_similarities

re_ws = re.compile(r'\s+')
re_num = re.compile(r'[^\w\s\']', flags=re.UNICODE)
THRESHOLD = 0.1
WEIGHTING = {
    'C': 2,
    'SC': 2,
    'SSC': 1,
    'WC': 3,
    'WSSC': 5
}
STOPWORDS_LANGUAGE = 'english'

class WModel:
    def __init__(self, model):
        self.model = model
        self._model_dims = model.get_dims()

    def __getitem__(self, name):
        # Save Rust worrying about lifetime of a numpy array
        a = np.zeros((self._model_dims,), dtype=np.float32)

        self.model.load_embedding(name, a)

        return a

class CategoryManager:
    _stop_words = None
    _model = None
    _classifier_bow = None
    _topic_vectors = None

    def __init__(self, word_model):
        self._categories = {}
        self._model = WModel(word_model)
        self._stop_words = stopwords.words(STOPWORDS_LANGUAGE)

    def add_categories_from_bow(self, name, classifier_bow):
        topic_vectors = [
            (np.mean([WEIGHTING[code] * self._model[w] for code, w in l], axis=0), [w for _, w in l]) for k, l in classifier_bow.items()
        ]
        self._categories[name] = (classifier_bow, topic_vectors)

    def closest(self, text, cat, classifier_bow_vec):
        word_list = set(sum(self.strip_document(text), []))
        word_scores = [
            (word,
                cosine_similarities(self._model[word], classifier_bow_vec[cat]).mean()

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
            result = cosine_similarities(vec, [t for t, _ in topic_vectors])

            top = np.nonzero(result > THRESHOLD)[0]

            tags.update({(result[i], classifier_bow.keys()[i]) for i in top})

        return sorted(tags, reverse=True)

