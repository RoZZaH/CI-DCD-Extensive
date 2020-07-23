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
from mongoengine.queryset.visitor import Q
from bandx.utils.gns import nav
from flask_nav.elements import Navbar, Subgroup, View
from bandx.models.entities import Band, Towns
from bandx.public.forms import SearchForm
from bandx.api.routes import list_genres, list_provinces
# import pymongo

public = Blueprint('public', __name__) # import_name , usually the current module
default_breadcrumb_root(public, '.')



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

@public.route('/')
@register_breadcrumb(public, '.', 'Bands')
def home():
    page = request.args.get("page", 1, type=int)
    bands = Band.objects.order_by('-date_created').paginate(per_page=5, page=page)
    #pagination = Pagination(page=page, total=bands.count(), record_name="bands", per_page=5 )
    return render_template("bands_list.html", bands=bands)

@public.route("/bands/")
def redirector():
    return redirect(url_for("public.home"))


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


@public.route('/genre')
def by_genre():
    form = SearchForm()
    genres = list_genres()
    province_counties = list_provinces()
    return render_template("genre_list.html", form=form, genrelist=genres, province_counties=province_counties)


@public.route('/search', methods=('GET', 'POST'))
def search():
    text_query = request.args.get("q")

    print(len(text_query))
    page = request.args.get("page", 1, type=int)
    genres = request.args.getlist("genres")
    andor = request.args.get("andor")
    letter = request.args.get("letter")
    counties = request.args.getlist("counties")
    search = request.query_string.decode('UTF-8')
    search = re.sub('\=[0-9]*', '=', search)
    
    Qs = [] #Q prefix complex mongoengine queries
    filters = {}
    
    if len(genres) == 0:
        filters['genres__exists'] = 1
        #Qs.append("Q(genres__exists=1)")
    else:
        if len(genres) == 1:
                genres = genres.pop()
                # bands = Band.objects(Q(genres=genres)).paginate(per_page=1, page=page)
                filters['genres'] = genres
                Qs.append(f"Q(genres='{genres}')")
        else:
            if andor == "true":
                Qs.append(f"Q(genres__all={genres})")
            else:
                Qs.append(f"Q(genres__in={genres})")
    
    if len(counties) > 0:
        if len(counties) == 1:
                county = counties.pop()
                Qs.append(f"Q(hometown__county__iexact='{county}')")
        else:
           Qs.append(f"Q(hometown__county__in={counties})")

    if letter:
        Qs.append(Q(band_name__istartswith=letter))

    # pipeline = Qs[0] if len(Qs) == 1 else (' & ').join(Qs)   
    pipeline = Q(**filters)
    print(pipeline)
    if len(text_query) > 0:
        bands = Band.objects.filter((pipeline))
        bands = bands.search_text(text_query).order_by("$text_score").paginate(per_page=3, page=page)
        count = bands.pages
    else: 
        bands = Band.objects((pipeline)).paginate(per_page=3, page=page) #??
        count = bands.pages
    if bands.total > 0:
        return render_template("bands_list.html", bands=bands, search=search, count=count)
    else:
        return "no query sing received", 200


@public.route('/location')
def by_location():

    #db.towns.aggregate([{"$group": {"_id": "$county", townz: {$push: {town: "$town"}}  }}])
    #aggregation = list(Towns.objects.aggregate([{"$group": { "_id": "$county", 
     #               "townz": {"$push": {"town": "$town"}}, "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}])) #towns per county
    
    aggregation = list(Towns.objects.aggregate([
                    {"$group": {"_id": { "county": "$county", "town": "$town" }}},
                    {"$group": {"_id" : "$_id.county", "towns": {"$push" :  "$_id.town"}}},
                    {"$sort": {"_id": 1}}]))

    aggregation2 = list(Band.objects.aggregate([
                    {"$group": {"_id": { "county": "$hometown.county", "town": "$hometown.town" }, "num_bands_in_town": {"$sum": 1} }},
                    {"$group": {"_id" : "$_id.county", "towns": {"$push" : {"name":"$_id.town", "num": "$num_bands_in_town"}}, "ctotal": {"$sum": "$num_bands_in_town"} }},
                    {"$sort": {"_id": 1}}]))

        
    pipeline = [
        # {
        #     u"$match": {
        #         u"county": u"Wexford"
        #     }
        # }, 
        {
            u"$lookup": {
                u"from": u"band",
                u"let": {
                    u"townt": u"$town",
                    u"townc": u"$county"
                },
                u"pipeline": [
                    {
                        u"$project": {
                            u"_id": 0.0,
                            u"band_name": 1.0,
                            u"hometown": 1.0
                        }
                    },
                    {
                        u"$replaceRoot": {
                            u"newRoot": {
                                u"$mergeObjects": [
                                    {
                                        u"bandname": u"$band_name",
                                        u"town": u"",
                                        u"county": u""
                                    },
                                    u"$hometown"
                                ]
                            }
                        }
                    },
                    {
                        u"$match": {
                            u"$expr": {
                                u"$and": [
                                    {
                                        u"$eq": [
                                            u"$town",
                                            u"$$townt"
                                        ]
                                    },
                                    {
                                        u"$eq": [
                                            u"$county",
                                            u"$$townc"
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                    {
                        u"$project": {
                            u"_id": 0.0,
                            u"bandname": 1.0
                        }
                    }
                ],
                u"as": u"bands"
            }
        }, 
        {
            u"$replaceRoot": {
                u"newRoot": {
                    u"$mergeObjects": [
                        {
                            u"bandlisting": {
                                u"$size": u"$bands.bandname"
                            },
                            u"town": u"$town",
                            u"county": u"$county"
                        }
                    ]
                }
            }
        }, 
        {
            u"$group": {
                u"_id": {
                    u"county": u"$county",
                    u"town": u"$town",
                    u"number_of_bands_per_town": u"$bandlisting"
                },
                u"number_of_towns_per_county": {
                    u"$sum": 1
                }
            }
        }, 
        {
            u"$group": {
                u"_id": u"$_id.county",
                u"towns": {
                    u"$push": {
                        u"name": u"$_id.town",
                        u"num": u"$_id.number_of_bands_per_town"
                    }
                },
                u"bands_total": {
                    u"$sum": u"$_id.number_of_bands_per_town"
                },
                u"ctotal": {
                    u"$sum": u"$number_of_towns_per_county"
                }
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]


    counties = Towns.objects.aggregate(pipeline)

    #return jsonify(counties)
    return render_template("counties_list.html", counties=counties)  #",".join(genres)

    # unclean counties
        # ["Antrim", "Armagh", 
        # "Carlow", "Cavan", "Clare" ,"Cork",
        # "Derry" , "Donega", "Donegal", "Down", "Dublin",
        # "Fermanagh", "Galway", 
        # "Kerry", "Kildare", "Kilkenny", 
        # "Laois", "Leitrim", "Limerick","Longford", "Louth",
        # "Mayo", "Meath", "Monaghan", "Offaly", 
        # "Roscommmon", "Roscommon", "Sligo", 
        # "Tipperary", "Tipperay",  "Tryone", "Tyrone", 
        # "Waterford", "Westmeath", "Wexford", "Wicklow"]




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





# @nav.navigation('mysite_navigation')
# def create_navbar():
#     home_view = (View('Home', 'public.home'))
#     register_view = (View('Register', 'user.register'))
#     manage_view = (View('Manage Bands', 'bands.manage_bands'))
#     return Navbar('MySite', home_view, register_view, manage_view)




'''
db.towns.aggregate([
{
    $lookup: {
         from: "band",
         let: { "fft" : "$hometown.town", "ffc": "$hometown.county", "bname" : "$band_name" },
         pipeline: [
             {$match:
                 { $expr: 
                     {$and: 
                        [ {$eq: ["$$fft", "$town" ]},
                          {$eq: ["$$ffc", "$county"]} ]
                      }
                   }
              },
               {$group: {"_id" : "$county",
               "townz": {$push: {"town": "$town"}}   }},
               {$sort: {"_id": 1}}],
         as : "common_bands"
    }
}])
'''