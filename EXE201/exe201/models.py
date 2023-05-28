from exe201 import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length=30), nullable = False, unique = True)
    email_address = db.Column(db.String(length=50), nullable = False, unique = True)
    password_hash = db.Column(db.String(length=60), nullable = False)

    #setter & getter
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        #decode password
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

'''
class Product(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    resource_id = db.Column(db.Integer())
    product_name = db.Column(db.String(length = 30), nullable = False, unique = False)
    author = db.Column(db.String(length = 30), nullable = False)
    release_date = db.Column(db.DateTime(), nullable = False)
    price = db.Column(db.Integer(), nullable = False)

class Resources(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    description = db.Column(db.String(1000), nullable = False)
    image_link = db.Column(db.String(300), nullable = False)
'''

class Profile(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    fullname = db.Column(db.String(length = 30), nullable = True)
    email_address = db.Column(db.String(length = 50), nullable = True, unique = True)
    phone_number = db.Column(db.String(length = 10), nullable = True, unique = True)
    address = db.Column(db.String(length = 100), nullable = True)
    city = db.Column(db.String(length = 30), nullable = True)
    state = db.Column(db.String(length = 30), nullable = True)
    zipcode = db.Column(db.String(length = 5), nullable = True)
    country = db.Column(db.String(length = 30), nullable = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref = 'profile', uselist = False)
