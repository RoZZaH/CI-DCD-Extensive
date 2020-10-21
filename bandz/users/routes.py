import csv, os, secrets, re, json
from datetime import datetime
from PIL import Image # Pillow
from flask_breadcrumbs import Breadcrumbs, default_breadcrumb_root, register_breadcrumb
from flask import (Blueprint, flash, current_app, jsonify,
    redirect, render_template, request, Response,
    url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import generate_password_hash, check_password_hash
# bandz modules
from bandz import app
from bandz.models.entities import User, Towns, Band, Phone, Contact, Email, Phone, BandMember, Assets
from bandz.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm)
from bandz.utils.helpers import *

user = Blueprint('user', __name__)
default_breadcrumb_root(user, '.')

@user.route('/setup_towns')
def setup_towns():
    resource_path = os.path.join(app.root_path, 'setup')
    with open(os.path.join(resource_path, 'towns.json')) as f:
        file_data = json.load(f)
    townz = []
    for town in file_data:
        townz.append(Towns(**town))
    Towns.objects.insert(townz)
    return True


@user.route('/setup', methods=("GET", "POST"))
def initial_setup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash(f"Account created for {form.username.data} -  Bands Added! You can now log in.", "success")
        uid = user.id
        if not Towns.objects():
            setup_towns()
        resource_path = os.path.join(app.root_path, 'setup')
        with open(os.path.join(resource_path, 'band.json')) as f:
            file_data = json.load(f)
        bandz = []
        for band in file_data:
            if 'date_created' in band.keys():
                date_created = datetime.strptime(band.pop('date_created'), "%Y-%m-%dT%H:%M:%S") 
            else:
                date_created = datetime.utcnow
            bandz.append(Band(**band, created_by = uid, date_created=date_created ))
        bands = Band.objects.insert(bandz)
        return redirect(url_for("user.login"))
    if len(list(Band.objects())) == 0:
        return render_template("setup.html", form=form, fullpage=True)
    else:
        flash(f"Initial Setup Complete", "success")
        return redirect(url_for("public.home"))


@user.route("/register", methods=("GET", "POST"))
@register_breadcrumb(user, '.register', 'Register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for("manage.mhome"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.save()
        flash(f"Account created for {form.username.data}! You are now able to log in.", "success")
        return redirect(url_for("user.login"))
    return render_template("register.html", title="Register", form=form, display_breadcrumbs=True)


@user.route("/login", methods=("GET","POST"))
@register_breadcrumb(user, '.login', 'Login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.account"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("manage.mhome"))
        else:
            flash(f"Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", form=form, display_breadcrumbs=True)


@user.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.home"))


@user.route("/account", methods=("GET","POST"))
@login_required
@register_breadcrumb(user, '.account', 'Account Settings')
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.save()
        flash(f"Your account has been updated.", "success")
        return redirect(url_for("user.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static_media', filename="user_profile_pics/" + current_user.image_file)
    return render_template("user_account.html", title="Account Settings", image_file=image_file, form=form, display_breadcrumbs=True, fullpage=True)
    
