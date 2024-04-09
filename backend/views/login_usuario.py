from models import db, User
from flask import request
from schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required

user_schema = UserSchema()


class LoginUsuarioView(Resource):

    def post(self):

        username = request.json["username"]
        password = request.json["password"]
        
        if not username or not password:
            return {"mensaje": "Credenciales inválidas"}, 400

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.hashed_password, password):
            return {"mensaje": "Credenciales inválidas"}, 400

        token_de_acceso = create_access_token(identity=user.id)
        return {"token": token_de_acceso}, 200
