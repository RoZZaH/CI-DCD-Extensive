import os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb

from flask_login import current_user, login_required, login_user, logout_user

from bandx.models.entities import Band, Towns, User, Phone, Contact, Links, Email, BandMember, Assets
from bandx.manage.forms import CreateUpdateBandForm, TourDetailsForm
from bandx.utils.gns import nav
from bandx.api.routes import list_genres
from bandx.utils.helpers import *

#from actx.models.entities import Address, User, Towns, Organisation, Band, Venue, Tour, TourDate
#from actx.users.forms import RegistrationForm, BandDetailsForm, LoginForm, UpdateAccountForm, CreateOrganisationForm, OrganisationDetailsForm, AddressForm, CreateVenueForm, TourDetailsForm

manage = Blueprint('manage', __name__, url_prefix='/manage') # import_name , usually the current module
default_breadcrumb_root(manage, '.public')

@manage.route("/")
@manage.route("/bands")
@register_breadcrumb(manage, '.', 'Manage My Bands')
def manage_bands_home():
    user = User.objects(id=current_user.id).first()
    page = request.args.get("page", 1, type=int)
    bands = Band.objects(created_by=user).order_by('-date_created').paginate(per_page=8, page=page)
    return render_template("manage_bands.html", bands=bands, sidebar=True)


@manage.route("/bands/new/", methods=("GET", "POST"))
def add_band():
    form = CreateUpdateBandForm()
    print(request.form)
    if form.validate_on_submit():
        return request.form
        user = User.objects(id=current_user.id).first()

        # Assets

        assests = Assets(
            featured_image = form.media_assets.featured_image.data,
            featured_video = form.media_assets.featured_video.data
        )

        contact = Contact()
        contact.contact_name = form.contact_details.contact_name.data
        contact.contact_title = form.contact_details.contact_title.data
        contact.contact_generic_title = form.contact_details.contact_generic_title.data
        for phone in form.contact_details.contact_numbers.data:
            new_phone = Phone(**phone)
            contact.contact_numbers.append(new_phone)
        for email in form.contact_details.contact_emails.data:
            new_email = Email(**email)
            contact.contact_emails.append(new_email)
        
        weblinks = Links()
        weblinks.enquiries = form.enquiries_url.data




        band = Band(
                band_name= form.band_name.data,
                description = form.description.data,
                created_by = user,
                genres = extract_tags(form.genres.data),
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




        band.save()
        # user.update(push__posts=post) remember to add band to user
        return redirect(url_for('public.show_tourdates'))
    form.hometown.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    genres = list_genres()
    form_legend = "Add Band"
    return render_template("manage_band_create_update_band.html", form=form, genrelist=genres, form_legend = form_legend, band=False)



@manage.route("/band/<string:band_name>/edit", methods=('GET', 'POST'))
# @login_required
def update_band_profile(band_name):
    # flask-login uses a proxy that doesn't play nice with mongoengine
    # so current_user must be cast as user 
    user = User.objects(id=current_user.id).first()
    band = Band.objects(band_name=band_name).first()
    if band.created_by.id != current_user.id:
        abort(403)
    form = CreateUpdateBandForm()
    image_file = url_for('static_media', filename='band_profile_pics/'+band.media_assets.featured_image)
    if form.validate_on_submit():
           # return request.form
       # doesn't change created by or date_created
        picture_file = None
        if form.media_assets.featured_image.data:
            picture_file = save_picture(form.media_assets.featured_image.data, band=True)
            assets = Assets(
                featured_image = picture_file,
                featured_video = form.media_assets.featured_video.data or None
            )
        elif form.media_assets.featured_video.data:
            assets = Assets(
                featured_image = picture_file,
                featured_video = form.media_assets.featured_video.data
            )
        else:
            assets = Assets()
        contact = Contact()
        contact.contact_name = form.contact_details.contact_name.data
        contact.contact_title = form.contact_details.contact_title.data
        contact.contact_generic_title = form.contact_details.contact_generic_title.data
        for phone in form.contact_details.contact_numbers.data:
            new_phone = Phone(**phone)
            contact.contact_numbers.append(new_phone)
        for email in form.contact_details.contact_emails.data:
            new_email = Email(**email) #contact.contact_emails.append(Email(**email)
            contact.contact_emails.append(new_email)
        
        weblinks = Links()
        weblinks.enquiries = form.enquiries_url.data
        # found band overwrite props
        band.band_name= form.band_name.data
        band.description = form.description.data
        band.genres.clear()
        band.genres = extract_tags(form.genres.data)
        band.hometown={"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data}
        band.profile = form.profile.data
        band.strapline = form.strapline.data
        band.contact_details = contact
        band.links = weblinks
        band.media_assets = assets
        band.band_members.clear() #must clear aut arrays before appending
        for member in form.members.data:
            new_member = BandMember()
            new_member.musician = member["musician"]
            new_member.instruments = member["instruments"]
            band.band_members.append(new_member)
        band.save()
        flash("band info updated!", "success")
        # redirect
        return redirect(url_for('manage.manage_bands_home'))
    elif request.method == "GET":
    
        form.band_name.data = band.band_name
        form.description.data = band.description
        form.strapline.data = band.strapline
        form.profile.data = band.profile
        form.contact_details.contact_name.data = band.contact_details.contact_name
        form.contact_details.contact_title.data = band.contact_details.contact_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        #form.contact_details.contact_emails = band.contact_details.contact_emails #sent as band object
        form.media_assets.featured_image.data = band.media_assets.featured_image
        form.media_assets.featured_video.data = band.media_assets.featured_video
        form.genres.data = ",".join(map(str,band.genres))
        form.enquiries_url.data = band.links.enquiries

    selected_county = band.hometown["county"] if band.hometown["county"] is not None else "Antrim"
    selected_town = band.hometown["town"] if band.hometown["town"] is not None else "none"
    # image_file = url_for('static_media', filename="band_profile_pics/" + band.image_file)
    genres = list_genres()
    form_legend="Edit Band Profile"
    return render_template("manage_band_create_update_form.html", form=form, genrelist=genres, form_legend="Edit Band Profile",
                            selected_county=selected_county, selected_town=selected_town, band=band, image_file=image_file) # image_file=image_file)


@manage.route("/band/<string:bname>/delete", methods=["POST"]) # only from modal
# @login_required
def delete_band(bname):
    band = Band.objects(band_name=bname).first() # Post.query.get(post_id)
    if band.created_by.id != current_user.id: #band.created_by.id != current_user.id
        abort(403) # forbidden
    band.delete()
    flash("Band has been deleted!", "success")
    return redirect(url_for("manage.manage_bands_home"))

# // ammend@manage.route("/band/<string:band_name>/edit", methods=('GET', 'POST'))
# # @login_required
# def update_band_profile(band_name):
#     # flask-login uses a proxy that doesn't play nice with mongoengine
#     # so current_user must be cast as user 
#     user = User.objects(id=current_user.id).first()
#     band = Band.objects(band_name=band_name).first()
#     if band.created_by.id != current_user.id:
#         abort(403)
#     form = CreateUpdateBandForm()
#     image_file = url_for('static_media', filename='band_profile_pics/'+band.media_assets.featured_image)
#     if form.validate_on_submit():
#         picture_file = None
#         if form.media_assets.featured_image.data:
#             picture_file = save_picture(form.media_assets.featured_image.data, band=True)
#             assets = Assets(
#                 featured_image = picture_file,
#                 featured_video = form.media_assets.featured_video.data or None
#             )
#         elif form.media_assets.featured_video.data:
#             assets = Assets(
#                 featured_image = picture_file,
#                 featured_video = form.media_assets.featured_video.data
#             )
#         else:
#             assets = Assets()
#     #     flash('Your post has been updated!', 'success')
#        # return request.form
#         contact = Contact()
#         contact.contact_name = form.contact_details.contact_name.data
#         contact.contact_title = form.contact_details.contact_title.data
#         contact.contact_generic_title = form.contact_details.contact_generic_title.data
#         for phone in form.contact_details.contact_numbers.data:
#             new_phone = Phone(**phone)
#             contact.contact_numbers.append(new_phone)
#         for email in form.contact_details.contact_emails.data:
#             new_email = Email(**email) #contact.contact_emails.append(Email(**email)
#             contact.contact_emails.append(new_email)
        
#         weblinks = Links()
#         weblinks.enquiries = form.enquiries_url.data
#         band = Band(
#                 band_name= form.band_name.data,
#                 description = form.description.data,
#                 created_by = user,
#                 genres = extract_tags(form.genres.data),
#                 hometown={"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data},
#                 profile = form.profile.data,
#                 strapline = form.strapline.data,
#                 contact_details = contact,
#                 links = weblinks,
#                 media_assets = assets,
#             )
#         # band.save()
#         band.band_members.clear()
#         for member in form.members.data:
#             new_member = BandMember()
#             new_member.musician = member["musician"]
#             new_member.instruments = member["instruments"]
#             band.band_members.append(new_member)
#         band.save()
#         flash("band info updated!", "success")
#         # redirect
#         return redirect(url_for('manage.manage_bands_home'))
#     elif request.method == "GET":
    
#         form.band_name.data = band.band_name
#         form.description.data = band.description
#         form.strapline.data = band.strapline
#         form.profile.data = band.profile
#         form.contact_details.contact_name.data = band.contact_details.contact_name
#         form.contact_details.contact_title.data = band.contact_details.contact_title
#         form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
#         #form.contact_details.contact_emails = band.contact_details.contact_emails #sent as band object
#         form.media_assets.featured_image.data = band.media_assets.featured_image
#         form.media_assets.featured_video.data = band.media_assets.featured_video
#         form.genres.data = ",".join(map(str,band.genres))
#         form.enquiries_url.data = band.links.enquiries

#     selected_county = band.hometown["county"] if band.hometown["county"] is not None else "Antrim"
#     selected_town = band.hometown["town"] if band.hometown["town"] is not None else "none"
#     # image_file = url_for('static_media', filename="band_profile_pics/" + band.image_file)
#     genres = list_genres()
#     form_legend="Edit Band Profile"
#     return render_template("manage_band_create_update_form.html", form=form, genrelist=genres, form_legend="Edit Band Profile",
#                             selected_county=selected_county, selected_town=selected_town, band=band, image_file=image_file) # image_file=image_file)



