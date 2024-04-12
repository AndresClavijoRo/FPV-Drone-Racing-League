from build_flask_app import create_flask_app
from models import db

app = None

flask_app = create_flask_app()

app = create_flask_app()
db.init_app(app)
db.create_all()