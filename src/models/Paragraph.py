from src.bootstrap_resources.mongodb import db

print('paragraph.py module')

class Paragraph(db.Document):
    para_content = db.StringField(required=True)