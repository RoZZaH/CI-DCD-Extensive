import re
from flask import jsonify, Blueprint, request
from bandx.models.entities import Band, Towns


api = Blueprint('api', __name__)

@api.route("/genrez")
def list_genres():
    return list(Band.objects.aggregate([
        {"$unwind": "$genres"},
        {"$group": { "_id": "null", "genres": {"$addToSet": "$genres"} }},
        {"$sort": {"genres": 1 }}
    ]))[0]["genres"]


@api.route('/towns/<county>')
def get_towns(county):
    return list(Towns.objects.aggregate([
        {"$match": {"county" : county }},
        {"$unwind": { "path": "$towns" }},
        {"$group": { "_id": "$county", 
                            "towns": {"$push" : {
                                "name": "$towns",
                                "val": "$towns"
                            }}}} ]))[0]

@api.route('/provinces')
def list_provinces():
    return list(Towns.objects.aggregate([
        {"$group": {"_id": "$province",
        "counties": { "$push" : "$county"}
        } }]))


@api.route('/townz/')
def getz_townz():
    return jsonify(Towns.objects(county="Antrim"))


@api.route('/check_band_name')
def check():
    bandname = re.sub(' {2,}', ' ', request.args.get("q"))
    print(bandname)
    results = list(Band.objects(band_name__iexact=bandname))
    lastmatch = ""
    if len(bandname) < 1 or len(results) < 1 :
        return jsonify(False), 400
    elif len(lastmatch) > 0 and (results[0].lower() == lastmatch.lower().rstrip()):
        return jsonify(False), 400
    elif len(lastmatch) > 0 and (result[0].lower() != lastmatch.lower().rstrip()):
        lastmatch = ""
        return jsonify(False), 400
    else:
        lastmatch = results[0]["band_name"]
        print(lastmatch)
        return jsonify(True), 200
