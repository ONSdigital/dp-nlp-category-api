from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from bonn.extract import CategoryManager
from ff_fasttext_api.scripts.ff_fasttext import main

def test_main():
    # Create a mock CategoryManager object to simulate the FastText model
    category_manager = MagicMock(spec=CategoryManager)
    category_manager.test.return_value = [
        (0.9, ['cat1', 'cat2']),
        (0.8, ['cat3']),
    ]

    # Use CliRunner to simulate user input
    runner = CliRunner()
    with patch('ff_fasttext_api.scripts.ff_fasttext.load', return_value=category_manager):
        result1 = runner.invoke(main, input="This is a test sentence.\n")
        result2 = runner.invoke(main, input="Another test sentence.\n")
        result3 = runner.invoke(main, input="\\quit\n")

        assert result1.exit_code == 1
        assert 'cat1->cat2(0.90)' in result1.output
        assert 'cat3(0.80)' in result1.output
        assert result2.exit_code == 1
        assert 'cat1->cat2(0.90)' in result2.output
        assert 'cat3(0.80)' in result2.output
        assert result3.exit_code == 0
