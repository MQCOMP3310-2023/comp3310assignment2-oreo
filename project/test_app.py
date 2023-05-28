import pytest
from flask import Flask, url_for
from . import create_app
from .models import Restaurant, Rating

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_submit_valid_rating(client):
    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit a valid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 5})
    assert response.status_code == 302  # Redirect to the restaurant menu page

    # Check that the rating was added to the database
    rating = Rating.query.filter_by(restaurant_id=restaurant.id).first()
    assert rating is not None
    assert rating.value == 4

def test_submit_invalid_rating(client):
    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit an invalid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 6})
    assert response.status_code == 400  # Bad request

def test_submit_multiple_ratings(client):
    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit a valid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 5})
    assert response.status_code == 302  # Redirect to the restaurant menu page

    # Submit another rating for the same restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 4})
    assert response.status_code == 400  # Bad request
