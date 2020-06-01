from datetime import datetime
from actx import login_manager
from actx.models.db import db # can't import from actx circular import
from flask_login import UserMixin # methods required by login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first() or None

class Towns(db.Document):
    town = db.StringField(max_length=50, required=True)
    county = db.StringField(max_legth=50, required=True)
    def __repr__(self):
        return f"Town('{self.town}', '{self.county}')"


class Band(db.Document):
    bandname = db.StringField(max_length=120, required=True)
    genres = db.ListField(db.StringField())
    # strapline = db.StringField(max_length=120, required=True)
    profile = db.StringField()
    date_posted = db.DateTimeField(required=True, default=datetime.utcnow)
    added_by = db.ReferenceField('User')
    contacts = db.ListField(db.ReferenceField('Contact', reverse_delete_rull=db.PULL))
    members = db.ListField(db.DictField())

    def __repr__(self):
        return f"Band('{self.bandname}', '{self.date_posted}')"

class Roles(db.EmbeddedDocument):
    pass


class Address(db.EmbeddedDocument):
    refname = db.StringField(max_length=50)
    contact_1 = db.StringField(max_length=120)
    contact_2 = db.StringField(max_length=120)
    address_lines = db.StringField()
    email_1 = db.EmailField(max_length=120)
    email_2 = db.EmailField(max_length=120)
    phone_1 = db.StringField(max_length=30)
    phone_2 = db.StringField(max_length=30)
    mobile_1 = db.StringField(max_length=30)
    mobile_2 = db.StringField(max_length=30)
    oTown = db.StringField(max_length=50)
    oCounty = db.StringField(max_length=50)
    specifically = db.StringField(max_length=50)
    post_eir_code = db.StringField(max_length=30)
    website_1 = db.StringField(max_length=120)
    website_2 = db.StringField(max_length=120)
    local_directions
    accessibility

class Links(db.EmbeddedDocument):
    refname = db.StringField(max_length=50)
    links = db.MapField(db.StringField)

class Role(db.EmbeddedDocument):
    role = db.StringField(max_length=30)
    org_ref = db.ReferenceField('Organisation')
    act_ref = db.ReferenceField('Band')   

# below Band reference error to Band (before created)
class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=2, max_length=30)
    first_name = db.StringField(max_length=120)
    common_name = db.StringField(max_length=60)
    last_name = db.StringField(max_length=120)
    email = db.EmailField(required=True, unique=True, max_length=120)
    image_file = db.StringField(max_length=20, required=True, default='default.jpg')
    password = db.StringField(required=True, min_length=6, max_length=60)
    # acts = db.ListField(db.ReferenceField('Act'))
    # orgs = db.ListField(db.ReferenceField('Organisation'))
    roles = db.EmbeddedDocuemntListField(Role) - User + Org
        contact_details = db.EmbeddedDocumentListField(Address)
        links = db.EmbeddedDocumentField(Links)
        description 200
        profile sf
        media_assets embedded

    def __repr__(self): #dunder or 'magic method'
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Contact(db.DynamicDocument):
    namec = db.StringField(max_length=120, required=True)
    number = db.StringField(max_length=120, required=True)
    band_ref = db.ReferenceField('Band')


class Organisation(db.DynamicDocument):
    org = db.StringField(max_length=120, required=True)
    created_by = db.ReferenceField('User')
    owned_by = db.ListField(db.ReferenceField('User'))
    team = db.ListField(db.ReferenceField('User'))
    address
    links
    profile
    media_assets

    assoc_orgs = db.ListField(db.ReferenceField('Organisation'))
    acts = db.ListField(db.ReferenceField('Band'))
    contacts = db.ListField(db.ReferenceField('User'))

'''
class Act():
    genres
    members (k v)
    discog 
    appearances (tour dates)
    upcoming_appearances tour tour dates venues

'''

class Race(db.Document):
    name = db.StringField(max_length=120, required=True)
    laps = db.ListField(db.ReferenceField('Lap', reverse_delete_rull=db.PULL))

class Lap(db.DynamicDocument):
    runner = db.StringField(max_length=120, required=True)
    lap_time = db.IntField(min_value=0, max_value=None, required=True)
    race_ref = db.ReferenceField('Band')

User.register_delete_rule(Band, 'added_by', db.CASCADE)
###
Race.register_delete_rule(Lap, 'race_ref', db.CASCADE)
Band.register_delete_rule(Contact, 'band_ref', db.CASCADE)


bands = [
    {
        #_id
        "name": "The Divine Comedy",
        "genres": ["rock, pop, comedy, satire"],
        "summary": "The Divine Comedy are a pop band from Northern Ireland, fronted by Neil Hannon. Over the years, many musicians have joined the band on tour and for recording sessions but the driving force of the band and its main (and sometimes only) member has always been Neil Hannon.",
        "members": [{ #cast k v
            "k": "vocals/keyboards/guitar",
            "v": "Neil Hannon",
            "k": "vocals/celesta",
            "v": "John Allen",
            "k": "bass guitar",
            "v": "Simon Little",
            "k": "vocals/guitar",
            "v": "Anthony 'Tosh' Flood"
        }],
        "links": [{ 
            "web": "thedivinecomedy.com",
            "music": [{
                "k": "youtube",
                "v": "divinecomedyhq",
                "k": "apple",
                "k": "the-divine-comedy",
                "v": "7EV6jW6dotBdvsHj6xPixi",
                "k": "google",
                "v": "Ao6zqphzxsmbgeegog3jfmtfciu",
                "k": "deezer",
                "v": "1298"
            }],
            "social": [{
                "k": "facebook",
                "v": "divinecomedyhq",
                "k": "twitter",
                "v": "divinecomedyhq",
                "k": "instagram",
                "v": "divinecomedyhq"
            }],
        }],
        "media_assets": [{
            "default":[{
                "pictures": [{
                    "landscape": "",
                    "square" : "",
                    "portrait": ""
                    }],
                "video": "https://www.youtube.com/watch?v=ZFjfa_RB6Pc",
                "audio": "",
                "text": [{
                        "single_sms":"The Divine Comedy are a pop band from Northern Ireland, fronted by the wry lyricist Neil Hannon.",
                        "tweet":"Chamber-Pop Band 'The Divine Comedy' new album launched and tour dates announced.",
                        "paragraph":"The Divine Comedy are a pop band from Northern Ireland, fronted by Neil Hannon. Over the years, many musicians have joined the band on tour and for recording sessions but the driving force of the band and its main (and sometimes only) member has always been Neil Hannon.",
                        "summary": "The Divine Comedy are a chamber pop band from Northern Ireland formed in 1989 and fronted by Neil Hannon. Hannon has been the only constant member of the group, playing, in some instances, all of the non-orchestral instrumentation except drums. To date, twelve studio albums have been released under the Divine Comedy name. The group achieved their greatest commercial success in the years 1996–99, during which they had nine singles that made the UK Top 40, including the top ten hit 'National Express'.",
                        "long":"Neil Hannon has been the only ever-present member of the band, being its founder in 1989 when he was joined by John McCullagh and Kevin Traynor. Their first album, the heavily R.E.M.-influenced and now-deleted Fanfare for the Comic Muse, enjoyed little success. A couple of equally unsuccessful EPs – Timewatch (1991); Europop (1992) – were to follow, with newly recruited member John Allen handling lead vocals on some tracks. After the commercial failure of the Europop EP, this line-up soon fell apart. Hannon, however, was not deterred in his efforts and re-entered the studio in March 1993, teaming up with co-producer/drummer Darren Allison, for the recording of Liberation.[1] Featuring a fairly diverse musical outlook that goes from the tongue-in-cheek synth pop of 'Europop' (nearly unrecognisable from the previously released version) to the classical stylings of 'Timewatching', it is also characterised by a plethora of literary references: 'Bernice Bobs Her Hair' recalls a short story by F. Scott Fitzgerald; 'Three Sisters' draws upon the play by Anton Chekhov; and 'Lucy' is essentially three William Wordsworth poems abridged to music. This led to a degree of critical acclaim, but commercial success still proved elusive. Indeed, it was only some minor success in France that really enabled Hannon to proceed to his second effort Promenade. Released in 1994, and co-produced, once again, with Darren Allison, this was heavily driven by classical influences, with Michael Nyman's stylings clearly an inspiration. Hannon himself acknowledged this when he apparently sent a copy of his new album to the composer, jokingly asking him not to sue. Essentially, a concept album about a day spent by two lovers, it also received similar critical acclaim to that which Liberation was afforded. Commercial success, though, was not forthcoming despite some of Hannon's best songwriting to date, including 'Don't Look Down', 'The Summerhouse' and subsequent live favourite 'Tonight We Fly'. Soon after the release of the album the Divine Comedy went on tour with Tori Amos, supporting her during her European dates.",
                        "markdown": "",
                        "pdf_link": "",
                  }],
            }],
              "latest":[{ #dupe
                "pictures": [{
                    "landscape": "",
                    "square" : "",
                    "portrait": ""
                    }],
                "video": "https://www.youtube.com/watch?v=-TvOIT4dLLo",
                "audio": "https://media.radiocms.net/uploads/2019/07/10165412/THE-DIVINE-COMEDY-SESSION.mp3",
                "text": [{
                        "single_sms":"",
                        "tweet":"",
                        "paragraph":"",
                        "summary": "",
                        "long":"",
                        "md": "",
                        "pdf": "",
                }],
            }],
        }],
        "current_tour_dates": [{ # 15 dates (per 6mths) from total
            "venue":"Wexford Arts Centre",
            "date": "2020-08-09-20:30:00",
            "status": "confirmed", # confirmed, tbc, rumor, cancelled, rescheduled
            "ticket_link": "wexfordartscentre.ticketsolve.com/shows/879613034",
            "venue_contacts": [{
                "k": "website",
                "v": "wexfordartscentre.ticketsolve.ie",
                "k": "email",
                "v": "boxoffice@wexfordartscentre.ie",
                "k": "Box Office Tel",
                "v": "+353539122334",
                "k": "Box Office Alt",
                "v": "+3535191345667"
            }]
        }],
        "contacts": [{
            "bookings": { # rule at least 2 contacts
                "name": "Neil Hannon",
                "phone": "+353873456677",
                "email": "neil@thedivinecomedy.com"
            },
            "bookings_alt": { # dupe
                "name": "Neil Hannon",
                "phone": "+447873456677",
                "email": "neil@thedivinecomedy.com"
            },
            "manager": {
                "name": "Denise Naughton",
                "company": "DN Promotions",
                "phone": "+445678234466",
                "address": {
                    "line_1": "3 The Pines",
                    "line_2": "Silvermines",
                    "town_city": "Ardragh",
                    "county_region": "County Antrim",
                    "post_eircode": "BT23 32CX",
                    "country": "Northern Ireland (UK)"
                    }
            },
            "mgmt_assistant": {
                "name": "Peter Browne",
                "company": "DN Promotions",
                "phone": "+44254556677",
                "mobile": "+4475562297833",
                "email": "peterb@dnpromo.com",
                "twitter": "dnpromos_com",
                "youtube": "dnpromos",
                "address": {
                    "line_1": "7 Slieverua Drive",
                    "line_2": "Beleek",
                    "town_city": "Ardragh",
                    "county_region": "County Antrim",
                    "post_eircode": "BT23 32CX",
                    "country": "Northern Ireland (UK)"
                    }
            },
            "tour_manager": {
                "name": "Peter Browne",
                "organisation": "DN Promotions",
                "phone": "+44343556777",
                "mobile": "+4475562297833",
                "email": "peterbrowne88@gmail.com",
                "twitter": "PBandCo_UK"
            }
        }]
}]
'''
tour info (edit dates / dupe)
tourname_bandname

shows = [{

    band/group/name _id
    show/title
    tour (start/end - 6mths) _id
    venue _id
    datetime
    status -> once tbc / confirmed added to current dates
    ticketing
    venue info
    venue contacts
        admin
        ??
        programme_mgr
        director
        book_office_mgr
        book_office_staff
        marketing_mgr
        marketing_assistant (associtae ) - same level
        accounts
    
    band contacts
        booking
        bandleader(s)
        manager
        mgmt_co
        promoter
        producer
        tour_manager
       
    band handles
    hashtags
    venue handles
    hashtags

    blurb
    (duplication but not in views as county/location and timelimited)

    genre/category
    _id,
    title: "name"
    datetime: "opening_time_iso"
    url: ticket_url,
    blurb
        types
            desc
        media
            images: {
               thumb: show.querySelector("url[size='thumb']").innerHTML,
               medium: show.querySelector("url[size='medium']").innerHTML,
               large: show.querySelector("url[size='large']").innerHTML
             }
           }



    promo_assets

    special_notice

   "current_tour_dates": [{ # 15 dates (per 6mths) from total
            "venue":"Wexford Arts Centre",
            "date": "2020-08-09-20:30:00",
            "status": "confirmed", # confirmed, tbc, rumor, cancelled, rescheduled
            "ticket_link": "wexfordartscentre.ticketsolve.com/shows/879613034",
            "venue_contacts": [{
                "k": "website",
                "v": "wexfordartscentre.ticketsolve.ie",
                "k": "email",
                "v": "boxoffice@wexfordartscentre.ie",
                "k": "Box Office Tel",
                "v": "+353539122334",
                "k": "Box Office Alt",
                "v": "+3535191345667"
            }]
        }],


}]

{
	"band": "Kerbdog",
    "title": "Kool for KK Cats",
    "strapline": "Kerbdog on tour with special guests"
   }

'''        
tours = [{
    "band": "The Divine Comedy",
    "title": "Venus, Cupid, Folly & Time",
    "strapline": "Thirty Years of The Divine Comedy",
    "datetime": "opening_time_iso",
    "main_ticket_url": "ticket_url",
    "tour_text": {
        "single_sms":"The Divine Comedy are a pop band from Northern Ireland, fronted by the wry lyricist Neil Hannon.",
        "tweet":"Chamber-Pop Band 'The Divine Comedy' new album launched and tour dates announced.",
        "paragraph":"The Divine Comedy are a pop band from Northern Ireland, fronted by Neil Hannon. Over the years, many musicians have joined the band on tour and for recording sessions but the driving force of the band and its main (and sometimes only) member has always been Neil Hannon.",
        "summary": "The Divine Comedy are a chamber pop band from Northern Ireland formed in 1989 and fronted by Neil Hannon. Hannon has been the only constant member of the group, playing, in some instances, all of the non-orchestral instrumentation except drums. To date, twelve studio albums have been released under the Divine Comedy name. The group achieved their greatest commercial success in the years 1996–99, during which they had nine singles that made the UK Top 40, including the top ten hit 'National Express'.",
        "long":"Neil Hannon has been the only ever-present member of the band, being its founder in 1989 when he was joined by John McCullagh and Kevin Traynor. Their first album, the heavily R.E.M.-influenced and now-deleted Fanfare for the Comic Muse, enjoyed little success. A couple of equally unsuccessful EPs – Timewatch (1991); Europop (1992) – were to follow, with newly recruited member John Allen handling lead vocals on some tracks. After the commercial failure of the Europop EP, this line-up soon fell apart. Hannon, however, was not deterred in his efforts and re-entered the studio in March 1993, teaming up with co-producer/drummer Darren Allison, for the recording of Liberation.[1] Featuring a fairly diverse musical outlook that goes from the tongue-in-cheek synth pop of 'Europop' (nearly unrecognisable from the previously released version) to the classical stylings of 'Timewatching', it is also characterised by a plethora of literary references: 'Bernice Bobs Her Hair' recalls a short story by F. Scott Fitzgerald; 'Three Sisters' draws upon the play by Anton Chekhov; and 'Lucy' is essentially three William Wordsworth poems abridged to music. This led to a degree of critical acclaim, but commercial success still proved elusive. Indeed, it was only some minor success in France that really enabled Hannon to proceed to his second effort Promenade. Released in 1994, and co-produced, once again, with Darren Allison, this was heavily driven by classical influences, with Michael Nyman's stylings clearly an inspiration. Hannon himself acknowledged this when he apparently sent a copy of his new album to the composer, jokingly asking him not to sue. Essentially, a concept album about a day spent by two lovers, it also received similar critical acclaim to that which Liberation was afforded. Commercial success, though, was not forthcoming despite some of Hannon's best songwriting to date, including 'Don't Look Down', 'The Summerhouse' and subsequent live favourite 'Tonight We Fly'. Soon after the release of the album the Divine Comedy went on tour with Tori Amos, supporting her during her European dates.",
        "markdown": "",
        "pdf_link": "",
    },
    "media": {
        "band_media": {
                "pictures": { #sizes
                            "landscape": "",
                            "square" : "",
                            "portrait": ""
                            },
                "video": "https://www.youtube.com/watch?v=ZFjfa_RB6Pc"
        },
        "tour_media": {
                "pictures": { #sizes
                            "landscape": "",
                            "square" : "venus_cupid_folly_time.jpg",
                            "portrait": "PW74WMEGXAI6VANDS2IMTCARCE.jpg"
                            },
                "video": "https://www.youtube.com/watch?v=-TvOIT4dLLo",
                "audio": "https://media.radiocms.net/uploads/2019/07/10165412/THE-DIVINE-COMEDY-SESSION.mp3",
                "other": [{
                    "k" : " ",
                    "v" : " "
                }]
        },
    }
},
    {"band": "A House",
    "title": "Last Chance Saloon",
    "strapline": "A House on tour with special guests",
    "tour_text": {
        "single_sms":"A-House were formed in 1985 upon the break up of Last Chance.",
        "tweet":"A-House would like to invite you to The Last Chance Saloon. Tour Dates announced.",
        "paragraph":"A-House were formed in 1985 upon the break up of Last Chance. The group was built around Dave Couse (Vocals), Fergal Banbury (Guitars) and Martin Healy (Bass Guitar). The line up saw several changes, however, this trio remained at the heart of A-House throughout their 12 year career. Throughout the late eighties and early nineties, A-House were consistenly viewed as the intelligent voice of Irish rock music. Unfortunately, this artistic respect scarely translated into popular success.",
        "summary": "In 1987, A-House opened their own account with the release of two singles, Kick Me Again Jesus and Snowball Down on their own independent label. Both were well received with Kick Me Again Jesus rated the 'Single Of The Week' by the NME. This early promise eventually led to a contract with Blanco-Y-Negro with whom they released their debut album, On Our Big Fat Merry-Go-Round, in 1988.",
        "long": "A-House were formed in 1985 upon the break up of Last Chance. The group was built around Dave Couse (Vocals), Fergal Banbury (Guitars) and Martin Healy (Bass Guitar). The line up saw several changes, however, this trio remained at the heart of A-House throughout their 12 year career. Throughout the late eighties and early nineties, A-House were consistenly viewed as the intelligent voice of Irish rock music. Unfortunately, this artistic respect scarely translated into popular success. In 1987, A-House opened their own account with the release of two singles, Kick Me Again Jesus and Snowball Down on their own independent label. Both were well received with Kick Me Again Jesus rated the 'Single Of The Week' by the NME. This early promise eventually led to a contract with Blanco-Y-Negro with whom they released their debut album, On Our Big Fat Merry-Go-Round, in 1988. This was followed by the realease of I Want To Much in 1990. The album was recorded on the Island of Innisboffin (off the west coast of Ireland). This album was to be A-House's final release with Blanco-Y-Negro as the lack of commercial success had taken its toll. Dermot Wylie decided to leave the band and soon after Blanco-Y-Negro also severed it's links with the band. The future looked bleak. Ironically, the departure from Blanco-Y-Negro paved the way for the most successful period in A-House's career. Soon after the split, the band released the 'Doodle E.P.' on Setanta records. This was soon followed by the release of the 'Bingo E.P.' featuring the wonderful Endless Art. The single was critically lauded and was on heavy rotation in the UK. Unfortunately, Setanta had limited resources with which to support the single which ultimately made little impression on the UK charts. By this time, the band's number had been swollen by the recruitment of Dave Dawson on drums, Dave Morrisey on keyboards and Susan Kavanagh on Backing vocals.",
        "markdown": "",
        "pdf_link": "",
    },

    }

]
