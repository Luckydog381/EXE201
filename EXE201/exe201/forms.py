from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_wtf.file import FileAllowed
from exe201.models import User, Profile
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
    #check if user or email existed!
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        #if not null
        if email_address and email_address_to_check.data != User.query.filter_by(id=current_user.id).first().email_address:
            raise ValidationError('Email address has already exists! Please try a different email!')

    # Check if phone number is existed!
    def validate_phone_number(self, phone_number_to_check):
        phone_number = Profile.query.filter_by(phone_number=phone_number_to_check.data).first()
        #if not null
        if phone_number and phone_number_to_check.data != Profile.query.filter_by(user_id=current_user.id).first().phone_number:
            raise ValidationError('Phone number has already exists! Please try a different phone number!')
        elif phone_number_to_check.data.isdigit() == False:
            raise ValidationError('Phone number must be a number!')
        elif len(phone_number_to_check.data) != 10:
            raise ValidationError('Phone number must be 10 digits!')
        

    fullname = StringField(label='Full name:', validators=[DataRequired()])
    image_file = FileField(label='Change Avatar', validators=[FileAllowed(['jpg', 'jpeg', 'png'])], render_kw={'accept': 'image/*', 'onchange': 'document.getElementById("profile-picture-preview").src = window.URL.createObjectURL(this.files[0])'})
    email_address = StringField(label='Email address:', validators=[Email(), DataRequired()])
    phone_number = StringField(label='Phone number:', validators=[DataRequired()])
    address = StringField(label='Address:', validators=[DataRequired()])
    city = StringField(label='City:', validators=[DataRequired()])
    state = StringField(label='State:', validators=[DataRequired()])
    zipcode = StringField(label='Zipcode:', validators=[DataRequired()])
    country = StringField(label='Country:', validators=[DataRequired()])
    about_me = TextAreaField(label='Introduction:')
    submit = SubmitField(label='Save Changes')

class CreateProduct(FlaskForm):
    name = StringField(label='Product name:', validators=[DataRequired()])
    price = StringField(label='Price:', validators=[DataRequired()])
    description = TextAreaField(label='Description:', validators=[DataRequired()])
    image_file = FileField(label='Press this button to upload your image', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'])], render_kw={'accept': 'image/*', 'onchange': 'document.getElementById("product-picture-preview").src = window.URL.createObjectURL(this.files[0])'})
    submit = SubmitField(label='Add Product')

class UpdateProduct(FlaskForm):
    name = StringField(label='Product name:', validators=[DataRequired()])
    price = StringField(label='Price:', validators=[DataRequired()])
    description = StringField(label='Description:', validators=[DataRequired()])
    submit = SubmitField(label='Update Product')