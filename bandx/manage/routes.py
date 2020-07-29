import os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root, register_breadcrumb

from flask_login import current_user, login_required, login_user, logout_user

from bandx.models.entities import Band, Towns, User, Phone, Contact, Links, Email, BandMember, Assets
from bandx.manage.forms import CreateUpdateBandForm
from bandx.utils.gns import nav
from bandx.api.routes import list_genres
from bandx.utils.helpers import *
from mongoengine.errors import NotUniqueError


manage = Blueprint('manage', __name__, url_prefix='/manage') # import_name , usually the current module
default_breadcrumb_root(manage, '.public')

@manage.route("/")
@manage.route("/bands")
@register_breadcrumb(manage, '.', 'Manage My Bands')
def manage_bands_home(bname=None):
    user = User.objects(id=current_user.id).first()
    page = request.args.get("page", 1, type=int)
    bands = Band.objects(created_by=user).order_by('-date_created').paginate(per_page=8, page=page)
    return render_template("manage_bands.html", bands=bands, sidebar=True)

@manage.route("/bands/")
def redirector():
    return redirect(url_for("manage.manage_bands_home"))


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



@manage.route("/bands/new/", methods=("GET", "POST"))
def add_band():
    form = CreateUpdateBandForm()
    genres = list_genres()
    form_legend = "Add Band"
    print(request.form)
    if form.validate_on_submit():
        #return request.form
        user = User.objects(id=current_user.id).first()
        if form.media_assets.featured_image.data:
            picture_file = save_picture(form.media_assets.featured_image.data, band=True)
            assets = Assets(
                        featured_image = picture_file if picture_file else 'defaultband.jpg'
                    )
        else:
            assets = Assets(
                featured_image = 'defaultband.jpg'
             )
        if form.media_assets.featured_video.data:
            get_video_service_and_id(form.media_assets.featured_video.data)
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
        new_phone = Phone(
                mobile = form.contact_details.contact_numbers.mobile.data,
                number = form.contact_details.contact_numbers.number.data
        )
        contact.contact_numbers = new_phone
        new_email = Email(
            email_title = form.contact_details.contact_emails.email_title.data,
            email_address = form.contact_details.contact_emails.email_address.data
        )
        contact.contact_emails = new_email
        weblinks = Links()
        weblinks.enquiries = form.enquiries_url.data
        catalogue_name = de_article(form.band_name.data)
        band = Band(
                band_name= form.band_name.data,
                catalogue_name = catalogue_name,
                description = form.description.data,
                created_by = user,
                hometown={"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data},
                profile = form.profile.data,
                strapline = form.strapline.data,
                contact_details = contact,
                links = weblinks,
                media_assets = assets
            )
        for member in form.members.data:
            new_member = BandMember(**member)
            band.band_members.append(new_member)
        genrelist = [genre.strip().replace(' ', '-').lower() for gl in request.form.getlist('genre') for genre in gl.split(',') ]
        band.genres = list(filter(None, set(genrelist)))
        try:
            band.save()
        except NotUniqueError:
            form.band_name.errors =  {"Unfortunately that Band Name already exists, please amend or choose something else."}
            return render_template("manage_band_create_update_form.html", form=form, genrelist=genres, form_legend = form_legend, band=False)
        # user.update(push__posts=post) remember to add band to user
        return redirect(url_for('manage.manage_bands_home'))
    towns = Towns.objects(county="Antrim").first()["towns"]
    form.hometown.origin_town.choices = [(otown, otown) for otown in towns]
    return render_template("manage_band_create_update_form.html", form=form, genrelist=genres, form_legend = form_legend, band=False)



@manage.route("/band/<string:bname>/")
# @register_breadcrumb(manage, '.', '', dynamic_list_constructor=view_band_dlc)
def preview_band(bname):
    band = Band.objects(band_name=bname).first()
    image_file = url_for('static_media', filename='band_profile_pics/'+band.media_assets.featured_image)
    return render_template("band_detail.html", band=band, image_file=image_file)


@manage.route("/band/<string:bname>/edit", methods=('GET', 'POST'))
# @login_required
def update_band_profile(bname):
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
        new_phone = Phone(
                mobile = bool(form.contact_details.contact_numbers.mobile.data),
                number = form.contact_details.contact_numbers.number.data
        )
        contact.contact_numbers = new_phone
        new_email = Email(
            email_title = form.contact_details.contact_emails.email_title.data,
            email_address = form.contact_details.contact_emails.email_address.data
        )
        contact.contact_emails = new_email
        weblinks = Links()
        weblinks.enquiries = form.enquiries_url.data
        band.band_name= form.band_name.data
        band.catalogue_name = de_article(form.band_name.data)
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
        return redirect(url_for('manage.manage_bands_home'))
    elif request.method == "GET":
        form.band_name.data = band.band_name
        form.description.data = band.description
        form.strapline.data = band.strapline
        form.profile.data = band.profile
        form.contact_details.contact_name.data = band.contact_details.contact_name
        form.contact_details.contact_title.data = band.contact_details.contact_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        form.contact_details.contact_numbers.mobile.data = band.contact_details.contact_numbers.mobile
        form.contact_details.contact_numbers.number.data = band.contact_details.contact_numbers.number
        form.contact_details.contact_emails.email_title.data = band.contact_details.contact_emails.email_title
        form.contact_details.contact_emails.email_address.data = band.contact_details.contact_emails.email_address
        form.media_assets.featured_video.data = (("https://www.youtube.com/watch?v=" if band.media_assets.featured_video["service"] == "youtube" else "https://www.vimeo.com/"  )   +band.media_assets.featured_video["vid"]) if band.media_assets.featured_video else None
        form.genres.data = ",".join(map(str,band.genres))
        form.enquiries_url.data = band.links.enquiries
    selected_county = band.hometown["county"] if band.hometown["county"] is not None else "Antrim"
    selected_town = band.hometown["town"] if band.hometown["town"] is not None else "none"
    genres = list_genres()
    form_legend="Edit Band Profile"
    return render_template("manage_band_create_update_form.html", form=form, genrelist=genres, form_legend="Edit Band Profile",
                            selected_county=selected_county, selected_town=selected_town, band=band)


@manage.route("/band/<string:bname>/delete", methods=["POST"])
# @login_required
def delete_band(bname):
    band = Band.objects(band_name=bname).first() 
    if band.created_by.id != current_user.id:
        abort(403)
    band.delete()
    flash("Band has been deleted!", "success")
    return redirect(url_for("manage.manage_bands_home"))


'''


def view_band_dlc(*args, **kwargs):
    if request.view_args:
        bname = ''
        bname = request.view_args['bname']
    # user = User.query.get(user_id)
    # return [{ 'text': 'Manage My Bands', 'url': url_for('manage.manage_bands_home')}, {'text': bname, 'url': url_for('manage.preview_band', bname=bname) }]
        return [{ 'text': 'Manage My Bands', 'url': url_for('manage.manage_bands_home')}, {'text': bname }]
    else:
        return []



{
  "band_name": "A Band 2", 
  "contact_details-contact_emails-email_address": "live@live.ie", 
  "contact_details-contact_emails-email_title": "", 
  "contact_details-contact_name": "", 
  "contact_details-contact_numbers-mobile": "True", 
  "contact_details-contact_numbers-number": "", 
  "contact_details-contact_title": "", 
  "created_by": "", 
  "csrf_token": "IjRjNTczOTEwNDYzODNiM2NiNWJlZjBiNDUzY2Q1ZmY5NWM3OTZiMjQi.XyGfrA.F1ACf3oApNNFfFh4eyl2UWxa3h0", 
  "description": "a", 
  "enquiries_url": "", 
  "genre": "", 
  "hometown-origin_county": "Antrim", 
  "hometown-origin_town": "Aghagallon", 
  "media_assets-featured_video": "", 
  "members-0-instruments": "", 
  "members-0-musician": "", 
  "profile": "a", 
  "strapline": "", 
  "submit": "Save"
}

'''