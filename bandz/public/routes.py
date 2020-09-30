import re, json, urllib
from flask import (jsonify, Blueprint, current_app,
    redirect, request, render_template,
    session, url_for)
from bson import json_util
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root, register_breadcrumb
from flask_wtf import FlaskForm
import phonenumbers
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from mongoengine.queryset import QuerySet
from flask_mongoengine.pagination import Pagination
from mongoengine.queryset.visitor import Q, QNode
from bandz.utils.gns import nav
from flask_nav.elements import Navbar, Subgroup, View
from bandz.models.entities import Band, Towns
from bandz.public.forms import SearchForm
from bandz.api.routes import list_genres, list_provinces

public = Blueprint('public', __name__)
default_breadcrumb_root(public, '.')

_AND = QNode.AND
_OR = QNode.OR

ALPHABET = 'abcdefghijklmnopqrstuvwxyz1'
SAMPLE_SIZE = 12
PAGE = 1
PER_PAGE = SAMPLE_SIZE

def band_dlc(*args,**kwargs):
    bname = request.view_args['bname'] if 'bname' in request.view_args else None
    letter = request.view_args['letter'] if 'letter' in request.view_args else None
    if bname and letter:
        return [{'text': 'A-Z', 'url': url_for('public.a2z') }, { 'text': letter.upper(), 'url': url_for('public.a2z', letter=letter) }, {'text': bname, 'url': url_for('public.band_detail', bname=bname, letter=letter)}]
    if bname:
        return [{'text': 'A-Z', 'url': url_for('public.a2z') }, {'text': bname, 'url': url_for('public.band_detail', bname=bname)}]

@public.route("/band/<string:bname>/", methods=('GET', 'POST'), defaults={'bname': 'band'})
@public.route("/band/<string:letter>/<string:bname>/", methods=('GET', 'POST'))
@register_breadcrumb(public, '.band_detail', '', dynamic_list_constructor=band_dlc)
def band_detail(bname, letter=None):
    referrer = request.referrer
    band = Band.objects(band_name=bname).first()
    if letter:
        return render_template("band_detail.html", band=band, letter=letter,  display_breadcrumbs=True,)
    else:
        return render_template("band_detail.html", band=band, display_breadcrumbs=True)


def view_alpha_dlc(*args, **kwargs):
    if request.path[1:4] == "a-z":
        alpha = ''
        alpha = request.view_args['letter']
        bname = None
        if 'band' in request.view_args:
            bname = request.view_args['band']
        referrer = request.referrer
        print(alpha)
        print(bname)
        if bname:
            return [{ 'text': 'A-Z', 'url': url_for('public.a2z')}, {'text': alpha.upper() }, {'text': bname.title()}]
        else:
            return [{ 'text': 'A-Z', 'url': url_for('public.a2z')}, {'text': alpha.upper() }]


    
def closest_letters(alphaset, letter):
    alphabet = 'abcdefghijklmnopqrstuvwxyz_'
    pos_letter = alphabet.find(letter.lower())
    rel_positions = [(index - pos_letter) for index, char in enumerate(alphabet) if char in alphaset]
    for n in rel_positions:
        if n < 0:
            neg = n
        else:
            pos = n
            return (alphabet[pos_letter+neg], alphabet[pos_letter+pos])
 


@public.route("/a-z/", defaults={'letter': 'a'})
@public.route("/a-z/<string:letter>") 
@register_breadcrumb(public, '.a2z', '', dynamic_list_constructor=view_alpha_dlc)
def a2z(letter='a', bname=None):
    page = request.args.get("page", 1, type=int)
    letter = '_' if letter == '1' else letter
    pipeline = [{ "$match" : {} },
                {
                    "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{letter.upper()}" } } }]
                    }
                }]
    result = list(Band.objects.aggregate(pipeline))[0]
    bands_by_letter = Pagination(result["bands_by_letter"], page, PER_PAGE)
    _alphabet = 'abcdefghijklmnopqrstuvwxyz_'
    alphabet = { obj["_id"].lower():int(obj["number_of_bands"]) for obj in result["numbers_by_letter"] }
    alphabet = { key:alphabet.setdefault(key, 0) for key in _alphabet }
    alphabet['1'] = alphabet.pop('_') #swap out for letter links 1 == '#' === '_'
    count = bands_by_letter.pages
    if bands_by_letter.total > 0:
        bands_total = bands_by_letter.total
        return render_template("bands_list.html", bands=bands_by_letter, count=count, bands_total=bands_total, display_breadcrumbs=True, alphabet=alphabet, letter=letter)
    else:
        return 'no bands' #closest letters_tup = closest_letters(alphaset, letter)



@public.route('/search', methods=('GET', 'POST'))
@register_breadcrumb(public, '.search', 'Search')
def search():
    form = SearchForm()
    genres = list_genres()
    province_counties = list_provinces()
    return render_template("search.html", form=form, genrelist=genres, province_counties=province_counties, display_breadcrumbs=True)


def view_genre_dlc(*args, **kwargs):
    genre = request.view_args['genre'] if 'genre' in request.view_args else None
    letter = request.view_args['letter'] if 'letter' in request.view_args else None
    if letter is not None:
        return [{ 'text': 'Genres', 'url': url_for('public.by_genre')}, {'text': genre.title(), 'url': url_for('public.get_by_genre', genre=genre)}, {'text': letter.title(), 'url': url_for('public.get_by_genre', genre=genre, letter=letter)}] # {'text': genre.upper() }]
    if genre is not None:
        return [{ 'text': 'Genres', 'url': url_for('public.by_genre')}, {'text': genre.title(), 'url': url_for('public.get_by_genre', genre=genre)}] # {'text': genre.upper() }]
    else:
        return [{ 'text': 'Genres', 'url': url_for('public.by_genre')}]


@public.route('/genres')
@public.route('/genres/')
@register_breadcrumb(public, '.by_genre', '', dynamic_list_constructor=view_genre_dlc)
def by_genre():
    pipeline = [{ "$unwind": "$genres"}, {"$group": {"_id": "$genres", "no_of_bands_per_genre": { "$sum": 1}}} ]
    genres = list(Band.objects.aggregate(pipeline))
    return render_template("genres.html", genres=genres, fullpage=True, display_breadcrumbs=True)


@public.route("/genres/<string:genre>", defaults={'letter': 'a', 'page': 1})
@public.route("/genres/<string:genre>/<string:letter>", defaults={'page': 1})
@public.route("/genres/<string:genre>/<string:letter>/<int:page>")
@register_breadcrumb(public, '.get_by_genre', ' ', dynamic_list_constructor=view_genre_dlc)
def get_by_genre(genre, letter, page):
    letter = '_' if letter == '1' else letter
    pipeline = [{"$match": { "genres": genre.lower() } },
                {
                    "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{letter.upper()}" } } }]
                    }
                }] 
    result = list(Band.objects.aggregate(pipeline))[0]
    # print(result["numbers_by_letter"])
    bands_by_letter = Pagination(result["bands_by_letter"], page, 12)
    _alphabet = 'abcdefghijklmnopqrstuvwxyz_'
    alphabet = { obj["_id"].lower():int(obj["number_of_bands"]) for obj in result["numbers_by_letter"] }
    alphabet = { key:alphabet.setdefault(key, 0) for key in _alphabet }
    alphabet['1'] = alphabet.pop('_') #swap out for letter links 1 == '#' === '_'
    count = bands_by_letter.pages
    if bands_by_letter.total > 0:
        bands_total = bands_by_letter.total
        return render_template("bands_list.html", bands=bands_by_letter, count=count, bands_total=bands_total, display_breadcrumbs=True, alphabet=alphabet, letter=letter)
    else:
        return 'no bands' #closest letters_tup = closest_letters(alphaset, letter)


@public.route('/?q')
@register_breadcrumb(public, '.', 'Sample')
def query():
    return render_template("search.html", title="tester")


# def home():
#     bands = list(Band.objects().aggregate({"$sample": {"size" : SAMPLE_SIZE}}))
#     bands = Pagination(bands, 1, SAMPLE_SIZE)
#     count = bands.pages
#     bands_total = bands.total
#     return render_template("bands_list.html", bands=bands, search=search, count=count, bands_total=bands_total, search_terms=search_terms,)  


@public.route('/')
@register_breadcrumb(public, '.', 'Bands')
def results():
    search_terms = ''
    filters = {}
    text_query = None
    search = None
    page = request.args.get("page", 1, type=int)
    if request.args:
        text_query = request.args.get("q")
        if text_query != None:
            if len(text_query) == 0:
                text_query = None
        genres = request.args.getlist("genres")
        andor = request.args.get("andor")
        letter = request.args.get("letter") if "letter" in request.args else "a"
        letter = '_' if letter == '1' else letter
        counties = request.args.getlist("counties")
        town = request.args.get("town")
        _request_arqs = request.args.to_dict(flat=False)
        _search = { key: _request_arqs[key] for key in _request_arqs if key not in ["page", "letter", "munster", "leinster", "connaght", "ulster"] } #re.sub('\=[0-9]*', '=', search)
        search = urllib.parse.urlencode(_search, doseq=True)
        if len(genres) > 0:
            if andor == 'f':
                search_terms = f"<b>{genres[0]}</b> bands" if (len(genres) <= 1) else "<b>" + ", ".join(genres[:-1]) + " or " + genres[-1] + " bands</b>"
            else:
                search_terms = f"<b>{genres[0]}</b> bands" if (len(genres) <= 1) else "<b>" + "-".join(genres) + " bands</b>"
        if len(counties) > 0:
            search_terms += f" in County {counties[0]}" if (len(counties) <= 1) else " in counties: " + ", ".join(counties[:-1]) + " and " + counties[-1]
        if len(genres) == 0 and len(counties) == 0:
            search_terms = "bands"
        if text_query:
            search_terms += f" containing <b>'{text_query}'</b>"
        if letter:
            search_terms += f" beginning with the letter <b>{letter.upper()}</b>"
        
  
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

        if town is None or len(town) == 0:
            pass
        else:
            filters['hometown__town__iexact'] = town

    queryset = Q(**filters) # use _AND or _OR Q Node Combinations
    # print(pipeline)
    if text_query != None:
        bands = Band.objects.filter(queryset)
        bands = bands.search_text(text_query).order_by("$text_score").paginate(per_page=12, page=page)
        count = bands.pages
    else:
        if not filters: # mobile test, smaller PER_PAGE?
            pipeline = [{"$sample": {"size" : SAMPLE_SIZE}},
                        {"$project": {"_id": 1, "band_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1 }}]
            bands = list(Band.objects().aggregate(pipeline))
            bands = Pagination(bands, 1, SAMPLE_SIZE)
            count = bands.pages
            if bands.total > 0:
                bands_total = bands.total
                alphabet = { key:0 for key in ALPHABET }
                return render_template("bands_list.html", bands=bands, search=search, count=count, bands_total=bands_total, search_terms=search_terms, display_breadcrumbs=False, alphabet=alphabet)
            else:
                return 'INITIAL Setup Required'

        if filters:
            pipeline = [{"$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{letter.upper()}" } } },
                                            {"$project": {"_id": 1, "band_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1 }},
                                            {"$sort": { "catalogue_name": 1 }}]
                        }}]
            result = list(Band.objects.filter(queryset).aggregate(pipeline))[0]
            bands = Pagination(result["bands_by_letter"], page, 12)
            _alphabet = 'abcdefghijklmnopqrstuvwxyz_'
            alphabet = { obj["_id"].lower():int(obj["number_of_bands"]) for obj in result["numbers_by_letter"] }
            alphabet = { key:alphabet.setdefault(key, 0) for key in _alphabet }
            alphabet['1'] = alphabet.pop('_') #swap out for letter links 1 == '#' === '_'
            count = bands.pages
            if bands.total > 0:
                bands_total = bands.total
                return render_template("bands_list.html", bands=bands, search=search, count=count, bands_total=bands_total, search_terms=search_terms, alphabet=alphabet, letter=letter)
            else:
                return 'for zero bands closest'


@public.route('/location')
@register_breadcrumb(public, '.by_location', 'Bands By County')
def by_location():
 
    pipeline = [{ "$unwind": "$towns" }, 
                { "$lookup": {
                    "from": "band",
                    "let": { "townt": "$towns", "townc": "$county" },
                    "pipeline": [
                        { "$project": { "_id": 0, "band_name": 1, "hometown": 1 } },
                        { "$replaceRoot": { "newRoot": 
                                            { "$mergeObjects": [ { "bandname": "$band_name", "town": "", "county": "" }, "$hometown" ] }
                                          }
                        },
                        { "$match": { "$expr": { "$and": [ { "$eq": [ "$town", "$$townt" ] }, { "$eq": [ "$county", "$$townc" ] } ] }} },
                        { "$project": { "_id": 1, "bandname": 1 }}
                    ],
                    "as": "bands"
                    }
                }, 
                { "$replaceRoot": { "newRoot": 
                                    { "$mergeObjects": 
                                        [ { "bandlisting": { "$size": "$bands.bandname" }, "town": "$towns", "county": "$county", "province": "$province" } ]
                                    }
                                }
                }, 
                { "$group": { "_id": { "province": "$province", "county": "$county" },
                                "towns": { "$push": { "town": "$town", "no_of_bands": "$bandlisting" }}}
                }, 
                { "$project": { "_id": 0, "province": "$_id.province", "counties": "$_id.county", "towns" : "$towns", "no_bands_per_county": { "$sum": "$towns.no_of_bands" } }}, 
                { "$group": { "_id": "$province", "counties": { "$push": {"county": "$counties", "no_of_bands_per_county": "$no_bands_per_county",  "towns": "$towns"} } }}
    ]
    provinces = Towns.objects.aggregate(pipeline)
    #return jsonify(list(provinces))
    return render_template("provinces.html", provinces=provinces, fullpage=True, display_breadcrumbs=True)




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


