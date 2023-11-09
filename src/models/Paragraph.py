from src.bootstrap_resources.mongodb import db

class Paragraph(db.Document):
    para_content = db.StringField(required=True)