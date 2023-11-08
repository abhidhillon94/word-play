from flask_mongoengine import MongoEngine
import os

print('mongodb module')

db = None

def initialize_mongodb(app):

    print('initializing mongo')

    global db
    # initialize the extention only if it has not been initialized already
    if db == None:
        db = MongoEngine()

        app.config['MONGODB_SETTINGS'] = {
            # 'host': os.environ['MONGO_SRV']
            'host': "mongodb://test:P35YApbsuLZfBuT3@localhost:27017/word_play?authSource=admin"
        }

        db.init_app(app)

