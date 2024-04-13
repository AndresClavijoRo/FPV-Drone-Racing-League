import datetime
import logging

from celery import shared_task

from moviepy.editor import VideoFileClip, vfx, ImageClip, CompositeVideoClip

from models import Task, TaskStatus, db


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


@shared_task(ignore_result=False)
def process_task(task_id: int):
    task: Task = Task.query.get(task_id)
    if not task:
        logger.error(f"Task with id {task_id} not found")
        return
    task.processing_started_at = datetime.datetime.now()
    try:
        video = VideoFileClip(task.video_path)
        processed_video = change_aspect_ratio(video)
        # Crop to 20 seconds
        processed_video = processed_video.subclip(0, min(20, processed_video.duration))
        # Add frames for log
        image = change_aspect_ratio((
            ImageClip("fpv_logo.png").set_duration(1).set_position(("center", "center"))
        ))
        processed_video_path = task.video_path.replace(".mp4", "_processed.mp4")
        final_video = CompositeVideoClip(
            [
                image,
                processed_video.set_start(1),
                image.set_start(processed_video.duration + 1),
            ]
        )
        final_video.write_videofile(processed_video_path)
        task.processed_video_path = processed_video_path
        task.status = TaskStatus.PROCESSED
    except Exception:
        logger.exception("Could not process the video")
    finally:
        task.processing_ended_at = datetime.datetime.now()
        db.session.commit()
