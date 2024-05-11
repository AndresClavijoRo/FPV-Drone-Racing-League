import datetime
import logging
import uuid
import os

from google.cloud import storage

from moviepy.editor import VideoFileClip, vfx, ImageClip, CompositeVideoClip

from models import Task, TaskStatus, db
import config


logger = logging.getLogger(__name__)


def change_aspect_ratio(clip: VideoFileClip) -> VideoFileClip:
    clip_resized = clip.resize(height=720)  # Resize height to 720p
    clip_resized = clip_resized.fx(
        vfx.crop,
        x_center=clip_resized.w / 2,
        y_center=clip_resized.h / 2,
        width=int(clip_resized.w),
        height=int(clip_resized.h * 9 / 16),
    )  # Crop to 16:9
    return clip_resized


def download_video_from_google_storage_cloud(video_path: str, file_path: str):
    client = storage.Client()
    bucket = client.bucket(config.GOOGLE_STORAGE_BUCKET)
    blob = bucket.blob(video_path)
    blob.download_to_filename(file_path)


def upload_video_to_google_storage_cloud(video_path):
    client = storage.Client()
    blob = client.bucket(config.GOOGLE_STORAGE_BUCKET).blob(video_path)
    blob.upload_from_filename(video_path)


def process_task(task_id: int):
    task: Task = Task.query.get(task_id)
    if not task or task.status != TaskStatus.UPLOADED:
        logger.error(f"Task with id {task_id} not found")
        return
    file_path = task.video_path
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    download_video_from_google_storage_cloud(task.video_path, file_path)

    task.processing_started_at = datetime.datetime.now()
    try:
        video = VideoFileClip(file_path)
        processed_video = change_aspect_ratio(video)
        # Crop to 20 seconds
        processed_video = processed_video.subclip(0, min(20, processed_video.duration))
        # Add frames for log
        image = change_aspect_ratio(
            (
                ImageClip("fpv_logo.png")
                .set_duration(1)
                .set_position(("center", "center"))
            )
        )
        processed_video_path = task.video_path.replace(".mp4", "_processed.mp4")
        final_video = CompositeVideoClip(
            [
                image,
                processed_video.set_start(1),
                image.set_start(processed_video.duration + 1),
            ]
        )
        final_video.write_videofile(
            processed_video_path, temp_audiofile=f"{uuid.uuid4()}.mp3", remove_temp=True
        )
        task.processed_video_path = processed_video_path
        task.status = TaskStatus.PROCESSED
        upload_video_to_google_storage_cloud(processed_video_path)

        # Delete folder with videos
        folder_path = os.path.dirname(task.video_path)
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            os.remove(file_path)
        os.rmdir(folder_path)
    except Exception:
        logger.exception("Could not process the video")
    finally:
        task.processing_ended_at = datetime.datetime.now()
        db.session.commit()
