from build_flask_app import create_flask_app
from models import db
flask_app = create_flask_app()
db.init_app(flask_app)
celery_app = flask_app.extensions["celery"]