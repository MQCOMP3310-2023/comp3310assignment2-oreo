from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Restaurant, MenuItem, User, Rating, user_restaurant_association
from sqlalchemy import asc
from . import db
# additional imports
from datetime import datetime
from flask_login import current_user, login_user,login_required, logout_user
from flask import flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

main = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

# Show all restaurants


@main.route('/')
@main.route('/restaurant/')
def showRestaurants():
    restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants=restaurants)


# Create a new restaurant
@main.route('/restaurant/new/', methods=['GET', 'POST'])
@login_required
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        db.session.add(newRestaurant)
        db.session.commit()

        db.session.execute(
            user_restaurant_association.insert().values(
                user_id=current_user.UserID,
                restaurant_id=newRestaurant.id
            )
        )
        db.session.commit()
        current_user.Role = 1  # change the role of the current user
        db.session.commit()  # commit the changes to the database
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        return redirect(url_for('main.showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@main.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    editedRestaurant = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('main.showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteRestaurant(restaurant_id):
    restaurantToDelete = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    ratings = db.session.query(Rating).filter_by(
        restaurant_id=restaurant_id).all()
    if request.method == 'POST':
        for rating in ratings:
            db.session.delete(rating)
        db.session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        db.session.commit()
        return redirect(url_for('main.showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)


# Show a restaurant menu


@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    # additional
    # Check if the user is authenticated
    if current_user.is_authenticated:
        association = db.session.execute(
            user_restaurant_association.select().where(
                (user_restaurant_association.c.user_id == current_user.UserID) &
                (user_restaurant_association.c.restaurant_id == restaurant_id)
            )).first()
        is_owner = association is not None
    else:
        is_owner = False
    return render_template('menu.html', items=items, restaurant=restaurant, is_owner=is_owner)


# Create a new menu item
@main.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
@login_required
def newMenuItem(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form['description'],
                           price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        db.session.add(newItem)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item


@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):

    editedItem = db.session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        db.session.add(editedItem)
        db.session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# Delete a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
# @login_required
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        db.session.delete(itemToDelete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


# ````````````````
# new input


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verify the user credentials
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.PasswordHash, password):
            # Password is correct, log in the user
            login_user(user)
            session['logged_in'] = True
            flash('Logged in successfully.')
            return redirect(url_for('main.showRestaurants'))
        else:
            # Invalid credentials
            flash('Invalid username or password.')

    return redirect(url_for('main.showRestaurants'))


@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('main.showRestaurants'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        password = request.form['password']
        # Check if the password meets the complexity requirements
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return redirect(url_for('main.signup'))

        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.')
            return redirect(url_for('main.signup'))

        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.')
            return redirect(url_for('main.signup'))

        if not re.search(r'\d', password):
            flash('Password must contain at least one number.')
            return redirect(url_for('main.signup'))

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            flash('Password must contain at least one special character.')
            return redirect(url_for('main.signup'))
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('main.signup'))

        # Check if the email or username already exists in the database
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please choose a different email.')
            return redirect(url_for('main.signup'))

        # Create a new user
        new_user = User(
            email=email,
            username=username,
            FirstName=first_name,
            LastName=last_name,
            PasswordHash=generate_password_hash(password),
            Role=0,
            DOB=dob
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Render the login template for GET requests
        flash('Please log in to continue.')
        return redirect('/')

    return render_template('signup.html')


@main.route('/restaurant/<int:restaurant_id>/rate', methods=['POST'])
def rate_restaurant(restaurant_id):
    value = request.form['value']

    # Create a new rating
    new_rating = Rating(value=value, restaurant_id=restaurant_id)
    db.session.add(new_rating)
    db.session.commit()
    flash('Your rating has been submitted.')

    return redirect(url_for('main.showMenu', restaurant_id=restaurant_id))
