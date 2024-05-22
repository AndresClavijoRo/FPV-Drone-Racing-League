# Executes load testing on the celery server
# Usage: python3 load_testing.py number_of_tasks
from typing import List
import datetime
import os
from uuid import uuid4
import shutil
import csv
import glob
import time



from google.cloud import storage
import config

from models import db, Task, User, TaskStatus
from process_task import process_task
from views.tasks import publish_task

WAIT_PER_TAKS = 60
MAX_CPU = 0.95 * 100
VIDEO_PATH = os.path.abspath("load_testing_video.mp4")
BASE_PATH = "load_testing"


def upload_video(video_path: str):
    """Upload video to the server."""
    client = storage.Client()
    blob = client.bucket(config.GOOGLE_STORAGE_BUCKET).blob(video_path)
    blob.upload_from_filename(VIDEO_PATH)


def upload_from_directory(directory_path: str, dest_blob_name: str):
    rel_paths = glob.glob(directory_path + "/**", recursive=True)
    client = storage.Client()
    bucket = client.get_bucket(config.GOOGLE_STORAGE_BUCKET)
    for local_file in rel_paths:
        remote_path = f'{dest_blob_name}/{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def create_task(folder_path: str, total_tasks: int) -> List[Task]:
    """Create queued tasks."""
    user = User.query.first()
    if not user:
        user = User(username="test", email="test", hashed_password="test")
        db.session.add(user)
        db.session.commit()
    tasks = []
    for _i in range(total_tasks):
        uuid = uuid4()
        video_folder = os.path.join(folder_path, str(uuid))
        video_path = os.path.abspath(os.path.join(video_folder, "video.mp4"))
        # Upload video
        upload_video(video_path)
        task = Task(
            status=TaskStatus.UPLOADED,
            created_by_id=user.id,
            video_path=video_path,
            file_name="test_video.mp4",
        )
        db.session.add(task)
        tasks.append(task)
    db.session.commit()
    return [t.id for t in tasks]


def delete_tasks(taks_ids: List[int]):
    """Delete tasks with results."""
    for task_id in taks_ids:
        task: Task = Task.query.get(task_id)
        client = storage.Client()
        bucket = client.bucket(config.GOOGLE_STORAGE_BUCKET)
        blobs = list(bucket.list_blobs(prefix=os.path.dirname(task.video_path)))
        bucket.delete_blobs(blobs)
        db.session.delete(task)


def write_results(
    folder_path: str, results: List[int]
) :
    """Write results to a csv file.
    Additionally says if all were processed correctly
    """
    # Ensure session is
    with open(f"{folder_path}/results.csv", mode="w") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "task_id",
                "status",
                "processing_time_seconds",
                "processing_started_at",
                "processing_ended_at",
            ]
        )
        for i, task_id in enumerate(results):
            task: Task = Task.query.get(task_id)
            writer.writerow(
                [
                    task.id,
                    task.status,
                    (
                        (
                            task.processing_ended_at - task.processing_started_at
                        ).total_seconds()
                        if task.processing_ended_at and task.processing_started_at
                        else None
                    ),
                    (
                        task.processing_started_at.isoformat()
                        if task.processing_started_at
                        else None
                    ),
                    (
                        task.processing_ended_at.isoformat()
                        if task.processing_ended_at
                        else None
                    )
                ]
            )

def wait_for_results(task_ids:List[int],end_at:datetime.datetime):
    """Use the database to check if all task are completed."""
    while datetime.datetime.now() < end_at:
        print("Waiting for results", (end_at - datetime.datetime.now()).total_seconds())
        db.session.close()
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        task_completed =[task.status == TaskStatus.PROCESSED for task in tasks]
        if all(task_completed):
            return
        print("Completed",task_completed.count(True), "of", len(task_completed))
        time.sleep(5)

def load_test( total_tasks: int, total_minutes: int):
    # Create tasks
    start_at = datetime.datetime.now()
    print(f"Starting load testing at {start_at} and max {total_minutes} minutes")
    # Create results folder
    folder_path = f"{BASE_PATH}/{start_at.isoformat()}"
    os.makedirs(folder_path, exist_ok=True)
    task_ids = create_task(folder_path, total_tasks)
    # Publish results to google
    for task_id in task_ids:
        publish_task(task_id)
    print(task_ids)
    end_at = datetime.datetime.now() + datetime.timedelta(minutes=total_minutes)
    # Wait for results
    wait_for_results(task_ids, end_at)
    # Write csv
    write_results(folder_path, task_ids)
    delete_tasks(task_ids)
    upload_from_directory(folder_path, folder_path)
    print(
        "Load testing finished",
        end_at,
        "total time",
        (end_at - start_at).total_seconds(),
    )
    # Delete folder
    shutil.rmtree(BASE_PATH)