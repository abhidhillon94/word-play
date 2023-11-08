from src.bootstrap_resources.mongodb import db

class WordsCount(db.Document):
    word = db.StringField(required=True)
    global_occurance_count = db.LongField(required=True)
    definition = db.StringField(required=False)