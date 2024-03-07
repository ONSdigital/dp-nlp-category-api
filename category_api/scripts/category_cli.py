import traceback

import click
from bonn.extract import load

from category_api.logger import setup_logging

logger = setup_logging()


@click.command()
def main():
    try:
        category_manager = load(settings.FIFU_FILE)
        logger.info(event="Category manager loaded successfully")
    except Exception:
        logger.error(
            event="Failed to load category manager", error=traceback.format_exception()
        )
        return

    word = None
    while word not in ("\\quit", "\\q"):
        word = input("Sentence? ")
        try:
            categories = category_manager.test(word.strip(), "onyxcats")
            categories = [
                "->".join(c[1]) + f"({c[0]:.2f})" for c in categories if c[0] > 0.3
            ][:5]
            logger.info(
                event="Categories found for that specific word",
                data={
                    "word": word,
                    "categories_found": categories,
                },
            )
            print("\n".join(categories))
        except Exception:
            logger.error(
                event="Failed to get categories for input",
                data=word,
                error=traceback.format_exception(),
            )
            continue
