import os
import src.bootstrap_resources.load_env_vars

from celery import Celery
from src.bootstrap_resources.flask_app import app
from src.bootstrap_resources.mongodb import initialize_mongodb

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")

initialize_mongodb(app)