from . import db

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    # new input 
    owner_id = db.Column(db.Integer, db.ForeignKey('users.UserID'))
    owner = db.relationship('User', backref='restaurants')

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }
 
class MenuItem(db.Model):
    name = db.Column(db.String(80), nullable = False)
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer,db.ForeignKey('restaurant.id'))
    restaurant = db.    relationship(Restaurant)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'       : self.name,
           'description' : self.description,
           'id'         : self.id,
           'price'      : self.price,
           'course'     : self.course,
       }


# general work - everything below is not original 

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    FirstName = db.Column(db.String(250), nullable=False)
    LastName = db.Column(db.String(250), nullable=False)
    Type = db.Column(db.Integer, nullable=False)
    DOB = db.Column(db.DateTime, nullable=False)


    def __repr__(self):
        return '<User {}>'.format(self.username)

    # Store the hashed password in the database
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify the password entered by the user
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

