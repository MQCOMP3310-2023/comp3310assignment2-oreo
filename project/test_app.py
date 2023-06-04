import pytest
from flask import Flask, url_for
from . import create_app
from .models import Restaurant, Rating, User, Favorite

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'

    with app.test_client() as client:
        with app.app_context():
            yield client
            
# def test_sql_injection_protection_new_restaurant(client):
#     # Submit a new restaurant with an SQL Injection attempt in its name
#     sql_injection_attempt = "Test'; DROP TABLE users; --"
#     response = client.post(url_for('main.new_restaurant'), data={'name': sql_injection_attempt})

#     # The application should reject the request
#     assert response.status_code == 401 # Unauthorized

#     # Check that the users table still exists
#     try:
#         User.query.first()
#     except Exception as e:
#         pytest.fail(f"SQL Injection attempt succeeded: {e}")

 
def test_homepage_redirect(client):
    # test the home page redirect
    response = client.get('/', follow_redirects = True)
    assert response.status_code == 200


def test_singup_form(client):
    # test the signup form
    response = client.get('/signup')
    assert response.status_code == 200





def test_submit_valid_rating(client):
    # login as public user
    client.post('/login', data={'username': 'public', 'password': 'password'})
    
    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit a valid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 4})
    assert response.status_code == 302  # Redirect to the restaurant menu page

    # Check that the rating was added to the database
    rating = Rating.query.filter_by(restaurant_id=restaurant.id).first()
    assert rating is not None
    assert rating.value == 4

def test_submit_invalid_rating(client):
    # login as public user
    client.post('/login', data={'username': 'public', 'password': 'password'})

    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit an invalid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 6})
    assert response.status_code == 400  # Bad request

def test_signup_with_valid_credentials(client):
    # Submit a valid signup form
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'Password123!'
    })
    assert response.status_code == 302  # Redirect to the main page

def test_signup_with_short_password(client):
    # Submit a signup form with a short password
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'Pass123!'
    })
    assert response.status_code == 400  # Bad request

def test_signup_with_missing_uppercase_letter(client):
    # Submit a signup form with a password missing an uppercase letter
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'password123!'
    })
    assert response.status_code == 400  # Bad request

def test_signup_with_missing_lowercase_letter(client):
    # Submit a signup form with a password missing a lowercase letter
    response = client.post('/signup', data={
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'PASSWORD123!'
    })
    assert response.status_code == 400  # Bad request

