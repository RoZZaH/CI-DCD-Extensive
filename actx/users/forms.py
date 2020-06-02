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



class AddressForm(Form):
    a_id = HiddenField(None)
    refname = StringField("Internal Ref Name",
                                render_kw={"placeholder":"The Office"},
                                validators=[DataRequired()])
    #home_town = FieldList(FormField(HomeTownForm))
    specifically = StringField("specifically",
                                render_kw={"placeholder":"More Exact Location"})
    address_lines = TextAreaField("Address",
                                render_kw={"placeholder":"Name/Home Number\nStreet/Estate Address\nRoad"})
    post_eir_code = StringField("Post/Eircode",
                                render_kw={"placeholder":"BT42 3HX"})
    contact_1 = StringField("Contact Name 1")
    contact_title_1 = StringField("Contact Title 1", 
                                render_kw={"placeholder":"Manager"})
                               # validators=[DataRequired()])
    contact_2 = StringField("Contact Name 2")
    contact_title_2 = StringField("Contact Title 2",
                                render_kw={"placeholder":"Asst Manager"})
    email_1 = StringField("Email 1", 
                                validators=[DataRequired(), Email()])
    email_2 = StringField("Email 2", 
                                validators=[Optional(strip_whitespace=True), Email()])
    phone_1 = StringField("Phone 1")
    phone_2 = StringField("Phone 1")
    mobile_1 = StringField("Mobile 1")
    mobile_2 = StringField("Mobile 2")
    website_1 = StringField("Website 1",
                                render_kw={"placeholder":"actx.ie"},
                                validators=[Optional(), URL()])
    website_2 = StringField("Website 2",
                                render_kw={"placeholder":"actx.ie"},
                                validators=[Optional(), URL()])
    #local_directions = TextAreaField("Local Directions")
    #accessibility = TextAreaField("Accessibility")

class CreateVenueForm(FlaskForm):
    venue_name = StringField("Name",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[DataRequired()])
    venue_description = StringField("Description",
                                render_kw={"placeholder": "Venue Type e.g. Arts Centre"})
    venue_hometown = FormField(HomeTownForm)
    venue_address = FormField(AddressForm)
    venue_accessibility = TextAreaField("Accessibility",
                                render_kw={"placeholder": "how accessible is the building to people with disabilities"})
    venue_directions = TextAreaField("Local Directions",
                                render_kw={"placeholder": "Wexford Arts Centre is located in Cornmarket around the corner from the Pike Man Monument on the Main Street; and between Clayton 'White\'s' Hotel and Wexford Town Library"})
    submit = SubmitField("Save Venue")



class CreateOrganisationForm(FlaskForm):
    org_type = SelectField("Type of Org/Group", 
                            choices=[("organisation", "Management Company"),
                                    ("organisation", "Production Company"),
                                    ("organisation", "Promotion Company"),
                                    ("organisation", "Record Label"),
                                    ("organisation", "Events Company"),
                                    ("band", "Band"),
                                    ("venue", "Venue Pub"),
                                    ("venue", "Venue Theatre Commerical"),
                                    ("venue", "Venue Theatre Arts Funded"),
                                    ("organisation", "Other")]) 
    org_name = StringField("Name",
                            render_kw={"placeholder": "Org Name / Band / Venue"},
                            validators=[DataRequired()])
    
    submit = SubmitField("Save")

class OrganisationDetailsForm(FlaskForm):
    oid = HiddenField(None)
    org_type = HiddenField(None, default="organisation")
    org_name = StringField("Name",
                            validators=[DataRequired()])
    description = StringField("Description",
                            render_kw={"placeholder": "Multigenre Management and Promotion Company"},
                            validators=[DataRequired()])
    profile = TextAreaField("Profile",
                            render_kw={"placeholder": "MGMTx is a multigenre production, management and promotion company working with some of Ireland’s and the world’s best talent. We bring unique insight and years of expertise across the creative business disciplines, from tour and concept delivery, to strategic management and promotion, to producing iconic events."},
                            validators=[DataRequired()])
   #hometown = FormField(HomeTownForm)
    contacts = FieldList(FormField(AddressForm), min_entries=1, max_entries=8)
    #links = FieldList(FormField())
    #media_assets = FieldList(FormField())
    submit = SubmitField("Save")




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


class LinksFormLet(Form):
    refname = StringField("Internet Links",
                            render_kw={"placeholder": "Links for ... "},
                            validators=[DataRequired()])
    weblinks = StringField("Link Descriptor",
                            render_kw={"placeholder": "Offical Website"},
                            validators=[Optional(),DataRequired()])
    weblink = StringField("Link",
                            render_kw={"placeholder": "https://actx.ie/"},
                            validators=[Optional(), URL()])
    social_service = StringField("Social Platform",
                            render_kw={"placeholder": "twitter"})
    social_handle = StringField("handle",
                            render_kw={"placeholder": "@drdre"})
    music_service = SelectField("Music Service",
                                choices=[
                                    ("youtube", "YouTube"),
                                    ("apple", "Apple Music"),
                                    ("spotify", "Spotify"),
                                    ("google", "Google Play"),
                                    ("deezer", "Deezer"),
                                    ("tidal", "Tidal"),
                                    ("amazon", "Amazon Prime"),
                                    ("soundcloud", "SoundCloud"),
                                    ("mixcloud", "MixCloud")
                                ])
    music_handle = StringField("music handle")
        

class MediaAssetsFormLet(Form):
    refname = StringField("Media Assets",
                            render_kw={"placeholder": "Promo shots for ... "},
                            validators=[DataRequired()])
    #default
    # pictures
    #     landscape
    #     portrait
    #     square
    #     widescreen

    # videolinks k v
    # text
    #     single_sms
    #     tweet
    #     paragraph
    #     summary
    #     article
    #     md
    #     file_url


class DefaultContact(FlaskForm):
    # org creator
    first_name = StringField("First Name",
                            validators=[DataRequired()])
    common_name = StringField("Known As e.g.'Pat','Paddy'")
    last_name = StringField("Last Name")
    address = FieldList(FormField(AddressForm))





class CreateUser(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", 
                            validators=[DataRequired(), Email()])
    first_name = StringField("First Name",
                            validators=[DataRequired()])
    common_name = StringField("Known As e.g.'Pat','Paddy'")
    last_name = StringField("Last Name")
    picture = FileField("Upload Profile Picture",
                            validators=[FileAllowed(["jpg", "jpeg", "png"])])
    # me org new org new band
    # existing org
    org_type = SelectField("Type of Organisation/Group", 
                        choices=[("organisation", "Management Company"),
                                 ("organisation", "Production Company"),
                                 ("organisation", "Promotion Company"),
                                 ("organisation", "Record Label"),
                                 ("organisation", "Events Company"),
                                 ("band", "Band"),
                                 ("venue", "Venue Pub"),
                                 ("venue", "Venue Theatre Commerical"),
                                 ("venue", "Venue Theatre Arts Funded"),
                                 ("organisation", "Other")]) 
    role_type = SelectField("User Role",
                            choices=[("org_creator", "Creator"),
                                     ("org_owner", "Owner"),
                                     ("org_user", "Staff"),
                                     ("org_owner", "Band Leader"),
                                     ("org_user", "Band Member")])
    role_ref = StringField("Reference", placeholder="Promoter for Band X")
    role_title = StringField("Role Title", placeholder="Band Manager")
    description = StringField("Description", placeholder="what person/org does")
    profile = TextAreaField("Profile", placeholder="Brief profile of company, band, artist, venue")
    submit = SubmitField("Save")
    #created_by = HiddenField()

