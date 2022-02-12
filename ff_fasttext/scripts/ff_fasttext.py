import click

from ff_fasttext.extract import load

@click.command()
def main():
    category_manager = load('test_data/wiki.en.fifu')
    word = None
    while word not in ('\\quit', '\\q'):
        word = input("Sentence? ")
        categories = category_manager.test(word.strip(), 'onyxcats')
        categories = ['->'.join(c[1]) + f'({c[0]:.2f})' for c in categories if c[0] > 0.3][:5]
        print('\n'.join(categories))
