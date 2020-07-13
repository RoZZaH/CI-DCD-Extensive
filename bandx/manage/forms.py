from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
#from actx.users.forms import HomeTownForm
from bandx.models.entities import User, Towns
from wtforms import (BooleanField, DateField, Form, FormField, FieldList, HiddenField, 
                    #IntegerField,
                      PasswordField, RadioField, SelectField, StringField, SubmitField, TextAreaField,)

from wtforms.validators import DataRequired, Optional, Length, EqualTo, Email, URL, ValidationError


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


class BandMemberFormlet(Form):
    instruments = StringField("Instrument(s)",
                            render_kw={"placeholder":"use commas, between, instruments"})
    musician = StringField("Musician's Name")


class PhoneFormlet(Form):
    mobile = RadioField("Mobile Y/N", 
                        choices=[("True","mobile"),("False","landline")],
                        render_kw={},
                        default="True")
    number = StringField("Number",
                        render_kw={"placeholder":"+353", "class":"number-field", "id":"phone"},
                        validators=[Length(max=15)])
    
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
                            render_kw={"placeholder": "Enquiries" },
                            validators=[Optional(), Email()])


class ContactFormlet(Form):
    contact_name = StringField("Booking Contact",
                            render_kw={"placeholder": "Band Booking Contact's Name" })
    contact_title = StringField("Booking Contact Title",
                            render_kw={"placeholder": "Title e.g. Band Leader or Band Manager" })
    contact_generic_title = StringField("Generic Contact Name",
                            render_kw={"placeholder": "e.g. Enquiries or Bookings" })
    contact_emails = FieldList(FormField(EmailFormlet), min_entries=1)
    contact_numbers = FieldList(FormField(PhoneFormlet), min_entries=1)



# class Genre(Form):
#     checked = BoeleanField()


# class GenresForm(Form):
#     genres_list = FieldList(BooleanField("Genre", render_kw={"name": "genre"}))
#     genres_other = StringField("", render_kw={"name": "genre"}, validators=[Length(max=15)])

# class LinksFormelet(Form)

class CreateUpdateBandForm(FlaskForm):
   # org_type = HiddenField()
    band_name = StringField("Band Name", #FORMAT The
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
    # genres = FormField(GenresForm)
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
    # tours
    # picture = FileField("Update Band Picture",
    #                         validators=[FileAllowed(["jpg", "jpeg", "png"])])
    #    links = FieldList(FormField())

























class TourDateFormlet(Form):
    td_date = DateField("Date")
    td_time_hh = SelectField("Time-Hour",
                        choices=[
                                (1,"1"),
                                (2,"2"),
                                (3,"3"),
                                (4,"4"),
                                (5,"5"),
                                (6,"6"),
                                (7,"7"),
                                (8,"8"),
                                (9,"9"),
                                (10,"10"),
                                (11, "11"),
                                (0,"12")],
                            default=8,
                            validate_choice=False,
                            render_kw={"class": "td_time_hh"})
    td_time_ampm = SelectField("AM/PM",
                                choices=[(0, "AM"), (12, "PM")],
                                default=12,
                                validate_choice=False,
                                render_kw={"class": "td_time_ampm"})
    td_time_mm = SelectField("Time-Mins",
                                choices=[(0, "00"),(15, "15"),(30, "30"), (45, "45")], 
                                default=0,
                                validate_choice=False,
                                render_kw={"class": "td_time_mm"})
    td_status = SelectField("Status",
                            choices=[
                                ("tbc", "T.B.C."),
                                ("confirmed", "Confirmed"),
                                ("cancelled", "Cancelled"),
                                ("rescheduled", "Rescheduled")
                            ], default="tbc")
    td_hometown = FormField(HomeTownForm)
    td_location = StringField("Specifically",
                            render_kw={"placeholder": "specific location if not listed in Town"},)
    
    td_venue = SelectField("Venue Name", choices=[(1,"TestVenue")], 
                            default=1, validate_choice=False)
    td_venue_url = StringField("Venue Website",
                                validators=[Optional(),URL()])
    td_venue_phones = TextAreaField("Booking Phone Numbers",
                                render_kw={"class":"td_phones"})
    td_ticket_urls = TextAreaField("Ticket links",
                                render_kw={"class":"td_phones"})




class TourDetailsForm(FlaskForm):
    org_type = HiddenField()
    org_name = StringField("Name",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[DataRequired()])
    tour_description = StringField("Tour Description",
                            render_kw={"placeholder": "Ska Reggae Band from Belfast"},
                            validators=[DataRequired()])
    tour_title = StringField("Tour Title", 
                            validators=[DataRequired()])
    strapline = StringField("Tour Strapline",
                            render_kw={"id": "testLower", 
                                       "placeholder": "100yrs of Tom Jones"})
    tour_text = TextAreaField("Tour Text",
                            render_kw={"placeholder": "Brief Bio/History Band Origins and Direction"},
                            validators=[DataRequired()])
    genres = StringField("Musical Genres", 
                            render_kw={"id": "testInput",
                                       "style":"text-transform: lowercase;"
                                       })
    picture = FileField("Upload Tour Picture",
                            validators=[FileAllowed(["jpg", "jpeg", "png"])])
    tour_dates = FieldList(FormField(TourDateFormlet), min_entries=1)
    member_instruments = StringField("Instrument(s)")
    member_name = StringField("Band Member")
    created_by = HiddenField()
#    contacts = FieldList(FormField(ContactForm), min_entries=1, max_entries=8)
#    links = FieldList(FormField())
#    media_assets = FieldList(FormField())
    submit = SubmitField("Save")