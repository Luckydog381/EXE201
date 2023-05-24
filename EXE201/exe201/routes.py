from exe201 import app, db
from flask import render_template, url_for, redirect
from exe201.models import User
from exe201.forms import RegisterForm, LoginForm
from flask_login import login_user, login_required, logout_user, current_user

# Set up the application context
app.app_context().push()

# Create the tables
db.create_all()


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
        attempted_user = User.query.filter_by(username = form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password = form.password.data
        ):
            print("Login successfully!")
            login_user(attempted_user)
            return redirect(url_for('home_page'))
        else:
            print("wrong password or username!")
    return render_template('login.html', form = form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    #create new user
    if form.validate_on_submit():
        print("processing!")
        user_to_create = User(username = form.username.data,
                              email_address = form.email_address.data,
                              password = form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        # return to homepage
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')
    return render_template('register.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    print("User logged out!")
    return redirect(url_for('home_page'))
