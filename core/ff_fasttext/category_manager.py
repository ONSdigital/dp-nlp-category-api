import numpy as np
import math
import re
from sortedcontainers import SortedDict
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

from .settings import settings
from .utils import cosine_similarities

re_ws = re.compile(r"\s+")
re_num = re.compile(r"[^\w\s\']", flags=re.UNICODE)
THRESHOLD = settings.get("CATEGORY_THRESHOLD", 0.1)
WEIGHTING = settings.get("WEIGHTING", {"C": 2, "SC": 2, "SSC": 1, "WC": 3, "WSSC": 5})
EXTRA_STOPWORDS = {
    "english": ["statistics", "data", "measure", "measures"],
    "welsh": [],
}
EXTRA_STOPWORDS.update(settings.get("EXTRA_STOPWORDS", {}))
STOPWORDS_LANGUAGE = settings.get("STOPWORDS_LANGUAGE", "english")


class WModel:
    def __init__(self, model):
        self.model = model
        self._model_dims = model.get_dims()

    def __getitem__(self, name):
        # Save Rust worrying about lifetime of a numpy array
        a = np.zeros((self._model_dims,), dtype=np.float32)

        self.model.load_embedding(name, a)

        return a


class Category:
    vector = None
    words = None

    def __init__(self, key, bow, model):
        self.key = key
        self.bow = bow

        self._set_vector(model)
        self._set_words()

    def _set_vector(self, model):
        vector = np.mean([WEIGHTING[code] * model[w] for code, w in self.bow], axis=0)
        self.vector = vector / sum([WEIGHTING[code] for code, _ in self.bow])

    def _set_words(self):
        self.words = [w for _, w in self.bow]


class CategoryManager:
    _stop_words = None
    _model = None
    _classifier_bow = None
    _topic_vectors = None

    def __init__(self, word_model):
        self._categories = SortedDict()
        self._model = WModel(word_model)
        self._stop_words = (
            stopwords.words(STOPWORDS_LANGUAGE) + EXTRA_STOPWORDS[STOPWORDS_LANGUAGE]
        )
        self._significance = np.vectorize(
            self._significance_for_vector, signature="(m)->()"
        )
        self._ltzr = WordNetLemmatizer()
        self.all_words = {}

    def set_all_words(self, all_words):
        total = sum(all_words.values())
        scale = lambda c: 0.25 + math.exp(1000 * (1 - c) / total) * 0.75
        self.all_words = {w: scale(c) for w, c in all_words.items()}

    def _scale_by_frequency(self, word):
        lword = self._ltzr.lemmatize(word)
        if lword in self.all_words:
            scale = self.all_words[lword]
            return scale

        return 1.0

    def add_categories_from_bow(self, name, classifier_bow):
        self._categories[name] = SortedDict(
            (k, Category(k, bow, self._model)) for k, bow in classifier_bow.items()
        )

    def closest(self, text, cat, classifier_bow_vec):
        word_list = set(sum(self.strip_document(text), []))
        word_scores = [
            (
                word,
                cosine_similarities(self._model[word], classifier_bow_vec[cat]).mean()
            )
            for word in word_list
            if cat in classifier_bow_vec
        ]
        return [
            word
            for word, score in sorted(
                word_scores, key=lambda word: word[1], reverse=True
            )
            if score > 0.3
        ]

    def strip_document(self, doc):
        if type(doc) is list:
            doc = " ".join(doc)

        docs = doc.split(",")
        word_list = []
        for doc in docs:
            doc = doc.replace("\n", " ").replace("_", " ").replace("'", "").lower()
            doc = re_ws.sub(" ", re_num.sub("", doc)).strip()

            if doc == "":
                return []

            word_list.append([w for w in doc.split(" ") if w not in self._stop_words])

        return word_list

    def test_category(self, sentence, category, category_group="dtcats"):
        cat = self._categories[category_group][category]

        clean = self.strip_document(sentence)

        if not clean:
            return []

        classifiers = {w: WEIGHTING[code] * self._model[w] for code, w in cat.bow}

        tags = {}
        for words in clean:
            if not words:
                continue

            vec = np.mean([self._model[w] for w in words], axis=0)
            result = cosine_similarities(vec, [cat.vector])[0]

            tags[" ".join(words)] = {
                "overall": result,
                "by-classifier": {
                    w: cosine_similarities(vec, [v])[0] for w, v in classifiers.items()
                },
            }

        return {
            "tags": tags,
            "vector": np.linalg.norm(cat.vector),
            "significance": self._significance_for_vector(cat.vector),
            "weightings": {w: WEIGHTING[code] for code, w in cat.bow},
        }

    @staticmethod
    def _significance_for_vector(vector):
        return min(max(0.5, np.linalg.norm(vector) * 1e2), 1.25)

    def test(self, sentence, category_group="dtcats"):
        categories = self._categories[category_group]

        clean = self.strip_document(sentence)

        if not clean:
            return []

        topic_vectors = np.array([c.vector for c in categories.values()])
        significance = self._significance(topic_vectors)

        tags = set()
        for words in clean:
            if not words:
                continue

            vec = np.mean(
                [self._model[w] * self._scale_by_frequency(w) for w in words], axis=0
            )
            result = cosine_similarities(vec, topic_vectors)
            result = np.multiply(result, significance)

            top = np.nonzero(result > THRESHOLD)[0]

            tags.update({(result[i], categories.keys()[i]) for i in top})

        return sorted(tags, reverse=True)
