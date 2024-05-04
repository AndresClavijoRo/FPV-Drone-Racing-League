from flask_restful import Resource


class TestView(Resource):
    def get(self):
        return {"message": "funcionó"}, 200
