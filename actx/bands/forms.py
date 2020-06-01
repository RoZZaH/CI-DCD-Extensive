from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
#from actx.users.forms import HomeTownForm
from actx.models.entities import User, Towns
from wtforms import Form, BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, FormField, FieldList, IntegerField

from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError


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
                                render_kw={"class": "origin-town"}) #depends on above



class ContactForm(Form):
    # SubForm
    namec = StringField('Contact Name')
    number = StringField('PhonexNumber')


class LapForm(Form):
    """
    Subform.
    CSRF is disabled for this subform (using `Form` as parent class) because
    it is never used by itself.
    """
    runner = StringField('Runner name')
    lap_time = IntegerField('Lap time')


class CreateBandForm(FlaskForm):
    bandname = StringField("Band Name", 
                            validators=[DataRequired()])
    # genres = StringField("Musical Genres", )#validators=[DataRequired(), Length(min=3, max=120)])
    # profile = TextAreaField("Profile",) # validators=[DataRequired()])
    hometown = FieldList(FormField(HomeTownForm))
    # members k v i.e. locals Neil Hannon
    contacts = FieldList(FormField(ContactForm), min_entries=1, max_entries=8)
    members = FieldList(FormField(ContactForm), min_entries=1, max_entries=8)
    submit = SubmitField("Create")





# class MainForm(FlaskForm):
#     """Parent form."""
#     name = StringField("Race Name",
#                             validators=[DataRequired(), Length(min=3, max=120)])
#     laps = FieldList(
#         FormField(LapForm),
#         min_entries=1,
#         max_entries=20
#     )

