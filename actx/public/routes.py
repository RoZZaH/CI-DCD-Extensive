from flask import jsonify, Blueprint, request, render_template

from actx.models.entities import Band, bands, tours, Towns

public = Blueprint('public', __name__) # import_name , usually the current module


@public.route("/")
def hello():
   # return "<h1>Hello</h1>"
   return jsonify(bands)

@public.route('/tours', methods=('POST', 'GET'))
def show_tours():
    if request.method == "POST":
        tour = request.get_json()
        tours.append(tour)
        return {'id': len(tours)}, 200
    return jsonify(tours)

@public.route('/tourdates')
def show_tourdates():
    #tourdates = tours
    bands = Band.objects.order_by('-date_created')

    return render_template("home.html", tourdates=bands)

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


