import pytest
from click.testing import CliRunner
from ff_fasttext_api.scripts.ff_fasttext import main
from ff_fasttext.extract import load

@pytest.fixture
def category_manager():
    return load('test_data/wiki.en.fifu')

def test_main():

    assert 0 == 0