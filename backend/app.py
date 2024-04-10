from build_flask_app import create_flask_app
from models import db

flask_app = create_flask_app()
app = create_flask_app()
if app.debug:
    db.create_all()
