from flask import Blueprint, render_template, request, flash, redirect, url_for, session,make_response
from .models import Restaurant, MenuItem, User, Rating, user_restaurant_association
from sqlalchemy import asc
from . import db
# additional imports
from flask_login import current_user, login_user,login_required, logout_user
from flask import flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import re

main = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

# Show all restaurants

main_show_restaurants = 'main.show_restaurants'        #created new variable to reference 'main.show.resturants

@main.route('/')
@main.route('/restaurant/')
def show_restaurants():      #Fixed the naming conventions
    restaurants = db.session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants=restaurants)


# Create a new restaurant
@main.route('/restaurant/new/', methods=['GET', 'POST'])
@login_required
def new_restaurant():     #Fixed the naming conventions
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'])
        db.session.add(new_restaurant)      #Fixed the naming conventions
        db.session.commit()

        db.session.execute(
            user_restaurant_association.insert().values(
                user_id=current_user.UserID,
                restaurant_id=new_restaurant.id     #Fixed the naming conventions
            )
        )
        db.session.commit()
        if current_user.Role == 0:
            current_user.Role = 1  # change the role of the current user
        db.session.commit()  # commit the changes to the database
        flash('New Restaurant %s Successfully Created' % new_restaurant.name)       #Fixed the naming conventions
        return redirect(url_for(main_show_restaurants))       #Fixed the naming conventions
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@main.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_restaurant(restaurant_id):  #Fixed the naming conventions
    
    # Check if the current user is the owner of the restaurant
    association = db.session.execute(
        user_restaurant_association.select().where(
            (user_restaurant_association.c.user_id == current_user.UserID) &
            (user_restaurant_association.c.restaurant_id == restaurant_id)
        )).first()
    
    if current_user.Role != 2:
        if not association:
            abort(403) # Forbidden
    
    edited_restaurant = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_restaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % edited_restaurant.name)
            db.session.commit()
            return redirect(url_for(main_show_restaurants))    #Fixed the naming conventions
    else:
        return render_template('editRestaurant.html', restaurant=edited_restaurant)


# Delete a restaurant
@main.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_restaurant(restaurant_id):       #Fixed the naming conventions
    
    # Check if the current user is the owner of the restaurant
    association = db.session.execute(
        user_restaurant_association.select().where(
            (user_restaurant_association.c.user_id == current_user.UserID) &
            (user_restaurant_association.c.restaurant_id == restaurant_id)
        )).first()
    
    if current_user.Role != 2:
        if not association:
            abort(403) # Forbidden
    
    restaurant_to_delete = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    ratings = db.session.query(Rating).filter_by(
        restaurant_id=restaurant_id).all()
    menu_items = db.session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    if request.method == 'POST':
        for rating in ratings:
            db.session.delete(rating)
        for menu_item in menu_items:
            db.session.delete(menu_item)
        db.session.delete(restaurant_to_delete)
        flash('%s Successfully Deleted' % restaurant_to_delete.name)
        db.session.commit()
        return redirect(url_for(main_show_restaurants, restaurant_id=restaurant_id))           #Fixed the naming conventions
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurant_to_delete)


# Show a restaurant menu

main_show_menu ='main.show_menu'     #created new variable to reference main.show.menu

@main.route('/restaurant/<int:restaurant_id>/')
@main.route('/restaurant/<int:restaurant_id>/menu/')
def show_menu(restaurant_id):       #Fixed the naming conventions
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
def new_menu_item(restaurant_id):   #Fixed the naming conventions
    
    # Check if the current user is the owner of the restaurant
    association = db.session.execute(
        user_restaurant_association.select().where(
            (user_restaurant_association.c.user_id == current_user.UserID) &
            (user_restaurant_association.c.restaurant_id == restaurant_id)
        )).first()
    
    if current_user.Role != 2:
        if not association:
            abort(403) # Forbidden
    
    # restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()           #UNUSED VARIABLE
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        course = request.form.get('course')
        if not name or not description or not price or not course:
            flash('All fields are required.')
            return render_template('newmenuitem.html', restaurant_id=restaurant_id)
        new_item = MenuItem(name=request.form['name'], description=request.form['description'],
                           price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        db.session.add(new_item)
        db.session.commit()
        flash('New Menu %s Item Successfully Created' % (new_item.name))
        return redirect(url_for(main_show_menu, restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item


@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_item(restaurant_id, menu_id):  #Fixed the naming conventions

    # Check if the current user is the owner of the restaurant
    association = db.session.execute(
        user_restaurant_association.select().where(
            (user_restaurant_association.c.user_id == current_user.UserID) &
            (user_restaurant_association.c.restaurant_id == restaurant_id)
        )).first()
    
    if current_user.Role != 2:
        if not association:
            abort(403) # Forbidden
        
    edited_item = db.session.query(MenuItem).filter_by(id=menu_id).one()
    # restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()           #UNUSED VARIABLE
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['price']:
            edited_item.price = request.form['price']
        if request.form['course']:
            edited_item.course = request.form['course']
        db.session.add(edited_item)
        db.session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for(main_show_menu, restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=edited_item)


# Delete a menu item
@main.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
# @login_required
def delete_menu_item(restaurant_id, menu_id):        #Fixed the naming conventions
    # restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()               #UNUSED VARIABLE
    
    # Check if the current user is the owner of the restaurant
    association = db.session.execute(
        user_restaurant_association.select().where(
            (user_restaurant_association.c.user_id == current_user.UserID) &
            (user_restaurant_association.c.restaurant_id == restaurant_id) 
        )).first()
    
    if current_user.Role != 2:
        if not association:
            abort(403) # Forbidden

    item_to_delete = db.session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for(main_show_menu, restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=item_to_delete)


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
            return redirect(url_for(main_show_restaurants))        #Fixed the naming conventions
        else:
            # Invalid credentials
            flash('Invalid username or password.')

    return redirect(url_for(main_show_restaurants))        #Fixed the naming conventions


@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for(main_show_restaurants))        #Fixed the naming conventions


signup_html = 'signup.html'    #created new variable to reference signup.html

# sensitive information non required removed
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Check if the password meets the complexity requirements
        # was advised to look into nist 800 and seems its already meeting the requirements excluding repeating letters and dictionaries to show weaknesses 
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        if not re.search(r'\d', password):
            flash('Password must contain at least one number.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            flash('Password must contain at least one special character.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        # Check if the email or username already exists in the database
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please choose a different email.')
            response = make_response(render_template(signup_html))
            response.status_code = 400
            return response

        # Create a new user
        new_user = User(
            email=email,
            username=username,
            PasswordHash=generate_password_hash(password),
            Role=0,
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Render the login template for GET requests
        flash('Please log in to continue.')
        return redirect('/')

    return render_template(signup_html)


@main.route('/restaurant/<int:restaurant_id>/rate', methods=['POST'])
def rate_restaurant(restaurant_id):
    # only normal users can do thsi 
    if current_user.Role != 0:
        abort(403)  # Forbidden

    # Check if the current user has already rated the restaurant
    existing_rating = db.session.query(Rating).filter_by(
        restaurant_id=restaurant_id, user_id=current_user.UserID).first()
    if existing_rating:
        flash('You have already submitted a rating for this restaurant.')
        return redirect(url_for(main_show_menu, restaurant_id=restaurant_id))

    value = int(request.form['value'])
    
    # Check if the rating value is between 1 and 5
    if value < 1 or value > 5:
        abort(400)

    # Create a new rating
    new_rating = Rating(value=value, restaurant_id=restaurant_id)
    db.session.add(new_rating)
    db.session.commit()
    flash('Your rating has been submitted.')

    return redirect(url_for(main_show_menu, restaurant_id=restaurant_id))
