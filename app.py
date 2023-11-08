# load env variables before any imports as they are used in various places
import os
from dotenv import load_dotenv
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

from src.bootstrap_resources.flask_app import app

# initialise mongoDb before any  other imports that require DB
from src.bootstrap_resources.mongodb import initialize_mongodb
initialize_mongodb(app)

from src.controllers.paragraph_controller import paragraphsBlueprint

app.register_blueprint(paragraphsBlueprint)

app.run(host='0.0.0.0')
