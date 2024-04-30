from models import db, User
from flask import request
from schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from sqlalchemy import exc
import re

user_schema = UserSchema()


class RegistroUsuarioView(Resource):

    def post(self):

        password = request.json["password1"]
        passwordConfirm = request.json["password2"]

        # Validate password strength
        if password != passwordConfirm:
            return {"mensaje": "Las contraseñas no coinciden"}, 400
        if len(password) < 8:
            return {"mensaje": "La contraseña debe tener al menos 8 caracteres"}, 400
        if not any(char.isdigit() for char in password):
            return {"mensaje": "La contraseña debe contener al menos un número"}, 400
        if not any(char.isupper() for char in password):
            return {"mensaje": "La contraseña debe contener al menos una letra mayúscula"}, 400
        if not any(char.islower() for char in password):
            return {"mensaje": "La contraseña debe contener al menos una letra minúscula"}, 400

        email = request.json["email"]
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"mensaje": "El correo electrónico no es válido"}, 400

        # Check if username or email already exists
        existing_user = User.query.filter_by(
            username=request.json["username"]).first()
        if existing_user:
            return {"mensaje": "Ya existe un usuario con este nombre de usuario"}, 400

        existing_email = User.query.filter_by(
            email=request.json["email"]).first()
        if existing_email:
            return {"mensaje": "Ya existe un usuario con este correo electrónico"}, 400

        nuevo_usuario = User(
            username=request.json["username"],
            email=request.json["email"],
            hashed_password=generate_password_hash(request.json["password1"])
        )

        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un usuario con este identificador"}, 400
        except exc.SQLAlchemyError:
            db.session.rollback()
            return {"mensaje": "Error en la base de datos"}, 500
        except Exception as e:
            db.session.rollback()
            return {"mensaje": str(e)}, 500

        token_de_acceso = create_access_token(identity=nuevo_usuario.id)
        return {
            "mensaje": "Usuario creado",
            "token": token_de_acceso,
            "correo": nuevo_usuario.email,
        }, 201
