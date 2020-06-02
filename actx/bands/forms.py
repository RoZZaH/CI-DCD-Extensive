from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
#from actx.users.forms import HomeTownForm
from actx.models.entities import User, Towns
from wtforms import (BooleanField, Form, FormField, FieldList, HiddenField, 
                    #IntegerField,
                     PasswordField, SelectField, StringField, SubmitField, TextAreaField,)

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
                                render_kw={"class": "origin-town"},
                                validate_choice=False) #depends on above



class CreateUpdateBandForm(FlaskForm):
    org_type = HiddenField()
    band_name = StringField("Band Name",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[DataRequired()])
    description = StringField("Description",
                            render_kw={"placeholder": "Ska Reggae Band from Belfast"},
                            validators=[DataRequired()])
    strapline = StringField("Band Motto / Strapline",
                            render_kw={"id": "testLower"})
    profile = TextAreaField("Profile",
                            render_kw={"placeholder": "Brief Bio/History Band Origins and Direction"},
                            validators=[DataRequired()])
    genres = StringField("Musical Genres", 
                            render_kw={"id": "testInput",
                                       "style":"text-transform: lowercase;"
                                       })
    picture = FileField("Update Band Picture",
                            validators=[FileAllowed(["jpg", "jpeg", "png"])])
    member_instruments = StringField("Instrument(s)")
    member_name = StringField("Band Member")
    hometown = FormField(HomeTownForm)
    created_by = HiddenField()
#    contacts = FieldList(FormField(ContactForm), min_entries=1, max_entries=8)
#    links = FieldList(FormField())
#    media_assets = FieldList(FormField())
    submit = SubmitField("Save")


