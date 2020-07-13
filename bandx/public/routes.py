from flask import (jsonify, Blueprint, \
    session, \
    redirect, request, render_template, \
        url_for)

from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb, Breadcrumbs
from flask_wtf import FlaskForm
import phonenumbers
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from mongoengine.queryset import QuerySet
from bandx.utils.gns import nav
from flask_nav.elements import Navbar, Subgroup, View
from bandx.models.entities import Band, Towns

public = Blueprint('public', __name__) # import_name , usually the current module
default_breadcrumb_root(public, '.')


# @nav.navigation('mysite_navigation')
# def create_navbar():
#     home_view = (View('Home', 'public.home'))
#     register_view = (View('Register', 'user.register'))
#     manage_view = (View('Manage Bands', 'bands.manage_bands'))
#     return Navbar('MySite', home_view, register_view, manage_view)




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
    return render_template("bands_list.html", bands=bands)


@public.route("/<string:bname>/", methods=('GET', 'POST'))
def band_detail(bname):
    band = Band.objects(band_name=bname).first()
    return render_template("band_detail.html", band=band)



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
