import os
from flask import Flask, send_from_directory
from flask_assets import Environment, Bundle
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from actx.utils.assets import bundles
from actx.models.db import initialise_db

app = Flask(__name__)

# ENVs
app.config["SECRET_KEY"] = "73a2e9f7248e6fc95140bbea471c49d6"

app.config["MONGODB_SETTINGS"] = {
    "db" : "actx",
    "host": "mongodb://localhost/actx"
}
# app.config.from_pyfile('the-config.cfg')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# custom endpoints
app.add_url_rule('/css/<path:filename>',
                 endpoint='css',
                 view_func=app.send_static_file)

app.add_url_rule('/js/<path:filename>',
                 endpoint='js',
                 view_func=app.send_static_file)

assets = Environment(app)
assets.register(bundles)

@app.route('/media/<path:filename>')
def static_media(filename):
    return send_from_directory(pictures_folder, filename)

pictures_folder = os.path.join(app.root_path, 'media')
profile_pics = os.path.join(pictures_folder, "user_profile_pics")

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
initialise_db(app)
login_manager.login_view = "user.login"
login_manager.login_message_category = "info" #boostrap category for flash message
# from actx.movies.routes import api
from actx.public.routes import public
from actx.users.routes import user
from actx.bands.routes import bands
# app.register_blueprint(api)
app.register_blueprint(public)
app.register_blueprint(bands)
app.register_blueprint(user)

