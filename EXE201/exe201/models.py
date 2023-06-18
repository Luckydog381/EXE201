from exe201 import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(length=30), nullable = False, unique = True)
    email_address = db.Column(db.String(length=50), nullable = False, unique = True)
    image_link = db.Column(db.String(length = 300), nullable = True, default = '/profile_img/default.webp')
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

class Profile(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    fullname = db.Column(db.String(length = 30), nullable = True)
    image_link = db.Column(db.String(length = 300), nullable = True, default = '/profile_img/default.webp')
    phone_number = db.Column(db.String(length = 10), nullable = True, unique = True)
    address = db.Column(db.String(length = 100), nullable = True)
    city = db.Column(db.String(length = 30), nullable = True)
    state = db.Column(db.String(length = 30), nullable = True)
    zipcode = db.Column(db.String(length = 5), nullable = True)
    country = db.Column(db.String(length = 30), nullable = True)
    about_me = db.Column(db.String(length = 1000), nullable = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

class Artist(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role = db.Column(db.String(length = 30), nullable = False)
    created_product = db.relationship('Product', backref='owned_artist', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(length = 30), nullable = False)
    image_link = db.Column(db.String(length = 300), nullable = True, default = 'meme_1.jpg')
    price = db.Column(db.Integer(), nullable = False)
    description = db.Column(db.String(length = 1000), nullable = True)
    creator = db.Column(db.Integer(), db.ForeignKey('artist.id'))
    
class Cart(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer(), nullable = False, default = 1)
    
class Order(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    status = db.Column(db.String(length = 30), nullable = False, default = 'Pending')
    created_at = db.Column(db.DateTime(), nullable = False, default = datetime.utcnow)
    total_price = db.Column(db.Integer(), nullable = False, default = 0)
    order_payment_content = db.Column(db.String(length = 1000), nullable = True)
    #order = db.relationship('Order', backref='owned_user', lazy=True)
    #order = db.relationship('Order', backref='owned_product', lazy=True)