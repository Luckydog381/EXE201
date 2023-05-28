from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from exe201.models import User
from flask_login import current_user

class RegisterForm(FlaskForm):

    #check if user or email existed!
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        #if user not null
        if user:
            raise ValidationError('Username has already exists! Please try a different username!')
            
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        #if not null
        if email_address:
            raise ValidationError('Email address has already exists! Please try a different email!')

    username = StringField(label = 'User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label = 'Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label = 'Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label = 'Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label = 'Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = StringField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class EditProfile(FlaskForm):

    fullname = StringField(label='Full name:', validators=[DataRequired()])
    email_address = StringField(label='Email address:', validators=[Email(), DataRequired()])
    phone_number = StringField(label='Phone number:', validators=[DataRequired()])
    address = StringField(label='Address:', validators=[DataRequired()])
    city = StringField(label='City:', validators=[DataRequired()])
    state = StringField(label='State:', validators=[DataRequired()])
    zipcode = StringField(label='Zipcode:', validators=[DataRequired()])
    country = StringField(label='Country:', validators=[DataRequired()])
    submit = SubmitField(label='Save Changes')