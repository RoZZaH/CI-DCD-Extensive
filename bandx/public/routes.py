import re, json
from flask import (jsonify, Blueprint, \
    session, \
    redirect, request, render_template, \
        url_for)

#from flask_paginate import Pagination
from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb, Breadcrumbs
from flask_wtf import FlaskForm
import phonenumbers
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from mongoengine.queryset import QuerySet
from mongoengine.queryset.visitor import Q, QNode
from bandx.utils.gns import nav
from flask_nav.elements import Navbar, Subgroup, View
from bandx.models.entities import Band, Towns
from bandx.public.forms import SearchForm
from bandx.api.routes import list_genres, list_provinces
# import pymongo

public = Blueprint('public', __name__) # import_name , usually the current module
default_breadcrumb_root(public, '.')

_AND = QNode.AND
_OR = QNode.OR

@public.route("/json")
def hello():
   # return "<h1>Hello</h1>"
   bands = Band.objects.order_by('-date_created')
   return jsonify(bands)

@public.route('/tours', methods=('POST', 'GET'))
def show_tours():
    if request.method == "POST":
        tour = request.get_json()
        tours.append(tour)
        return {'id': len(tours)}, 200
    return jsonify(tours)




@public.route("/band/<string:bname>/", methods=('GET', 'POST'))
def band_detail(bname):
    band = Band.objects(band_name=bname).first()
    return render_template("band_detail.html", band=band)


# @public.route('/a2z', defaults={'initial': 'a'})
@public.route("/a2z")
@register_breadcrumb(public, '.', 'Bands')
def a2z():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
 
    page = request.args.get("page", 1, type=int)
    letter = request.args.get("letter", "a")
    bands = Band.objects(band_name__istartswith=letter).paginate(per_page=5, page=page, search=search)
    if bands.total > 0:
        return render_template("bands_list.html", bands=bands, alphabet=alphabet)
    else:
        return "no query sting received", 200


# @public.route('/')
# @register_breadcrumb(public, '.', 'Bands')
# def home():
#     page = request.args.get("page", 1, type=int)
#     bands = Band.objects.order_by('-date_created').paginate(per_page=5, page=page)
#     return render_template("bands_list.html", bands=bands)

@public.route("/bands/")
def redirector():
    return redirect(url_for("public.home"))


@public.route('/search') #/genre
def by_genre():
    form = SearchForm()
    genres = list_genres()
    province_counties = list_provinces()
    return render_template("search.html", form=form, genrelist=genres, province_counties=province_counties)


@public.route('/', methods=('GET', 'POST'))
@register_breadcrumb(public, '.', 'Bands')
def results():
    filters = {}
    text_query = None
    search = None
    page = request.args.get("page", 1, type=int)
    if request.args:
        text_query = request.args.get("q")
        if text_query != None:
            print(len(text_query))
        genres = request.args.getlist("genres")
        andor = request.args.get("andor")
        letter = request.args.get("letter")
        counties = request.args.getlist("counties")
        search = request.query_string.decode('UTF-8')
        search = re.sub('\=[0-9]*', '=', search)
       
        if len(genres) == 0:
            pass
        else:
            if len(genres) == 1:
                    genres = genres.pop()
                    filters['genres'] = genres
            else:
                if andor == "t":
                    filters['genres__all']=genres
                else:
                    filters['genres__in']=genres
        
        if len(counties) > 0:
            if len(counties) == 1:
                    county = counties.pop()
                    filters['hometown__county__iexact'] = county
            else:
                filters['hometown__county__in'] = counties

        if letter:
            filters['band_name__istartswith'] = letter


    pipeline = Q(**filters) #Combination Mode Const
    #print(pipeline)
    if text_query != None:
        bands = Band.objects.filter(pipeline)
        bands = bands.search_text(text_query).order_by("$text_score").paginate(per_page=3, page=page)
        count = bands.pages
    else: 
        bands = Band.objects(pipeline).paginate(per_page=5, page=page) #??
        count = bands.pages
    if bands.total > 0:
        return render_template("bands_list.html", bands=bands, search=search, count=count)
    else:
        return "no query sing received", 200


@public.route('/location')
def by_location():
 
    pipeline = [
        { "$unwind": { "path": "$towns" } }, 
        { "$lookup": { "from": "band",
                        "let": { "townt": "$towns", "townc": "$county" },
                "pipeline": [
                    { "$project": { "_id": 0, "band_name": 1, "hometown": 1 } },
                    { "$replaceRoot": { "newRoot": 
                                        { "$mergeObjects": [
                                            {
                                                "bandname": "$band_name",
                                                "town": "",
                                                "county": ""
                                            },
                                            "$hometown"
                                            ]
                                        }
                                    }},
                    { "$match": { "$expr": { "$and": [ { "$eq": [ "$town", "$$townt" ] }, { "$eq": [ "$county", "$$townc" ] } ]}}},
                    { "$project": { "_id": 1, "bandname": 1 } } 
                    ], "as": "bands" }}, 
        { "$replaceRoot": { "newRoot": { "$mergeObjects": [ { "bandlisting": { "$size": "$bands.bandname" }, "town": "$towns", "county": "$county" } ] }}}, 
        { "$group": { "_id": {
                            "county": "$county",
                            "town": "$town",
                            "number_of_bands_per_town": "$bandlisting"
                            },
                            "number_of_towns_per_county": { "$sum": 1 }
                    }
        }, 
        { "$group": { "_id": "$_id.county", "towns": { "$push": { "name": "$_id.town", "num": "$_id.number_of_bands_per_town" }},
                            "bands_total": { "$sum": "$_id.number_of_bands_per_town"},
                            "ctotal": {"$sum": "$number_of_towns_per_county"}
                    }
        }, 
        { "$sort": { "_id": 1 }}
    ]

    counties = Towns.objects.aggregate(pipeline)
    return render_template("counties_list.html", counties=counties)




@public.route('/tours/<int:index>', methods=['PUT'])
def update_tour(index):
    tour = request.get_json()
    tours[index] = tour
    return jsonify(tours[index]), 200

@public.route('/tours/<int:index>', methods=['DELETE'])
def delete_tour(index):
    tours.pop(index)
    return 'None', 200

@public.route('/grid')
def show_grid():
    return render_template("grid.html")


class PhoneForm(FlaskForm):
    mobile = RadioField("Mobile Y/N", 
                        choices=[("True","mobile"),("False","landline")],
                        render_kw={},
                        default="True")
    region = RadioField('', choices= [
                                    ('IE', 'Ireland'),
                                    ('GB', 'N.I./UK'),
                                    ('None','Other')

                        ], default='IE')
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # def validate(self):
    #     if not Form.validate(self):
    #         return False
    #     result = True
    #     for field in [self.region, self.phone]:
    #         if :
    #             field.errors.append("Please do soemthing")
    #             result = False
    #         else:
    #             .add(field.data)
    #     return result

    def validate_phone(self, phone):
        try:
            # if self.region.data == "None":
                # p = phonenumbers.parse(phone.data)
            # else:
            p = phonenumbers.parse(phone.data, self.region.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


@public.route('/phone', methods=('POST', 'GET'))
def form_phone():
    form = PhoneForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        # return request.form
        p = phonenumbers.parse(form.phone.data, form.region.data)
        session['phone'] = phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
        return redirect(url_for('public.show_phone'))
    return render_template("public_phonenumber.html", form=form)

@public.route('/showphone')
def show_phone():
    return render_template('public_show_phone.html', phone=session['phone'])

