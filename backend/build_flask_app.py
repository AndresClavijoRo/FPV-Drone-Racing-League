from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from celery import Celery, Task

import config as config
from models import User
from views import registro_usuario, test, login_usuario, tasks


def create_flask_app():
    """Create flask application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = config.SECRET_KEY
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config.from_mapping(
        CELERY=dict(
            broker_url=config.CELERY_BROKER_URL,
            result_backend=config.CELERY_RESULT_BACKEND,
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    app_context = app.app_context()
    app_context.push()
    add_urls(app)
    celery_init_app(app)
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()  
    return app


def add_urls(app):
    api = Api(app)
    api.add_resource(test.TestView, "/test")
    api.add_resource(registro_usuario.RegistroUsuarioView, "/signup")
    api.add_resource(login_usuario.LoginUsuarioView, "/login")
    api.add_resource(tasks.TasksListView, "/tasks")
    api.add_resource(tasks.TaskView, "/tasks/<int:task_id>")

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

