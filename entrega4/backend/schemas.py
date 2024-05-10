# Schemas for the models

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models import  User, Task


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        include_fk = True
        load_instance = True

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        include_fk = True
        load_instance = True

    created_by = fields.Nested(UserSchema)
    created_by_id = fields.Int()
    status = fields.Str()
    