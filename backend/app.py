import os
from build_flask_app import create_flask_app
from models import db

flask_app = create_flask_app()
app = create_flask_app()

if os.getenv("FLASK_ENV") == "testing":
    app.testing = True

if app.debug or app.testing:
    db.create_all()
