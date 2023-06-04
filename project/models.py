from . import db
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

user_restaurant_association = Table('user_restaurant_association', db.Model.metadata,
                                    Column('user_id', Integer,
                                           ForeignKey('Users.UserID')),
                                    Column('restaurant_id', Integer,
                                           ForeignKey('restaurant.id'))
                                    )


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    owners = db.relationship(
        'User', secondary=user_restaurant_association, overlaps="restaurant")
    favorites = db.relationship('Favorite', back_populates='restaurant')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(db.Model):
    name = db.Column(db.String(80), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.    relationship(Restaurant)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


# general work - everything below is not original

# sensitive information that shouldnt be stored removed
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    Role = db.Column(db.Integer, nullable=False)
    restaurants = db.relationship(
        'Restaurant', secondary=user_restaurant_association, overlaps="owners")
    favorites = db.relationship('Favorite', back_populates='user')

    @property
    def is_active(self):
        # Return True if the user account is active
        return True

    def get_id(self):
        return str(self.UserID)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    # Store the hashed password in the database
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify the password entered by the user
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey(
        'restaurant.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'Users.UserID'), nullable=True)
    restaurant = db.relationship(
        'Restaurant', backref=db.backref('restaurant_ratings', lazy=True))


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))

    user = db.relationship('User', back_populates='favorites')
    restaurant = db.relationship('Restaurant', back_populates='favorites')
