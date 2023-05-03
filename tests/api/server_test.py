import pytest
from fastapi.testclient import TestClient
from ff_fasttext_api.server import make_app
from unittest.mock import MagicMock
from bonn.extract import CategoryManager
from ff_fasttext_api.healthcheck import Healthcheck

@pytest.fixture(scope='module')
def test_client():
    # Create a mock CategoryManager object to simulate the FastText model
    category_manager = MagicMock(spec=CategoryManager)
    category_manager.test.return_value = [
        (0.9, ['cat1', 'cat2']),
        (0.8, ['cat3']),
    ]

    health = MagicMock(spec=Healthcheck)
    app = make_app(category_manager, health)
    client = TestClient(app)
    yield client


def test_health_check(test_client):
    response = test_client.get('/health')
    assert response.status_code == 200

def test_get_categories(test_client):
    response = test_client.get('/categories?query=test')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_category(test_client):
    response = test_client.get('/categories/healthandsocialcare?query=dentist')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
