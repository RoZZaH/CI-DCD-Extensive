from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from bandx.models.entities import User, Band, Towns
from wtforms import (BooleanField, DateField, Form, FormField, FieldList, HiddenField, 
                      PasswordField, RadioField, SelectField, StringField, SubmitField, TextAreaField,)
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, Optional, URL, ValidationError, StopValidation
import phonenumbers

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
    origin_town = SelectField("From Town/Locality",
                                choices=[],
                                render_kw={"class": "origin-town"},
                                validate_choice=False)


class BandMemberFormlet(Form):
    instruments = StringField("Instrument(s)",
                            render_kw={"placeholder":"use commas, between, instruments"})
    musician = StringField("Musician's Name")


class PhoneFormlet(Form):
    mobile = RadioField("Mobile Y/N", 
                        choices=[(1, "mobile"),(0,"landline")],
                        coerce=int,
                        render_kw={},
                        default="True")
    region = RadioField('', choices= [
                                    ('IE', 'Ireland'),
                                    ('GB', 'N.I./UK'),
                                    ('None','Other')

                        ], default='IE')
    phone = StringField('', validators=[DataRequired()])
    # number = StringField("Number",
    #                     render_kw={"placeholder":"+353", "class":"number-field", "id":"phone"},
    #                     validators=[Length(max=15)])  

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data, self.region.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class MediaAssetsFormlet(Form):
    featured_image = FileField("Band Profile Image",
                                validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
                                )
    featured_video = StringField("Featured Video Link",
                            render_kw={"placeholder": "link to youtube or vimeo"},
                            validators=[Optional(), URL()])


class EmailFormlet(Form):
    email_title = StringField("Email Title",
                            render_kw={"placeholder": "Enquiries" },
                            validators=[Optional()])
    email_address = StringField("Email Address",
                            render_kw={"placeholder": "enquiries@bandx.ie" },
                            validators=[DataRequired(), Email()])


class ContactFormlet(Form):
    contact_name = StringField("Booking Contact",
                            render_kw={"placeholder": "Band Booking Contact's Name" })
    contact_title = StringField("Booking Contact Title",
                            render_kw={"placeholder": "Title e.g. Band Leader or Band Manager" })
    contact_generic_title = StringField("Generic Contact Name",
                            render_kw={"placeholder": "e.g. Enquiries or Bookings" })
    contact_emails = FormField(EmailFormlet)
    contact_numbers = FormField(PhoneFormlet)



class CreateUpdateBandForm(FlaskForm):
    band_name = StringField("Band Name",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[DataRequired()])
    description = StringField("Description",
                            render_kw={"placeholder": "Ska Reggae Band from Belfast"},
                            validators=[DataRequired()])
    strapline = StringField("Band Motto / Strapline",
                            render_kw={"id": "testLower"})
    profile = TextAreaField("Profile",
                            render_kw={"placeholder": "Brief Bio/History, band origins and direction"},
                            validators=[DataRequired()])
    genres = StringField("Musical Genres", 
                            render_kw={"id": "testInput",
                                       "style":"text-transform: lowercase;",
                                       })
    hometown = FormField(HomeTownForm)
    members = FieldList(FormField(BandMemberFormlet), min_entries=1)
    created_by = HiddenField()
    contact_details = FormField(ContactFormlet)
    enquiries_url = StringField("Online Enquiries Link",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[Optional(), URL()])
    media_assets = FormField(MediaAssetsFormlet)
    submit = SubmitField("Save")


def check_bandname_unique(form, field):
        bname = field.data
        if len(list(Band.objects(band_name__iexact=bname))) > 0:
            raise ValidationError("This band name is already taken; sorry.")


class CreateBandForm1(FlaskForm):
    band_name = StringField(render_kw={"placeholder": "Band Name"},
                            validators=[check_bandname_unique])
    hometown = FormField(HomeTownForm)


class CreateBandForm2(FlaskForm):
    # band_name = StringField("Band Name",
    #                         render_kw={"placeholder": "Org Name / Band / Venue"},
    #                         validators=[DataRequired()])
    description = StringField("Description",
                            render_kw={"placeholder": "Ska Reggae Band from Belfast"},
                            validators=[DataRequired()])
    strapline = StringField("Band Motto / Strapline",
                            render_kw={"id": "testLower"})
    genres = StringField("Musical Genres", 
                            render_kw={"id": "testInput",
                                       "style":"text-transform: lowercase;",})
    created_by = HiddenField()
    submit = SubmitField("Next")
    
    
class CreateBandForm3(FlaskForm):
    # hometown = FormField(HomeTownForm)
    profile = TextAreaField("Profile",
                            render_kw={"placeholder": "Brief Bio/History, band origins and direction"},
                            validators=[DataRequired()]
                            )
    members = FieldList(FormField(BandMemberFormlet), min_entries=1)
    featured_image = FileField("Band Profile Image",
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
                            )
    submit = SubmitField("Next")


class CreateBandForm4(FlaskForm):
    contact_details = FormField(ContactFormlet)
    enquiries_url = StringField("Online Enquiries Link",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[Optional(), URL()])
    featured_video = StringField("Featured Video Link",
                            render_kw={"placeholder": "link to youtube or vimeo"},
                            validators=[Optional(), URL()])
    submit = SubmitField("Save")