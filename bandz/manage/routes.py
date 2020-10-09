import os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    session, url_for)
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root, register_breadcrumb
from flask_login import current_user, login_required, login_user, logout_user
from flask_mongoengine.pagination import Pagination
from mongoengine.errors import NotUniqueError
import phonenumbers
# bandz modules
from bandz.models.entities import Band, Towns, User, Phone, Contact, Links, Email, BandMember, Assets
from bandz.manage.forms import CreateUpdateBandForm, CreateBandForm1, CreateBandForm2, CreateBandForm3, CreateBandForm4
from bandz.utils.gns import nav
from bandz.api.routes import list_genres
from bandz.utils.helpers import *

# MANAGE const
manage = Blueprint('manage', __name__, url_prefix='/manage') # import_name , usually the current module
default_breadcrumb_root(manage, '.public')
PER_PAGE = 10
ALPHABET = 'abcdefghijklmnopqrstuvwxyz1'


# dynamic list constructor for MANAGE breadcrumbs
def view_manage_dlc(*args, **kwargs):
    if request.referrer and request.referrer != request.url_root:
        referrer = request.referrer.replace(request.url_root,'')
        referrer = referrer.split("/",5) if len(referrer) > 0 else ['mhome']
        print(referrer)
        if referrer[0] == 'mhome':
            return [{'text': 'Manage My Bands'}]
        if len(referrer) > 2:
            band_view = 'recent' if (referrer[2] == 'recent' or referrer[2] == '') and ('band_view' not in request.view_args or request.view_args['band_view'] == 'recent') else 'alpha'
        else:
            band_view = 'recent' if 'band_view' not in request.view_args else 'alpha'
        letter = request.view_args['letter'] if 'letter' in request.view_args else 'a'
        bname = request.view_args['bname'] if 'bname' in request.view_args else None
        if bname == None:
            if band_view == 'alpha':
                return [
                    { 'text': 'alphabetically', 'url': url_for('.manage_bands_home', band_view=band_view, letter='a') }, 
                    { 'text': letter.upper(), 'url': url_for('.manage_bands_home', band_view=band_view, letter=letter) },
                    ]
            else:
                return [{'text': 'Recent Edits', 'url': url_for('.manage_bands_home', band_view=band_view )} ]
        else:
            if band_view == 'alpha':
                return [
                        { 'text': 'alphabetically', 'url': url_for('.manage_bands_home', band_view=band_view, letter='a') }, 
                        { 'text': letter.upper(), 'url': url_for('.manage_bands_home', band_view=band_view, letter=letter) },
                        { 'text': bname.title() }]
            if band_view == 'recent':
                return [{ 'text': band_view.lower(), 'url': url_for('.manage_bands_home', band_view=band_view) },
                        { 'text': bname.title() }]
    else:
        return [{'text': 'Recent'}]


@manage.route("/")
@register_breadcrumb(manage, '.', 'Manage My Bands')
@login_required
def mhome():
    page = request.args.get("page", 1, type=int)
    user = User.objects(id=current_user.id).first()
    bands = Band.objects(created_by=user).order_by('-date_updated', '-date_created').paginate(per_page=PER_PAGE, page=page)
    alphabet = { key:0 for key in ALPHABET }
    return render_template("manage_bands.html", bands=bands, display_breadcrumbs=True, alphabet=alphabet)
    
@manage.route("/bands/")
@manage.route("/bands/<path:band_view>")
@manage.route("/bands/<path:band_view>/<string:letter>/")
@register_breadcrumb(manage, '.manage_bands_home', '', dynamic_list_constructor=view_manage_dlc)
@login_required
def manage_bands_home(band_view='recent', letter='a'):
    letter = '_' if letter == '1' else letter
    user = User.objects(id=current_user.id).first()
    page = request.args.get("page", 1, type=int)
    if band_view == 'recent':
        bands = Band.objects(created_by=user).order_by('-date_updated', '-date_created').paginate(per_page=PER_PAGE, page=page)
        alphabet = { key:0 for key in ALPHABET }
        return render_template("manage_bands.html", bands=bands, display_breadcrumbs=True, alphabet=alphabet)
    else:
        pipeline = [{"$match": { "created_by": user.id } },
                {
                    "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{str(letter.upper())}" } } },
                                            { "$project": {"_id": 1, "band_name": 1, "catalogue_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]}}}}, 
                                            { "$sort": { "catalogue_name": 1 }}]
                    }
                }] 
        result = list(Band.objects.aggregate(pipeline))[0]
        bands_by_letter = Pagination(result["bands_by_letter"], int(page), 12)
        _alphabet = 'abcdefghijklmnopqrstuvwxyz_'
        alphabet = { obj["_id"].lower():int(obj["number_of_bands"]) for obj in result["numbers_by_letter"] }
        alphabet = { key:alphabet.setdefault(key, 0) for key in _alphabet }
        alphabet['1'] = alphabet.pop('_') #swap out for letter links 1 == '#' === '_'
        count = bands_by_letter.pages
        if bands_by_letter.total > 0:
            bands_total = bands_by_letter.total
            #bands = Band.objects(created_by=user).order_by('-catalogue_name').paginate(per_page=PER_PAGE, page=page)
            return render_template("manage_bands.html", bands=bands_by_letter, bands_total=bands_total, count=count, display_breadcrumbs=True, alphabet=alphabet)
        else:
            return 'no bands created' #redirect


# @manage.route("/bands/")
# def redirector():
#     return redirect(url_for("manage.manage_bands_home"))


def get_video_service_and_id(url):
    video = {}
    if "youtu" in url:
        video["service"] = "youtube"
    elif "vimeo" in url:
        video["service"] = "vimeo"
    else:
        return None
    v = re.search("(?:https?:\/\/)?(?:www\.)?(?:vimeo.com\/|youtu(?:\.be\/|be.com\/\S*(?:watch|embed)(?:(?:(?=\/[^&\s\?]+(?!\S))\/)|(?:\S*v=|v\/))))([^&\s\?]+)", url)
    video["vid"] = v.group(1).split("=")[1] if v.group(1).startswith("v=") else v.group(1)
    return video


# @manage.route('/bands/checkband')
# def checkband():
#     form = CreateBandForm1()
#     genres = list_genres()
#     return render_template('manage_new_stage1_band_check.html', form=form, genrelist=genres) #form_legend = form_legend, title=title or form_legend, step=step, )


@manage.route('/bands/new/', defaults={'stage': 1}, methods=("GET","POST"))
@manage.route('/bands/new/<int:stage>/', methods=("GET","POST"))
def add_band(stage):
    genres = list_genres()
    if stage == 1:
        form = CreateBandForm1()
        if request.method == "POST" and form.validate_on_submit(): 
            #return request.form
            if form.band_name.validate(form):
                catalogue_name = de_article(form.band_name.data) if int(form.solo.data) == 0 else de_singularise(form.band_name.data)
            session["band"] = { 
            "band_name": form.band_name.data,
            "catalogue_name" : catalogue_name,
            "hometown" : {"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data},
            "solo": form.solo.data
            }
            form = CreateBandForm2()
            stage=2
            return render_template("manage_new_stage2_band_details.html", form=form, stage=stage, genrelist=genres, bname=session["band"]["band_name"])
        else: 
            form = CreateBandForm1()
            return render_template('manage_new_stage1_band_check.html', form=form, stage=1)
    
    if stage == 2:
        form = CreateBandForm2()
        if request.method == "POST" and form.validate_on_submit():
            returned_genrelist = [genre.strip().replace(' ', '-').lower() for gl in request.form.getlist('genre') for genre in gl.split(',') ]
            session["band"]["strapline"] = form.strapline.data
            session["band"]["description"] = form.description.data
            session["band"]["genres"] = list(filter(None, set(returned_genrelist)))
            session.modified = True
            form = CreateBandForm3()
            stage = 3
           # return jsonify(session["band"])
            return render_template("manage_new_stage3_band_profile.html", form=form, stage=stage, bname=session["band"]["band_name"])
        else:
            stage = 2
            return render_template("manage_new_stage2_band_details.html", form=form, stage=stage, genrelist=genres, bname=session["band"]["band_name"])
         
    if stage == 3:
        form = CreateBandForm3()
        if request.method == "POST" and form.validate_on_submit():
            if form.featured_image.data:
                picture_file = save_picture(form.featured_image.data, band=True)
                featured_image = picture_file if picture_file else 'defaultband.jpg'
            else:
                featured_image = "defaultband.jpg"
            session["band"]["featured_image"] = featured_image
            session["band"]["profile"] = form.profile.data
            session["band"]["members"] = [{**member} for member in form.members.data ]
            session.modified = True
            form = CreateBandForm4()
            stage = 4
            return render_template("manage_new_stage4_band_contact.html", form=form, stage=stage, bname=session["band"]["band_name"])
        else:
            stage = 3
            return render_template("manage_new_stage3_band_profile.html", form=form, stage=stage, bname=session["band"]["band_name"])

    if stage == 4:
        form = CreateBandForm4()
        if request.method == "POST" and form.validate_on_submit():
            user = User.objects(id=current_user.id).first()
            contact = Contact()
            contact.contact_name = form.contact_details.contact_name.data
            if len(form.contact_details.contact_title.data.rstrip()) == 0:
                contact.contact_title = "Enquiries"
            else:
                contact.contact_title = form.contact_details.contact_title.data
            if len(form.contact_details.contact_generic_title.data.rstrip()) == 0:
                contact.contact_generic_title = "Enquiries"
            else:
                contact.contact_generic_title = form.contact_details.contact_generic_title.data
            _phone = phonenumbers.parse(form.contact_details.contact_numbers.phone.data, form.contact_details.contact_numbers.region.data)
            contact.contact_numbers = Phone(
                    mobile = bool(form.contact_details.contact_numbers.mobile.data),
                    number = phonenumbers.format_number(_phone, phonenumbers.PhoneNumberFormat.E164)
            )
            contact.contact_emails = Email(
                email_title = form.contact_details.contact_emails.email_title.data,
                email_address = form.contact_details.contact_emails.email_address.data
            )
            weblinks = Links( enquiries = form.enquiries_url.data )
            assets = Assets(
                featured_image = session["band"]["featured_image"]
            )
            if form.featured_video.data:
                assets["featured_video"] = get_video_service_and_id(form.featured_video.data)

            band = Band(
                    band_name = session["band"]["band_name"],
                    catalogue_name =  session["band"]["catalogue_name"],
                    genres = session["band"]["genres"],
                    hometown = session["band"]["hometown"],
                    description = session["band"]["description"],
                    strapline = session["band"]["strapline"],
                    profile = session["band"]["profile"],
                    band_members = [BandMember(**member) for member in session["band"]["members"]],
                    media_assets = assets,
                    contact_details = contact,
                    links = weblinks,
                    created_by = user,
                    solo = bool(session["band"]["solo"])
                )
            band.save()
            band_id = band.id
            # user.update(push__posts=post) remember to add band to user
            band = Band.objects(id=band_id).first()
            return render_template("band_detail.html", band=band)
        else:
            stage = 4
            return render_template("manage_new_stage4_band_contact.html", form=form, stage=stage, bname=session["band"]["band_name"])




@manage.route("/band/<string:band_view>/<string:letter>/<string:bname>/")
@register_breadcrumb(manage, '.preview_band', '', dynamic_list_constructor=view_manage_dlc)
@login_required
def preview_band(bname=None, band_view='recent', letter='a'):
    if bname == None:
        return redirect(url_for('manage.manage_bands_home', band_view='alpha'))
    band = Band.objects(band_name=bname).first()
    image_file = url_for('static_media', filename='band_profile_pics/'+band.media_assets.featured_image)
    return render_template("band_detail.html", band=band, image_file=image_file, display_breadcrumbs=True)


def view_update_dlc(*args, **kwargs):
    bname = request.view_args['bname']
    return [{'text': 'Edit Band', 'url': url_for('.manage_bands_home')}, {'text': bname.title() }]


@manage.route("/band/<string:band_view>/<string:letter>/<string:bname>/edit", methods=('GET', 'POST'))
@register_breadcrumb(manage, '.update_band_profile', '', dynamic_list_constructor=view_update_dlc) 
@login_required
def update_band_profile(bname, letter, band_view):
    # flask-login uses a proxy that doesn't play nice with mongoengine
    # so current_user must be cast as user 
    user = User.objects(id=current_user.id).first()
    band = Band.objects(band_name=bname).first()
    if band.created_by.id != current_user.id:
        abort(403)
    form = CreateUpdateBandForm()
    if form.validate_on_submit():
        if form.media_assets.featured_image.data:
            picture_file = save_picture(form.media_assets.featured_image.data, band=True)
            band.media_assets.featured_image = picture_file
        if form.media_assets.featured_video.data:
           band.media_assets.featured_video = get_video_service_and_id(form.media_assets.featured_video.data)
        contact = Contact()
        contact.contact_name = form.contact_details.contact_name.data
        contact.contact_title = form.contact_details.contact_title.data
        contact.contact_generic_title = form.contact_details.contact_generic_title.data
        phone = phonenumbers.parse(form.contact_details.contact_numbers.phone.data, form.contact_details.contact_numbers.region.data)
        new_phone = Phone(
                mobile = bool(form.contact_details.contact_numbers.mobile.data),
                number = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        )
        contact.contact_numbers = new_phone
        new_email = Email(
            email_title = form.contact_details.contact_emails.email_title.data,
            email_address = form.contact_details.contact_emails.email_address.data
        )
        contact.contact_emails = new_email
        weblinks = Links()
        weblinks.enquiries = form.enquiries_url.data
        band.solo = bool(form.solo.data)
        band.band_name= form.band_name.data
        band.catalogue_name = de_article(form.band_name.data)
        band.date_updated = datetime.utcnow
        band.description = form.description.data
        band.genres.clear()
        genrelist = [genre.strip().replace(' ', '-').lower() for gl in request.form.getlist('genre') for genre in gl.split(',') ]
        band.genres = list(filter(None, set(genrelist)))
        band.hometown= {"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data}
        band.profile = form.profile.data
        band.strapline = form.strapline.data
        band.contact_details = contact
        band.links = weblinks
        band.band_members.clear()
        for member in form.members.data:
            new_member = BandMember()
            new_member.musician = member["musician"]
            new_member.instruments = member["instruments"]
            band.band_members.append(new_member)
        band.save()
        flash("Band details updated!", "success")
        return redirect(url_for('manage.manage_bands_home', toggle='recent'))
    elif request.method == "GET":
        form.solo.data = False if band.solo else True
        form.band_name.data = band.band_name
        form.description.data = band.description
        form.strapline.data = band.strapline
        form.profile.data = band.profile
        form.contact_details.contact_name.data = band.contact_details.contact_name
        form.contact_details.contact_title.data = band.contact_details.contact_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        form.contact_details.contact_numbers.mobile.data = band.contact_details.contact_numbers.mobile
        form.contact_details.contact_numbers.region.data = "None"
        form.contact_details.contact_numbers.phone.data = band.contact_details.contact_numbers.number
        form.contact_details.contact_emails.email_title.data = band.contact_details.contact_emails.email_title
        form.contact_details.contact_emails.email_address.data = band.contact_details.contact_emails.email_address
        form.media_assets.featured_video.data = (("https://www.youtube.com/watch?v=" if band.media_assets.featured_video["service"] == "youtube" else "https://www.vimeo.com/"  )   +band.media_assets.featured_video["vid"]) if band.media_assets.featured_video else None
        form.genres.data = ",".join(map(str,band.genres))
        form.enquiries_url.data = band.links.enquiries
    selected_county = band.hometown["county"] if band.hometown["county"] is not None else "Antrim"
    selected_town = band.hometown["town"] if band.hometown["town"] is not None else "none"
    genres = list_genres()
    form_legend="Edit Band Profile"
    return render_template("manage_band_update_form.html", form=form, genrelist=genres, form_legend="Edit Band Profile",
                            selected_county=selected_county, selected_town=selected_town, band=band, display_breadcrumbs=True)


@manage.route("/band/<string:bname>/delete", methods=("GET", "POST"))
@login_required
def delete_band(bname):
    band = Band.objects(band_name=bname).first() 
    if band.created_by.id != current_user.id:
        abort(403)
    band.delete()
    flash("Band has been deleted!", "success")
    return redirect(url_for("manage.manage_bands_home", band_view='recent'))
