from threading import Thread

from flask import request
from flask_restful import Resource

from process_task import process_task
import config

class PorcessTaskView(Resource):

    def post(self):
        # Comprueba si el archivo de video está presente en la solicitud
        body = request.get_json()
        subscription = body.get("subscription")

        if config.SUB_NAME != subscription:
            return {"mensaje": "Invalid subscription"}, 400
        message = body.get("message",{})
        try:
            taks_id = int(message.get("data").decode("utf-8"))
            # Start a thread to process the task
            thread = Thread(target = process_task, args = (taks_id, ))
            thread.start()
            return {"mensaje": "Task processed"}, 200
        except Exception:
            return {"mensaje": "Invalid task id"}, 400