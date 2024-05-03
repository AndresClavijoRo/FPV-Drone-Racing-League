import os
import uuid
from datetime import datetime, timedelta

from flask import request
from flask_restful import Resource
from flask_jwt_extended import current_user, jwt_required
from werkzeug.utils import secure_filename
from google.cloud import storage
from google import auth
from google.auth.transport import requests

from models import db, Task, TaskStatus
from views.validaciones_video import validaciones_video
from celery_tasks import process_task
import config


def upload_video_to_google_storage_cloud(file: "File", video_path: str) -> str:
    client = storage.Client()
    blob = client.bucket(config.GOOGLE_STORAGE_BUCKET).blob(video_path)
    blob.upload_from_file(file)
    return blob.public_url


def get_signed_url(video_path: str) -> str:
    if credentiasl_path := os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        credentials, _x = auth.load_credentials_from_file(
            credentiasl_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
    else:
        credentials, _project_id = auth.default()
    client = storage.Client()
    bucket = client.bucket(config.GOOGLE_STORAGE_BUCKET)
    blob = bucket.blob(video_path)
    if credentials.token is None:
        #     # Perform a refresh request to populate the access token of the
        #     # current credentials.
        credentials.refresh(requests.Request())
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(hours=config.URL_HOURS_TO_EXPIRE),
        method="GET",
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
    )


def get_task_detail(task: Task) -> dict:
    return {
        "id": task.id,
        "file_name": task.file_name,
        "status": task.status.value,
        "uploaded_video_path": get_signed_url(task.video_path),
        "processed_video_path": (
            get_signed_url(task.processed_video_path)
            if task.processed_video_path
            else None
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
        ),
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
        def is_it_true(value):
            return value.lower() == 'true'
        trigger_task = request.args.get("trigger_task", default=True, type=is_it_true)
        video = request.files["fileName"]

        validaciones = validaciones_video(video)

        if validaciones.valid is False:
            return {"mensaje": validaciones.mensaje}, 400

        # Upload video to google storage cloud
        filename = secure_filename(video.filename)
        vide_path = f"{uuid.uuid4()}/{filename}"
        upload_video_to_google_storage_cloud(video, vide_path)
        try:
            # Crea una nueva tarea
            task = Task(
                created_by_id=current_user.id,
                file_name=filename,
                video_path=vide_path,
                status=TaskStatus.UPLOADED,
            )
            db.session.add(task)
            db.session.commit()
            if trigger_task:
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
        if task.status != TaskStatus.PROCESSED:
            return {"mensaje": "No se puede eliminar una tarea no procesada"}, 400

        db.session.delete(task)
        db.session.commit()

        folder_path = os.path.dirname(task.video_path)

        # Delete from cloud storage
        client = storage.Client()
        bucket = client.bucket(config.GOOGLE_STORAGE_BUCKET)
        blobs = list(bucket.list_blobs(prefix=folder_path))
        bucket.delete_blobs(blobs)
        return {"mensaje": "Tarea eliminada exitosamente"}, 200
