from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from actx.models.entities import User
from wtforms import BooleanField, DateField, Form, FormField, FieldList, HiddenField, PasswordField, RadioField, StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length, EqualTo, Email, URL, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField("Username", 
                            validators=[DataRequired(), Length(min=2,max=30)])
    email = StringField("Email",
                            validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                            validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                            validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username): # template for validation error
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose somthing else.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('That email is already assocaited with a user. Please reset your password.')


class LoginForm(FlaskForm):
    email = StringField("Email",
                            validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                            validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                            validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture",
                            validators=[FileAllowed(["jpg", "jpeg", "png"])])
    submit = SubmitField("Update")

    def validate_username(self, username): # template for validation error
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose somthing else.')

    def validate_email(self, email):
        if email.data != current_user.email: 
            user = User.objects(email=email.data).first()
            if user:
                raise ValidationError('That email is already assocaited with a user. Please reset your password.')


class HomeTownForm(Form):
    origin_county = SelectField("From County", choices = [
                            ("Antrim",	"Antrim"),
                            ("Armagh",	"Armagh"),
                            ("Carlow",	"Carlow"),
                            ("Cavan",	"Cavan"),
                            ("Clare",	"Clare"),
                            ("Cork",	"Cork"),
                            ("Derry",	"L/Derry"),
                            ("Donegal",	"Donegal"),
                            ("Down",	"Down"),
                            ("Dublin",	"Dublin"),
                            ("Fermanagh", "Fermanagh"),	
                            ("Galway",	"Galway"),
                            ("Kerry",	"Kerry"),
                            ("Kildare",	"Kildare"),
                            ("Kilkenny","Kilkenny"),
                            ("Laois",	"Laois"),
                            ("Leitrim",	"Leitrim"),
                            ("Limerick","Limerick"),	
                            ("Longford","Longford"),	
                            ("Louth",	"Louth"),
                            ("Mayo",	"Mayo"),
                            ("Meath",	"Meath"),
                            ("Monaghan","Monaghan"),	
                            ("Offaly",	"Offaly"),
                            ("Roscommon","Roscommon"),
                            ("Sligo",	"Sligo"),
                            ("Tipperary", "Tipperary"),	
                            ("Tyrone",	"Tyrone"),
                            ("Waterford", "Waterford"),	
                            ("Westmeath", "Westmeath"),	
                            ("Wexford",	"Wexford"),
                            ("Wicklow",	"Wicklow")
                            ],
                            render_kw={"class": "origin-county"})
    origin_town = SelectField("From Town/Locale",
                                choices=[],
                                # coerce=StringField,
                                render_kw={"class": "origin-town"},
                                validate_choice=False
                                ) #depends on above


