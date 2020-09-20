import csv, os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
#from resizeimage import resizeimage
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_bcrypt import generate_password_hash, check_password_hash
from bandz import app
from bandz.models.entities import User, Towns, Band, Phone, Contact, Email, Phone, BandMember, Assets#Venue, Tour, TourDate
from bandz.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm)
from flask_login import current_user, login_required, login_user, logout_user

user = Blueprint('user', __name__) # import_name , usually the current module



def setup_towns():
    resource_path = os.path.join(app.root_path, 'setup')
    with open(os.path.join(resource_path, 'towns.json')) as f:
        file_data = json.load(f)
    townz = []
    for town in file_data:
            townz.append(Towns(**town))
    Towns.objects.insert(townz)
    return True


def setup_bands():
    pass


@user.route('/setup', methods=("GET", "POST"))
def initial_setup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) #bcrypt hashed_pw
        user.save() #db.session.add(user), db.session.commit()
        flash(f"Account created for {form.username.data} - Now Adding Bands! You'll be redirected shortly.", "success") #tuple (msg,cat)
        uid = user.id
        setup_towns()
        resource_path = os.path.join(app.root_path, 'setup')
        with open(os.path.join(resource_path, 'band.json')) as f:
            file_data = json.load(f)
        bandz = []
        for band in file_data:
            if 'date_created' in band.keys():
                date_created = datetime.strptime(band.pop('date_created'), "%Y-%m-%dT%H:%M:%S") 
            else:
                date_created = datetime.utcnow
            bandz.append(Band(**band, created_by = uid, date_created=date_created ))
        bands = Band.objects.insert(bandz)
        return jsonify(bands)

        
        # assets = Assets(
        #         featured_image = "default_band.jpg",
        #         featured_video = {"service": "youtube", "vid": "cDo6Lgylsjg"}
        #         )
        # contact = Contact(
        #         contact_name = "Keith Cullen",
        #         contact_title = "M.D. Setanta Records"
        #         )
        # contact.contact_numbers = Phone(
        #         mobile = bool(0),
        #         number = "+35316078894"
        #         )
        # contact.contact_emails = Email(
        #         email_title = "Bookings",
        #         email_address = "kcullen@setantarecords.com"
        #         )
        # members = [
        #         { "musician": "Dave Couse", "instruments": "vocals" },
        #         { "musician": "Fergal Bunbury", "instruments": "guitar"},
        #         { "musician": "Martin Healy", "instruments": "bass" },
        #         { "musician": "Dermot Wylie", "instruments": "drums"}
        #         ]
        # band = Band(
        #             band_name = "A House",
        #             catalogue_name =  "A-House",
        #             genres = ["indie", "rock"],
        #             hometown = {"town": "Dublin City", "county": "Dublin"},
        #             description = "Intelligent Indie Rock from Dublin",
        #             strapline = "critical acclaim without commerical concern",
        #             profile = "The first single from I Am The Greatest helped both sales and appeal. 'Endless Art', a shopping list litany of deceased cultural icons, is one of the best Irish rock singles of all time. A simple idea executed with style and intelligence, Dave Couse is aware that the song could become a creative albatross around the band's collective neck. \"It depends on whether we allow it to be. I don't think A House are like that. Our feeling is that 'Endless Art' is one good song, so why not have a few more?\"There are a hundred deadbeat Irish rock wannabees for every A-House, who have just released their fifth and best album No More Apologies. Alan Corr met guitarist Fergal Bunbury and vocalist Dave Couse to talk begrudgery, failure and good songwriting. Every time A House release a record (which is refreshingly often) three things happen. First, the Irish rock media is divided down the middle between those who dismiss them as whinging failures and those who proclaim them a national institution who've made consistently great music. Second, at least 30,000 people go out and buy the new album. Third, and most important, the band themselves get on with recording the next one.",
        #             band_members = [BandMember(**member) for member in members],
        #             media_assets = assets,
        #             contact_details = contact,
        #             created_by = uid,
        #             solo = bool(0)
        #         )
        # band.save()
        return redirect(url_for("user.login"))
    if len(list(Band.objects())) == 0:
        return render_template("setup.html", form=form, sidebar=0)
    else:
        print("Inital Setup Completed Already")
        return redirect(url_for("public.results"))




@user.route("/register", methods=("GET", "POST"))
def register():
    if current_user.is_authenticated:
        return redirect(url_for("public.results"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) #bcrypt hashed_pw
        user.save() #db.session.add(user), db.session.commit()
        flash(f"Account created for {form.username.data}! You are now able to log in.", "success") #tuple (msg,cat)
        return redirect(url_for("user.login"))
    return render_template("register.html", title="Register", form=form, sidebar=0)





@user.route("/login", methods=("GET","POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.results"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next") # paam for page trying to access
            return redirect(next_page) if next_page else redirect(url_for("manage.manage_bands_home"))
        else:
            flash(f"Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", form=form)


@user.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.results"))

default_size = (125, 125)
def save_picture(form_picture, output_size=default_size ):
    rand_hex = secrets.token_hex(8)
    _fn, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = rand_hex + f_ext
    picture_path = os.path.join(profile_pics, picture_fn)
    # url_for('static_media', filename="user_profile_pics/" + current_user.image_file)
    # resize
    i = Image.open(form_picture)
    #i.thumbnail(output_size)
    i = i.resize(output_size)
    i.save(picture_path)

    return picture_fn

@user.route("/account", methods=("GET","POST")) #can update
@login_required # here not above
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.save()
        flash(f"Your account has been updated.", "success")
        return redirect(url_for("user.account")) #get rather than repost
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static_media', filename="user_profile_pics/" + current_user.image_file)
    return render_template("user_account.html", title="Account Settings", 
                            image_file=image_file, form=form)



@user.route("/genres")
def list_genres():
    aggregation = list(Band.objects.aggregate([
        {"$unwind": "$genres"},
        {"$group": { "_id": "$genres"} }
    ]))
    genres = []
    for genre in aggregation:
        for k,v in genre.items():
            genres.append(v)
    return ",".join(genres)


def extract_tags(tags):
    whitespace = re.compile("\s")
    nowhite = whitespace.sub("", tags.lower())
    tags_array = nowhite.split(",")

    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned



@user.route("/add_org", methods=("GET", "POST"))
@login_required
def create_org():
    # if User.objects(email=current_user.email, created_orgs__size=0):
    #     return "is empty"
    # else:
    #     orgs = list(User.objects().aggregate([
    #         {"$match": {"email" : current_user.email}},
    #         {"$project":{"created_orgs": 1, "_id": 0} }]))
    #     print(orgs[0]["created_orgs"])
    form = CreateOrganisationForm()
    if form.validate_on_submit():
        org_name=form.org_name.data
        org_type=form.org_type.data
        if org_type == "organisation":
            form = OrganisationDetailsForm()
            form.org_type.data=org_type
            form.org_name.data=org_name
            #form.hometown.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
            if form.validate_on_submit():
                user = User.objects(id=current_user.id).first()
                new_org = Organisation(
                            org_title=form.org_name.data,
                            created_by=user,
                            profile=form.profile.data,
                            description=form.description.data
                            )
                #contacts = Address()
                for contact in form.contacts.data:
                    new_con = Address(**contact)
                    new_org.contact_details.append(new_con)
                new_org.save()
                user.update(push__created_orgs=new_org)
                user.save()
                flash(f"New organisation {form.org_name.data} has been updated.", "success")
                #return redirect(url_for("user.account")) 
                return jsonify(form.contacts.data)
            return render_template("org_details.html", form=form)
        elif org_type == "venue":
            form = CreateVenueForm()
            form.venue_name.data = org_name
            return render_template("venue_details.html", form=form)
        else:
            return redirect(url_for('user.add_band', band_name=org_name))
    return render_template("create_org.html", title="Create Orgnaisation",
                            form=form)

@user.route("/orgs")
def list_orgs():
    #page = request.args.get("page", 1, type=int)
    orgs = Organisation.objects.order_by('-date_created') #.paginate(page=page, per_page=5)
    return render_template("orgs.html", orgs=orgs, title="List of Organisations")


@user.route("/edit_org/<org_name>", methods=("GET", "POST"))
def edit_org(org_name):
    user = User.objects(id=current_user.id).first()
    org = Organisation.objects(org_title=org_name).first()
    # if org.created_by.id != current_user.id:
    #     abort(403)
    form = OrganisationDetailsForm()
    if form.validate_on_submit():       
        org.org_title=form.org_name.data
        org.created_by=user
        org.profile=form.profile.data
        org.description=form.description.data

        org.contact_details.clear()
        for contact in form.contacts.data:
            new_con = Address(**contact)
            org.contact_details.append(new_con)
        org.save()
        f = request.form
        return f
     
    elif request.method == "GET":
        form.oid.data = org.id
        form.org_name.data = org.org_title 
        form.description.data = org.description 
        form.profile.data = org.profile
        form.contacts = [AddressForm(prefix=f"contacts-{i}-",obj=a) for i,a in enumerate(org.contact_details)]  
    return render_template("edit_org.html", title="Update Organisation", form=form)







@user.route("/edit_venue", methods=("GET", "POST"))
def venue_edit():
    form = CreateVenueForm()
    if form.validate_on_submit():
        user = User.objects(id=current_user.id).first()
        if form.venue_address.specifically.data:
            otown = form.venue_address.specifically.data
        else:
            otown = form.venue_hometown.origin_town.data
        venue = Venue(
                org_title=form.venue_name.data,
                description = form.venue_description.data,
                hometown={"town": otown, "county": form.venue_hometown.origin_county.data},
                local_directions=form.venue_directions.data,
                accessibility=form.venue_accessibility.data)
        venue.save()
        #print(form.venue_address.data)
        new_con = Address(**form.venue_address.data)
            # print(contact)
            # new_con = Address(**contact)
        venue.contact_details.append(new_con)
        venue.save()


        return redirect(url_for('public.show_tourdates'))
    form.venue_hometown.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    genres = list_genres()
    return render_template("venue_details.html", form=form)



@user.route("/get_user")
def get_user():
    return current_user.oid
    
