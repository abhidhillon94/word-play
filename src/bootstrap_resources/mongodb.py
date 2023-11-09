from flask_mongoengine import MongoEngine
import os

db = None

def initialize_mongodb(app):

    global db
    # initialize the extention only if it has not been initialized already
    if db == None:
        db = MongoEngine()

        app.config['MONGODB_SETTINGS'] = {
            'host': os.environ['MONGO_SRV']
        }

        db.init_app(app)

