from exe201 import app, db
from flask import render_template, url_for, redirect, request, flash
from exe201.models import User, Profile, Product, Cart, Artist
from exe201.forms import RegisterForm, LoginForm, EditProfile, CreateProduct
from exe201.utils import save_image, create_product_info
from flask_login import login_user, login_required, logout_user, current_user
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest

# Set up the PayPal environment
client_id = 'ARafNYmSC69Xd-E6zTtV5FI0NXOaDduq4f8ow6EB8OPeJg_4HTDeclFQDY5spcxp77P9FJoQu-b2gkBj'
client_secret = 'EDeLFTm97h2nFd15IdI1bo8X8N9nX4ZWLhRsN66eZuZqYgKmr8b9i4939N0XP3mVoy88ao0cl0Boq_7I'
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)


# Set up the application context
app.app_context().push()

# Create the tables
db.create_all()

#create_product_info()

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/aboutus')
def about_us_page():
    return render_template('about_us.html')

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
                            email_address = form.email_address.data,
                            password = form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        #create new profile
        profile_to_create = Profile(user_id = user_to_create.id,
                                    fullname = None,
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
        return redirect(url_for('edit_profile'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/profile/<int:user_id>')
@login_required
def profile_page(user_id):
    user_profile = Profile.query.filter_by(user_id=user_id).first()
    user_email_address = User.query.filter_by(id=user_id).first().email_address

    # Get the user's role
    user_role = Artist.query.filter_by(user_id=user_id).first()
    if user_role:
        user_role = user_role.role
    else:
        user_role = 'Customer'

    # Check if user in the artist list
    artist_products = None
    if Artist.query.filter_by(user_id=user_id).first():
        # Get the artist's products
        artist_products = Product.query.filter_by(creator=user_id).all()
        return render_template('profile.html', user_profile = user_profile, user_email_address = user_email_address, user_role = user_role, artist_products = artist_products)

    return render_template('profile.html', user_profile = user_profile, user_email_address = user_email_address, user_role = user_role)

@app.route('/setting/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Query the database to get the user's profile
    profile_to_update = Profile.query.filter_by(user_id=current_user.id).first()
    user_image_link = User.query.filter_by(id=current_user.id).first().image_link
    user_email_address = User.query.filter_by(id=current_user.id).first().email_address
    # Create a form object and pass in the user's profile
    form = EditProfile(
        fullname = profile_to_update.fullname,
        email_address = user_email_address,
        phone_number = profile_to_update.phone_number,
        address = profile_to_update.address,
        city = profile_to_update.city,
        state = profile_to_update.state,
        zipcode = profile_to_update.zipcode,
        country = profile_to_update.country,
        about_me = profile_to_update.about_me
    )
    
    if form.validate_on_submit():
        # Check if the form has a picture
        if form.image_file.data:
            # Save the picture and get the saved picture's filename
            picture_file = save_image(form.image_file.data, folder = 'static/profile_img')
            # Update the profile's image link with the new picture
            user_image_link = f'profile_img/{picture_file}'
            # Update the user's image link in the database
            user_to_update = User.query.filter_by(id=current_user.id).first()
            user_to_update.image_link = user_image_link
            db.session.commit()
            



        # Update the profile attributes with the new information from the form
        profile_to_update.fullname = form.fullname.data
        user_email_address = form.email_address.data
        profile_to_update.image_link = user_image_link
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
        return redirect(url_for('profile_page', user_id = current_user.id))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', category='danger')
    return render_template('edit_profile.html', 
                           form = form, 
                           profile_to_update = profile_to_update, 
                           user_image_link = user_image_link
                           )

@app.route('/create_product', methods=['GET', 'POST'])
@login_required
def create_product_page():
    form = CreateProduct()
    if form.validate_on_submit():
        #create new product
        product_to_create = Product(name = form.name.data,
                                    image_link = form.image_file.data.filename,
                                    price = form.price.data,
                                    description = form.description.data,
                                    creator = current_user.id)
        db.session.add(product_to_create)
        db.session.commit()
        #save image
        if form.image_file.data:
            #save image
            picture_file = save_image(form.image_file.data, folder = 'static/img')
            product_to_create.image_link = f'img/{picture_file}'
        db.session.commit()
        flash(f'Product added!', category='success')
        return redirect(url_for('gallery_page'))
    return render_template('create_product.html', form = form)

@app.route('/gallery')
def gallery_page():
    # Query the database to get all the products
    products = Product.query.all()
    # Fetch the creator's name of each product
    for product in products:
        product.creator = Artist.query.filter_by(id=product.creator).first().user_id
    # Fetch the creator's profile of each product
    for product in products:
        product.creator = Profile.query.filter_by(user_id=product.creator).first().fullname
    
    # Query the database to get all the artists
    # Get all artists user id
    artists_user_id = []
    for artist_id in Artist.query.all():
        artists_user_id.append(User.query.get_or_404(artist_id.user_id))
    # Get all artists profile
    artists_user_profile = []
    for artist in artists_user_id:
        artists_user_profile.append(Profile.query.filter_by(user_id=artist.id).first())
    # Fetch the artist role
    for i in range(len(artists_user_id)):
        artists_user_profile[i].role = Artist.query.filter_by(user_id=artists_user_id[i].id).first().role
    
    return render_template('gallery.html', 
                           products = products, 
                           artists_user_profile = artists_user_profile)

@app.route('/gallery/<int:product_id>', methods=['GET', 'POST'])
def product_page(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_info.html', product = product)

@app.route('/gallery/<int:product_id>/add_to_cart', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        flash(f'Product already in cart!', category='danger')
    else:
        cart = Cart(user_id = current_user.id, product_id = product_id)
        db.session.add(cart)
        db.session.commit()
        flash(f'Product was added to cart!', category='success')
    return redirect(url_for('gallery_page'))

@app.route('/gallery/<int:product_id>/remove_from_cart', methods=['GET', 'POST'])
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
    service_fee *= total_money_without_service_free
    total_money = total_money_without_service_free + service_fee
    service_fee = '{:.2f}'.format(service_fee)
    return render_template('cart.html', 
                           products = products,
                           cart = cart, 
                           products_amount = products_amount,  
                           service_fee = service_fee,
                           total_money = total_money, 
                           total_money_without_service_free = total_money_without_service_free
                           )

# Create chat page
@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

# Paypal payment
# Define the PayPal checkout route
@app.route('/paypal_checkout', methods=['POST'])
@login_required
def paypal_checkout():
    # Get the total amount and service fee from the form data
    total_money = request.form['total_money']

    # Create an order request
    request = OrdersCreateRequest()
    request.prefer('return=representation')
    request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": str(total_money)
                }
            }
        ]
    })

    # Call the PayPal API to create the order
    response = client.execute(request)

    # Get the approval URL from the response
    approval_url = None
    for link in response.result.links:
        if link.rel == "approve":
            approval_url = link.href
            break

    # Redirect the user to the approval URL
    if approval_url:
        flash(f'Payment successful!', category='success')
        return redirect(approval_url)
    else:
        flash(f'Payment failed!', category='danger')
        return "Failed to create PayPal order"

@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out!', category='info')
    return redirect(url_for('home_page'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
@app.errorhandler(401)
def page_forbidden(e):
    flash(f'You need to login to use your service!', category='danger')
    return redirect(url_for('login_page'))