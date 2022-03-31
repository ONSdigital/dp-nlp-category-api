import json
from google.cloud import translate_v2 as translate

CHUNK = 100
TARGET_LANG = "cy"

def run():
    translate_client = translate.Client()
    try:
        with open("cache/cache.json", "r") as f:
            cache = json.load(f)
    except IOError as e:
        print(
            "If you have not yet created a cache in English from "
            "Elasticsearch, you should do so now, by running the "
            "ff_fasttext API in English. This cache will be used for "
            "automatic translation. WARNING: manual translation is "
            "required for production usage."
        )
        raise e

    translation_words = list(set(cache["all-words"].keys()).union({
        w
        for cat, tokens in cache["classifier-bow"]
        for c, w in tokens
    }))
    text = "parents"
    chunked_translation_words = [
        translation_words[i: i+CHUNK]
        for i in range(0, len(translation_words), CHUNK)
    ]
    translation = {}
    for chunk in chunked_translation_words:
        result = translate_client.translate(chunk, target_language="cy", source_language="en")
        translation.update({res["input"]: res["translatedText"] for res in result})

    translated_cache = {
        "lang": TARGET_LANG,
        "config": cache["config"],
        "all-words": {translation[k]: v for k, v in cache["all-words"].items()},
        "classifier-bow": [
            [cat, [[c, translation[w]] for c, w in tokens]]
            for cat, tokens in cache["classifier-bow"]
        ]
    }

    with open(f"cache/cache-{TARGET_LANG}.json", "w") as f:
        json.dump(translated_cache, f)

if __name__ == "__main__":
    run()
