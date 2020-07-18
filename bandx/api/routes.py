from flask import jsonify, Blueprint, request
from bandx.models.entities import Band, Towns

api = Blueprint('api', __name__)

@api.route("/genres")
def list_genres():
    return list(Band.objects.aggregate([
        {"$unwind": "$genres"},
        {"$group": { "_id": "null", "genres": {"$addToSet": "$genres"} }},
        {"$sort": {"genres": 1 }}
    ]))[0]["genres"]

@api.route('/towns/<county>')
def get_towns(county):
    # [(otown.town, otown.town) for otown in Towns.objects(county="Antrim")]
    # towns = Towns.objects(county=county)
    return list(Towns.objects.aggregate([
        {"$match": {"county" : county }},
        {"$group": {"_id": "$county", "towns": { "$push": {"name": "$town", "val" : "$town"} } } }
    ]))[0]

    # townsArray = []

    # for town in towns:
    #     townObj = {}
    #     townObj["val"] = town.town
    #     townObj["name"] = town.town
    #     townsArray.append(townObj)

    # return jsonify({"towns": townsArray})
    # return jsonify(towns)