from datetime import datetime
from bandx import login_manager
from bandx.models.db import db # can't import from actx circular import
from flask_login import UserMixin # methods required by login_manager
from bson.objectid import ObjectId

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first() or None

class Towns(db.Document):
    towns = db.ListField(db.StringField(max_length=50, required=True))
    province = db.StringField(max_length=30, required=True, choices=["Connacht","Leinster","Munster","Ulster"])
    county = db.StringField(max_legth=50, required=True)
    def __repr__(self):
        return f"Town('{self.towns}', '{self.county}', '{self.province})"


class Email(db.EmbeddedDocument):
    email_title = db.StringField(max_length=30, default="Enquiries")
    email_address = db.EmailField(max_length=120) 


class Phone(db.EmbeddedDocument):
    mobile = db.BooleanField(default=1)
    number = db.StringField(max_length=30)    


class Contact(db.EmbeddedDocument):
    contact_name = db.StringField(max_length=120)
    contact_title = db.StringField(max_length=50, default="Enquiries")
    contact_generic_title = db.StringField(max_length=50, default="Enquiries")
    contact_emails = db.EmbeddedDocumentField(Email, default=Email)
    contact_numbers = db.EmbeddedDocumentField(Phone, default=Phone)


class Links(db.EmbeddedDocument):
    refname = db.StringField(max_length=50, default="Weblinks")
    enquiries = db.StringField()
    websites = db.MapField(db.StringField())
    social_media = db.MapField(db.StringField())
    music = db.MapField(db.StringField())


class Assets(db.EmbeddedDocument):
    featured_image = db.StringField(max_length=20, required=True, default='defaultband.jpg')
    featured_video = db.MapField(db.StringField())


class BandMember(db.EmbeddedDocument):
    musician = db.StringField()
    instruments = db.StringField()


class Band(db.DynamicDocument):
    created_by = db.ReferenceField('User') 
    date_created = db.DateTimeField(required=True, default=datetime.utcnow)
    band_name = db.StringField(unique=True, max_length=120, required=True)
    catalogue_name = db.StringField(max_length=120, required=True)
    profile = db.StringField()
    description = db.StringField(max_length=120)
    genres = db.ListField(db.StringField(default='unclassified'))
    strapline = db.StringField(max_length=120)
    hometown = db.MapField(db.StringField())
    contact_details = db.EmbeddedDocumentField(Contact, default=Contact) 
    links = db.EmbeddedDocumentField(Links,  default=Links) 
    media_assets = db.EmbeddedDocumentField(Assets) 
    band_members = db.EmbeddedDocumentListField(BandMember)

    meta = {"indexes" : [ { "fields" : {"$**": "text"} ,
                         "default_language" : "english",
                         "textIndexVersion" : 3,
                         "weights": {"$**": 1},
                         "cls": False
                         } ]}



    def __repr__(self):
        return f"Band('{self.bandname}', '{self.date_posted}')"




class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=2, max_length=30)
    first_name = db.StringField(max_length=120)
    common_name = db.StringField(max_length=60)
    last_name = db.StringField(max_length=120)
    email = db.EmailField(required=True, unique=True, max_length=120)
    image_file = db.StringField(max_length=20, required=True, default='default.jpg')
    password = db.StringField(required=True, min_length=6, max_length=60)

    meta = {'strict': False}
    
    def __repr__(self): #dunder or 'magic method'
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"




User.register_delete_rule(Band, 'added_by', db.CASCADE)


