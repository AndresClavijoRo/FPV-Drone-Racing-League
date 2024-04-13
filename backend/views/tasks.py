from models import db, Task, TaskStatus
from flask import request
from schemas import TaskSchema
from flask_restful import Resource
from flask_jwt_extended import current_user, jwt_required
from werkzeug.utils import secure_filename
import os
from views.validaciones_video import validaciones_video
from celery_tasks import process_task
import config

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

def get_task_detail(task: Task) -> dict:
    url = config.ROOT_SERVER_URL
    return {
        "id": task.id,
        "file_name": task.file_name,
        "status": task.status.value,
        "uploaded_video_path": url + task.video_path,
        "processed_video_path": (
            url + task.processed_video_path if task.processed_video_path else None
        ),
        "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": (
            task.updated_at.strftime("%Y-%m-%d %H:%M:%S") if task.updated_at else None
        ),
        "processing_started_at": (
            task.processing_started_at.strftime("%Y-%m-%d %H:%M:%S")
            if task.processing_started_at
            else None
        ),
        "processing_ended_at": (
            task.processing_ended_at.strftime("%Y-%m-%d %H:%M:%S")
            if task.processing_ended_at
            else None
        )
    }


class TasksListView(Resource):

    @jwt_required()
    def get(self):

        max_registros = request.args.get("max", default=100, type=int)
        order = request.args.get("order", default=0, type=int)

        tasks = (
            Task.query.filter_by(created_by_id=current_user.id)
            .order_by(Task.id.asc() if order == 0 else Task.id.desc())
            .limit(max_registros)
            .all()
        )
        return {"tasks": [get_task_detail(task) for task in tasks]}

    @jwt_required()
    def post(self):
        # Comprueba si el archivo de video está presente en la solicitud
        if "fileName" not in request.files:
            return {"mensaje": "No se encontró el archivo de video"}, 400
        video = request.files["fileName"]

        validaciones = validaciones_video(video)

        if validaciones.valid is False:
            return {"mensaje": validaciones.mensaje}, 400

        # Guarda el archivo de video
        filename = secure_filename(video.filename)
        video_path = f'{os.getenv("UPLOAD_FOLDER")}/{filename}'
        video.save(video_path)

        try:
            # Crea una nueva tarea
            task = Task(
                created_by_id=current_user.id,
                file_name=filename,
                video_path=video_path,
                status=TaskStatus.UPLOADED,
            )
            db.session.add(task)
            db.session.commit()
            process_task.delay(task.id)
            return get_task_detail(task), 201
        except Exception as e:
            return {"mensaje": str(e)}, 500


class TaskView(Resource):
    @jwt_required()
    def get(self, task_id):
        task = Task.query.filter_by(
            id=task_id, created_by_id=current_user.id
        ).one_or_none()

        if task is None:
            return {"mensaje": "Tarea no encontrada"}, 404
        return get_task_detail(task)

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.filter_by(
            id=task_id, created_by_id=current_user.id
        ).one_or_none()

        if task is None:
            return {"mensaje": "Tarea no encontrada"}, 404

        db.session.delete(task)
        db.session.commit()

        delete_file(task.video_path)
        if task.processed_video_path:
            delete_file(task.processed_video_path)

        return {"mensaje": "Tarea eliminada exitosamente"}, 200
