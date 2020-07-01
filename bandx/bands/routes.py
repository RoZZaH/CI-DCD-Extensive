import os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb

from flask_login import current_user, login_required, login_user, logout_user

from bandx.models.entities import Band, Towns, User, Tour, Phone, Contact, Links, Email, BandMember
from bandx.bands.forms import CreateUpdateBandForm, TourDetailsForm
from bandx import pictures_folder, profile_pics
from bandx.utils.gns import nav
from bandx.api.routes import list_genres
from bandx.utils.helpers import *

#from actx.models.entities import Address, User, Towns, Organisation, Band, Venue, Tour, TourDate
#from actx.users.forms import RegistrationForm, BandDetailsForm, LoginForm, UpdateAccountForm, CreateOrganisationForm, OrganisationDetailsForm, AddressForm, CreateVenueForm, TourDetailsForm

bands = Blueprint('bands', __name__, url_prefix='/bands') # import_name , usually the current module
default_breadcrumb_root(bands, '.public')

# def list_bands():
#     bands = Band.objects.order_by('org_title')
#     return render_template("bands_list.html", bands=bands)

# @bands.route("/")
# @bands.route("/bands/")
# @bands.route("/bands/<string:band_name>")
# @bands.route("/bands/<string:band_name>/") #, methods=("GET", "POST")
# def bands_list(band_name=None):
#     if band_name is not None:
#         bands = Band.objects(band_name=band_name).first()
#     else:
#         bands = Band.objects.order_by('-date_created')
#     return render_template("bands_list.html", bands=bands)


@bands.route("/bands/manage/new/", methods=("GET", "POST"))
def add_band():
    form = CreateUpdateBandForm()
    print(request.form)
    if form.validate_on_submit():
        return request.form
        user = User.objects(id=current_user.id).first()
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
        band = Band(
                band_name= form.band_name.data,
                description = form.description.data,
                created_by = user,
                genres = extract_tags(form.genres.data),
                hometown={"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data},
                profile = form.profile.data,
                strapline = form.strapline.data,
                contact_details = contact,
                links = weblinks
                #media_assets = form.media_assets.data,
            )
        for member in form.members.data:
            new_member = BandMember(**member)
            band.band_members.append(new_member)
        band.save()
        return redirect(url_for('public.show_tourdates'))
    form.hometown.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    genres = list_genres()
    form_legend = "Add Band"
    return render_template("band_create_update_form.html", form=form, genrelist=genres, form_legend = form_legend, band=False)



@bands.route("/bands/manage/<string:band_name>/edit", methods=('GET', 'POST'))
# @login_required
def update_band_profile(band_name):
    # flask-login uses a proxy that doesn't play nice with mongoengine
    # so current_user must be cast as user 
    user = User.objects(id=current_user.id).first()
    band = Band.objects(band_name=band_name).first()
    if band.created_by.id != current_user.id:
        abort(403)
    form = CreateUpdateBandForm()
    if form.validate_on_submit():
        return request.form
    #     post.title = form.title.data
    #     post.content = form.content.data
    #     post.author = user
    #     post.save()
    #     flash('Your post has been updated!', 'success')
    #     return redirect(url_for('post.get_post', post_id=post.id))
    elif request.method == "GET":
    
        form.band_name.data = band.band_name
        form.description.data = band.description
        form.strapline.data = band.strapline
        form.profile.data = band.profile
        form.contact_details.contact_name.data = band.contact_details.contact_name
        form.contact_details.contact_title.data = band.contact_details.contact_title
        form.contact_details.contact_generic_title.data = band.contact_details.contact_generic_title
        #form.contact_details.contact_emails = band.contact_details.contact_emails #sent as band object
        form.genres.data = ",".join(map(str,band.genres))
        form.enquiries_url.data = band.links.enquiries

    selected_county = band.hometown["county"] if band.hometown["county"] is not None else "Antrim"
    selected_town = band.hometown["town"] if band.hometown["town"] is not None else "none"
    # image_file = url_for('static_media', filename="band_profile_pics/" + band.image_file)
    genres = list_genres()
    form_legend="Edit Band Profile"
    return render_template("band_create_update_form.html", form=form, genrelist=genres, form_legend="Edit Band Profile",
                            selected_county=selected_county, selected_town=selected_town, band=band) # image_file=image_file)



@bands.route("/manage")

# @bands.route("/bands/manage/")
@register_breadcrumb(bands, '.', 'Manage Bands')
def manage_bands():
    user = User.objects(id=current_user.id).first()
    bands = Band.objects(created_by=user)
    return render_template("band_manage_bands.html", bands=bands, sidebar=True)


@bands.route("/bands/manage/band/<string:band_name>", methods=("GET","POST"))
def manage_band_profile(band_name):
    band = Band.objects(org_title=band_name).first()
    form = CreateUpdateBandForm()
    if form.validate_on_submit():
        if form.picture.data:
            output_size = (400,400)
            picture_file = save_picture(form.picture.data, output_size)

        user = User.objects(id=current_user.id).first()
        band.org_title = form.band_name.data
        band.hometown = {"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data}
        band.description = form.description.data
        band.profile = form.profile.data
        band.strapline = form.strapline.data
        band.genres = extract_tags(form.genres.data)
        if form.picture.data:
            band.image_file = picture_file
        band.save()
        band.members.clear()
        # return request.form
        for member in form.band_members.data:
            new_member = BandMember(
                musician = member.pop("musician"),
                instruments = extract_tags(member.pop("instruments"))
            )
            band.members.append(new_member)
        band.save()

        return redirect(url_for('bands.bands_list'))
    #elif request.method == "GET":
    form.band_name.data = band.org_title
    form.genres.data = ",".join(map(str,band.genres))
    form.strapline.data = band.strapline
    form.description.data = band.description
    form.profile.data = band.profile
    form.hometown.origin_county.data = band.hometown["county"]
    form.hometown.origin_town.data = band.hometown["town"]
    selected_county=form.hometown.origin_county.data if form.hometown.origin_county.data is not None else "Antrim"
    selected_town=form.hometown.origin_town.data if form.hometown.origin_town.data is not None else "none"
    image_file = url_for('static_media', filename="band_profile_pics/" + band.image_file)
    genres = list_genres()
    form_legend="Edit Band Profile"
    return render_template("band_create_update_form.html", form=form, genrelist=genres, form_legend=form_legend,
                            selected_county=selected_county, selected_town=selected_town, image_file=image_file)







    
@bands.route("/bands/manage/<string:band_name>/tours")
def manage_tours(band_name):
    band = Band.objects(org_title=band_name).first()
    if Band.objects(org_title=band_name, tours__size=0):
        band.id = None
        band._cls = "Organisation.Band.Tour"
        band.tours = None
        tour = Tour(**band.to_mongo())
        tour.tour_title = f"New Tour for {band.org_title}"
        tour.save()
        band = Band.objects(org_title=band_name).first()
        band.update(push__tours=tour)
        band.save()
        return "no longer empty"
    else:
        tours = Tour.objects(class_check=True, org_title=band_name)
        return jsonify(tours)
        return render_template("manage_tours.html", tours=tours)

# Tours #

@bands.route("/bands/tours/")
def list_tours():
    tours = Tour.objects()
    #return jsonify(tours)# render_template("manage_tours.html", tours=tours)
    return render_template("manage_tours.html", tours=tours)

@bands.route("/tours/edit/<tour_id>", methods=("GET","POST"))
def edit_tour(tour_id):
    tour = Tour.objects(id=tour_id).first()
    # return jsonify(tour)
    form = TourDetailsForm()
    if form.validate_on_submit(): 
        tour = Tour(
                    org_title=form.org_name.data,
                    tour_strapline=form.strapline.data,
                    tour_title = form.tour_title.data,
                    tour_description = form.tour_description.data,
                    tour_text = form.tour_text.data,
                    genres = extract_tags(form.genres.data)
                )
        tour.save()
        tour.tour_dates.clear()
        for tour_date in form.tour_dates.data:
            strdate =  str(tour_date.pop("td_date")) + " "
            strdate += str(int(tour_date.pop("td_time_hh")) + int(tour_date.pop("td_time_ampm"))) 
            strdate +=  ":" + str(tour_date.pop("td_time_mm")).zfill(2) 
            phones = extract_tags(tour_date.pop("td_venue_phones"))
            urls = extract_tags(tour_date.pop("td_ticket_urls"))
            # for k,v in tour_date.items():
            #         print(f"{k} : {v}")
            hometown = tour_date.pop("td_hometown")
            new_date = TourDate(**tour_date)
            new_date["td_datetime"] = datetime.strptime(strdate, "%Y-%m-%d %H:%M" )
            new_date["td_hometown"] = hometown
            new_date["td_venue_phones"] = phones
            new_date["td_ticket_urls"] = urls
            tour.tour_dates.append(new_date)
        tour.save()
        return request.form
    else:
        genres = list_genres()
        form.org_name.data = tour.org_title
        form.genres.data = ",".join(map(str,tour.genres))
        form.strapline.data = tour.strapline
        form.tour_title.data = tour.tour_title
        form.tour_description.data = tour.description
        form.tour_text.data = tour.tour_text
        # form.tour_dates 
        
    return render_template("tour_details.html", form=form, genrelist=genres)
