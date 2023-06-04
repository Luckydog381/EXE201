import os
import secrets
from PIL import Image
from exe201 import app, db
from flask import render_template, url_for, redirect, request, flash
from exe201.models import User, Profile, Product, Cart
from exe201.forms import RegisterForm, LoginForm, EditProfile, CreateProduct
from exe201.utils import save_image
from flask_login import login_user, login_required, logout_user, current_user

# Set up the application context
app.app_context().push()

# Create the tables
db.create_all()

def create_product_info():
    product1 = Product(name = 'Bugs bunny 1', image_link = 'img/meme_1.jpg', price = 32, description = 'This is product 1', author = 'admin', owner = None)
    product2 = Product(name = 'Bugs bunny 2', image_link = 'img/meme_2.jpg', price = 10, description = 'This is product 2', author = 'admin 2', owner = None)
    product3 = Product(name = 'Bugs bunny 3', image_link = 'img/meme_3.jpg', price = 50, description = 'This is product 3', author = 'admin 3', owner = None)
    product4 = Product(name = 'Bugs bunny 4', image_link = 'img/meme_4.jpg', price = 100, description = 'This is product 4', author = 'admin', owner = None)

    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(product4)
    db.session.commit()

#create_product_info()

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/contact')
def contact_info():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        if 'login_with_Google' in request.form:
            pass
        elif 'login_with_Facebook' in request.form:
            pass
        else:
            #login and check input information 
            attempted_user = User.query.filter_by(username = form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(
                attempted_password = form.password.data
            ):
                login_user(attempted_user)
                flash(f'Welcome back, {attempted_user.username}', category='success')
                return redirect(url_for('home_page'))
            else:
                flash(f'Username or password is incorrect!', category='danger')
    return render_template('login.html', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    #create new user
    if form.validate_on_submit():
        #create new user
        user_to_create = User(username = form.username.data,
                            password = form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        #create new profile
        profile_to_create = Profile(user_id = user_to_create.id,
                                    fullname = None,
                                    email_address = form.email_address.data,
                                    phone_number = None,
                                    address = None,
                                    city = None,
                                    state = None,
                                    zipcode = None,
                                    country = None,
                                    about_me = None)
        db.session.add(profile_to_create)
        db.session.commit()
        login_user(user_to_create)
        # return to homepage
        return redirect(url_for('edit_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/profile')
@login_required
def profile_page():
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    return render_template('profile.html', user_profile = user_profile)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_page():
    # Query the database to get the user's profile
    profile_to_update = Profile.query.filter_by(user_id=current_user.id).first()
    form = EditProfile(
        fullname = profile_to_update.fullname,
        email_address = profile_to_update.email_address,
        image_link = profile_to_update.image_link,
        phone_number = profile_to_update.phone_number,
        address = profile_to_update.address,
        city = profile_to_update.city,
        state = profile_to_update.state,
        zipcode = profile_to_update.zipcode,
        country = profile_to_update.country,
        about_me = profile_to_update.about_me
        )
    if form.validate_on_submit():
        # Update the profile attributes with the new information from the form
        profile_to_update.fullname = form.fullname.data
        profile_to_update.email_address = form.email_address.data
        profile_to_update.phone_number = form.phone_number.data
        profile_to_update.address = form.address.data
        profile_to_update.city = form.city.data
        profile_to_update.state = form.state.data
        profile_to_update.zipcode = form.zipcode.data
        profile_to_update.country = form.country.data
        profile_to_update.about_me = form.about_me.data

        # Commit the changes to the database
        db.session.commit()
        flash(f'Profile updated!', category='success')
        return redirect(url_for('profile_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', category='danger')
    return render_template('edit_profile.html', form = form, profile_to_update = profile_to_update)

@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def add_product_page():
    form = CreateProduct()
    if form.validate_on_submit():
        #create new product
        product_to_create = Product(name = form.name.data,
                                    image_link = form.image_file.data.filename,
                                    price = form.price.data,
                                    description = form.description.data,
                                    author = current_user.username,
                                    owner = current_user.id)
        db.session.add(product_to_create)
        db.session.commit()
        #save image
        if form.image_file.data:
            #save image
            picture_file = save_image(form.image_file.data, folder = 'static/img')
            product_to_create.image_link = f'img/{picture_file}'
        db.session.commit()
        flash(f'Product added!', category='success')
        return redirect(url_for('marketplace_page'))
    return render_template('create_product.html', form = form)

@app.route('/marketplace')
@login_required
def marketplace_page():
    products = Product.query.all()
    return render_template('marketplace.html', products = products)

@app.route('/marketplace/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_info.html', product = product)

@app.route('/marketplace/<int:product_id>/add_to_cart', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        flash(f'Product already in cart!', category='danger')
    else:
        cart = Cart(user_id = current_user.id, product_id = product_id)
        db.session.add(cart)
        db.session.commit()
        flash(f'Product added to cart!', category='success')
    return redirect(url_for('marketplace_page'))

@app.route('/marketplace/<int:product_id>/remove_from_cart', methods=['GET', 'POST'])
@login_required
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash(f'Product removed from cart!', category='success')
    else:
        flash(f'Product not in cart!', category='danger')
    return redirect(url_for('cart_page'))

@app.route('/cart')
@login_required
def cart_page():
    cart = Cart.query.filter_by(user_id = current_user.id).all()
    products = []
    total_money_without_service_free = 0
    service_fee = 0.1
    for product_in_cart in cart:
        products.append(Product.query.get_or_404(product_in_cart.product_id))
        total_money_without_service_free += Product.query.get_or_404(product_in_cart.product_id).price
    products_amount = len(cart)
    total_money = total_money_without_service_free + total_money_without_service_free * service_fee
    return render_template('cart.html', products = products, cart = cart, products_amount = products_amount, total_money = total_money, service_fee = service_fee)



@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out!', category='info')
    return redirect(url_for('home_page'))
