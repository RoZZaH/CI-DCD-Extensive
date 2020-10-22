import os
from flask import Flask, send_from_directory
from flask_assets import Environment, Bundle
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_breadcrumbs import Breadcrumbs
from flask_nav.elements import Navbar, Subgroup, View
from bandz.utils.assets import bundles
from bandz.utils.mongoengine_jsonencoder import MongoEngineJSONEncoder
from bandz.utils.gns import nav, initialise_nav
from bandz.models.db import initialise_db

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')

app.json_encoder = MongoEngineJSONEncoder

# config via object - remove/comment out if not using config.py, see simple config below
os.sys.path.append('../')
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

# simple config add secret key + MONGODB_SETTINGS not MONGODB_URI for MongoEngine
# SECRET_KEY = <some secret string> #or wrap in env variable if not localhost
# MONGODB_SETTINGS = {
#     "db" : <dbname>, #e.g. "bandz"
#     "host" : <mongo srv uri> #or wrap in env variable
# }

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

PICTURES_FOLDER = app.config['PICTURES_FOLDER']

js_folder = os.path.join(app.static_folder, 'js')

@app.route('/js/<path:filename>')
def static_js(filename):
    return send_from_directory(js_folder, filename)

css_folder = os.path.join(app.static_folder, 'css')
@app.route('/css/<path:filename>')
def static_css(filename):
    return send_from_directory(css_folder, filename)

img_folder = os.path.join(app.static_folder, 'img')
@app.route('/img/<path:filename>')
def static_img(filename):
    return send_from_directory(img_folder, filename)

pictures_folder = os.path.join(app.root_path, PICTURES_FOLDER)
@app.route('/media/<path:filename>')
def static_media(filename):
    return send_from_directory(pictures_folder, filename)


assets = Environment(app)
assets.register(bundles)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
initialise_db(app)
initialise_nav(app)
login_manager.login_view = "user.login"
login_manager.login_message_category = "info" #boostrap category for flash message

from bandz.api.routes import api
from bandz.public.routes import public
from bandz.users.routes import user
from bandz.manage.routes import manage
Breadcrumbs(app=app)
app.register_blueprint(api)
app.register_blueprint(public)
app.register_blueprint(manage)
app.register_blueprint(user)