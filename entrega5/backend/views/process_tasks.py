from threading import Thread
import base64

from flask import request
from flask_restful import Resource

import config
from models import db

def process_taks_in_background(task_id):
    from build_flask_app import create_flask_app
    app = create_flask_app()
    db.init_app(app)
    with app.app_context():
        from process_task import process_task
        process_task(task_id)

class PorcessTaskView(Resource):

    def post(self):
        # Comprueba si el archivo de video está presente en la solicitud
        body = request.get_json()
        print(body)
        subscription = body.get("subscription")

        if config.SUB_NAME != subscription:
            return {"mensaje": "Invalid subscription"}, 400
        message = body.get("message",{})
        try:
            task_id_encoded = message.get("data")
            task_id_bytes = base64.b64decode(task_id_encoded)
            taks_id = int(task_id_bytes.decode("utf-8"))
            # Start a thread to process the task
            thread = Thread(target = process_taks_in_background, args = (taks_id, ))
            thread.start()
            return {"mensaje": "Task processed"}, 200
        except Exception:
            return {"mensaje": "Invalid task id"}, 400