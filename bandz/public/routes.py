import re, json, urllib
from flask import (jsonify, Blueprint, current_app,
    redirect, request, render_template,
    session, url_for)
from bson import json_util
from bson.son import SON
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root, register_breadcrumb
from flask_nav.elements import Navbar, Subgroup, View
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from mongoengine.queryset import QuerySet
from mongoengine.queryset.visitor import Q, QNode
from flask_mongoengine.pagination import Pagination
# bandz modules
from bandz.utils.gns import nav
from bandz.models.entities import Band, Towns
from bandz.public.forms import SearchForm
from bandz.api.routes import list_genres, list_provinces
from bandz.utils.helpers import *
# const for PUBLIC module/routes
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
    letter = request.args.get('letter') if 'letter' in request.args else de_article(bname)[0]
    if request.referrer and request.referrer != request.url_root:
        referrer = request.referrer.replace(request.url_root,'') if request.referrer != request.url_root else ''
        referrer = referrer.split("/",2) if len(referrer) > 0 else ['home']
        #print(referrer)
        if referrer[0] == 'genres':
            return [{'text': 'Genre', 'url': url_for('public.by_genre')}, {'text': referrer[1].title(), 'url': url_for('public.get_by_genre', genre=referrer[1].lower(), letter=letter.lower()) }, {'text': bname, 'url': url_for('public.band_detail', bname=bname, letter=letter.lower())}]
        if referrer[0] == 'search':
            return [{'text': 'search results' }]
        if (referrer[0] == 'home' or referrer[0] == 'a-z'):  
            if bname and letter:
                return [{'text': 'A-Z', 'url': url_for('public.a2z') }, { 'text': letter.upper(), 'url': url_for('public.a2z', letter=letter.lower()) }, {'text': bname, 'url': url_for('public.band_detail', bname=bname, letter=letter.lower())}]
            if bname:
                return [{'text': 'A-Z', 'url': url_for('public.a2z') }, {'text': bname, 'url': url_for('public.band_detail', bname=bname)}]


@public.route("/band/", methods=('GET', 'POST'))
@public.route("/band/<string:bname>/", methods=('GET', 'POST') )
@register_breadcrumb(public, '.band_detail', '', dynamic_list_constructor=band_dlc)
def band_detail(bname=None, letter='a'):
    letter = request.args.get("letter")
    band = Band.objects(band_name=bname).first()
    if letter:
        return render_template("band_detail.html", band=band, letter=letter,  display_breadcrumbs=True)
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
        if bname:
            return [{ 'text': 'A-Z', 'url': url_for('public.a2z')}, {'text': alpha.upper() }, {'text': bname.title()}]
        else:
            return [{ 'text': 'A-Z', 'url': url_for('public.a2z')}, {'text': alpha.upper() }]


def closest_letters(alphaset, letter):
    pos_letter = ALPHABET.find(letter.lower())
    rel_positions = [(index - pos_letter) for index, char in enumerate(ALPHABET) if char in alphaset]
    for n in rel_positions:
        if n < 0:
            neg = n
        else:
            try:
                neg 
            except NameError:
                neg = 0
            pos = n
            return (ALPHABET[pos_letter+neg], ALPHABET[pos_letter+pos])


@public.route("/a-z/", defaults={'letter': 'a'})
@public.route("/a-z/<string:letter>") 
@register_breadcrumb(public, '.a2z', '', dynamic_list_constructor=view_alpha_dlc)
def a2z(letter, bname=None):
    page = request.args.get("page", 1, type=int)
    letter = '_' if letter == '1' else letter
    pipeline = [{ "$match" : {} },
                {
                    "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [ { "$match": { "catalogue_name": { "$regex": f"^{letter.upper()}" } } },
                                             { "$project": {"_id": 1, "band_name": 1, "catalogue_name" :1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]}}}},
                                             { "$sort" : { "catalogue_name": 1}}]
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
        alphaset = [ ltr for ltr in alphabet.keys() if alphabet[ltr] > 0]
        return render_template("bands_list.html", closest_letters = closest_letters(alphaset, letter), display_breadcrumbs=True, alphabet=alphabet, letter=letter) #closest 



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


@public.route("/genres/<path:genre>", defaults={'letter': 'a', 'page': '1'})
@public.route("/genres/<path:genre>/<path:letter>", defaults={'page': '1'})
@public.route("/genres/<path:genre>/<path:letter>/<path:page>")
@register_breadcrumb(public, '.get_by_genre', '', dynamic_list_constructor=view_genre_dlc)
def get_by_genre(genre, letter, page):
    letter = '_' if letter == '1' else letter.lower()
    pipeline = [{"$match": { "genres": genre.lower() } },
                {
                    "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{str(letter.upper())}" } } },
                                            { "$project": {"_id": 1, "catalogue_name":1, "band_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]}}}},
                                            { "$sort" : { "catalogue_name": 1}}
                                            ]
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
        return render_template("bands_list.html", bands=bands_by_letter, count=count, bands_total=bands_total, display_breadcrumbs=True, alphabet=alphabet, letter=letter)
    else:
        return 'no bands' #closest letters_tup = closest_letters(alphaset, letter)


@public.route('/')
@register_breadcrumb(public, '.', 'Bands')
def home():
    pipeline = [{"$sample": {"size" : SAMPLE_SIZE}},
                {"$project": {"_id": 1, "band_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]} }}}]
    bands = list(Band.objects().aggregate(pipeline))
    bands = Pagination(bands, 1, SAMPLE_SIZE)
    count = bands.pages
    if bands.total > 0:
        bands_total = bands.total
        alphabet = { key:0 for key in ALPHABET }
        return render_template("bands_list_home.html", bands=bands, count=count, bands_total=bands_total, display_breadcrumbs=False, alphabet=alphabet)
    else:
        return redirect(url_for('user.initial_setup'))


@public.route('/search', methods=('GET', 'POST'))
@register_breadcrumb(public, '.search', 'Search')
def search():
    form = SearchForm()
    genres = list_genres()
    province_counties = list_provinces()
    return render_template("search.html", form=form, genrelist=genres, province_counties=province_counties, display_breadcrumbs=True)


@public.route('/search/results/')
@register_breadcrumb(public, '.results', 'Results')
def results():
    search_terms = ''
    filters = {}
    text_query = None
    search = None
    town = None
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
        #print(counties)
        town = request.args.get("town")
        _request_arqs = request.args.to_dict(flat=False)
        _search = { key: _request_arqs[key] for key in _request_arqs if key not in ["page", "letter", "munster", "leinster", "connaght", "ulster"] } #re.sub('\=[0-9]*', '=', search)
        search = urllib.parse.urlencode(_search, doseq=True)
        
        # towns
        if town:
            search_terms += f"in {town}, County {counties[0]}"
            bands = Band.objects(hometown__town__iexact=town).paginate(per_page=PER_PAGE, page=page)
            search_terms = search_terms.replace('bands', 'band') if bands.total == 1 else search_terms
            return render_template("bands_list_results.html", bands=bands, search=search, count=bands.pages, bands_total=bands.total, search_terms=search_terms)
        
        # build search_terms text string
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
        if text_query==None:
            search_terms += f" beginning with the letter <b>{letter.upper()}</b>"
        # build QSet filters ala mongoengine
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

    queryset = Q(**filters) # use _AND or _OR Q Node Combinations
    # print(pipeline)
    if text_query != None:
        bands = Band.objects.filter(queryset) #text has to be first pipeline
        pipeline = [{ "$match": { "$text": { "$search": text_query } }}, 
                    { "$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter":   [ { "$project": {"_id": 1, "band_name": 1, "strapline": 1, "hometown": 1,
                                                              "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]}}}} ]
                    }}]
        result = list(bands.aggregate(pipeline))[0]
        bands = Pagination(result["bands_by_letter"], page, 12)
        _alphabet = 'abcdefghijklmnopqrstuvwxyz_'
        alphabet = { obj["_id"].lower():int(obj["number_of_bands"]) for obj in result["numbers_by_letter"] }
        alphabet = { key:alphabet.setdefault(key, 0) for key in _alphabet }
        alphabet['1'] = alphabet.pop('_') #swap out for letter links 1 == '#' === '_'
        count = bands.pages
        if bands.total > 0:
            bands_total = bands.total
            search_terms = search_terms.replace('bands', 'band') if bands_total == 1 else search_terms
            return render_template("bands_list_results.html", bands=bands, search=search, count=count, bands_total=bands_total, search_terms=search_terms, letter=letter)
    
    else:
        if not filters: # mobile test, smaller PER_PAGE?
            return redirect(url_for("public.home"))

        if filters:
            pipeline = [{"$facet": {
                        "numbers_by_letter": [ {"$group": { "_id": { "$substr": [ "$catalogue_name", 0, 1]}, 
                                                            "number_of_bands": { "$sum": 1 }}} ],
                        "bands_by_letter": [{ "$match": { "catalogue_name": { "$regex": f"^{letter.upper()}" } } },
                                            {"$project": {"_id": 1, "band_name": 1, "strapline": 1, "hometown": 1, "profile": 1, "description": 1, "genres": 1, "media_assets": 1, "letter": {"$toLower": { "$substr": [ "$catalogue_name", 0, 1]} }}},
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
                total_bands_in_query = sum(alphabet.values())
                search_terms += f'; there are {total_bands_in_query} resullts in total - use the alphabet to navigate between them.'
                return render_template("bands_list_results.html", bands=bands, search=search, count=count, bands_total=bands_total, search_terms=search_terms, alphabet=alphabet, letter=letter)
            else:
                alphaset = [ ltr for ltr in alphabet.keys() if alphabet[ltr] > 0]
                return render_template("bands_list_results.html", closest_letters=closest_letters(alphaset, letter), search=search, display_breadcrumbs=True, alphabet=alphabet, letter=letter)
    


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
    return render_template("provinces.html", provinces=provinces, fullpage=True, display_breadcrumbs=True)




