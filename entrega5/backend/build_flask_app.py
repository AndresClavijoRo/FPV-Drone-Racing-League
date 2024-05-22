from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

import config as config
from models import User
from views import registro_usuario, test, login_usuario, tasks, process_tasks


def create_flask_app():
    """Create flask application."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = config.SECRET_KEY
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=config.HOURS_TO_EXPIRE)
    app.config.from_prefixed_env()
    app_context = app.app_context()
    app_context.push()
    add_urls(app)
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()  
    return app


def add_urls(app):
    api = Api(app,"/api")
    if config.AS_WORKER == "True" :
        api.add_resource(test.TestView, "/test")
        api.add_resource(registro_usuario.RegistroUsuarioView, "/auth/signup")
        api.add_resource(login_usuario.LoginUsuarioView, "/auth/login")
        api.add_resource(tasks.TasksListView, "/tasks")
        api.add_resource(tasks.TaskView, "/tasks/<int:task_id>")
    else:
        api.add_resource(process_tasks.PorcessTaskView, "/protected/process_taks")


