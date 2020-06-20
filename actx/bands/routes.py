import os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_login import current_user, login_required, login_user, logout_user

from actx.models.entities import Band, Towns, User, Tour, BandMember
from actx.bands.forms import CreateUpdateBandForm, TourDetailsForm
from actx import pictures_folder, profile_pics
from actx.api.routes import list_genres
from actx.utils.helpers import *

#from actx.models.entities import Address, User, Towns, Organisation, Band, Venue, Tour, TourDate
#from actx.users.forms import RegistrationForm, BandDetailsForm, LoginForm, UpdateAccountForm, CreateOrganisationForm, OrganisationDetailsForm, AddressForm, CreateVenueForm, TourDetailsForm

bands = Blueprint('bands', __name__) # import_name , usually the current module


# def list_bands():
#     bands = Band.objects.order_by('org_title')
#     return render_template("bands_list.html", bands=bands)

@bands.route("/bands")
@bands.route("/bands/")
@bands.route("/bands/<band_name>")
@bands.route("/bands/<band_name>/") #, methods=("GET", "POST")
def bands_list(band_name=None):
    if band_name is not None:
        bands = Band.objects(band_name=band_name).first()
    else:
        bands = Band.objects.order_by('-date_created')
    return render_template("bands_list.html", bands=bands)


@bands.route("/bands/manage/new", methods=("GET", "POST"))
def add_band():
    form = CreateUpdateBandForm()
    if form.validate_on_submit():
        return request.form
        # if form.picture.data:
        #     output_size = (400,400)
        #     picture_file = save_picture(form.picture.data, output_size)
# {
#   "band_members-0-instruments": "vocals", 
#   "band_members-0-musician": "Ross", 
#   "band_name": "Test Band", 
#   "contact_details-contact_emails-0-email_address": "ross_geoghegan@hotmail.com", 
#   "contact_details-contact_emails-0-email_title": "Enquiries", 
#   "contact_details-contact_generic_title": "", 
#   "contact_details-contact_name": "", 
#   "contact_details-contact_numbers-0-mobile": "True", 
#   "contact_details-contact_numbers-0-number": "+44470988363", 
#   "contact_details-contact_title": "", 
#   "created_by": "", 
#   "csrf_token": "ImRiNWNkZmE5YjBiNGQxMjg2MGZmNjJlNWJlZTBhMmIxYjY1NWUzZmUi.Xu4tYQ._GQ1AsCEO1_HDWQ58G6dR-FZ4BY", 
#   "description": "Test Description", 
#   "enquiries_url": "https://www.live.ie", 
#   "genres": "", 
#   "hometown-origin_county": "Wexford", 
#   "hometown-origin_town": "Adamstown", 
#   "members-1-band_member": "Ray McClure", 
#   "members-1-instrument": "guitar", 
#   "profile": "History", 
#   "strapline": "Motto", 
#   "submit": "Save"
# }
        user = User.objects(id=current_user.id).first()
        band = Band(
                band_name=form.band_name.data,
                description = form.description.data,
                genres = extract_tags(form.genres.data),
                hometown={"town": form.hometown.origin_town.data, "county": form.hometown.origin_county.data},
                profile = form.profile.data,
                strapline = form.strapline.data,
                band_members = form.band_members.data,
                media_assets = form.media_assets.data,
                contact_details = form.contact_details.data,
                links = form.links.data

                )
        # if form.picture.data:
        #     band.image_file = picture_file
        band.save()
        return redirect(url_for('public.show_tourdates'))
    form.hometown.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    genres = list_genres()
    form_legend = "Add Band"
    return render_template("band_create_update_form.html", form=form, genrelist=genres, form_legend = form_legend)



@bands.route("/bands/manage")
@bands.route("/band/manage/")
def manage_bands():
    pass




@bands.route("/bands/manage/<band_name>", methods=("GET","POST"))
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


    
@bands.route("/bands/manage/<band_name>/tours")
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
