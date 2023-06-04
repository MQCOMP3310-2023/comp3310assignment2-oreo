import pytest
from flask import Flask, url_for
from . import create_app
from project.models import User
from .models import Restaurant, Rating, User, Favorite
from werkzeug.security import check_password_hash

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost.localdomain'

    with app.test_client() as client:
        with app.app_context():
            yield client

def test_homepage_redirect(client):
    # test the home page redirect
    response = client.get('/', follow_redirects = True)
    assert response.status_code == 200


def test_singup_form(client):
    # test the signup form
    response = client.get('/signup')
    assert response.status_code == 200

def test_submit_invalid_rating(client):
    # login as public user
    client.post('/login', data={'username': 'public', 'password': 'password'})

    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None

    # Submit an invalid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 6})
    assert response.status_code == 400  # Bad request

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
    
def test_resubmitting_rating_not_allowed(client):
    # login as public user
    client.post('/login', data={'username': 'public', 'password': 'password'})
    
    # Get a restaurant to rate
    restaurant = Restaurant.query.first()
    assert restaurant is not None
    
    existing_ratings_count = Rating.query.filter_by(restaurant_id=restaurant.id).count()

    # Submit a valid rating for the restaurant
    response = client.post(url_for('main.rate_restaurant', restaurant_id=restaurant.id), data={'value': 5}, follow_redirects=True)
    
    # Check if there's a message "You have already submitted a rating for this restaurant."
    assert b'You have already submitted a rating for this restaurant.' in response.data

    # Check if the total number of ratings for the restaurant has not increased
    new_ratings_count = Rating.query.filter_by(restaurant_id=restaurant.id).count()
    assert new_ratings_count == existing_ratings_count

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


def test_sql_injection_attack(client):
    #test for sql injection attack
    response = client.post('/signup', data = {
        'email' : 'userhacker@test.com"; drop table user; -- ',
        'name' : 'hacker101',
        'password' : 'Test123!45'
    }, follow_redirects = True)
    assert response.status_code == 400 


def test_hashed_passwords(client):
    response = client.post('/signup', data={
        'email': 'hashuser@example.com',
        'username': 'hashuser',
        'password': 'Hashuser!2345'
    })
    assert response.status_code == 302


    user = User.query.filter_by(email='hashuser@example.com').first()
    assert user is not None
    assert check_password_hash(user.PasswordHash, 'Hashuser!2345')
