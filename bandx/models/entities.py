from datetime import datetime
from bandx import login_manager
from bandx.models.db import db # can't import from actx circular import
from flask_login import UserMixin # methods required by login_manager
from bson.objectid import ObjectId

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first() or None

class Towns(db.Document):  #Venues ? Diaspora
    town = db.StringField(max_length=50, required=True)
    county = db.StringField(max_legth=50, required=True)
    def __repr__(self):
        return f"Town('{self.town}', '{self.county}')"


class Email(db.EmbeddedDocument):
    email_title = db.StringField(max_length=30) #!!! = not :
    email_address = db.EmailField(max_length=120) 


class Phone(db.EmbeddedDocument):
    mobile = db.BooleanField(default=True)
    number = db.StringField(max_length=30)    


class Contact(db.EmbeddedDocument):
       # c_id = db.StringField(default=ObjectId)
    contact_name = db.StringField(max_length=120) #option public
    contact_title = db.StringField(max_length=50)
    contact_generic_title = db.StringField(max_length=50, default="Enquiries")
    contact_emails = db.EmbeddedDocumentListField(Email)
    contact_numbers = db.EmbeddedDocumentListField(Phone)
#   refname = db.StringField(max_length=50, default="Booking Contact")


class Links(db.EmbeddedDocument):
    refname = db.StringField(max_length=50, default="Weblinks")
    enquiries = db.StringField()
    websites = db.MapField(db.StringField())
    social_media = db.MapField(db.StringField())
    music = db.MapField(db.StringField())


class Assets(db.EmbeddedDocument):
    featured_image = db.StringField(max_length=20, required=True, default='defaultband.jpg')
    featured_video = db.StringField()


class BandMember(db.EmbeddedDocument):
    musician = db.StringField()
    instruments = db.StringField() #comma seperate could be list of tags 


class Band(db.DynamicDocument):
    created_by = db.ReferenceField('User') 
    date_created = db.DateTimeField(required=True, default=datetime.utcnow)
    band_name = db.StringField(max_length=120, required=True) #Unique=True
    profile = db.StringField()
    description = db.StringField(max_length=120)
    genres = db.ListField(db.StringField(default='unclassified'))
    strapline = db.StringField(max_length=120)
    hometown = db.MapField(db.StringField())
    contact_details = db.EmbeddedDocumentField(Contact, default=Contact) #copy oCreator role
    links = db.EmbeddedDocumentField(Links,  default=Links) #copy oCreator role
    media_assets = db.EmbeddedDocumentField(Assets) #copy oCreator role
    band_members = db.EmbeddedDocumentListField(BandMember)
#    tours = db.ListField(db.ReferenceField('Tour'))
    # publish
    # meta = {
    #     "allow_inheritance": True
    # }
    # abstract is option for DRY but different cols
    def __repr__(self):
        return f"Band('{self.bandname}', '{self.date_posted}')"


# Announcement

class TourDate(db.EmbeddedDocument):
    td_datetime = db.DateTimeField()
    td_status = db.StringField()
    td_location = db.StringField()
    td_hometown = db.MapField(db.StringField())
    td_venue = db.StringField()
    td_venue_url = db.StringField()
    td_venue_phones = db.ListField(db.StringField())
    td_ticket_urls = db.ListField(db.StringField())


class Tour():
    # image_file =  db.StringField(max_length=20, required=True, default='defaultband.jpg')
    # genres = db.ListField(db.StringField(default='unclassified'))
    # members = db.MapField(db.StringField())
    tour_strapline = db.StringField(max_length=120)
    tour_title = db.StringField()
    tour_description = db.StringField()
    tour_assets = db.EmbeddedDocumentField(Assets)
    tour_text = db.StringField()
    tour_dates = db.EmbeddedDocumentListField(TourDate)


# class Venue(Organisation):
#     local_directions = db.StringField()
#     accessibility = db.StringField()



# below Band reference error to Band (before created)
class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=2, max_length=30)
    first_name = db.StringField(max_length=120)
    common_name = db.StringField(max_length=60)
    last_name = db.StringField(max_length=120)
    email = db.EmailField(required=True, unique=True, max_length=120)
    image_file = db.StringField(max_length=20, required=True, default='default.jpg')
    password = db.StringField(required=True, min_length=6, max_length=60)
    #roles = db.EmbeddedDocumentListField(Role)
    #created_users = db.ListField(db.ReferenceField('User'))
    #created_orgs = db.ListField(db.ReferenceField('Organisation'))
    meta = {'strict': False}
    
    def __repr__(self): #dunder or 'magic method'
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"




User.register_delete_rule(Band, 'added_by', db.CASCADE)
###
# Band.register_delete_rule(Contact, 'band_ref', db.CASCADE)

