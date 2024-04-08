from flask_restful import Resource

from models import Task
from schemas import TaskSchema

task_schema = TaskSchema()


class TestView(Resource):
    def get(self):
        tasks = Task.query.all()
        return task_schema.dump(tasks, many=True)