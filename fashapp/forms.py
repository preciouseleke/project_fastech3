from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,  EmailField, SubmitField,TextAreaField,HiddenField, SelectField,RadioField,FloatField

from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import DataRequired, Email,NumberRange



class LoginForm(FlaskForm):
    email =EmailField("Email: ",validators=[Email(message="Enter Email")])

    password =PasswordField("password:",validators=[DataRequired(message="password can not be empty")])

    submit =SubmitField("Login")


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(message="Password can not be empty")])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    fullname = StringField('Fullname', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[])
    send =SubmitField('send')

    class Meta:
        csrf=True
        csrf_time_limit=7200

class ProfileForm(FlaskForm):
    cust_firstname =StringField('  firstName',validators=[DataRequired()])
    cust_lname =StringField(' lastname',validators=[DataRequired()])
    cust_email =EmailField('Email:', validators=[DataRequired(), Email()])
    cust_password =PasswordField("password:",validators=[DataRequired(message="password can not be empty")])
    cust_coverimage =FileField('cover image', validators=[FileAllowed(['jpg','png','jpeg','gif'],'images only')])
    submit = SubmitField('Update')

class DesignForm(FlaskForm):
    design_id= HiddenField('Design ID', validators=[DataRequired()])
    design_name =StringField('  Name',validators=[DataRequired(message="Design name is required.")])
    design_catid =SelectField('Category',choices=[('1','Category 1', '2', 'Category 2', '3', 'Category 3', '4', 'Category 4')], validators=[DataRequired(message="please select a category.")])
    design_cust_id = HiddenField('Customer ID', validators=[DataRequired(message="Customer ID is required.")])
    submit = SubmitField('Update')

class CheckoutForm(FlaskForm):
    cust_firstname = StringField("First Name", validators=[DataRequired()])
    cust_lname = StringField("Last Name", validators=[DataRequired()])
    cust_email = StringField("Email", validators=[DataRequired()])
    payment_method = RadioField("Payment Method", choices=[('paystack', 'Paystack')], default='paystack')
    submit = SubmitField("Proceed to Payment")


class AddProductForm(FlaskForm):
    pro_name = StringField("Product Name", validators=[DataRequired()])
    pro_design_id = SelectField("Design", coerce=int, validators=[DataRequired()])
    price_amt = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    pro_status = SelectField(
        "Status", 
        choices=[("Available", "Available"), ("Out of stock", "Out of stock"), ("Pending", "Pending"), ("Discontinued", "Discontinued")], 
        validators=[DataRequired()]
    )
    pro_pix = FileField("Product Image")
    submit = SubmitField("Add Product")

    
    