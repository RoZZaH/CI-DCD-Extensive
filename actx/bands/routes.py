import re
from flask import jsonify
from flask import (Blueprint, flash, current_app,
    redirect, render_template, request, Response,
    url_for)

from actx.models.entities import tours, Band, Towns
from flask_login import current_user, login_required, login_user, logout_user
from actx.bands.forms import CreateBandForm


bands = Blueprint('bands', __name__) # import_name , usually the current module


@bands.route("/bandz")
def list_all():
   # return "<h1>Hello</h1>"
   bandz = Band.objects()
   return jsonify(bandz)

@bands.route("/genres2")
def list_genres():
    aggregation = list(Band.objects.aggregate([ # {'$unwind': '$tags'},
        # {'$match': {'bandname': {'$exists': 'true'}}},
         {'$unwind': '$genres'},
       # {'$match': {'genres': 'ska'}},
        {'$group': {
            "_id": "$genres",
           # "number": {"$sum": 1}
            }
        }
    ]))
    genres = []
    for genre in aggregation:
        for k,v in genre.items():
            genres.append(v)
    return ','.join(genres)


def extract_tags(tags):
    whitespace = re.compile('\s')
    nowhite = whitespace.sub("", tags)
    tags_array = nowhite.split(',')

    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned


@bands.route('/bands/new', methods=('POST', 'GET'))
# @login_required
def new_band():
    form = CreateBandForm()
    form.origin_town.choices = [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    genres = list_genres()
    if form.validate_on_submit():
        # genres_array = extract_tags(form.genres.data)
        # user = "Joker"
        # band = Band(bandname=form.bandname.data, profile=form.profile.data, genres=genres_array, added_by=user) #bcrypt hashed_pw
        # band.save()
        # flash(f"Genres: {genres_array} created!", "success") #tuple (msg,cat)
        # return redirect(url_for("bands.list_all"))
        return f"<h1>{form.origin_county.data} - town: {form.origin_town.data}</h1>"
    return render_template("create_band.html", title=genres, form=form, genrelist=genres)



@bands.route('/band/add', methods=['GET', 'POST'])
def add_dand():
    form = CreateBandForm()

    if form.validate_on_submit():
        # Create race
        #return jsonify(form.laps.data)
        new_race = Band(bandname=form.bandname.data)
        new_race.save()

        for contact in form.contacts.data:
            #new_lap = Lap(runner=lap['runner'], lap_time=lap['lap_time'])
            new_lap = Contact(**contact)         
            # Add to race
            new_lap.save()
            new_race.update(push__contacts=new_lap)

        for contact in form.members.data:
            #new_lap = Lap(runner=lap['runner'], lap_time=lap['lap_time'])
            #new_lap = Contact(**contact)     
            new_lap = {
                "key": contact["namec"],
                "value": contact["number"]
             }      
            # Add to race
            #new_lap.save()
            new_race.update(push__members=new_lap)
        
        new_race.save()

        #db.session.commit()

    races = Band.objects()

    return render_template(
        'add_band.html',
        form=form,
        races=races
    )




@bands.route('/race', methods=['GET', 'POST'])
def index():
    form = MainForm()

    if form.validate_on_submit():
        # Create race
        #return jsonify(form.laps.data)
        new_race = Race(name=form.name.data)
        new_race.save()

        for lap in form.laps.data:
            #new_lap = Lap(runner=lap['runner'], lap_time=lap['lap_time'])
            new_lap = Lap(**lap)           
            # Add to race
            new_lap.save()
            new_race.update(push__laps=new_lap)
        
        new_race.save()

        #db.session.commit()

    races = Race.objects()

    return render_template(
        'race.html',
        form=form,
        races=races
    )



@bands.route('/race/<race_name>', methods=['GET'])
def show_race(race_name):
    """Show the details of a race."""
    race = Race.objects(name=race_name).first()

    return render_template(
        'results.html',
        race=race
    )

@bands.route('/contacts/<band_name>', methods=['GET'])
def show_contacts(band_name):
    """Show the details of a race."""
    race = Band.objects(bandname=band_name).first()

    return render_template(
        'contacts.html',
        race=race
    )