import os
from flask import Flask, send_from_directory
from flask_assets import Environment, Bundle
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_breadcrumbs import Breadcrumbs  #from flask_breadcrumbs import current_breadcrumbs
from flask_nav.elements import Navbar, Subgroup, View
from bandz.utils.assets import bundles
from bandz.utils.mongoengine_jsonencoder import MongoEngineJSONEncoder # Overcome Objectionable ObjectIds
from bandz.utils.gns import nav, initialise_nav
from bandz.models.db import initialise_db


app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static',
            template_folder='web/templates')


app.json_encoder = MongoEngineJSONEncoder

# ENVs
app.config["SECRET_KEY"] = "73a2e9f7248e6fc95140bbea471c49d6"

app.config["MONGODB_SETTINGS"] = {
    "db" : "bandx",
    "host": "mongodb://localhost/bandx"
}
# app.config.from_pyfile('the-config.cfg')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# app.url_map.strict_slashes = False

# @app.before_request
# def clear_trailing():
#     from flask import redirect, request

#     rp = request.path 
#     if rp != '/' and rp.endswith('/'):
#         return redirect(rp[:-1])


# custom endpoints
# app.add_url_rule('/css/<path:filename>',
#                  endpoint='css',
#                  view_func=app.send_static_file)

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

pictures_folder = os.path.join(app.root_path, "media")

@app.route('/media/<path:filename>')
def static_media(filename):
    return send_from_directory(pictures_folder, filename)


# nav.register_element('top', topbar)

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
# nav.register_element('secondary', sns)