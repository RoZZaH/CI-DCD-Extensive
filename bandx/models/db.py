from flask_mongoengine import MongoEngine

db = MongoEngine()

def initialise_db(app):
    db.init_app(app)