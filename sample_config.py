class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "<some-secret-string>"
    PICTURES_FOLDER = "media"
    

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    MONGODB_SETTINGS = {
        "db" : "bandz", 
        "host": "mongodb://localhost/bandz" #simple connection to local mongodb community edition
    }


class ProductionConfig(Config):
    SECRET_KEY = "<some-stronger-secret-key>"
    MONGODB_SETTINGS = {
        "db" : "bandz",
        "host" : "mongodb+srv://<USER>:<PASSWORD>@ci-cdc-bandz.nkdw4.mongodb.net/<DBNAME>?retryWrites=true&w=majority"
    }


class TestingConfig(Config):
    TESTING = True