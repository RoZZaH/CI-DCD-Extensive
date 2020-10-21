class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "73a2e9f7248e6fc95140bbea471c49d6"
    PICTURES_FOLDER = "media"
    

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    MONGODB_SETTINGS = {
        "db" : "bandx",
        "host": "mongodb://localhost/bandx"
    }


class ProductionConfig(Config):
    SECRET_KEY = "73a2e9/f7248e6f-95140&bbea47??.1c49d6"
    MONGODB_SETTINGS = {
        "db" : "bandz",
        "host" : "mongodb+srv://ci-test-user:Bandz2010@ci-cdc-bandz.nkdw4.mongodb.net/bandz?retryWrites=true&w=majority"
    }


class TestingConfig(Config):
    TESTING = True