from exe201 import app, db
from flask import render_template, url_for, redirect, request, flash
from exe201.models import User, Profile, Product, Cart, Artist, Order
from exe201.forms import RegisterForm, LoginForm, EditProfile, CreateProduct
from exe201.utils import save_image
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import random
'''
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest

# Set up the PayPal environment
client_id = 'ARafNYmSC69Xd-E6zTtV5FI0NXOaDduq4f8ow6EB8OPeJg_4HTDeclFQDY5spcxp77P9FJoQu-b2gkBj'
client_secret = 'EDeLFTm97h2nFd15IdI1bo8X8N9nX4ZWLhRsN66eZuZqYgKmr8b9i4939N0XP3mVoy88ao0cl0Boq_7I'
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)
'''

# Set up the application context
app.app_context().push()

# Create the tables
db.create_all()

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/aboutus')
def about_us_page():
    return render_template('about_us.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Check if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))

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
    # Check if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('gallery_page'))
    
    # Create form to create new user
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
   
    artist_products = Product.query.filter_by(creator=user_id).all()
    if artist_products:
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
        cart_item.quantity += 1
        db.session.commit()
        flash(f'Product was added to cart!', category='success')
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

@app.route('/gallery/<int:product_id>/increase_quantity', methods=['GET', 'POST'])
@login_required
def increase_quantity(product_id):
    cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        cart_item.quantity += 1
        db.session.commit()
    else:
        flash(f'Product not in cart!', category='danger')
    return redirect(url_for('cart_page'))

@app.route('/gallery/<int:product_id>/decrease_quantity', methods=['GET', 'POST'])
@login_required
def decrease_quantity(product_id):
    cart_item = Cart.query.filter_by(user_id = current_user.id, product_id = product_id).first()
    if cart_item:
        cart_item.quantity -= 1
        if cart_item.quantity == 0:
            db.session.delete(cart_item)
            flash(f'Product removed from cart!', category='success')
        db.session.commit()
    else:
        flash(f'Product not in cart!', category='danger')
    return redirect(url_for('cart_page'))

@app.route('/cart')
@login_required
def cart_page():
    # Query the database to get all the products in cart
    cart = Cart.query.filter_by(user_id = current_user.id).all()

    # Fetch the products and prices
    products = []
    total_money_without_service_free = 0
    service_fee = 0.1
    for product_in_cart in cart:
        products.append(Product.query.get_or_404(product_in_cart.product_id))
        total_money_without_service_free += (Product.query.get_or_404(product_in_cart.product_id).price * product_in_cart.quantity)

    for i in range(len(products)):
        products[i].quantity = cart[i].quantity
        products[i].creator = Profile.query.filter_by(id=products[i].creator).first().fullname

    # Count total amount of products in cart
    products_amount = len(cart)

    # Calculate total money
    service_fee *= total_money_without_service_free
    total_money = total_money_without_service_free + service_fee
    service_fee = '{:.2f}'.format(service_fee)

    # Create the order content
    order_content = ''
    # Get the current username
    username = User.query.get_or_404(current_user.id).username
    # Generate random 4 digit numbers
    order_id = random.randint(1000, 9999)
    order_content += username+ ' ' + str(order_id)

    return render_template('cart.html', 
                           products = products,
                           cart = cart, 
                           products_amount = products_amount,  
                           service_fee = service_fee,
                           total_money = total_money, 
                           total_money_without_service_free = total_money_without_service_free,
                           order_content = order_content
                           )

# Create chat page
@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

'''
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
'''

# Create order 
@app.route('/create_order/<string:order_content>/<int:total_money>', methods=['GET', 'POST'])
@login_required
def create_order(order_content, total_money):
    # if there is no product in cart
    if total_money == 0:
        flash(f'You have no product in cart!', category='danger')
        return redirect(url_for('cart_page'))
    else:
        # Get buyer id
        buyer_id = current_user.id
        # Get order created time
        created_time = datetime.now()
        # Get order status
        order_status = 'Pending'
        # Create order
        order = Order(
            user_id = buyer_id, 
            created_at = created_time, 
            total_price = total_money, 
            order_payment_content = order_content, 
            status = order_status,
            )
        db.session.add(order)
        db.session.commit()
        flash(f'Order created! Please wait for our side to confirm your purchase', category='success')
        return redirect(url_for('purchase_success_page'))

@app.route('/purchase-success')
@login_required
def purchase_success_page():
    return render_template('purchase_success.html')

@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out!', category='info')
    return redirect(url_for('home_page'))


# Dash board
@app.route('/dash_board')
def dash_board_page():
    return render_template('dash_board_main.html')

@app.route('/dash_board/orders')
def dash_board_orders_page():
    # Fetch all orders
    orders = Order.query.all()
    for order in orders:
        order.user_image_link = Profile.query.filter_by(user_id=order.user_id).first().image_link
        order.fullname = Profile.query.filter_by(user_id=order.user_id).first().fullname
    
    # Fetch all products in the order's cart
    for order in orders:
        cart = Cart.query.filter_by(user_id = order.user_id).all()
        order.cart = cart
        for product in order.cart:
            product.name = Product.query.filter_by(id=product.product_id).first().name
            product.price = Product.query.filter_by(id=product.product_id).first().price
            product.image_link = Product.query.filter_by(id=product.product_id).first().image_link
            product.quantity = Cart.query.filter_by(user_id=order.user_id, product_id=product.product_id).first().quantity
        
    return render_template('dash_board_orders.html', orders = orders)

@app.route('/dash_board/orders/<string:order_id>/delete')
def dash_board_order_delete(order_id):
    order_id = int(order_id)
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash(f'Order deleted!', category='success')
    return redirect(url_for('dash_board_orders_page'))

@app.route('/dash_board/orders/<string:order_id>/confirm')
def dash_board_order_confirm(order_id):
    order_id = int(order_id)
    order = Order.query.get_or_404(order_id)
    order.status = 'Confirmed'
    db.session.commit()
    flash(f'Order confirmed!', category='success')
    return redirect(url_for('dash_board_orders_page'))


@app.route('/dash_board/products')
def dash_board_products_page():
    # Get all products
    products = Product.query.all()
    for product in products:
        product.creator = Profile.query.filter_by(id=product.creator).first().fullname
    return render_template('dash_board_products.html', products = products)

@app.route('/dash_board/products/<string:product_id>/delete')
def dash_board_product_delete(product_id):
    product_id = int(product_id)
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product deleted!', category='success')
    return redirect(url_for('dash_board_products_page'))

@app.route('/dash_board/users')
def dash_board_users_page():
    # Get all users
    users = User.query.all()
    for user in users:
        user.fullname = Profile.query.filter_by(id=user.id).first().fullname
        user.about_me = Profile.query.filter_by(id=user.id).first().about_me
        user.phone_number = Profile.query.filter_by(id=user.id).first().phone_number
    return render_template('dash_board_users.html', users = users)

@app.route('/dash_board/users/<string:user_id>/delete')
def dash_board_user_delete(user_id):
    user_id = int(user_id)
    
    # Delete user
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    # Delete profile associated with user
    profile = Profile.query.filter_by(user_id = user.id).first()
    db.session.delete(profile)
    db.session.commit()

    # Delete cart associated with user
    cart = Cart.query.filter_by(user_id = user_id).all()
    for cart_item in cart:
        db.session.delete(cart_item)
        db.session.commit()

    # Delete order associated with user
    orders = Order.query.filter_by(user_id = user_id).all()
    for order in orders:
        db.session.delete(order)
        db.session.commit()

    # Check if user is artist, delete artist associated with user
    artist = Artist.query.filter_by(user_id = user_id).first()
    if artist:
        db.session.delete(artist)
        db.session.commit()

    # Delete product associated with user
    products = Product.query.filter_by(creator = user_id).all()
    for product in products:
        db.session.delete(product)
        db.session.commit()

    flash(f'User deleted!', category='success')
    return redirect(url_for('dash_board_users_page'))

