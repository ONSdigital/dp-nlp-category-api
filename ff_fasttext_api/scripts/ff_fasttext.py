import click

from ff_fasttext.extract import load
from ff_fasttext_api.logger import configure_logging, setup_logger

configure_logging()
logger = setup_logger(severity=0)

@click.command()
def main():
    category_manager = load('test_data/wiki.en.fifu')
    logger.info(event="Catageory manager loaded successfully")
    word = None
    while word not in ('\\quit', '\\q'):
        word = input("Sentence? ")
        categories = category_manager.test(word.strip(), 'onyxcats')
        categories = ['->'.join(c[1]) + f'({c[0]:.2f})' for c in categories if c[0] > 0.3][:5]
        logger.info(
            event="Categories found for that specific word",
            word=word,
            categories_found=categories
        )

        print('\n'.join(categories))
